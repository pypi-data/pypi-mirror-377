from http import HTTPStatus
from typing import Any

import httpx

from peertube import errors
from peertube.client import AuthenticatedClient, Client
from peertube.models.get_video_channel_followers_response_200 import (
    GetVideoChannelFollowersResponse200,
)
from peertube.models.get_video_channel_followers_sort import (
    GetVideoChannelFollowersSort,
)
from peertube.types import UNSET, Response, Unset


def _get_kwargs(
    channel_handle: str,
    *,
    start: Unset | int = UNSET,
    count: Unset | int = 15,
    sort: Unset | GetVideoChannelFollowersSort = UNSET,
    search: Unset | str = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["start"] = start

    params["count"] = count

    json_sort: Unset | str = UNSET
    if not isinstance(sort, Unset):
        json_sort = sort.value

    params["sort"] = json_sort

    params["search"] = search

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/api/v1/video-channels/{channel_handle}/followers",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> GetVideoChannelFollowersResponse200 | None:
    if response.status_code == 200:
        response_200 = GetVideoChannelFollowersResponse200.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[GetVideoChannelFollowersResponse200]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    channel_handle: str,
    *,
    client: AuthenticatedClient,
    start: Unset | int = UNSET,
    count: Unset | int = 15,
    sort: Unset | GetVideoChannelFollowersSort = UNSET,
    search: Unset | str = UNSET,
) -> Response[GetVideoChannelFollowersResponse200]:
    """List followers of a video channel

    Args:
        channel_handle (str):  Example: my_username | my_username@example.com.
        start (Union[Unset, int]): Starting index for pagination.
        count (Union[Unset, int]):  Default: 15.
        sort (Union[Unset, GetVideoChannelFollowersSort]): Sorting criteria for results.
        search (Union[Unset, str]): Search query filter.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetVideoChannelFollowersResponse200]
    """

    kwargs = _get_kwargs(
        channel_handle=channel_handle,
        start=start,
        count=count,
        sort=sort,
        search=search,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    channel_handle: str,
    *,
    client: AuthenticatedClient,
    start: Unset | int = UNSET,
    count: Unset | int = 15,
    sort: Unset | GetVideoChannelFollowersSort = UNSET,
    search: Unset | str = UNSET,
) -> GetVideoChannelFollowersResponse200 | None:
    """List followers of a video channel

    Args:
        channel_handle (str):  Example: my_username | my_username@example.com.
        start (Union[Unset, int]): Starting index for pagination.
        count (Union[Unset, int]):  Default: 15.
        sort (Union[Unset, GetVideoChannelFollowersSort]): Sorting criteria for results.
        search (Union[Unset, str]): Search query filter.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetVideoChannelFollowersResponse200
    """

    return sync_detailed(
        channel_handle=channel_handle,
        client=client,
        start=start,
        count=count,
        sort=sort,
        search=search,
    ).parsed


async def asyncio_detailed(
    channel_handle: str,
    *,
    client: AuthenticatedClient,
    start: Unset | int = UNSET,
    count: Unset | int = 15,
    sort: Unset | GetVideoChannelFollowersSort = UNSET,
    search: Unset | str = UNSET,
) -> Response[GetVideoChannelFollowersResponse200]:
    """List followers of a video channel

    Args:
        channel_handle (str):  Example: my_username | my_username@example.com.
        start (Union[Unset, int]): Starting index for pagination.
        count (Union[Unset, int]):  Default: 15.
        sort (Union[Unset, GetVideoChannelFollowersSort]): Sorting criteria for results.
        search (Union[Unset, str]): Search query filter.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetVideoChannelFollowersResponse200]
    """

    kwargs = _get_kwargs(
        channel_handle=channel_handle,
        start=start,
        count=count,
        sort=sort,
        search=search,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    channel_handle: str,
    *,
    client: AuthenticatedClient,
    start: Unset | int = UNSET,
    count: Unset | int = 15,
    sort: Unset | GetVideoChannelFollowersSort = UNSET,
    search: Unset | str = UNSET,
) -> GetVideoChannelFollowersResponse200 | None:
    """List followers of a video channel

    Args:
        channel_handle (str):  Example: my_username | my_username@example.com.
        start (Union[Unset, int]): Starting index for pagination.
        count (Union[Unset, int]):  Default: 15.
        sort (Union[Unset, GetVideoChannelFollowersSort]): Sorting criteria for results.
        search (Union[Unset, str]): Search query filter.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetVideoChannelFollowersResponse200
    """

    return (
        await asyncio_detailed(
            channel_handle=channel_handle,
            client=client,
            start=start,
            count=count,
            sort=sort,
            search=search,
        )
    ).parsed
