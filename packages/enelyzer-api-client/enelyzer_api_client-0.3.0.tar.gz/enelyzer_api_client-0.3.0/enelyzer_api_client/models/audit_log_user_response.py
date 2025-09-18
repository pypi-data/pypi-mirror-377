from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.audit_log_user import AuditLogUser


T = TypeVar("T", bound="AuditLogUserResponse")


@_attrs_define
class AuditLogUserResponse:
    """
    Example:
        {'user': {'userId': '70361904-0dd0-44ed-97da-26bf72c86471', 'userName': 'John Doe'}}

    Attributes:
        user (Union['AuditLogUser', None, Unset]):
    """

    user: Union["AuditLogUser", None, Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.audit_log_user import AuditLogUser

        user: Union[None, Unset, dict[str, Any]]
        if isinstance(self.user, Unset):
            user = UNSET
        elif isinstance(self.user, AuditLogUser):
            user = self.user.to_dict()
        else:
            user = self.user

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if user is not UNSET:
            field_dict["user"] = user

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.audit_log_user import AuditLogUser

        d = dict(src_dict)

        def _parse_user(data: object) -> Union["AuditLogUser", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                user_type_1 = AuditLogUser.from_dict(data)

                return user_type_1
            except:  # noqa: E722
                pass
            return cast(Union["AuditLogUser", None, Unset], data)

        user = _parse_user(d.pop("user", UNSET))

        audit_log_user_response = cls(
            user=user,
        )

        audit_log_user_response.additional_properties = d
        return audit_log_user_response

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
