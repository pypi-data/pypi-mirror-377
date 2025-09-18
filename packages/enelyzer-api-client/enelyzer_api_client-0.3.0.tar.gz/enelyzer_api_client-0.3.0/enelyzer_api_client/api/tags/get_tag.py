from http import HTTPStatus
from typing import Any, Optional, Union
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.api_tag import ApiTag
from ...models.error_response_payload import ErrorResponsePayload
from ...types import Response


def _get_kwargs(
    organisation_group: str,
    organisation_id: UUID,
    tag_id: UUID,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/v1/{organisation_group}/{organisation_id}/energy-efficiency/tags/{tag_id}",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[ApiTag, ErrorResponsePayload]]:
    if response.status_code == 200:
        response_200 = ApiTag.from_dict(response.json())

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
) -> Response[Union[ApiTag, ErrorResponsePayload]]:
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
) -> Response[Union[ApiTag, ErrorResponsePayload]]:
    """
    Args:
        organisation_group (str):
        organisation_id (UUID):
        tag_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ApiTag, ErrorResponsePayload]]
    """

    kwargs = _get_kwargs(
        organisation_group=organisation_group,
        organisation_id=organisation_id,
        tag_id=tag_id,
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
) -> Optional[Union[ApiTag, ErrorResponsePayload]]:
    """
    Args:
        organisation_group (str):
        organisation_id (UUID):
        tag_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ApiTag, ErrorResponsePayload]
    """

    return sync_detailed(
        organisation_group=organisation_group,
        organisation_id=organisation_id,
        tag_id=tag_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    organisation_group: str,
    organisation_id: UUID,
    tag_id: UUID,
    *,
    client: AuthenticatedClient,
) -> Response[Union[ApiTag, ErrorResponsePayload]]:
    """
    Args:
        organisation_group (str):
        organisation_id (UUID):
        tag_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ApiTag, ErrorResponsePayload]]
    """

    kwargs = _get_kwargs(
        organisation_group=organisation_group,
        organisation_id=organisation_id,
        tag_id=tag_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    organisation_group: str,
    organisation_id: UUID,
    tag_id: UUID,
    *,
    client: AuthenticatedClient,
) -> Optional[Union[ApiTag, ErrorResponsePayload]]:
    """
    Args:
        organisation_group (str):
        organisation_id (UUID):
        tag_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ApiTag, ErrorResponsePayload]
    """

    return (
        await asyncio_detailed(
            organisation_group=organisation_group,
            organisation_id=organisation_id,
            tag_id=tag_id,
            client=client,
        )
    ).parsed
