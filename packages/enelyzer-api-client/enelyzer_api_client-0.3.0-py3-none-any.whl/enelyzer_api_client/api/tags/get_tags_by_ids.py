from http import HTTPStatus
from typing import Any, Optional, Union
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.api_tag import ApiTag
from ...models.error_response_payload import ErrorResponsePayload
from ...models.tag_ids_payload import TagIdsPayload
from ...types import Response


def _get_kwargs(
    organisation_group: str,
    organisation_id: UUID,
    *,
    body: TagIdsPayload,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/v1/{organisation_group}/{organisation_id}/energy-efficiency/tags/filter",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[ErrorResponsePayload, list["ApiTag"]]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = ApiTag.from_dict(response_200_item_data)

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
) -> Response[Union[ErrorResponsePayload, list["ApiTag"]]]:
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
    body: TagIdsPayload,
) -> Response[Union[ErrorResponsePayload, list["ApiTag"]]]:
    """
    Args:
        organisation_group (str):
        organisation_id (UUID):
        body (TagIdsPayload):  Example: {'tagIds': ['550e8400-e29b-41d4-a716-446655440000'],
            'withConversions': False, 'withFormula': False, 'withFullComposition': False}.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponsePayload, list['ApiTag']]]
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
    client: AuthenticatedClient,
    body: TagIdsPayload,
) -> Optional[Union[ErrorResponsePayload, list["ApiTag"]]]:
    """
    Args:
        organisation_group (str):
        organisation_id (UUID):
        body (TagIdsPayload):  Example: {'tagIds': ['550e8400-e29b-41d4-a716-446655440000'],
            'withConversions': False, 'withFormula': False, 'withFullComposition': False}.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponsePayload, list['ApiTag']]
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
    client: AuthenticatedClient,
    body: TagIdsPayload,
) -> Response[Union[ErrorResponsePayload, list["ApiTag"]]]:
    """
    Args:
        organisation_group (str):
        organisation_id (UUID):
        body (TagIdsPayload):  Example: {'tagIds': ['550e8400-e29b-41d4-a716-446655440000'],
            'withConversions': False, 'withFormula': False, 'withFullComposition': False}.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponsePayload, list['ApiTag']]]
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
    client: AuthenticatedClient,
    body: TagIdsPayload,
) -> Optional[Union[ErrorResponsePayload, list["ApiTag"]]]:
    """
    Args:
        organisation_group (str):
        organisation_id (UUID):
        body (TagIdsPayload):  Example: {'tagIds': ['550e8400-e29b-41d4-a716-446655440000'],
            'withConversions': False, 'withFormula': False, 'withFullComposition': False}.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponsePayload, list['ApiTag']]
    """

    return (
        await asyncio_detailed(
            organisation_group=organisation_group,
            organisation_id=organisation_id,
            client=client,
            body=body,
        )
    ).parsed
