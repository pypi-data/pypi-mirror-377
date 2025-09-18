import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="ApiReading")


@_attrs_define
class ApiReading:
    """
    Example:
        {'delta': 123.45, 'deltaNormalisedMasked': None, 'deltaReportingRendition': 67.89,
            'deltaReportingRenditionOverride': 67.89, 'timestamp': '2023-11-14T23:13:20+01:00'}

    Attributes:
        delta (Union[None, Unset, float]): The aggregated delta value of the normalized data.
        delta_normalised_masked (Union[None, Unset, float]): `delta` except when rendition is active, then NULL. Can be
            combined with `delta_reporting_rendition` to get continuous data with rendition replacing deltas.
        delta_reporting_rendition (Union[None, Unset, float]): The aggregated delta value of the reporting rendition.
        delta_reporting_rendition_override (Union[None, Unset, float]): `delta_reporting_rendition` when rendition is
            active, otherwise `delta` data.
        timestamp (Union[None, Unset, datetime.datetime]): The start or end of the period the data has been aggregated
            over.
            For groupings under a day, this is the end of the period.
            e.g 2019-12-30T10:15:00 with quarterHourly captures data from 2019-12-30T10:00:01 to 2019-12-30T10:15:00
            For groupings of a day or more, this is the start of the period.
            e.g 2019-12-01 with monthly captures data from 2019-12-01T00:00:00 to 2019-12-31T23:59:59
    """

    delta: Union[None, Unset, float] = UNSET
    delta_normalised_masked: Union[None, Unset, float] = UNSET
    delta_reporting_rendition: Union[None, Unset, float] = UNSET
    delta_reporting_rendition_override: Union[None, Unset, float] = UNSET
    timestamp: Union[None, Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        delta: Union[None, Unset, float]
        if isinstance(self.delta, Unset):
            delta = UNSET
        else:
            delta = self.delta

        delta_normalised_masked: Union[None, Unset, float]
        if isinstance(self.delta_normalised_masked, Unset):
            delta_normalised_masked = UNSET
        else:
            delta_normalised_masked = self.delta_normalised_masked

        delta_reporting_rendition: Union[None, Unset, float]
        if isinstance(self.delta_reporting_rendition, Unset):
            delta_reporting_rendition = UNSET
        else:
            delta_reporting_rendition = self.delta_reporting_rendition

        delta_reporting_rendition_override: Union[None, Unset, float]
        if isinstance(self.delta_reporting_rendition_override, Unset):
            delta_reporting_rendition_override = UNSET
        else:
            delta_reporting_rendition_override = self.delta_reporting_rendition_override

        timestamp: Union[None, Unset, str]
        if isinstance(self.timestamp, Unset):
            timestamp = UNSET
        elif isinstance(self.timestamp, datetime.datetime):
            timestamp = self.timestamp.isoformat() + "Z"
        else:
            timestamp = self.timestamp

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if delta is not UNSET:
            field_dict["delta"] = delta
        if delta_normalised_masked is not UNSET:
            field_dict["deltaNormalisedMasked"] = delta_normalised_masked
        if delta_reporting_rendition is not UNSET:
            field_dict["deltaReportingRendition"] = delta_reporting_rendition
        if delta_reporting_rendition_override is not UNSET:
            field_dict["deltaReportingRenditionOverride"] = delta_reporting_rendition_override
        if timestamp is not UNSET:
            field_dict["timestamp"] = timestamp

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_delta(data: object) -> Union[None, Unset, float]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, float], data)

        delta = _parse_delta(d.pop("delta", UNSET))

        def _parse_delta_normalised_masked(data: object) -> Union[None, Unset, float]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, float], data)

        delta_normalised_masked = _parse_delta_normalised_masked(d.pop("deltaNormalisedMasked", UNSET))

        def _parse_delta_reporting_rendition(data: object) -> Union[None, Unset, float]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, float], data)

        delta_reporting_rendition = _parse_delta_reporting_rendition(d.pop("deltaReportingRendition", UNSET))

        def _parse_delta_reporting_rendition_override(data: object) -> Union[None, Unset, float]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, float], data)

        delta_reporting_rendition_override = _parse_delta_reporting_rendition_override(
            d.pop("deltaReportingRenditionOverride", UNSET)
        )

        def _parse_timestamp(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                timestamp_type_0 = isoparse(data)

                return timestamp_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        timestamp = _parse_timestamp(d.pop("timestamp", UNSET))

        api_reading = cls(
            delta=delta,
            delta_normalised_masked=delta_normalised_masked,
            delta_reporting_rendition=delta_reporting_rendition,
            delta_reporting_rendition_override=delta_reporting_rendition_override,
            timestamp=timestamp,
        )

        api_reading.additional_properties = d
        return api_reading

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
