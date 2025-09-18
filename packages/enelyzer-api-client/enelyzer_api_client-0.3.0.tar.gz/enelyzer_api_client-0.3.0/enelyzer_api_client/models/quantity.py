from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="Quantity")


@_attrs_define
class Quantity:
    """
    Example:
        {'belongsTo': ['ENERGY_SOURCES/ELECTRICITY', 'WATER_AND_OTHER_LIQUIDS/HOT_WATER',
            'WATER_AND_OTHER_LIQUIDS/THERMAL_OIL', 'WATER_AND_OTHER_LIQUIDS/OTHER_LIQUID', 'STEAM_AND_OTHER_GASSES/STEAM',
            'STEAM_AND_OTHER_GASSES/OTHER_GAS', 'WEATHER/SOLAR_RADIATION', 'RESOURCES/WASTE', 'RESOURCES/SOLIDS_MATERIALS',
            'RESOURCES/BATTERY', 'OTHER/OTHER'], 'instantaneous': False, 'name': 'ENERGY', 'unit': 'KILOWATT_HOUR'}

    Attributes:
        belongs_to (list[str]):
        instantaneous (bool):
        name (str):
        unit (str):
    """

    belongs_to: list[str]
    instantaneous: bool
    name: str
    unit: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        belongs_to = self.belongs_to

        instantaneous = self.instantaneous

        name = self.name

        unit = self.unit

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "belongsTo": belongs_to,
                "instantaneous": instantaneous,
                "name": name,
                "unit": unit,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        belongs_to = cast(list[str], d.pop("belongsTo"))

        instantaneous = d.pop("instantaneous")

        name = d.pop("name")

        unit = d.pop("unit")

        quantity = cls(
            belongs_to=belongs_to,
            instantaneous=instantaneous,
            name=name,
            unit=unit,
        )

        quantity.additional_properties = d
        return quantity

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
