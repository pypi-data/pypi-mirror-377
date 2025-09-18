import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.address import Address
    from ..models.geo_location import GeoLocation


T = TypeVar("T", bound="Facility")


@_attrs_define
class Facility:
    """
    Example:
        {'address': {'addressLine1': '123 Main St', 'addressLine2': 'Suite 100', 'city': 'Brussels', 'country':
            'Belgium', 'postalCode': '1000'}, 'created': '2024-01-01T00:00:00Z', 'enabled': True, 'facilityType':
            'PRODUCTION', 'friendlyName': 'Main Facility', 'geo': {'geoLat': 50.8503, 'geoLng': 4.3517}, 'id':
            '123e4567-e89b-12d3-a456-426614174000', 'info': 'This is the main facility.', 'name': 'main_facility',
            'organisationId': '123e4567-e89b-12d3-a456-426614174000', 'updated': '2024-06-01T00:00:00Z'}

    Attributes:
        created (datetime.datetime):
        enabled (bool):
        facility_type (str):
        friendly_name (str):
        geo (GeoLocation):  Example: {'geoLat': 50.8503, 'geoLng': 4.3517}.
        id (UUID):
        name (str):
        organisation_id (UUID):
        address (Union['Address', None, Unset]):
        info (Union[None, Unset, str]):
        logo (Union[None, Unset, str]):
        updated (Union[None, Unset, datetime.datetime]):
    """

    created: datetime.datetime
    enabled: bool
    facility_type: str
    friendly_name: str
    geo: "GeoLocation"
    id: UUID
    name: str
    organisation_id: UUID
    address: Union["Address", None, Unset] = UNSET
    info: Union[None, Unset, str] = UNSET
    logo: Union[None, Unset, str] = UNSET
    updated: Union[None, Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.address import Address

        created = self.created.isoformat() + "Z"

        enabled = self.enabled

        facility_type = self.facility_type

        friendly_name = self.friendly_name

        geo = self.geo.to_dict()

        id = str(self.id)

        name = self.name

        organisation_id = str(self.organisation_id)

        address: Union[None, Unset, dict[str, Any]]
        if isinstance(self.address, Unset):
            address = UNSET
        elif isinstance(self.address, Address):
            address = self.address.to_dict()
        else:
            address = self.address

        info: Union[None, Unset, str]
        if isinstance(self.info, Unset):
            info = UNSET
        else:
            info = self.info

        logo: Union[None, Unset, str]
        if isinstance(self.logo, Unset):
            logo = UNSET
        else:
            logo = self.logo

        updated: Union[None, Unset, str]
        if isinstance(self.updated, Unset):
            updated = UNSET
        elif isinstance(self.updated, datetime.datetime):
            updated = self.updated.isoformat() + "Z"
        else:
            updated = self.updated

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "created": created,
                "enabled": enabled,
                "facilityType": facility_type,
                "friendlyName": friendly_name,
                "geo": geo,
                "id": id,
                "name": name,
                "organisationId": organisation_id,
            }
        )
        if address is not UNSET:
            field_dict["address"] = address
        if info is not UNSET:
            field_dict["info"] = info
        if logo is not UNSET:
            field_dict["logo"] = logo
        if updated is not UNSET:
            field_dict["updated"] = updated

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.address import Address
        from ..models.geo_location import GeoLocation

        d = dict(src_dict)
        created = isoparse(d.pop("created"))

        enabled = d.pop("enabled")

        facility_type = d.pop("facilityType")

        friendly_name = d.pop("friendlyName")

        geo = GeoLocation.from_dict(d.pop("geo"))

        id = UUID(d.pop("id"))

        name = d.pop("name")

        organisation_id = UUID(d.pop("organisationId"))

        def _parse_address(data: object) -> Union["Address", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                address_type_1 = Address.from_dict(data)

                return address_type_1
            except:  # noqa: E722
                pass
            return cast(Union["Address", None, Unset], data)

        address = _parse_address(d.pop("address", UNSET))

        def _parse_info(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        info = _parse_info(d.pop("info", UNSET))

        def _parse_logo(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        logo = _parse_logo(d.pop("logo", UNSET))

        def _parse_updated(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                updated_type_0 = isoparse(data)

                return updated_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        updated = _parse_updated(d.pop("updated", UNSET))

        facility = cls(
            created=created,
            enabled=enabled,
            facility_type=facility_type,
            friendly_name=friendly_name,
            geo=geo,
            id=id,
            name=name,
            organisation_id=organisation_id,
            address=address,
            info=info,
            logo=logo,
            updated=updated,
        )

        facility.additional_properties = d
        return facility

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
