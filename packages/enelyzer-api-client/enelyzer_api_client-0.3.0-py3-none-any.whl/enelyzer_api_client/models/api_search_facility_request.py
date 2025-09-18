from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.sorting_direction import SortingDirection
from ..types import UNSET, Unset

T = TypeVar("T", bound="ApiSearchFacilityRequest")


@_attrs_define
class ApiSearchFacilityRequest:
    """
    Example:
        {'ids': None, 'name': 'Main Facility', 'order': 'asc', 'orderBy': 'name', 'page': 1, 'pageSize': 10,
            'technicalNames': None}

    Attributes:
        page (int):
        page_size (int):
        ids (Union[None, Unset, list[UUID]]):
        name (Union[None, Unset, str]):
        order (Union[None, SortingDirection, Unset]):
        order_by (Union[None, Unset, str]):
        technical_names (Union[None, Unset, list[str]]):
    """

    page: int
    page_size: int
    ids: Union[None, Unset, list[UUID]] = UNSET
    name: Union[None, Unset, str] = UNSET
    order: Union[None, SortingDirection, Unset] = UNSET
    order_by: Union[None, Unset, str] = UNSET
    technical_names: Union[None, Unset, list[str]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        page = self.page

        page_size = self.page_size

        ids: Union[None, Unset, list[str]]
        if isinstance(self.ids, Unset):
            ids = UNSET
        elif isinstance(self.ids, list):
            ids = []
            for ids_type_0_item_data in self.ids:
                ids_type_0_item = str(ids_type_0_item_data)
                ids.append(ids_type_0_item)

        else:
            ids = self.ids

        name: Union[None, Unset, str]
        if isinstance(self.name, Unset):
            name = UNSET
        else:
            name = self.name

        order: Union[None, Unset, str]
        if isinstance(self.order, Unset):
            order = UNSET
        elif isinstance(self.order, SortingDirection):
            order = self.order.value
        else:
            order = self.order

        order_by: Union[None, Unset, str]
        if isinstance(self.order_by, Unset):
            order_by = UNSET
        else:
            order_by = self.order_by

        technical_names: Union[None, Unset, list[str]]
        if isinstance(self.technical_names, Unset):
            technical_names = UNSET
        elif isinstance(self.technical_names, list):
            technical_names = self.technical_names

        else:
            technical_names = self.technical_names

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "page": page,
                "pageSize": page_size,
            }
        )
        if ids is not UNSET:
            field_dict["ids"] = ids
        if name is not UNSET:
            field_dict["name"] = name
        if order is not UNSET:
            field_dict["order"] = order
        if order_by is not UNSET:
            field_dict["orderBy"] = order_by
        if technical_names is not UNSET:
            field_dict["technicalNames"] = technical_names

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        page = d.pop("page")

        page_size = d.pop("pageSize")

        def _parse_ids(data: object) -> Union[None, Unset, list[UUID]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                ids_type_0 = []
                _ids_type_0 = data
                for ids_type_0_item_data in _ids_type_0:
                    ids_type_0_item = UUID(ids_type_0_item_data)

                    ids_type_0.append(ids_type_0_item)

                return ids_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[UUID]], data)

        ids = _parse_ids(d.pop("ids", UNSET))

        def _parse_name(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        name = _parse_name(d.pop("name", UNSET))

        def _parse_order(data: object) -> Union[None, SortingDirection, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                order_type_1 = SortingDirection(data)

                return order_type_1
            except:  # noqa: E722
                pass
            return cast(Union[None, SortingDirection, Unset], data)

        order = _parse_order(d.pop("order", UNSET))

        def _parse_order_by(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        order_by = _parse_order_by(d.pop("orderBy", UNSET))

        def _parse_technical_names(data: object) -> Union[None, Unset, list[str]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                technical_names_type_0 = cast(list[str], data)

                return technical_names_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[str]], data)

        technical_names = _parse_technical_names(d.pop("technicalNames", UNSET))

        api_search_facility_request = cls(
            page=page,
            page_size=page_size,
            ids=ids,
            name=name,
            order=order,
            order_by=order_by,
            technical_names=technical_names,
        )

        api_search_facility_request.additional_properties = d
        return api_search_facility_request

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
