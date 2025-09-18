from http import HTTPStatus
from typing import Any, Optional, Union
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.calculation_method import CalculationMethod
from ...models.error_response_payload import ErrorResponsePayload
from ...types import Response


def _get_kwargs(
    organisation_group: str,
    organisation_id: UUID,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/v1/{organisation_group}/{organisation_id}/co2/calculation-methods",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[ErrorResponsePayload, list[CalculationMethod]]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = CalculationMethod(response_200_item_data)

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
) -> Response[Union[ErrorResponsePayload, list[CalculationMethod]]]:
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
) -> Response[Union[ErrorResponsePayload, list[CalculationMethod]]]:
    """
    Args:
        organisation_group (str):
        organisation_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponsePayload, list[CalculationMethod]]]
    """

    kwargs = _get_kwargs(
        organisation_group=organisation_group,
        organisation_id=organisation_id,
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
) -> Optional[Union[ErrorResponsePayload, list[CalculationMethod]]]:
    """
    Args:
        organisation_group (str):
        organisation_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponsePayload, list[CalculationMethod]]
    """

    return sync_detailed(
        organisation_group=organisation_group,
        organisation_id=organisation_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    organisation_group: str,
    organisation_id: UUID,
    *,
    client: AuthenticatedClient,
) -> Response[Union[ErrorResponsePayload, list[CalculationMethod]]]:
    """
    Args:
        organisation_group (str):
        organisation_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponsePayload, list[CalculationMethod]]]
    """

    kwargs = _get_kwargs(
        organisation_group=organisation_group,
        organisation_id=organisation_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    organisation_group: str,
    organisation_id: UUID,
    *,
    client: AuthenticatedClient,
) -> Optional[Union[ErrorResponsePayload, list[CalculationMethod]]]:
    """
    Args:
        organisation_group (str):
        organisation_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponsePayload, list[CalculationMethod]]
    """

    return (
        await asyncio_detailed(
            organisation_group=organisation_group,
            organisation_id=organisation_id,
            client=client,
        )
    ).parsed
