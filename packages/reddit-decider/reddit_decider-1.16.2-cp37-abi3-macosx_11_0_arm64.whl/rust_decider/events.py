import json

from abc import ABC
from abc import abstractmethod
from copy import deepcopy
from dataclasses import dataclass
from enum import Enum
from typing import Callable
from typing import Optional


class EventType(Enum):
    EXPOSE = "expose"


@dataclass
class Experiment:
    id: int
    version: str
    name: str
    variant: str
    bucket_val: str  # corresponds to bucketing_key in v2 event schema
    start_ts: Optional[int]
    stop_ts: Optional[int]
    bucketing_value: str
    is_override: Optional[bool]


class ExposerABC(ABC):
    def __init__(self, expose_fn: Callable):
        self._expose_fn = expose_fn

    @abstractmethod
    def expose_event(self, event: str) -> None:
        pass


class Exposer(ExposerABC):
    def expose_event(self, event: str) -> None:
        if event and self._expose_fn:
            self._expose_fn(event)


class ExperimentLoggerExposerAdapter(Exposer):
    def __init__(self, logger):
        self._logger = logger

    def expose_event(self, event: str):
        if event and self._logger:
            event_dict = self._make_event_dict(event)
            self._logger.log(**event_dict)

    def _make_event_dict(self, event_str: str) -> dict:
        """
        Convert thrift event schema json string into dict used as params by ExperimentLogger.

        e.g. turns:
            {
                "1": {"str": "experiment"},
                "2": {"str": "expose"},
                "3": {"str": "user_id"},
                "107": {
                    "rec": {
                        "2": {"str": "ios"},
                        "4": {"i32": 1234},
                        "6": {"str": "us_en"
                    }
                }
                ...
            }
        into:
            {
                "source": "experiment",
                "action": "expose",
                "noun": "user_id",
                "app": {
                    "name": "ios",
                    "build_number": 1234,
                    "relevant_locale": "us_en"
                }
                ...
            }

        Based around the ExperimentLogger definition that can be found here:
            https://github.snooguts.net/reddit/data-schemas/blob/master/thrift_packages/py/event_utils/v2_event_utils.py
        ExperimentLogger has been copy/pasted across many repos with some modifications for which fields get exposed.

        Those modifications are no longer supported, since the expose event has been pruned to this protobuf schema:
            https://github.snooguts.net/reddit/event-schema-protos/blob/main/proto/events/experiments-team/experiment__expose.proto
        and only fields that are defined in Decider's context and propogated from the Decision
        have been mapped to their thrift json serialized v2 event schema counterpart.
        """
        event_fields = {}
        event = json.loads(event_str)
        for e_num, e_schema in event.items():
            e_map = EVENT_FIELD_MAPPING.get(e_num)
            if e_map:
                event_fields[e_map["field_name"]] = e_map["schema_to_struct_fn"](
                    e_schema
                )

        experiment = event_fields.pop("experiment")
        full_fields = self._add_flattened_fields(event_fields)
        full_fields = {
            **full_fields,
            **{experiment.bucket_val: experiment.bucketing_value},
        }

        return dict(
            experiment=experiment,
            variant=experiment.variant,
            span=None,
            event_type=EventType.EXPOSE,
            inputs=full_fields,
            **full_fields,
        )

    def _add_flattened_fields(self, event_fields: dict) -> dict:
        """
        Add fields that are accessed as top-level kwargs, or from "inputs" kwarg.

        See here:
            https://github.snooguts.net/reddit/data-schemas/blob/36d11b5c9519b48b2c49b5adda23cbe9a95b8875/thrift_packages/py/event_utils/v2_event_utils.py#L137-L138
        """
        inputs = deepcopy(event_fields)

        app_struct = inputs.get("app", {})

        app_name = app_struct.get("name")
        if app_name:
            inputs["app_name"] = app_name

        build_number = app_struct.get("build_number")
        if build_number:
            inputs["build_number"] = build_number

        user_is_employee = inputs.get("user", {}).get("is_employee")
        if user_is_employee:
            inputs["user_is_employee"] = user_is_employee

        subreddit_id = inputs.get("subreddit", {}).get("id")
        if subreddit_id:
            inputs["subreddit_id"] = subreddit_id

        user_dict = inputs.get("user", {})
        user_dict.pop("id", None)
        user_dict.pop("is_employee", None)

        return {
            **inputs,
            **inputs.get("platform", {}),
            **inputs.get("request", {}),
            **inputs.get("geo", {}),
            **user_dict,
        }


