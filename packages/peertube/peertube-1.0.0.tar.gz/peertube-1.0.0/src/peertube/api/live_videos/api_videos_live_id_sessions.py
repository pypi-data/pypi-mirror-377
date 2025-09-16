from http import HTTPStatus
from typing import Any
from uuid import UUID

import httpx

from peertube import errors
from peertube.client import AuthenticatedClient, Client
from peertube.models.get_api_v1_videos_live_id_sessions_response_200 import (
    GetApiV1VideosLiveIdSessionsResponse200,
)
from peertube.types import Response


def _get_kwargs(
    id: UUID | int | str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/api/v1/videos/live/{id}/sessions",
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> GetApiV1VideosLiveIdSessionsResponse200 | None:
    if response.status_code == 200:
        response_200 = GetApiV1VideosLiveIdSessionsResponse200.from_dict(
            response.json()
        )

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[GetApiV1VideosLiveIdSessionsResponse200]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    id: UUID | int | str,
    *,
    client: AuthenticatedClient,
) -> Response[GetApiV1VideosLiveIdSessionsResponse200]:
    """List live sessions

     List all sessions created in a particular live

    Args:
        id (Union[UUID, int, str]): Unique identifier for the entity.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetApiV1VideosLiveIdSessionsResponse200]
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
    client: AuthenticatedClient,
) -> GetApiV1VideosLiveIdSessionsResponse200 | None:
    """List live sessions

     List all sessions created in a particular live

    Args:
        id (Union[UUID, int, str]): Unique identifier for the entity.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetApiV1VideosLiveIdSessionsResponse200
    """

    return sync_detailed(
        id=id,
        client=client,
    ).parsed


async def asyncio_detailed(
    id: UUID | int | str,
    *,
    client: AuthenticatedClient,
) -> Response[GetApiV1VideosLiveIdSessionsResponse200]:
    """List live sessions

     List all sessions created in a particular live

    Args:
        id (Union[UUID, int, str]): Unique identifier for the entity.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetApiV1VideosLiveIdSessionsResponse200]
    """

    kwargs = _get_kwargs(
        id=id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    id: UUID | int | str,
    *,
    client: AuthenticatedClient,
) -> GetApiV1VideosLiveIdSessionsResponse200 | None:
    """List live sessions

     List all sessions created in a particular live

    Args:
        id (Union[UUID, int, str]): Unique identifier for the entity.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetApiV1VideosLiveIdSessionsResponse200
    """

    return (
        await asyncio_detailed(
            id=id,
            client=client,
        )
    ).parsed
