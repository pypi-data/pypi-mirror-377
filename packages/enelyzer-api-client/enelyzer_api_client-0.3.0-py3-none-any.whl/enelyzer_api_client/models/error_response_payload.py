from collections.abc import Mapping
from typing import Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="ErrorResponsePayload")


@_attrs_define
class ErrorResponsePayload:
    """
    Attributes:
        detail (str):  Example: Failed to fetch X due to Y.
        instance (str):  Example: /v1/enelyzer/550e8400-e29b-41d4-a716-446655440000/tags.
        status (int):  Example: 500.
        title (str):  Example: Internal Server Error.
        type_ (str):  Example: INTERNAL_SERVER_ERROR.
        uuid (UUID):  Example: 550e8400-e29b-41d4-a716-446655440000.
    """

    detail: str
    instance: str
    status: int
    title: str
    type_: str
    uuid: UUID
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        detail = self.detail

        instance = self.instance

        status = self.status

        title = self.title

        type_ = self.type_

        uuid = str(self.uuid)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "detail": detail,
                "instance": instance,
                "status": status,
                "title": title,
                "type": type_,
                "uuid": uuid,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        detail = d.pop("detail")

        instance = d.pop("instance")

        status = d.pop("status")

        title = d.pop("title")

        type_ = d.pop("type")

        uuid = UUID(d.pop("uuid"))

        error_response_payload = cls(
            detail=detail,
            instance=instance,
            status=status,
            title=title,
            type_=type_,
            uuid=uuid,
        )

        error_response_payload.additional_properties = d
        return error_response_payload

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
