import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

T = TypeVar("T", bound="AddReportingRenditionPayload")


@_attrs_define
class AddReportingRenditionPayload:
    """
    Example:
        {'endDate': '2023-11-15T22:13:20Z', 'startDate': '2023-11-14T22:13:20Z', 'value': 123.45}

    Attributes:
        end_date (datetime.datetime):
        start_date (datetime.datetime):
        value (float):
    """

    end_date: datetime.datetime
    start_date: datetime.datetime
    value: float
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        end_date = self.end_date.isoformat() + "Z"

        start_date = self.start_date.isoformat() + "Z"

        value = self.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "endDate": end_date,
                "startDate": start_date,
                "value": value,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        end_date = isoparse(d.pop("endDate"))

        start_date = isoparse(d.pop("startDate"))

        value = d.pop("value")

        add_reporting_rendition_payload = cls(
            end_date=end_date,
            start_date=start_date,
            value=value,
        )

        add_reporting_rendition_payload.additional_properties = d
        return add_reporting_rendition_payload

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
