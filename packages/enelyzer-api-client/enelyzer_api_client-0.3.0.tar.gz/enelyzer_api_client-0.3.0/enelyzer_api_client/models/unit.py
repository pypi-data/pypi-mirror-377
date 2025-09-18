from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="Unit")


@_attrs_define
class Unit:
    """
    Example:
        {'displayableUnit': 'kWh', 'enelyzerUnit': 'KILOWATT_HOUR'}

    Attributes:
        displayable_unit (str):
        enelyzer_unit (str):
    """

    displayable_unit: str
    enelyzer_unit: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        displayable_unit = self.displayable_unit

        enelyzer_unit = self.enelyzer_unit

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "displayableUnit": displayable_unit,
                "enelyzerUnit": enelyzer_unit,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        displayable_unit = d.pop("displayableUnit")

        enelyzer_unit = d.pop("enelyzerUnit")

        unit = cls(
            displayable_unit=displayable_unit,
            enelyzer_unit=enelyzer_unit,
        )

        unit.additional_properties = d
        return unit

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
