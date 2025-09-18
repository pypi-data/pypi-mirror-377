import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.aggregation import Aggregation
from ..models.data_grouping import DataGrouping
from ..models.data_type import DataType
from ..types import UNSET, Unset

T = TypeVar("T", bound="ApiReadingsRequest")


@_attrs_define
class ApiReadingsRequest:
    """
    Example:
        {'dataTypes': ['normalised'], 'deltaAggregation': 'sum', 'groupTimeBy': 'quarterHour', 'limit': 1000, 'offset':
            0, 'tagId': '550e8400-e29b-41d4-a716-446655440000', 'timeEnd': '2023-11-14T22:15:00Z', 'timeStart':
            '2023-11-14T22:13:20Z', 'timezone': 'Europe/London', 'unitTo': None}

    Attributes:
        delta_aggregation (Aggregation):  Example: sum.
        tag_id (UUID):
        time_end (datetime.datetime):
        time_start (datetime.datetime):
        data_types (Union[None, Unset, list[DataType]]):
        group_time_by (Union[DataGrouping, None, Unset]):
        limit (Union[None, Unset, int]):
        offset (Union[None, Unset, int]):
        timezone (Union[None, Unset, str]): Timezone name, e.g. "Europe/London".
        unit_to (Union[None, Unset, str]):
    """

    delta_aggregation: Aggregation
    tag_id: UUID
    time_end: datetime.datetime
    time_start: datetime.datetime
    data_types: Union[None, Unset, list[DataType]] = UNSET
    group_time_by: Union[DataGrouping, None, Unset] = UNSET
    limit: Union[None, Unset, int] = UNSET
    offset: Union[None, Unset, int] = UNSET
    timezone: Union[None, Unset, str] = UNSET
    unit_to: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        delta_aggregation = self.delta_aggregation.value

        tag_id = str(self.tag_id)

        time_end = self.time_end.isoformat() + "Z"

        time_start = self.time_start.isoformat() + "Z"

        data_types: Union[None, Unset, list[str]]
        if isinstance(self.data_types, Unset):
            data_types = UNSET
        elif isinstance(self.data_types, list):
            data_types = []
            for data_types_type_0_item_data in self.data_types:
                data_types_type_0_item = data_types_type_0_item_data.value
                data_types.append(data_types_type_0_item)

        else:
            data_types = self.data_types

        group_time_by: Union[None, Unset, str]
        if isinstance(self.group_time_by, Unset):
            group_time_by = UNSET
        elif isinstance(self.group_time_by, DataGrouping):
            group_time_by = self.group_time_by.value
        else:
            group_time_by = self.group_time_by

        limit: Union[None, Unset, int]
        if isinstance(self.limit, Unset):
            limit = UNSET
        else:
            limit = self.limit

        offset: Union[None, Unset, int]
        if isinstance(self.offset, Unset):
            offset = UNSET
        else:
            offset = self.offset

        timezone: Union[None, Unset, str]
        if isinstance(self.timezone, Unset):
            timezone = UNSET
        else:
            timezone = self.timezone

        unit_to: Union[None, Unset, str]
        if isinstance(self.unit_to, Unset):
            unit_to = UNSET
        else:
            unit_to = self.unit_to

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "deltaAggregation": delta_aggregation,
                "tagId": tag_id,
                "timeEnd": time_end,
                "timeStart": time_start,
            }
        )
        if data_types is not UNSET:
            field_dict["dataTypes"] = data_types
        if group_time_by is not UNSET:
            field_dict["groupTimeBy"] = group_time_by
        if limit is not UNSET:
            field_dict["limit"] = limit
        if offset is not UNSET:
            field_dict["offset"] = offset
        if timezone is not UNSET:
            field_dict["timezone"] = timezone
        if unit_to is not UNSET:
            field_dict["unitTo"] = unit_to

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        delta_aggregation = Aggregation(d.pop("deltaAggregation"))

        tag_id = UUID(d.pop("tagId"))

        time_end = isoparse(d.pop("timeEnd"))

        time_start = isoparse(d.pop("timeStart"))

        def _parse_data_types(data: object) -> Union[None, Unset, list[DataType]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                data_types_type_0 = []
                _data_types_type_0 = data
                for data_types_type_0_item_data in _data_types_type_0:
                    data_types_type_0_item = DataType(data_types_type_0_item_data)

                    data_types_type_0.append(data_types_type_0_item)

                return data_types_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[DataType]], data)

        data_types = _parse_data_types(d.pop("dataTypes", UNSET))

        def _parse_group_time_by(data: object) -> Union[DataGrouping, None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                group_time_by_type_1 = DataGrouping(data)

                return group_time_by_type_1
            except:  # noqa: E722
                pass
            return cast(Union[DataGrouping, None, Unset], data)

        group_time_by = _parse_group_time_by(d.pop("groupTimeBy", UNSET))

        def _parse_limit(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        limit = _parse_limit(d.pop("limit", UNSET))

        def _parse_offset(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        offset = _parse_offset(d.pop("offset", UNSET))

        def _parse_timezone(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        timezone = _parse_timezone(d.pop("timezone", UNSET))

        def _parse_unit_to(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        unit_to = _parse_unit_to(d.pop("unitTo", UNSET))

        api_readings_request = cls(
            delta_aggregation=delta_aggregation,
            tag_id=tag_id,
            time_end=time_end,
            time_start=time_start,
            data_types=data_types,
            group_time_by=group_time_by,
            limit=limit,
            offset=offset,
            timezone=timezone,
            unit_to=unit_to,
        )

        api_readings_request.additional_properties = d
        return api_readings_request

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
