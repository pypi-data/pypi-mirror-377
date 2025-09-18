from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.paginated_result_carbon_emission_results_item import PaginatedResultCarbonEmissionResultsItem


T = TypeVar("T", bound="PaginatedResultCarbonEmission")


@_attrs_define
class PaginatedResultCarbonEmission:
    """
    Attributes:
        page (int):
        page_size (int):
        results (list['PaginatedResultCarbonEmissionResultsItem']):
        total (int):
    """

    page: int
    page_size: int
    results: list["PaginatedResultCarbonEmissionResultsItem"]
    total: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        page = self.page

        page_size = self.page_size

        results = []
        for results_item_data in self.results:
            results_item = results_item_data.to_dict()
            results.append(results_item)

        total = self.total

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "page": page,
                "pageSize": page_size,
                "results": results,
                "total": total,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.paginated_result_carbon_emission_results_item import PaginatedResultCarbonEmissionResultsItem

        d = dict(src_dict)
        page = d.pop("page")

        page_size = d.pop("pageSize")

        results = []
        _results = d.pop("results")
        for results_item_data in _results:
            results_item = PaginatedResultCarbonEmissionResultsItem.from_dict(results_item_data)

            results.append(results_item)

        total = d.pop("total")

        paginated_result_carbon_emission = cls(
            page=page,
            page_size=page_size,
            results=results,
            total=total,
        )

        paginated_result_carbon_emission.additional_properties = d
        return paginated_result_carbon_emission

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
