# generated by datamodel-codegen:
#   filename:  lightdash-dbt-2.0.json

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional, Union

from lightdash_pre_commit.parsers.base import BaseParserModel
from pydantic import ConfigDict, Field, RootModel, confloat, constr


class Version(Enum):
    number_2 = 2


class Docs(BaseParserModel):
    show: Optional[bool] = None


class Join(BaseParserModel):
    join: str
    sql_on: str
    always: Optional[bool] = None


class OrderFieldsBy(Enum):
    index = 'index'
    label = 'label'


class GroupDetails(BaseParserModel):
    label: constr(min_length=1)
    description: Optional[str] = None


class Type(Enum):
    percentile = 'percentile'
    median = 'median'
    average = 'average'
    boolean = 'boolean'
    count = 'count'
    count_distinct = 'count_distinct'
    date = 'date'
    max = 'max'
    min = 'min'
    number = 'number'
    string = 'string'
    sum = 'sum'


class Group(RootModel[constr(min_length=1)]):
    root: constr(min_length=1)


class Interval(Enum):
    """
    The default time interval to use when analyzing this time dimension
    """

    DAY = 'DAY'
    WEEK = 'WEEK'
    MONTH = 'MONTH'
    YEAR = 'YEAR'


class DefaultTimeDimension(BaseParserModel):
    """
    Specifies the default time dimension field and interval to use for time-based analysis on this metric. If specified, both field and interval are required. If there is already a default time dimension set in the model, this will override it.
    """

    field: str = Field(
        ..., description='The name of the field to use as the default time dimension'
    )
    interval: Interval = Field(
        ...,
        description='The default time interval to use when analyzing this time dimension',
    )


class Visibility(Enum):
    show = 'show'
    hide = 'hide'


class Spotlight(BaseParserModel):
    """
    Set the visibility and/or categories of a metric in Spotlight
    """

    visibility: Visibility
    categories: Optional[List[str]] = Field(
        None, description='An array of categories for the metric in Spotlight'
    )


class Spotlight1(BaseParserModel):
    """
    Set the visibility and/or categories of a metric in Spotlight
    """

    visibility: Optional[Visibility] = None
    categories: List[str] = Field(
        ..., description='An array of categories for the metric in Spotlight'
    )


class Metrics(BaseParserModel):
    type: Type
    label: Optional[constr(min_length=1)] = None
    description: Optional[constr(min_length=1)] = None
    sql: constr(min_length=1)
    hidden: Optional[bool] = None
    round: Optional[confloat(ge=0.0)] = Field(
        None, description='Rounds the metric to the specified number of decimal places'
    )
    format: Optional[str] = None
    percentile: Optional[float] = None
    groups: Optional[List[Group]] = Field(
        None,
        description='Groups are used to group dimensions and metrics in the sidebar. You can create nested groups up to 3 levels',
        max_length=3,
    )
    default_time_dimension: Optional[DefaultTimeDimension] = Field(
        None,
        description='Specifies the default time dimension field and interval to use for time-based analysis on this metric. If specified, both field and interval are required. If there is already a default time dimension set in the model, this will override it.',
    )
    spotlight: Optional[Union[Spotlight, Spotlight1]] = Field(
        None,
        description='Set the visibility and/or categories of a metric in Spotlight',
    )


class DefaultTimeDimension1(BaseParserModel):
    """
    Specifies the default time dimension field and interval to use for time-based analysis (on any metric in the model). If specified, both field and interval are required.
    """

    field: str = Field(
        ..., description='The name of the field to use as the default time dimension'
    )
    interval: Interval = Field(
        ...,
        description='The default time interval to use when analyzing this time dimension',
    )


class Spotlight2(BaseParserModel):
    """
    Set the visibility and/or categories of a metric in Spotlight
    """

    visibility: Visibility
    categories: Optional[List[str]] = Field(
        None,
        description='An optional array of categories for all metrics in this model in Spotlight',
    )


class Spotlight3(BaseParserModel):
    """
    Set the visibility and/or categories of a metric in Spotlight
    """

    visibility: Optional[Visibility] = None
    categories: List[str] = Field(
        ...,
        description='An optional array of categories for all metrics in this model in Spotlight',
    )


class Meta(BaseParserModel):
    joins: Optional[List[Join]] = None
    order_fields_by: Optional[OrderFieldsBy] = None
    group_details: Optional[Dict[constr(pattern=r'^[a-zA-Z0-9_]+$'), GroupDetails]] = (
        Field(
            None,
            description='Set up group_details so you can group your dimensions and metrics in the sidebar using the groups parameter. You can create nested groups up to 3 levels',
        )
    )
    metrics: Optional[Dict[constr(pattern=r'^[a-z0-9_]+$'), Metrics]] = None
    default_time_dimension: Optional[DefaultTimeDimension1] = Field(
        None,
        description='Specifies the default time dimension field and interval to use for time-based analysis (on any metric in the model). If specified, both field and interval are required.',
    )
    spotlight: Optional[Union[Spotlight2, Spotlight3]] = Field(
        None,
        description='Set the visibility and/or categories of a metric in Spotlight',
    )


DefaultTimeDimension2 = DefaultTimeDimension


Spotlight4 = Spotlight


Spotlight5 = Spotlight1


class Metrics1(BaseParserModel):
    type: Type
    label: Optional[constr(min_length=1)] = None
    description: Optional[constr(min_length=1)] = None
    sql: Optional[constr(min_length=1)] = None
    hidden: Optional[bool] = None
    round: Optional[confloat(ge=0.0)] = None
    format: Optional[str] = None
    percentile: Optional[float] = None
    groups: Optional[List[Group]] = Field(
        None,
        description='Groups are used to group dimensions and metrics in the sidebar. You can create nested groups up to 3 levels',
        max_length=3,
    )
    default_time_dimension: Optional[DefaultTimeDimension2] = Field(
        None,
        description='Specifies the default time dimension field and interval to use for time-based analysis on this metric. If specified, both field and interval are required. If there is already a default time dimension set in the model, this will override it.',
    )
    spotlight: Optional[Union[Spotlight4, Spotlight5]] = Field(
        None,
        description='Set the visibility and/or categories of a metric in Spotlight',
    )


