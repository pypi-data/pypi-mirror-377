from http import HTTPStatus
from typing import Any, Optional, Union
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response_payload import ErrorResponsePayload
from ...models.paginated_result_api_tag import PaginatedResultApiTag
from ...models.sorting_direction import SortingDirection
from ...models.tag_field import TagField
from ...types import UNSET, Response, Unset


def _get_kwargs(
    organisation_group: str,
    organisation_id: UUID,
    *,
    page: Union[None, Unset, int] = UNSET,
    page_size: Union[None, Unset, int] = UNSET,
    query: Union[None, Unset, str] = UNSET,
    order_by: Union[None, TagField, Unset] = UNSET,
    direction: Union[None, SortingDirection, Unset] = UNSET,
) -> dict[str, Any]:
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

    json_query: Union[None, Unset, str]
    if isinstance(query, Unset):
        json_query = UNSET
    else:
        json_query = query
    params["query"] = json_query

    json_order_by: Union[None, Unset, str]
    if isinstance(order_by, Unset):
        json_order_by = UNSET
    elif isinstance(order_by, TagField):
        json_order_by = order_by.value
    else:
        json_order_by = order_by
    params["orderBy"] = json_order_by

    json_direction: Union[None, Unset, str]
    if isinstance(direction, Unset):
        json_direction = UNSET
    elif isinstance(direction, SortingDirection):
        json_direction = direction.value
    else:
        json_direction = direction
    params["direction"] = json_direction

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/v1/{organisation_group}/{organisation_id}/energy-efficiency/tags",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[ErrorResponsePayload, PaginatedResultApiTag]]:
    if response.status_code == 200:
        response_200 = PaginatedResultApiTag.from_dict(response.json())

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
) -> Response[Union[ErrorResponsePayload, PaginatedResultApiTag]]:
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
    page: Union[None, Unset, int] = UNSET,
    page_size: Union[None, Unset, int] = UNSET,
    query: Union[None, Unset, str] = UNSET,
    order_by: Union[None, TagField, Unset] = UNSET,
    direction: Union[None, SortingDirection, Unset] = UNSET,
) -> Response[Union[ErrorResponsePayload, PaginatedResultApiTag]]:
    """
    Args:
        organisation_group (str):
        organisation_id (UUID):
        page (Union[None, Unset, int]):
        page_size (Union[None, Unset, int]):
        query (Union[None, Unset, str]):
        order_by (Union[None, TagField, Unset]):
        direction (Union[None, SortingDirection, Unset]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponsePayload, PaginatedResultApiTag]]
    """

    kwargs = _get_kwargs(
        organisation_group=organisation_group,
        organisation_id=organisation_id,
        page=page,
        page_size=page_size,
        query=query,
        order_by=order_by,
        direction=direction,
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
    page: Union[None, Unset, int] = UNSET,
    page_size: Union[None, Unset, int] = UNSET,
    query: Union[None, Unset, str] = UNSET,
    order_by: Union[None, TagField, Unset] = UNSET,
    direction: Union[None, SortingDirection, Unset] = UNSET,
) -> Optional[Union[ErrorResponsePayload, PaginatedResultApiTag]]:
    """
    Args:
        organisation_group (str):
        organisation_id (UUID):
        page (Union[None, Unset, int]):
        page_size (Union[None, Unset, int]):
        query (Union[None, Unset, str]):
        order_by (Union[None, TagField, Unset]):
        direction (Union[None, SortingDirection, Unset]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponsePayload, PaginatedResultApiTag]
    """

    return sync_detailed(
        organisation_group=organisation_group,
        organisation_id=organisation_id,
        client=client,
        page=page,
        page_size=page_size,
        query=query,
        order_by=order_by,
        direction=direction,
    ).parsed


async def asyncio_detailed(
    organisation_group: str,
    organisation_id: UUID,
    *,
    client: AuthenticatedClient,
    page: Union[None, Unset, int] = UNSET,
    page_size: Union[None, Unset, int] = UNSET,
    query: Union[None, Unset, str] = UNSET,
    order_by: Union[None, TagField, Unset] = UNSET,
    direction: Union[None, SortingDirection, Unset] = UNSET,
) -> Response[Union[ErrorResponsePayload, PaginatedResultApiTag]]:
    """
    Args:
        organisation_group (str):
        organisation_id (UUID):
        page (Union[None, Unset, int]):
        page_size (Union[None, Unset, int]):
        query (Union[None, Unset, str]):
        order_by (Union[None, TagField, Unset]):
        direction (Union[None, SortingDirection, Unset]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponsePayload, PaginatedResultApiTag]]
    """

    kwargs = _get_kwargs(
        organisation_group=organisation_group,
        organisation_id=organisation_id,
        page=page,
        page_size=page_size,
        query=query,
        order_by=order_by,
        direction=direction,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    organisation_group: str,
    organisation_id: UUID,
    *,
    client: AuthenticatedClient,
    page: Union[None, Unset, int] = UNSET,
    page_size: Union[None, Unset, int] = UNSET,
    query: Union[None, Unset, str] = UNSET,
    order_by: Union[None, TagField, Unset] = UNSET,
    direction: Union[None, SortingDirection, Unset] = UNSET,
) -> Optional[Union[ErrorResponsePayload, PaginatedResultApiTag]]:
    """
    Args:
        organisation_group (str):
        organisation_id (UUID):
        page (Union[None, Unset, int]):
        page_size (Union[None, Unset, int]):
        query (Union[None, Unset, str]):
        order_by (Union[None, TagField, Unset]):
        direction (Union[None, SortingDirection, Unset]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponsePayload, PaginatedResultApiTag]
    """

    return (
        await asyncio_detailed(
            organisation_group=organisation_group,
            organisation_id=organisation_id,
            client=client,
            page=page,
            page_size=page_size,
            query=query,
            order_by=order_by,
            direction=direction,
        )
    ).parsed
