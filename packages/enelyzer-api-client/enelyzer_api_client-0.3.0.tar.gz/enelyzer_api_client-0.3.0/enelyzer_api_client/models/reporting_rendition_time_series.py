from collections.abc import Mapping
from typing import Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="ReportingRenditionTimeSeries")


@_attrs_define
class ReportingRenditionTimeSeries:
    """
    Example:
        {'id': '550e8400-e29b-41d4-a716-446655440000', 'isActive': True, 'organisationId':
            '550e8400-e29b-41d4-a716-446655440000', 'tagId': '550e8400-e29b-41d4-a716-446655440000', 'timeSeriesId': 1}

    Attributes:
        id (UUID):
        is_active (bool):
        organisation_id (UUID):
        tag_id (UUID):
        time_series_id (int):
    """

    id: UUID
    is_active: bool
    organisation_id: UUID
    tag_id: UUID
    time_series_id: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        is_active = self.is_active

        organisation_id = str(self.organisation_id)

        tag_id = str(self.tag_id)

        time_series_id = self.time_series_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "isActive": is_active,
                "organisationId": organisation_id,
                "tagId": tag_id,
                "timeSeriesId": time_series_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = UUID(d.pop("id"))

        is_active = d.pop("isActive")

        organisation_id = UUID(d.pop("organisationId"))

        tag_id = UUID(d.pop("tagId"))

        time_series_id = d.pop("timeSeriesId")

        reporting_rendition_time_series = cls(
            id=id,
            is_active=is_active,
            organisation_id=organisation_id,
            tag_id=tag_id,
            time_series_id=time_series_id,
        )

        reporting_rendition_time_series.additional_properties = d
        return reporting_rendition_time_series

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
