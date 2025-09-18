import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

T = TypeVar("T", bound="CO2EmissionSearchParameters")


@_attrs_define
class CO2EmissionSearchParameters:
    """
    Attributes:
        from_date (datetime.datetime): The start date for CO2 emissions retrieval (UTC format).
            Example: `"2023-12-31T23:00:00Z"` to represent the beginning of January 2024 in Brussels time.
        to_date (datetime.datetime): The end date for CO2 emissions retrieval (UTC format).
            Example: `"2024-01-31T23:00:00Z"` to cover the full month of January 2024 in Brussels time.
    """

    from_date: datetime.datetime
    to_date: datetime.datetime
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from_date = self.from_date.isoformat() + "Z"

        to_date = self.to_date.isoformat() + "Z"

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "fromDate": from_date,
                "toDate": to_date,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        from_date = isoparse(d.pop("fromDate"))

        to_date = isoparse(d.pop("toDate"))

        co2_emission_search_parameters = cls(
            from_date=from_date,
            to_date=to_date,
        )

        co2_emission_search_parameters.additional_properties = d
        return co2_emission_search_parameters

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