def parse_experiment_schema(experiment_schema: dict) -> Experiment:
    exp_data = experiment_schema["rec"]
    is_override = exp_data.get("10", {}).get("tf")

    return Experiment(
        id=exp_data["1"]["i64"],
        name=exp_data["2"]["str"],
        variant=exp_data["4"]["str"],
        start_ts=exp_data.get("5", {}).get("i64"),
        stop_ts=exp_data.get("6", {}).get("i64"),
        bucket_val=exp_data["7"]["str"],
        version=exp_data["8"]["str"],
        bucketing_value=exp_data["9"]["str"],
        is_override=bool(is_override) if is_override is not None else None,
    )


def parse_top_level_str_schema(schema: dict):
    return schema["str"]


def parse_top_level_i64_schema(schema: dict):
    return schema["i64"]


def event_mapping_dict(field_name: str, parsing_fn: Callable):
    return {"field_name": field_name, "schema_to_struct_fn": parsing_fn}


def parse_app_schema(app_schema: dict) -> dict:
    app_data = app_schema["rec"]
    app_struct = {}

    name = app_data.get("2", {}).get("str")
    if name:
        app_struct["name"] = name

    build_number = app_data.get("4", {}).get("i32")
    if build_number:
        app_struct["build_number"] = build_number

    relevant_locale = app_data.get("6", {}).get("str")
    if relevant_locale:
        app_struct["relevant_locale"] = relevant_locale

    return app_struct


def parse_platform_schema(platform_schema: dict) -> dict:
    platform_data = platform_schema["rec"]
    platform_struct = {}

    device_id = platform_data.get("2", {}).get("str")
    if device_id:
        platform_struct["device_id"] = device_id

    return platform_struct


def parse_request_schema(request_schema: dict) -> dict:
    request_data = request_schema["rec"]
    request_struct = {}

    canonical_url = request_data.get("17", {}).get("str")
    if canonical_url:
        request_struct["canonical_url"] = canonical_url

    base_url = request_data.get("3", {}).get("str")
    if base_url:
        request_struct["base_url"] = base_url

    user_agent = request_data.get("1", {}).get("str")
    if user_agent:
        request_struct["user_agent"] = user_agent

    return request_struct


def parse_referrer_schema(referrer_schema: dict) -> dict:
    referrer_data = referrer_schema["rec"]
    referrer_struct = {}

    url = referrer_data.get("2", {}).get("str")
    if url:
        referrer_struct["url"] = url

    return referrer_struct


def parse_user_schema(user_schema: dict) -> dict:
    user_data = user_schema["rec"]
    user_struct = {}

    user_id = user_data.get("1", {}).get("str")
    if user_id:
        user_struct["user_id"] = user_id

    logged_in = user_data.get("3", {}).get("tf")
    if logged_in is not None:
        user_struct["logged_in"] = bool(logged_in)

    cookie_created_timestamp = user_data.get("4", {}).get("i64")
    if cookie_created_timestamp:
        user_struct["cookie_created_timestamp"] = cookie_created_timestamp

    is_employee = user_data.get("16", {}).get("tf")
    if is_employee is not None:
        user_struct["is_employee"] = bool(is_employee)

    return user_struct


def parse_subreddit_schema(subreddit_schema: dict) -> dict:
    subreddit_data = subreddit_schema["rec"]
    subreddit_struct = {}

    id = subreddit_data.get("1", {}).get("str")
    if id:
        subreddit_struct["id"] = id

    return subreddit_struct


def parse_geo_schema(geo_schema: dict) -> dict:
    geo_data = geo_schema["rec"]
    geo_struct = {}

    country_code = geo_data.get("1", {}).get("str")
    if country_code:
        geo_struct["country_code"] = country_code

    return geo_struct


EVENT_FIELD_MAPPING = {
    "1": event_mapping_dict("source", parse_top_level_str_schema),
    "2": event_mapping_dict("action", parse_top_level_str_schema),
    "3": event_mapping_dict("noun", parse_top_level_str_schema),
    "5": event_mapping_dict("client_timestamp", parse_top_level_i64_schema),
    "6": event_mapping_dict("uuid", parse_top_level_str_schema),
    "8": event_mapping_dict("correlation_id", parse_top_level_str_schema),
    "107": event_mapping_dict("app", parse_app_schema),
    "108": event_mapping_dict("platform", parse_platform_schema),
    "109": event_mapping_dict("request", parse_request_schema),
    "110": event_mapping_dict("referrer", parse_referrer_schema),
    "112": event_mapping_dict("user", parse_user_schema),
    "114": event_mapping_dict("subreddit", parse_subreddit_schema),
    "129": event_mapping_dict("experiment", parse_experiment_schema),
    "500": event_mapping_dict("geo", parse_geo_schema),
}
