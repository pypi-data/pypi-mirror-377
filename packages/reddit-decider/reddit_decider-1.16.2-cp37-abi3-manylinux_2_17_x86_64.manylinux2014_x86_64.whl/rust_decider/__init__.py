import logging

from typing import Any
from typing import Callable
from typing import Dict
from typing import ItemsView
from typing import Iterator
from typing import KeysView
from typing import List
from typing import Mapping
from typing import Optional
from typing import Union
from typing import ValuesView

from .events import Exposer
from .prometheus_metrics import decider_client_counter
from .rust_decider import Decider as PyDecider
from .rust_decider import DeciderException
from .rust_decider import DeciderInitException
from .rust_decider import FeatureNotFoundException
from .rust_decider import init  # noqa: F401
from .rust_decider import make_ctx
from .rust_decider import PartialLoadException
from .rust_decider import ValueTypeMismatchException
from .rust_decider import version

logger = logging.getLogger(__name__)

DEFAULT_DECISIONMAKERS = (
    "darkmode overrides targeting holdout mutex_group fractional_availability value"
)

JsonValue = Union[
    None, int, float, str, bool, List["JsonValue"], Mapping[str, "JsonValue"]
]


class BaseMapping(Mapping[str, Any]):
    def keys(self) -> KeysView[str]:
        return self.__dict__.keys()

    def items(self) -> ItemsView[str, Any]:
        return self.__dict__.items()

    def values(self) -> ValuesView[Any]:
        return self.__dict__.values()

    def get(self, key: str, default=None) -> Optional[Any]:
        return self.__dict__.get(key, default)

    def __contains__(self, key: str) -> bool:
        return key in self.__dict__

    def __getitem__(self, key: str) -> Any:
        return self.__dict__[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self.__dict__)

    def __len__(self) -> int:
        return len(self.__dict__)


class Decision(BaseMapping):
    def __init__(
        self,
        variant: Optional[str],
        value: Optional[JsonValue],
        feature_id: int,
        feature_name: str,
        feature_version: int,
        events: List[str],
        full_events: List[str],
    ):
        self.variant = variant
        self.value = value
        self.feature_id = feature_id
        self.feature_name = feature_name
        self.feature_version = feature_version
        self.events = events
        self.full_events = full_events


class Feature(BaseMapping):
    def __init__(
        self,
        id: int,
        name: str,
        version: int,
        bucket_val: str,
        start_ts: int,
        stop_ts: int,
        emit_event: bool,
        measured: bool,
        owner: str = None,
    ):
        self.id = id
        self.name = name
        self.version = version
        self.bucket_val = bucket_val
        self.start_ts = start_ts
        self.stop_ts = stop_ts
        self.emit_event = emit_event
        self.measured = measured


class Event(BaseMapping):
    def __init__(
        self,
        decision_kind: str,
        exposure_key: str,
        json_str: str,
    ):
        self.decision_kind = decision_kind
        self.exposure_key = exposure_key
        self.json_str = json_str  # thrift encoded v2 event schema json string


