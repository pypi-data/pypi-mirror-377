from http import HTTPStatus
from typing import Any, Optional, Union
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.api_reading import ApiReading
from ...models.api_readings_request import ApiReadingsRequest
from ...models.error_response_payload import ErrorResponsePayload
from ...types import Response


def _get_kwargs(
    organisation_group: str,
    organisation_id: UUID,
    *,
    body: ApiReadingsRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/v1/{organisation_group}/{organisation_id}/energy-efficiency/tags/query",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[ErrorResponsePayload, list["ApiReading"]]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = ApiReading.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200

    if response.status_code == 400:
        response_400 = ErrorResponsePayload.from_dict(response.json())

        return response_400

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[ErrorResponsePayload, list["ApiReading"]]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    organisation_group: str,
    organisation_id: UUID,
    *,
    client: Union[AuthenticatedClient, Client],
    body: ApiReadingsRequest,
) -> Response[Union[ErrorResponsePayload, list["ApiReading"]]]:
    """
    Args:
        organisation_group (str):
        organisation_id (UUID):
        body (ApiReadingsRequest):  Example: {'dataTypes': ['normalised'], 'deltaAggregation':
            'sum', 'groupTimeBy': 'quarterHour', 'limit': 1000, 'offset': 0, 'tagId':
            '550e8400-e29b-41d4-a716-446655440000', 'timeEnd': '2023-11-14T22:15:00Z', 'timeStart':
            '2023-11-14T22:13:20Z', 'timezone': 'Europe/London', 'unitTo': None}.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponsePayload, list['ApiReading']]]
    """

    kwargs = _get_kwargs(
        organisation_group=organisation_group,
        organisation_id=organisation_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    organisation_group: str,
    organisation_id: UUID,
    *,
    client: Union[AuthenticatedClient, Client],
    body: ApiReadingsRequest,
) -> Optional[Union[ErrorResponsePayload, list["ApiReading"]]]:
    """
    Args:
        organisation_group (str):
        organisation_id (UUID):
        body (ApiReadingsRequest):  Example: {'dataTypes': ['normalised'], 'deltaAggregation':
            'sum', 'groupTimeBy': 'quarterHour', 'limit': 1000, 'offset': 0, 'tagId':
            '550e8400-e29b-41d4-a716-446655440000', 'timeEnd': '2023-11-14T22:15:00Z', 'timeStart':
            '2023-11-14T22:13:20Z', 'timezone': 'Europe/London', 'unitTo': None}.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponsePayload, list['ApiReading']]
    """

    return sync_detailed(
        organisation_group=organisation_group,
        organisation_id=organisation_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    organisation_group: str,
    organisation_id: UUID,
    *,
    client: Union[AuthenticatedClient, Client],
    body: ApiReadingsRequest,
) -> Response[Union[ErrorResponsePayload, list["ApiReading"]]]:
    """
    Args:
        organisation_group (str):
        organisation_id (UUID):
        body (ApiReadingsRequest):  Example: {'dataTypes': ['normalised'], 'deltaAggregation':
            'sum', 'groupTimeBy': 'quarterHour', 'limit': 1000, 'offset': 0, 'tagId':
            '550e8400-e29b-41d4-a716-446655440000', 'timeEnd': '2023-11-14T22:15:00Z', 'timeStart':
            '2023-11-14T22:13:20Z', 'timezone': 'Europe/London', 'unitTo': None}.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponsePayload, list['ApiReading']]]
    """

    kwargs = _get_kwargs(
        organisation_group=organisation_group,
        organisation_id=organisation_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    organisation_group: str,
    organisation_id: UUID,
    *,
    client: Union[AuthenticatedClient, Client],
    body: ApiReadingsRequest,
) -> Optional[Union[ErrorResponsePayload, list["ApiReading"]]]:
    """
    Args:
        organisation_group (str):
        organisation_id (UUID):
        body (ApiReadingsRequest):  Example: {'dataTypes': ['normalised'], 'deltaAggregation':
            'sum', 'groupTimeBy': 'quarterHour', 'limit': 1000, 'offset': 0, 'tagId':
            '550e8400-e29b-41d4-a716-446655440000', 'timeEnd': '2023-11-14T22:15:00Z', 'timeStart':
            '2023-11-14T22:13:20Z', 'timezone': 'Europe/London', 'unitTo': None}.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponsePayload, list['ApiReading']]
    """

    return (
        await asyncio_detailed(
            organisation_group=organisation_group,
            organisation_id=organisation_id,
            client=client,
            body=body,
        )
    ).parsed
