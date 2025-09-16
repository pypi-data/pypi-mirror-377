from http import HTTPStatus
from typing import Any
from uuid import UUID

import httpx

from peertube import errors
from peertube.client import AuthenticatedClient, Client
from peertube.models.list_video_storyboards_response_200 import (
    ListVideoStoryboardsResponse200,
)
from peertube.types import Response


def _get_kwargs(
    id: UUID | int | str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/api/v1/videos/{id}/storyboards",
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ListVideoStoryboardsResponse200 | None:
    if response.status_code == 200:
        response_200 = ListVideoStoryboardsResponse200.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[ListVideoStoryboardsResponse200]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    id: UUID | int | str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[ListVideoStoryboardsResponse200]:
    """List storyboards of a video

     **PeerTube >= 6.0**

    Args:
        id (Union[UUID, int, str]): Unique identifier for the entity.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ListVideoStoryboardsResponse200]
    """

    kwargs = _get_kwargs(
        id=id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    id: UUID | int | str,
    *,
    client: AuthenticatedClient | Client,
) -> ListVideoStoryboardsResponse200 | None:
    """List storyboards of a video

     **PeerTube >= 6.0**

    Args:
        id (Union[UUID, int, str]): Unique identifier for the entity.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ListVideoStoryboardsResponse200
    """

    return sync_detailed(
        id=id,
        client=client,
    ).parsed


async def asyncio_detailed(
    id: UUID | int | str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[ListVideoStoryboardsResponse200]:
    """List storyboards of a video

     **PeerTube >= 6.0**

    Args:
        id (Union[UUID, int, str]): Unique identifier for the entity.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ListVideoStoryboardsResponse200]
    """

    kwargs = _get_kwargs(
        id=id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    id: UUID | int | str,
    *,
    client: AuthenticatedClient | Client,
) -> ListVideoStoryboardsResponse200 | None:
    """List storyboards of a video

     **PeerTube >= 6.0**

    Args:
        id (Union[UUID, int, str]): Unique identifier for the entity.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ListVideoStoryboardsResponse200
    """

    return (
        await asyncio_detailed(
            id=id,
            client=client,
        )
    ).parsed
