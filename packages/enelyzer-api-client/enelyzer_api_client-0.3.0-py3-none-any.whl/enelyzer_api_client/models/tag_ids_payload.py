from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="TagIdsPayload")


@_attrs_define
class TagIdsPayload:
    """
    Example:
        {'tagIds': ['550e8400-e29b-41d4-a716-446655440000'], 'withConversions': False, 'withFormula': False,
            'withFullComposition': False}

    Attributes:
        tag_ids (list[UUID]):
        with_conversions (Union[None, Unset, bool]):
        with_formula (Union[None, Unset, bool]):
        with_full_composition (Union[None, Unset, bool]):
    """

    tag_ids: list[UUID]
    with_conversions: Union[None, Unset, bool] = UNSET
    with_formula: Union[None, Unset, bool] = UNSET
    with_full_composition: Union[None, Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        tag_ids = []
        for tag_ids_item_data in self.tag_ids:
            tag_ids_item = str(tag_ids_item_data)
            tag_ids.append(tag_ids_item)

        with_conversions: Union[None, Unset, bool]
        if isinstance(self.with_conversions, Unset):
            with_conversions = UNSET
        else:
            with_conversions = self.with_conversions

        with_formula: Union[None, Unset, bool]
        if isinstance(self.with_formula, Unset):
            with_formula = UNSET
        else:
            with_formula = self.with_formula

        with_full_composition: Union[None, Unset, bool]
        if isinstance(self.with_full_composition, Unset):
            with_full_composition = UNSET
        else:
            with_full_composition = self.with_full_composition

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "tagIds": tag_ids,
            }
        )
        if with_conversions is not UNSET:
            field_dict["withConversions"] = with_conversions
        if with_formula is not UNSET:
            field_dict["withFormula"] = with_formula
        if with_full_composition is not UNSET:
            field_dict["withFullComposition"] = with_full_composition

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        tag_ids = []
        _tag_ids = d.pop("tagIds")
        for tag_ids_item_data in _tag_ids:
            tag_ids_item = UUID(tag_ids_item_data)

            tag_ids.append(tag_ids_item)

        def _parse_with_conversions(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        with_conversions = _parse_with_conversions(d.pop("withConversions", UNSET))

        def _parse_with_formula(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        with_formula = _parse_with_formula(d.pop("withFormula", UNSET))

        def _parse_with_full_composition(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        with_full_composition = _parse_with_full_composition(d.pop("withFullComposition", UNSET))

        tag_ids_payload = cls(
            tag_ids=tag_ids,
            with_conversions=with_conversions,
            with_formula=with_formula,
            with_full_composition=with_full_composition,
        )

        tag_ids_payload.additional_properties = d
        return tag_ids_payload

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
