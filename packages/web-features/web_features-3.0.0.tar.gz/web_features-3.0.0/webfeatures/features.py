from dataclasses import dataclass
from datetime import date
from enum import StrEnum
from typing import Annotated, Any, Literal, Mapping, Optional, Union

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field


class BaselineStatus(StrEnum):
    none = "none"
    low = "low"
    high = "high"


@dataclass
class BaselineDate:
    date: date
    is_upper_bound: bool = False


def ensure_list(value: Any) -> list[Any]:
    if not isinstance(value, list):
        return [value]
    return value


def to_baseline_status(value: Any) -> BaselineStatus:
    if value is False:
        return BaselineStatus.none
    if value == "low":
        return BaselineStatus.low
    if value == "high":
        return BaselineStatus.high
    raise ValueError(f"{value} is not a valid BaselineStatus")


def to_baseline_date(value: Any) -> BaselineDate:
    if not isinstance(value, str):
        raise ValueError(f"{value} is not a string")

    is_upper_bound = False
    if value[0] == "≤":
        is_upper_bound = True
        value = value[1:]

    return BaselineDate(date=date.fromisoformat(value), is_upper_bound=is_upper_bound)


class BrowserVersion(BaseModel):
    date: date
    version: str


class BrowserData(BaseModel):
    name: str
    releases: list[BrowserVersion]


class CompatKeyStatus(BaseModel):
    baseline: Annotated[BaselineStatus, BeforeValidator(to_baseline_status)]
    baseline_high_date: Optional[
        Annotated[BaselineDate, BeforeValidator(to_baseline_date)]
    ] = None
    baseline_low_date: Optional[
        Annotated[BaselineDate, BeforeValidator(to_baseline_date)]
    ] = None
    support: Mapping[str, str]


class FeatureStatus(BaseModel):
    baseline: Annotated[BaselineStatus, BeforeValidator(to_baseline_status)]
    baseline_high_date: Optional[
        Annotated[BaselineDate, BeforeValidator(to_baseline_date)]
    ] = None
    baseline_low_date: Optional[
        Annotated[BaselineDate, BeforeValidator(to_baseline_date)]
    ] = None
    by_compat_key: Mapping[str, CompatKeyStatus] = {}
    support: Mapping[str, str]


class FeatureDiscouraged(BaseModel):
    according_to: Annotated[list[str], BeforeValidator(ensure_list)] = []
    alternatives: Annotated[list[str], BeforeValidator(ensure_list)] = []


class Feature(BaseModel):
    kind: Literal["feature"]

    caniuse: Annotated[list[str], BeforeValidator(ensure_list)] = []
    compat_features: Annotated[list[str], BeforeValidator(ensure_list)] = []
    description: str
    description_html: str
    discouraged: Optional[FeatureDiscouraged] = None
    group: Annotated[list[str], BeforeValidator(ensure_list)] = []
    name: str
    spec: Annotated[list[str], BeforeValidator(ensure_list)] = []
    snapshot: Annotated[list[str], BeforeValidator(ensure_list)] = []
    status: FeatureStatus


class FeatureMoved(BaseModel):
    kind: Literal["moved"]

    redirect_target: str


class FeatureSplit(BaseModel):
    kind: Literal["split"]

    redirect_targets: list[str]


class Group(BaseModel):
    name: str
    parent: Optional[str] = None


class Snapshot(BaseModel):
    name: str
    spec: str


class FeaturesFile(BaseModel):
    model_config = ConfigDict(validate_by_alias=True)

    browsers: Mapping[str, BrowserData]
    features: Mapping[
        str,
        Annotated[
            Union[Feature, FeatureMoved, FeatureSplit], Field(discriminator="kind")
        ],
    ]
    groups: Mapping[str, Group]
    snapshots: Mapping[str, Snapshot]