class Decider:
    """Decider class wraps python bindings for Rust decider crate."""

    def __init__(self, path: str, exposer: Optional[Exposer] = None):
        """Initialize a :code:`Decider` class using config file at specified :code:`path`.

        Takes an optional :code:`Exposer` class to emit expose events directly
        (enabled via `expose` bool param in bucketing API).

        Raises :code:`PartialLoadException` if an error occurs when initializing :code:`Decider`
        and any of the features in the config file are malformed.

        Raises general :code:`DeciderInitException` if an error occurs when initializing :code:`Decider`
        (:code:`PartialLoadException` is a sub-exception of :code:`DeciderInitException`).
        """
        self._pkg_version = version()
        self._exposer = exposer

        try:
            self._decider = PyDecider(path)
        except PartialLoadException as e:
            decider_client_counter.labels(
                operation="init",
                success="false",
                error_type="partial_init_exception",
                pkg_version=self._pkg_version,
            ).inc()

            # log errors of misconfigured features
            logger.error(f"{e.args[0]}: {e.args[2]}")

            # set _decider to partially initialized PyDecider instance
            self._decider = e.args[1]
            return
        except DeciderInitException as e:
            decider_client_counter.labels(
                operation="init",
                success="false",
                error_type="init_exception",
                pkg_version=self._pkg_version,
            ).inc()
            raise e

        decider_client_counter.labels(
            operation="init",
            success="true",
            error_type="",
            pkg_version=self._pkg_version,
        ).inc()

    def choose(
        self,
        feature_name: str,
        context: Mapping[str, JsonValue],
        expose: Optional[bool] = False,
        expose_holdout: Optional[bool] = False,
    ) -> Decision:
        """Return a :code:`Decision` for a given :code:`feature_name` and :code:`context`.

        If dict() is called on the Decision instance, the following fields are returned:
            .. code-block:: python
            {
                "variant": Optional[str],
                "value": Optional[JsonValue],
                "feature_id": int,
                "feature_name": str,
                "feature_version": int,
                "events": [str]
            }

        Raises :code:`DeciderException` if an error occurs when fetching the Decision.

        :param feature_name: Name of feature you want a variant or value for.

        :param context: A required :code:`Mapping[str, JsonValue]` of context fields used for
            feature overrides, targeting, & bucketing.

        :param expose: Emit expose events via instance's :code:`self._exposer` if set to True.

        :param expose_holdout: Emit expose events for Holdout Groups via instance's :code:`self._exposer` if set to True,
            whih can be combined with :code:`expose=False` to only emit Holdout exposures.

        :return: A :code:`Decision` instance if feature is active/exists,
            raises a :code:`FeatureNotFoundException`
            (a sub-exception of :code:`DeciderException`) otherwise.
        """
        if context is None:
            decider_client_counter.labels(
                operation="choose",
                success="false",
                error_type="missing_context",
                pkg_version=self._pkg_version,
            ).inc()
            raise DeciderException(
                f"Missing `context` param for feature_name: {feature_name}"
            )

        ctx = make_ctx(context)
        ctx_err = ctx.err()
        if ctx_err:
            decider_client_counter.labels(
                operation="choose",
                success="false",
                error_type="invalid_context",
                pkg_version=self._pkg_version,
            ).inc()
            raise DeciderException(
                f"Encountered error from rust_decider.make_ctx() for context: {ctx_err}"
            )

        try:
            decision = self._decider.choose(feature_name, ctx)
        except FeatureNotFoundException as e:
            decider_client_counter.labels(
                operation="choose",
                success="false",
                error_type="feature_not_found",
                pkg_version=self._pkg_version,
            ).inc()
            raise e
        except DeciderException as e:
            decider_client_counter.labels(
                operation="choose",
                success="false",
                error_type="decider_exception",
                pkg_version=self._pkg_version,
            ).inc()
            raise e
        except Exception as e:
            decider_client_counter.labels(
                operation="choose",
                success="false",
                error_type="exception",
                pkg_version=self._pkg_version,
            ).inc()
            raise e

        decider_client_counter.labels(
            operation="choose",
            success="true",
            error_type="",
            pkg_version=self._pkg_version,
        ).inc()

        if (expose or expose_holdout) and self._exposer:
            for event in decision.events:
                if expose or (expose_holdout and event.decision_kind == "Holdout"):
                    try:
                        self._exposer.expose_event(event.json_str)
                    except Exception as e:
                        decider_client_counter.labels(
                            operation="choose",
                            success="false",
                            error_type="expose",
                            pkg_version=self._pkg_version,
                        ).inc()
                        raise e

        return Decision(
            variant=decision.variant_name,
            feature_id=decision.feature_id,
            feature_name=decision.feature_name,
            feature_version=decision.feature_version,
            value=decision.value,
            events=decision.event_data,  # legacy :::: delimited string format
            full_events=self._map_events(decision.events),
        )

    def _map_events(self, events) -> List[Event]:
        return [
            Event(
                decision_kind=e.decision_kind,
                exposure_key=e.exposure_key,
                json_str=e.json_str,
            )
            for e in events
        ]

    def choose_all(
        self,
        context: Mapping[str, JsonValue],
        bucketing_field_filter: Optional[str] = None,
    ) -> Dict[str, Decision]:
        """Return a :code:`Dict[str, Decision]` for all active features...

        with the key as the feature name (not including features
        of :code:`"type": "dynamic_config"`) using the :code:`context` for bucketing.

        If dict() is called on a Decision instance, the following fields are returned:
            .. code-block:: python
            {
                "variant": Optional[str],
                "value": Optional[JsonValue],
                "feature_id": int,
                "feature_name": str,
                "feature_version": int,
                "events": [str]
            }

        Raises :code:`DeciderException` if an error occurs.

        :param context: A required :code:`Mapping[str, JsonValue]` of context fields used for
            feature overrides, targeting, & bucketing.

        :param bucketing_field_filter: An optional string used to filter out features to be bucketed.
            Features with a "bucket_val" field that does not match the
            :code:`bucketing_field_filter` param will be excluded from bucketing.

        :return: A dict of Decision instances as the values and the corresponding
            feature name as the key.
        """
        if context is None:
            decider_client_counter.labels(
                operation="choose_all",
                success="false",
                error_type="missing_context",
                pkg_version=self._pkg_version,
            ).inc()
            raise DeciderException("Missing `context` param")

        ctx = make_ctx(context)
        ctx_err = ctx.err()
        if ctx_err:
            decider_client_counter.labels(
                operation="choose_all",
                success="false",
                error_type="invalid_context",
                pkg_version=self._pkg_version,
            ).inc()
            raise DeciderException(
                f"Encountered error from rust_decider.make_ctx() for context: {ctx_err}"
            )

        try:
            all_decisions = self._decider.choose_all(ctx, bucketing_field_filter)
        except Exception as e:
            decider_client_counter.labels(
                operation="choose_all",
                success="false",
                error_type="exception",
                pkg_version=self._pkg_version,
            ).inc()
            raise e

        output_decisions = {}

        for feature_name, decision in all_decisions.items():
            output_decisions[feature_name] = Decision(
                variant=decision.variant_name,
                feature_id=decision.feature_id,
                feature_name=decision.feature_name,
                feature_version=decision.feature_version,
                value=decision.value,
                events=decision.event_data,
                full_events=self._map_events(decision.events),
            )

        decider_client_counter.labels(
            operation="choose_all",
            success="true",
            error_type="",
            pkg_version=self._pkg_version,
        ).inc()

        return output_decisions

    def get_bool(self, feature_name: str, context: Mapping[str, JsonValue]) -> bool:
        """Fetch a Dynamic Configuration of boolean type.

        Raises :code:`DeciderException` if an error occurs when fetching DC.

        Raises :code:`ValueTypeMismatchException` (a sub-exception of :code:`DeciderException`)
        if requested feature is not of type boolean.

        :param feature_name: Name of the dynamic config you want a value for.

        :param context: A required :code:`Mapping[str, JsonValue]` of context fields used for
            feature overrides & targeting.

        :return: the boolean value of the dyanimc config if it is active/exists,
            raises a :code:`FeatureNotFoundException`
            (a sub-exception of :code:`DeciderException`) otherwise.
        """
        return self._get_dynamic_config_value(
            feature_name, context, self._decider.get_bool
        )

    def get_int(self, feature_name: str, context: Mapping[str, JsonValue]) -> int:
        """Fetch a Dynamic Configuration of int type.

        Raises :code:`DeciderException` if an error occurs when fetching DC.

        Raises :code:`ValueTypeMismatchException` (a sub-exception of :code:`DeciderException`)
        if requested feature is not of type integer.

        :param feature_name: Name of the dynamic config you want a value for.

        :param context: A required :code:`Mapping[str, JsonValue]` of context fields used for
            feature overrides & targeting.

        :return: the int value of the dyanimc config if it is active/exists,
            raises a :code:`FeatureNotFoundException`
            (a sub-exception of :code:`DeciderException`) otherwise.
        """
        return self._get_dynamic_config_value(
            feature_name, context, self._decider.get_int
        )

    def get_float(self, feature_name: str, context: Mapping[str, JsonValue]) -> float:
        """Fetch a Dynamic Configuration of float type.

        Raises :code:`DeciderException` if an error occurs when fetching DC.

        Raises :code:`ValueTypeMismatchException` (a sub-exception of :code:`DeciderException`)
        if requested feature is not of type float.

        :param feature_name: Name of the dynamic config you want a value for.

        :param context: A required :code:`Mapping[str, JsonValue]` of context fields used for
            feature overrides & targeting.

        :return: the float value of the dyanimc config if it is active/exists,
            raises a :code:`FeatureNotFoundException`
            (a sub-exception of :code:`DeciderException`) otherwise.
        """
        return self._get_dynamic_config_value(
            feature_name, context, self._decider.get_float
        )

    def get_string(self, feature_name: str, context: Mapping[str, JsonValue]) -> str:
        """Fetch a Dynamic Configuration of string type.

        Raises :code:`DeciderException` if an error occurs when fetching DC.

        Raises :code:`ValueTypeMismatchException` (a sub-exception of :code:`DeciderException`)
        if requested feature is not of type string.

        :param feature_name: Name of the dynamic config you want a value for.

        :param context: A required :code:`Mapping[str, JsonValue]` of context fields used for
            feature overrides & targeting.

        :return: the string value of the dyanimc config if it is active/exists,
            raises a :code:`FeatureNotFoundException`
            (a sub-exception of :code:`DeciderException`) otherwise.
        """
        return self._get_dynamic_config_value(
            feature_name, context, self._decider.get_string
        )

    def get_map(
        self, feature_name: str, context: Mapping[str, JsonValue]
    ) -> Optional[dict]:
        """Fetch a Dynamic Configuration of map type.

        Raises :code:`DeciderException` if an error occurs when fetching DC.

        Raises :code:`ValueTypeMismatchException` (a sub-exception of :code:`DeciderException`)
        if requested feature is not of type map.

        :param feature_name: Name of the dynamic config you want a value for.

        :param context: A required :code:`Mapping[str, JsonValue]` of context fields used for
            feature overrides & targeting.

        :return: the map value of the dyanimc config if it is active/exists,
            raises a :code:`FeatureNotFoundException`
            (a sub-exception of :code:`DeciderException`) otherwise.
        """
        return self._get_dynamic_config_value(
            feature_name, context, self._decider.get_map
        )

    def _get_dynamic_config_value(
        self,
        feature_name: str,
        context: Mapping[str, JsonValue],
        get_fn: Callable,
    ) -> Optional[Any]:
        dc_type = get_fn.__name__

        if context is None:
            decider_client_counter.labels(
                operation=f"{dc_type}",
                success="false",
                error_type="missing_context",
                pkg_version=self._pkg_version,
            ).inc()
            raise DeciderException(
                f"Missing `context` param for feature_name: {feature_name}"
            )

        ctx = make_ctx(context)
        ctx_err = ctx.err()
        if ctx_err:
            decider_client_counter.labels(
                operation=f"{dc_type}",
                success="false",
                error_type="invalid_context",
                pkg_version=self._pkg_version,
            ).inc()
            raise DeciderException(
                f"Encountered error from rust_decider.make_ctx(): {ctx_err}"
            )

        try:
            dc = get_fn(feature_name, ctx)
        except FeatureNotFoundException as e:
            decider_client_counter.labels(
                operation=f"{dc_type}",
                success="false",
                error_type="feature_not_found",
                pkg_version=self._pkg_version,
            ).inc()
            raise e
        except ValueTypeMismatchException as e:
            decider_client_counter.labels(
                operation=f"{dc_type}",
                success="false",
                error_type="type_mismatch",
                pkg_version=self._pkg_version,
            ).inc()
            raise e
        except DeciderException as e:
            decider_client_counter.labels(
                operation=f"{dc_type}",
                success="false",
                error_type="decider_exception",
                pkg_version=self._pkg_version,
            ).inc()
            raise e
        except Exception as e:
            decider_client_counter.labels(
                operation=f"{dc_type}",
                success="false",
                error_type="exception",
                pkg_version=self._pkg_version,
            ).inc()
            raise e

        decider_client_counter.labels(
            operation=f"{dc_type}",
            success="true",
            error_type="",
            pkg_version=self._pkg_version,
        ).inc()

        return dc

    def all_values(
        self,
        context: Mapping[str, JsonValue],
    ) -> Dict[str, JsonValue]:
        """Return a :code:`Dict[str, JsonValue]` for all active Dynamic Configurations...

        (with the key as the feature_name) using the :code:`context` for overrides/targeting.

        The value of the return dict contains the Dynamic Config value.

        Dynamic Configurations that are malformed, fail parsing, or otherwise
        error for any reason are included in the response and have their respective default
        values set:

        .. code-block:: python

            boolean -> False
            integer -> 0
            float   -> 0.0
            string  -> ""
            map     -> {}

        :param context: A required :code:`Mapping[str, JsonValue]` of context fields used for
            feature overrides & targeting.

        :return: A dict of Dynamic Config :code:`JsonValue`s as the dict values and
        the corresponding :code:`feature_name` as the key.
        """
        if context is None:
            decider_client_counter.labels(
                operation="all_values",
                success="false",
                error_type="missing_context",
                pkg_version=self._pkg_version,
            ).inc()
            raise DeciderException("Missing `context` param")

        ctx = make_ctx(context)
        ctx_err = ctx.err()
        if ctx_err:
            decider_client_counter.labels(
                operation="all_values",
                success="false",
                error_type="invalid_context",
                pkg_version=self._pkg_version,
            ).inc()
            raise DeciderException(
                f"Encountered error from rust_decider.make_ctx() for context: {ctx_err}"
            )

        try:
            all_decisions = self._decider.all_values(ctx)
        except Exception as e:
            decider_client_counter.labels(
                operation="all_values",
                success="false",
                error_type="exception",
                pkg_version=self._pkg_version,
            ).inc()
            raise e

        values = {}

        for feature_name, decision in all_decisions.items():
            values[feature_name] = decision.value

        decider_client_counter.labels(
            operation="all_values",
            success="true",
            error_type="",
            pkg_version=self._pkg_version,
        ).inc()

        return values

    def get_feature(self, feature_name: str) -> Optional[Feature]:
        """Get a :py:class:`~rust_decider.Feature` representation of a feature...

        if it's active/exists, otherwise raises :code:`FeatureNotFoundException`
        (a sub-exception of :code:`DeciderException`).

        :param feature_name: Name of the feature to be fetched.

        :return: a :py:class:`~reddit_decider.Feature` representation
            of a feature if found, raises :code:`FeatureNotFoundException`
            (a sub-exception of :code:`DeciderException`) otherwise.
        """
        try:
            feature = self._decider.get_feature(feature_name)
        except FeatureNotFoundException as e:
            decider_client_counter.labels(
                operation="get_feature",
                success="false",
                error_type="feature_not_found",
                pkg_version=self._pkg_version,
            ).inc()
            raise e
        except DeciderException as e:
            decider_client_counter.labels(
                operation="get_feature",
                success="false",
                error_type="decider_exception",
                pkg_version=self._pkg_version,
            ).inc()
            raise e
        except Exception as e:
            decider_client_counter.labels(
                operation="get_feature",
                success="false",
                error_type="exception",
                pkg_version=self._pkg_version,
            ).inc()
            raise e

        decider_client_counter.labels(
            operation="get_feature",
            success="true",
            error_type="",
            pkg_version=self._pkg_version,
        ).inc()

        return Feature(
            id=feature.id,
            name=feature.name,
            version=feature.version,
            bucket_val=feature.bucket_val,
            start_ts=feature.start_ts,
            stop_ts=feature.stop_ts,
            emit_event=feature.emit_event,
            measured=feature.measured,
        )