class Type2(Enum):
    string = 'string'
    number = 'number'
    timestamp = 'timestamp'
    date = 'date'
    boolean = 'boolean'


class TimeInterval(Enum):
    RAW = 'RAW'
    DAY = 'DAY'
    WEEK = 'WEEK'
    MONTH = 'MONTH'
    QUARTER = 'QUARTER'
    YEAR = 'YEAR'
    HOUR = 'HOUR'
    MINUTE = 'MINUTE'
    SECOND = 'SECOND'
    MILLISECOND = 'MILLISECOND'
    WEEK_NUM = 'WEEK_NUM'
    MONTH_NUM = 'MONTH_NUM'
    MONTH_NAME = 'MONTH_NAME'
    DAY_OF_WEEK_NAME = 'DAY_OF_WEEK_NAME'
    QUARTER_NAME = 'QUARTER_NAME'
    DAY_OF_WEEK_INDEX = 'DAY_OF_WEEK_INDEX'
    DAY_OF_MONTH_NUM = 'DAY_OF_MONTH_NUM'
    DAY_OF_YEAR_NUM = 'DAY_OF_YEAR_NUM'
    QUARTER_NUM = 'QUARTER_NUM'
    YEAR_NUM = 'YEAR_NUM'
    HOUR_OF_DAY_NUM = 'HOUR_OF_DAY_NUM'
    MINUTE_OF_HOUR_NUM = 'MINUTE_OF_HOUR_NUM'


class TimeIntervals(Enum):
    default = 'default'
    OFF = 'OFF'


class Dimension(BaseParserModel):
    type: Optional[Type2] = None
    label: Optional[constr(min_length=1)] = None
    description: Optional[constr(min_length=1)] = None
    sql: Optional[constr(min_length=1)] = None
    hidden: Optional[bool] = None
    round: Optional[confloat(ge=0.0)] = None
    format: Optional[str] = None
    time_intervals: Optional[Union[List[TimeInterval], TimeIntervals]] = None
    groups: Optional[List[Group]] = Field(
        None,
        description='Groups are used to group dimensions and metrics in the sidebar. You can create nested groups up to 3 levels',
        max_length=3,
    )


class AdditionalDimensions(BaseParserModel):
    type: Optional[Type2] = None
    label: Optional[constr(min_length=1)] = None
    description: Optional[constr(min_length=1)] = None
    sql: Optional[constr(min_length=1)] = None
    time_intervals: Optional[Union[List[TimeInterval], TimeIntervals]] = None


class Meta1(BaseParserModel):
    metrics: Optional[Dict[constr(pattern=r'^[a-z0-9_]+$'), Metrics1]] = None
    dimension: Optional[Dimension] = None
    additional_dimensions: Optional[
        Dict[constr(pattern=r'^[a-z0-9_]+$'), AdditionalDimensions]
    ] = None


class Column(BaseParserModel):
    name: Optional[str] = None
    description: Optional[str] = None
    quote: Optional[bool] = None
    tests: Optional[List[Union[Dict[str, Any], str]]] = None
    data_tests: Optional[List[Union[Dict[str, Any], str]]] = None
    tags: Optional[List[str]] = None
    meta: Optional[Meta1] = None


class Model(BaseParserModel):
    name: str
    description: Optional[str] = None
    docs: Optional[Docs] = None
    tests: Optional[List[Union[Dict[str, Any], str]]] = None
    data_tests: Optional[List[Union[Dict[str, Any], str]]] = None
    meta: Optional[Meta] = None
    columns: Optional[List[Column]] = None


DefaultTimeDimension3 = DefaultTimeDimension


Spotlight6 = Spotlight


Spotlight7 = Spotlight1


class Meta2(BaseParserModel):
    hidden: Optional[bool] = None
    round: Optional[confloat(ge=0.0)] = None
    format: Optional[str] = None
    default_time_dimension: Optional[DefaultTimeDimension3] = Field(
        None,
        description='Specifies the default time dimension field and interval to use for time-based analysis on this metric. If specified, both field and interval are required. If there is already a default time dimension set in the model, this will override it.',
    )
    spotlight: Optional[Union[Spotlight6, Spotlight7]] = Field(
        None,
        description='Set the visibility and/or categories of a metric in Spotlight',
    )


class Metric(BaseParserModel):
    name: str
    model: Optional[str] = None
    label: Optional[str] = None
    description: Optional[str] = None
    type: Optional[str] = None
    sql: Optional[str] = None
    timestamp: Optional[str] = None
    time_grains: Optional[List[str]] = None
    dimensions: Optional[List[str]] = None
    filters: Optional[List[Dict[str, Any]]] = None
    meta: Optional[Meta2] = None


class LightdashV20(BaseParserModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    version: Optional[Version] = None
    models: Optional[List[Model]] = None
    metrics: Optional[List[Metric]] = None
    seeds: Optional[List[Dict[str, Any]]] = None
    snapshots: Optional[List[Dict[str, Any]]] = None
    tests: Optional[List[Dict[str, Any]]] = None
    unit_tests: Optional[List[Dict[str, Any]]] = None
    sources: Optional[List[Dict[str, Any]]] = None
    analyses: Optional[List[Dict[str, Any]]] = None
    exposures: Optional[List[Dict[str, Any]]] = None
    macros: Optional[List[Dict[str, Any]]] = None
