from http import HTTPStatus
from typing import Any, Optional, Union
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.add_reporting_rendition_payload import AddReportingRenditionPayload
from ...models.error_response_payload import ErrorResponsePayload
from ...models.reporting_rendition_time_series import ReportingRenditionTimeSeries
from ...types import Response


def _get_kwargs(
    organisation_group: str,
    organisation_id: UUID,
    tag_id: UUID,
    *,
    body: AddReportingRenditionPayload,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/v1/{organisation_group}/{organisation_id}/energy-efficiency/tags/{tag_id}/reporting-renditions",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[ErrorResponsePayload, ReportingRenditionTimeSeries]]:
    if response.status_code == 201:
        response_201 = ReportingRenditionTimeSeries.from_dict(response.json())

        return response_201

    if response.status_code == 400:
        response_400 = ErrorResponsePayload.from_dict(response.json())

        return response_400

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[ErrorResponsePayload, ReportingRenditionTimeSeries]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    organisation_group: str,
    organisation_id: UUID,
    tag_id: UUID,
    *,
    client: AuthenticatedClient,
    body: AddReportingRenditionPayload,
) -> Response[Union[ErrorResponsePayload, ReportingRenditionTimeSeries]]:
    """
    Args:
        organisation_group (str):
        organisation_id (UUID):
        tag_id (UUID):
        body (AddReportingRenditionPayload):  Example: {'endDate': '2023-11-15T22:13:20Z',
            'startDate': '2023-11-14T22:13:20Z', 'value': 123.45}.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponsePayload, ReportingRenditionTimeSeries]]
    """

    kwargs = _get_kwargs(
        organisation_group=organisation_group,
        organisation_id=organisation_id,
        tag_id=tag_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    organisation_group: str,
    organisation_id: UUID,
    tag_id: UUID,
    *,
    client: AuthenticatedClient,
    body: AddReportingRenditionPayload,
) -> Optional[Union[ErrorResponsePayload, ReportingRenditionTimeSeries]]:
    """
    Args:
        organisation_group (str):
        organisation_id (UUID):
        tag_id (UUID):
        body (AddReportingRenditionPayload):  Example: {'endDate': '2023-11-15T22:13:20Z',
            'startDate': '2023-11-14T22:13:20Z', 'value': 123.45}.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponsePayload, ReportingRenditionTimeSeries]
    """

    return sync_detailed(
        organisation_group=organisation_group,
        organisation_id=organisation_id,
        tag_id=tag_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    organisation_group: str,
    organisation_id: UUID,
    tag_id: UUID,
    *,
    client: AuthenticatedClient,
    body: AddReportingRenditionPayload,
) -> Response[Union[ErrorResponsePayload, ReportingRenditionTimeSeries]]:
    """
    Args:
        organisation_group (str):
        organisation_id (UUID):
        tag_id (UUID):
        body (AddReportingRenditionPayload):  Example: {'endDate': '2023-11-15T22:13:20Z',
            'startDate': '2023-11-14T22:13:20Z', 'value': 123.45}.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponsePayload, ReportingRenditionTimeSeries]]
    """

    kwargs = _get_kwargs(
        organisation_group=organisation_group,
        organisation_id=organisation_id,
        tag_id=tag_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    organisation_group: str,
    organisation_id: UUID,
    tag_id: UUID,
    *,
    client: AuthenticatedClient,
    body: AddReportingRenditionPayload,
) -> Optional[Union[ErrorResponsePayload, ReportingRenditionTimeSeries]]:
    """
    Args:
        organisation_group (str):
        organisation_id (UUID):
        tag_id (UUID):
        body (AddReportingRenditionPayload):  Example: {'endDate': '2023-11-15T22:13:20Z',
            'startDate': '2023-11-14T22:13:20Z', 'value': 123.45}.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponsePayload, ReportingRenditionTimeSeries]
    """

    return (
        await asyncio_detailed(
            organisation_group=organisation_group,
            organisation_id=organisation_id,
            tag_id=tag_id,
            client=client,
            body=body,
        )
    ).parsed
