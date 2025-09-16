from http import HTTPStatus
from typing import Any

import httpx

from peertube import errors
from peertube.client import AuthenticatedClient, Client
from peertube.models.get_playlists_response_200 import GetPlaylistsResponse200
from peertube.models.video_playlist_type_set import VideoPlaylistTypeSet
from peertube.types import UNSET, Response, Unset


def _get_kwargs(
    *,
    start: Unset | int = UNSET,
    count: Unset | int = 15,
    sort: Unset | str = UNSET,
    playlist_type: Unset | VideoPlaylistTypeSet = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["start"] = start

    params["count"] = count

    params["sort"] = sort

    json_playlist_type: Unset | int = UNSET
    if not isinstance(playlist_type, Unset):
        json_playlist_type = playlist_type.value

    params["playlistType"] = json_playlist_type

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/video-playlists",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> GetPlaylistsResponse200 | None:
    if response.status_code == 200:
        response_200 = GetPlaylistsResponse200.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[GetPlaylistsResponse200]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    start: Unset | int = UNSET,
    count: Unset | int = 15,
    sort: Unset | str = UNSET,
    playlist_type: Unset | VideoPlaylistTypeSet = UNSET,
) -> Response[GetPlaylistsResponse200]:
    """List video playlists

    Args:
        start (Union[Unset, int]): Starting index for pagination.
        count (Union[Unset, int]):  Default: 15.
        sort (Union[Unset, str]):  Example: -createdAt.
        playlist_type (Union[Unset, VideoPlaylistTypeSet]): The video playlist type (Regular =
            `1`, Watch Later = `2`)

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetPlaylistsResponse200]
    """

    kwargs = _get_kwargs(
        start=start,
        count=count,
        sort=sort,
        playlist_type=playlist_type,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    start: Unset | int = UNSET,
    count: Unset | int = 15,
    sort: Unset | str = UNSET,
    playlist_type: Unset | VideoPlaylistTypeSet = UNSET,
) -> GetPlaylistsResponse200 | None:
    """List video playlists

    Args:
        start (Union[Unset, int]): Starting index for pagination.
        count (Union[Unset, int]):  Default: 15.
        sort (Union[Unset, str]):  Example: -createdAt.
        playlist_type (Union[Unset, VideoPlaylistTypeSet]): The video playlist type (Regular =
            `1`, Watch Later = `2`)

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetPlaylistsResponse200
    """

    return sync_detailed(
        client=client,
        start=start,
        count=count,
        sort=sort,
        playlist_type=playlist_type,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    start: Unset | int = UNSET,
    count: Unset | int = 15,
    sort: Unset | str = UNSET,
    playlist_type: Unset | VideoPlaylistTypeSet = UNSET,
) -> Response[GetPlaylistsResponse200]:
    """List video playlists

    Args:
        start (Union[Unset, int]): Starting index for pagination.
        count (Union[Unset, int]):  Default: 15.
        sort (Union[Unset, str]):  Example: -createdAt.
        playlist_type (Union[Unset, VideoPlaylistTypeSet]): The video playlist type (Regular =
            `1`, Watch Later = `2`)

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetPlaylistsResponse200]
    """

    kwargs = _get_kwargs(
        start=start,
        count=count,
        sort=sort,
        playlist_type=playlist_type,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    start: Unset | int = UNSET,
    count: Unset | int = 15,
    sort: Unset | str = UNSET,
    playlist_type: Unset | VideoPlaylistTypeSet = UNSET,
) -> GetPlaylistsResponse200 | None:
    """List video playlists

    Args:
        start (Union[Unset, int]): Starting index for pagination.
        count (Union[Unset, int]):  Default: 15.
        sort (Union[Unset, str]):  Example: -createdAt.
        playlist_type (Union[Unset, VideoPlaylistTypeSet]): The video playlist type (Regular =
            `1`, Watch Later = `2`)

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetPlaylistsResponse200
    """

    return (
        await asyncio_detailed(
            client=client,
            start=start,
            count=count,
            sort=sort,
            playlist_type=playlist_type,
        )
    ).parsed
