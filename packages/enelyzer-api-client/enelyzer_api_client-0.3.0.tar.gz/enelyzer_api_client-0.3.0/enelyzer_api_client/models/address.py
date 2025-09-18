from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="Address")


@_attrs_define
class Address:
    """
    Example:
        {'addressLine1': '123 Main St', 'addressLine2': 'Suite 100', 'city': 'Brussels', 'country': 'Belgium',
            'postalCode': '1000'}

    Attributes:
        address_line_1 (str):
        city (str):
        country (str):
        postal_code (str):
        address_line_2 (Union[None, Unset, str]):
    """

    address_line_1: str
    city: str
    country: str
    postal_code: str
    address_line_2: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        address_line_1 = self.address_line_1

        city = self.city

        country = self.country

        postal_code = self.postal_code

        address_line_2: Union[None, Unset, str]
        if isinstance(self.address_line_2, Unset):
            address_line_2 = UNSET
        else:
            address_line_2 = self.address_line_2

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "addressLine1": address_line_1,
                "city": city,
                "country": country,
                "postalCode": postal_code,
            }
        )
        if address_line_2 is not UNSET:
            field_dict["addressLine2"] = address_line_2

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        address_line_1 = d.pop("addressLine1")

        city = d.pop("city")

        country = d.pop("country")

        postal_code = d.pop("postalCode")

        def _parse_address_line_2(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        address_line_2 = _parse_address_line_2(d.pop("addressLine2", UNSET))

        address = cls(
            address_line_1=address_line_1,
            city=city,
            country=country,
            postal_code=postal_code,
            address_line_2=address_line_2,
        )

        address.additional_properties = d
        return address

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
