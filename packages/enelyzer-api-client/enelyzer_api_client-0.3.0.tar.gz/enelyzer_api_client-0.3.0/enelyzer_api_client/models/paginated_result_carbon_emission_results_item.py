import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.calculation_method import CalculationMethod
from ..models.co_2_category import Co2Category
from ..models.scope import Scope
from ..types import UNSET, Unset

T = TypeVar("T", bound="PaginatedResultCarbonEmissionResultsItem")


@_attrs_define
class PaginatedResultCarbonEmissionResultsItem:
    """
    Example:
        {'page': 1, 'pageSize': 10, 'results': [{'activityId': '550e8400-e29b-41d4-a716-446655440000', 'activityName':
            'Bakery products – production', 'buildingId': '550e8400-e29b-41d4-a716-446655440000', 'buildingName': 'Building
            A', 'calculationMethod': 'MARKET_BASED', 'co2Category': 'electricity', 'emissionFactor': 0.123,
            'emissionFactorUnit': 'kgCO2e/kWh', 'emissionSource': 'Source A', 'endDateUtc': '2024-01-31T00:00:00Z',
            'facilityId': '550e8400-e29b-41d4-a716-446655440000', 'facilityName': 'Brussels', 'facilityTechnicalName':
            'brussels', 'scope': 'SCOPE_1', 'startDateUtc': '2024-01-01T00:00:00Z', 'tagCategory': 'Electricity',
            'tagConsumption': 12345.6789, 'tagEmission': 123.456, 'tagEmissionUnit': 'KILOGRAM_CARBON_DIOXIDE_EQUIVALENT',
            'tagId': '550e8400-e29b-41d4-a716-446655440000', 'tagName': 'BigMeter', 'tagTechnicalName': 'bigmeter',
            'tagUnit': 'KILOWATT_HOUR', 'yearMonth': '2024-01'}], 'total': 100}

    Attributes:
        building_id (UUID):
        building_name (str):
        calculation_method (CalculationMethod):  Example: MARKET_BASED.
        co_2_category (Co2Category):  Example: electricity.
        emission_factor (float): Serialised with 6 decimal places
        emission_factor_unit (str):
        emission_source (str):
        end_date_utc (datetime.datetime): The end date of the carbon emission data in UTC.
        facility_id (UUID):
        facility_name (str):
        facility_technical_name (str):
        scope (Scope):  Example: SCOPE_1.
        start_date_utc (datetime.datetime): The start date of the carbon emission data in UTC.
        tag_category (str):
        tag_emission_unit (str):
        tag_id (UUID):
        tag_name (str):
        tag_technical_name (str):
        year_month (str): The year and month of the carbon emission data in the format "YYYY-MM" in localtime.
        activity_id (Union[None, UUID, Unset]):
        activity_name (Union[None, Unset, str]):
        tag_consumption (Union[None, Unset, float]): Serialised with 6 decimal places
        tag_emission (Union[None, Unset, float]): Serialised with 6 decimal places
        tag_unit (Union[None, Unset, str]):
    """

    building_id: UUID
    building_name: str
    calculation_method: CalculationMethod
    co_2_category: Co2Category
    emission_factor: float
    emission_factor_unit: str
    emission_source: str
    end_date_utc: datetime.datetime
    facility_id: UUID
    facility_name: str
    facility_technical_name: str
    scope: Scope
    start_date_utc: datetime.datetime
    tag_category: str
    tag_emission_unit: str
    tag_id: UUID
    tag_name: str
    tag_technical_name: str
    year_month: str
    activity_id: Union[None, UUID, Unset] = UNSET
    activity_name: Union[None, Unset, str] = UNSET
    tag_consumption: Union[None, Unset, float] = UNSET
    tag_emission: Union[None, Unset, float] = UNSET
    tag_unit: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        building_id = str(self.building_id)

        building_name = self.building_name

        calculation_method = self.calculation_method.value

        co_2_category = self.co_2_category.value

        emission_factor = self.emission_factor

        emission_factor_unit = self.emission_factor_unit

        emission_source = self.emission_source

        end_date_utc = self.end_date_utc.isoformat() + "Z"

        facility_id = str(self.facility_id)

        facility_name = self.facility_name

        facility_technical_name = self.facility_technical_name

        scope = self.scope.value

        start_date_utc = self.start_date_utc.isoformat() + "Z"

        tag_category = self.tag_category

        tag_emission_unit = self.tag_emission_unit

        tag_id = str(self.tag_id)

        tag_name = self.tag_name

        tag_technical_name = self.tag_technical_name

        year_month = self.year_month

        activity_id: Union[None, Unset, str]
        if isinstance(self.activity_id, Unset):
            activity_id = UNSET
        elif isinstance(self.activity_id, UUID):
            activity_id = str(self.activity_id)
        else:
            activity_id = self.activity_id

        activity_name: Union[None, Unset, str]
        if isinstance(self.activity_name, Unset):
            activity_name = UNSET
        else:
            activity_name = self.activity_name

        tag_consumption: Union[None, Unset, float]
        if isinstance(self.tag_consumption, Unset):
            tag_consumption = UNSET
        else:
            tag_consumption = self.tag_consumption

        tag_emission: Union[None, Unset, float]
        if isinstance(self.tag_emission, Unset):
            tag_emission = UNSET
        else:
            tag_emission = self.tag_emission

        tag_unit: Union[None, Unset, str]
        if isinstance(self.tag_unit, Unset):
            tag_unit = UNSET
        else:
            tag_unit = self.tag_unit

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "buildingId": building_id,
                "buildingName": building_name,
                "calculationMethod": calculation_method,
                "co2Category": co_2_category,
                "emissionFactor": emission_factor,
                "emissionFactorUnit": emission_factor_unit,
                "emissionSource": emission_source,
                "endDateUtc": end_date_utc,
                "facilityId": facility_id,
                "facilityName": facility_name,
                "facilityTechnicalName": facility_technical_name,
                "scope": scope,
                "startDateUtc": start_date_utc,
                "tagCategory": tag_category,
                "tagEmissionUnit": tag_emission_unit,
                "tagId": tag_id,
                "tagName": tag_name,
                "tagTechnicalName": tag_technical_name,
                "yearMonth": year_month,
            }
        )
        if activity_id is not UNSET:
            field_dict["activityId"] = activity_id
        if activity_name is not UNSET:
            field_dict["activityName"] = activity_name
        if tag_consumption is not UNSET:
            field_dict["tagConsumption"] = tag_consumption
        if tag_emission is not UNSET:
            field_dict["tagEmission"] = tag_emission
        if tag_unit is not UNSET:
            field_dict["tagUnit"] = tag_unit

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        building_id = UUID(d.pop("buildingId"))

        building_name = d.pop("buildingName")

        calculation_method = CalculationMethod(d.pop("calculationMethod"))

        co_2_category = Co2Category(d.pop("co2Category"))

        emission_factor = d.pop("emissionFactor")

        emission_factor_unit = d.pop("emissionFactorUnit")

        emission_source = d.pop("emissionSource")

        end_date_utc = isoparse(d.pop("endDateUtc"))

        facility_id = UUID(d.pop("facilityId"))

        facility_name = d.pop("facilityName")

        facility_technical_name = d.pop("facilityTechnicalName")

        scope = Scope(d.pop("scope"))

        start_date_utc = isoparse(d.pop("startDateUtc"))

        tag_category = d.pop("tagCategory")

        tag_emission_unit = d.pop("tagEmissionUnit")

        tag_id = UUID(d.pop("tagId"))

        tag_name = d.pop("tagName")

        tag_technical_name = d.pop("tagTechnicalName")

        year_month = d.pop("yearMonth")

        def _parse_activity_id(data: object) -> Union[None, UUID, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                activity_id_type_0 = UUID(data)

                return activity_id_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, UUID, Unset], data)

        activity_id = _parse_activity_id(d.pop("activityId", UNSET))

        def _parse_activity_name(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        activity_name = _parse_activity_name(d.pop("activityName", UNSET))

        def _parse_tag_consumption(data: object) -> Union[None, Unset, float]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, float], data)

        tag_consumption = _parse_tag_consumption(d.pop("tagConsumption", UNSET))

        def _parse_tag_emission(data: object) -> Union[None, Unset, float]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, float], data)

        tag_emission = _parse_tag_emission(d.pop("tagEmission", UNSET))

        def _parse_tag_unit(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        tag_unit = _parse_tag_unit(d.pop("tagUnit", UNSET))

        paginated_result_carbon_emission_results_item = cls(
            building_id=building_id,
            building_name=building_name,
            calculation_method=calculation_method,
            co_2_category=co_2_category,
            emission_factor=emission_factor,
            emission_factor_unit=emission_factor_unit,
            emission_source=emission_source,
            end_date_utc=end_date_utc,
            facility_id=facility_id,
            facility_name=facility_name,
            facility_technical_name=facility_technical_name,
            scope=scope,
            start_date_utc=start_date_utc,
            tag_category=tag_category,
            tag_emission_unit=tag_emission_unit,
            tag_id=tag_id,
            tag_name=tag_name,
            tag_technical_name=tag_technical_name,
            year_month=year_month,
            activity_id=activity_id,
            activity_name=activity_name,
            tag_consumption=tag_consumption,
            tag_emission=tag_emission,
            tag_unit=tag_unit,
        )

        paginated_result_carbon_emission_results_item.additional_properties = d
        return paginated_result_carbon_emission_results_item

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
