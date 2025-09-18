import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.api_tag_state_label import ApiTagStateLabel
from ..models.status import Status
from ..models.value_type_label import ValueTypeLabel
from ..types import UNSET, Unset

T = TypeVar("T", bound="ApiTag")


@_attrs_define
class ApiTag:
    """
    Example:
        {'page': 1, 'pageSize': 10, 'results': [{'category': 'WATER', 'description': 'Tag below the red box',
            'fromDate': '2023-11-14T22:13:20Z', 'id': '550e8400-e29b-41d4-a716-446655440000', 'logInterval': 900, 'name':
            'Boiler Water East 4', 'normalizedUnit': 'CUBIC_METER', 'quantity': 'Volume', 'rawUnit': 'LITRE', 'tagState':
            'composed', 'tagStatus': 'active', 'technicalName': 'boiler_water_4', 'tillDate': '2023-11-14T22:13:20Z',
            'valueType': 'index'}], 'total': 100}

    Attributes:
        category (str):
        from_date (datetime.datetime):
        id (UUID):
        log_interval (int):
        name (str):
        normalized_unit (str):
        quantity (str):
        tag_state (ApiTagStateLabel):  Example: Composed.
        tag_status (Status):
        technical_name (str):
        value_type (ValueTypeLabel):
        description (Union[None, Unset, str]):
        raw_unit (Union[None, Unset, str]):
        till_date (Union[None, Unset, datetime.datetime]):
    """

    category: str
    from_date: datetime.datetime
    id: UUID
    log_interval: int
    name: str
    normalized_unit: str
    quantity: str
    tag_state: ApiTagStateLabel
    tag_status: Status
    technical_name: str
    value_type: ValueTypeLabel
    description: Union[None, Unset, str] = UNSET
    raw_unit: Union[None, Unset, str] = UNSET
    till_date: Union[None, Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        category = self.category

        from_date = self.from_date.isoformat() + "Z"

        id = str(self.id)

        log_interval = self.log_interval

        name = self.name

        normalized_unit = self.normalized_unit

        quantity = self.quantity

        tag_state = self.tag_state.value

        tag_status = self.tag_status.value

        technical_name = self.technical_name

        value_type = self.value_type.value

        description: Union[None, Unset, str]
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        raw_unit: Union[None, Unset, str]
        if isinstance(self.raw_unit, Unset):
            raw_unit = UNSET
        else:
            raw_unit = self.raw_unit

        till_date: Union[None, Unset, str]
        if isinstance(self.till_date, Unset):
            till_date = UNSET
        elif isinstance(self.till_date, datetime.datetime):
            till_date = self.till_date.isoformat() + "Z"
        else:
            till_date = self.till_date

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "category": category,
                "fromDate": from_date,
                "id": id,
                "logInterval": log_interval,
                "name": name,
                "normalizedUnit": normalized_unit,
                "quantity": quantity,
                "tagState": tag_state,
                "tagStatus": tag_status,
                "technicalName": technical_name,
                "valueType": value_type,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if raw_unit is not UNSET:
            field_dict["rawUnit"] = raw_unit
        if till_date is not UNSET:
            field_dict["tillDate"] = till_date

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        category = d.pop("category")

        from_date = isoparse(d.pop("fromDate"))

        id = UUID(d.pop("id"))

        log_interval = d.pop("logInterval")

        name = d.pop("name")

        normalized_unit = d.pop("normalizedUnit")

        quantity = d.pop("quantity")

        tag_state = ApiTagStateLabel(d.pop("tagState"))

        tag_status = Status(d.pop("tagStatus"))

        technical_name = d.pop("technicalName")

        value_type = ValueTypeLabel(d.pop("valueType"))

        def _parse_description(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        description = _parse_description(d.pop("description", UNSET))

        def _parse_raw_unit(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        raw_unit = _parse_raw_unit(d.pop("rawUnit", UNSET))

        def _parse_till_date(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                till_date_type_0 = isoparse(data)

                return till_date_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        till_date = _parse_till_date(d.pop("tillDate", UNSET))

        api_tag = cls(
            category=category,
            from_date=from_date,
            id=id,
            log_interval=log_interval,
            name=name,
            normalized_unit=normalized_unit,
            quantity=quantity,
            tag_state=tag_state,
            tag_status=tag_status,
            technical_name=technical_name,
            value_type=value_type,
            description=description,
            raw_unit=raw_unit,
            till_date=till_date,
        )

        api_tag.additional_properties = d
        return api_tag

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
