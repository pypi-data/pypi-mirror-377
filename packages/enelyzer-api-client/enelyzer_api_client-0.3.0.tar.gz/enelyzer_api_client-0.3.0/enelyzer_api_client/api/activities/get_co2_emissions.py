from http import HTTPStatus
from typing import Any, Optional, Union
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.co2_emission_search_parameters import CO2EmissionSearchParameters
from ...models.error_response_payload import ErrorResponsePayload
from ...models.paginated_result_carbon_emission import PaginatedResultCarbonEmission
from ...types import UNSET, Response, Unset


def _get_kwargs(
    organisation_group: str,
    organisation_id: UUID,
    *,
    body: CO2EmissionSearchParameters,
    page: Union[None, Unset, int] = UNSET,
    page_size: Union[None, Unset, int] = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    params: dict[str, Any] = {}

    json_page: Union[None, Unset, int]
    if isinstance(page, Unset):
        json_page = UNSET
    else:
        json_page = page
    params["page"] = json_page

    json_page_size: Union[None, Unset, int]
    if isinstance(page_size, Unset):
        json_page_size = UNSET
    else:
        json_page_size = page_size
    params["pageSize"] = json_page_size

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/v1/{organisation_group}/{organisation_id}/activities/co2-emissions",
        "params": params,
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[ErrorResponsePayload, PaginatedResultCarbonEmission]]:
    if response.status_code == 200:
        response_200 = PaginatedResultCarbonEmission.from_dict(response.json())

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
) -> Response[Union[ErrorResponsePayload, PaginatedResultCarbonEmission]]:
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
    client: AuthenticatedClient,
    body: CO2EmissionSearchParameters,
    page: Union[None, Unset, int] = UNSET,
    page_size: Union[None, Unset, int] = UNSET,
) -> Response[Union[ErrorResponsePayload, PaginatedResultCarbonEmission]]:
    """
    Args:
        organisation_group (str):
        organisation_id (UUID):
        page (Union[None, Unset, int]):
        page_size (Union[None, Unset, int]):
        body (CO2EmissionSearchParameters):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponsePayload, PaginatedResultCarbonEmission]]
    """

    kwargs = _get_kwargs(
        organisation_group=organisation_group,
        organisation_id=organisation_id,
        body=body,
        page=page,
        page_size=page_size,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    organisation_group: str,
    organisation_id: UUID,
    *,
    client: AuthenticatedClient,
    body: CO2EmissionSearchParameters,
    page: Union[None, Unset, int] = UNSET,
    page_size: Union[None, Unset, int] = UNSET,
) -> Optional[Union[ErrorResponsePayload, PaginatedResultCarbonEmission]]:
    """
    Args:
        organisation_group (str):
        organisation_id (UUID):
        page (Union[None, Unset, int]):
        page_size (Union[None, Unset, int]):
        body (CO2EmissionSearchParameters):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponsePayload, PaginatedResultCarbonEmission]
    """

    return sync_detailed(
        organisation_group=organisation_group,
        organisation_id=organisation_id,
        client=client,
        body=body,
        page=page,
        page_size=page_size,
    ).parsed


async def asyncio_detailed(
    organisation_group: str,
    organisation_id: UUID,
    *,
    client: AuthenticatedClient,
    body: CO2EmissionSearchParameters,
    page: Union[None, Unset, int] = UNSET,
    page_size: Union[None, Unset, int] = UNSET,
) -> Response[Union[ErrorResponsePayload, PaginatedResultCarbonEmission]]:
    """
    Args:
        organisation_group (str):
        organisation_id (UUID):
        page (Union[None, Unset, int]):
        page_size (Union[None, Unset, int]):
        body (CO2EmissionSearchParameters):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponsePayload, PaginatedResultCarbonEmission]]
    """

    kwargs = _get_kwargs(
        organisation_group=organisation_group,
        organisation_id=organisation_id,
        body=body,
        page=page,
        page_size=page_size,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    organisation_group: str,
    organisation_id: UUID,
    *,
    client: AuthenticatedClient,
    body: CO2EmissionSearchParameters,
    page: Union[None, Unset, int] = UNSET,
    page_size: Union[None, Unset, int] = UNSET,
) -> Optional[Union[ErrorResponsePayload, PaginatedResultCarbonEmission]]:
    """
    Args:
        organisation_group (str):
        organisation_id (UUID):
        page (Union[None, Unset, int]):
        page_size (Union[None, Unset, int]):
        body (CO2EmissionSearchParameters):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponsePayload, PaginatedResultCarbonEmission]
    """

    return (
        await asyncio_detailed(
            organisation_group=organisation_group,
            organisation_id=organisation_id,
            client=client,
            body=body,
            page=page,
            page_size=page_size,
        )
    ).parsed
