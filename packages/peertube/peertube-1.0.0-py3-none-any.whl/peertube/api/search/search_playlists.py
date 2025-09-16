from http import HTTPStatus
from typing import Any, cast

import httpx

from peertube import errors
from peertube.client import AuthenticatedClient, Client
from peertube.models.search_playlists_response_200 import SearchPlaylistsResponse200
from peertube.models.search_playlists_search_target import SearchPlaylistsSearchTarget
from peertube.types import UNSET, Response, Unset


def _get_kwargs(
    *,
    search: str,
    start: Unset | int = UNSET,
    count: Unset | int = 15,
    search_target: Unset | SearchPlaylistsSearchTarget = UNSET,
    sort: Unset | str = UNSET,
    host: Unset | str = UNSET,
    uuids: Unset | Any = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["search"] = search

    params["start"] = start

    params["count"] = count

    json_search_target: Unset | str = UNSET
    if not isinstance(search_target, Unset):
        json_search_target = search_target.value

    params["searchTarget"] = json_search_target

    params["sort"] = sort

    params["host"] = host

    params["uuids"] = uuids

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/search/video-playlists",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | SearchPlaylistsResponse200 | None:
    if response.status_code == 200:
        response_200 = SearchPlaylistsResponse200.from_dict(response.json())

        return response_200

    if response.status_code == 500:
        response_500 = cast("Any", None)
        return response_500

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Any | SearchPlaylistsResponse200]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    search: str,
    start: Unset | int = UNSET,
    count: Unset | int = 15,
    search_target: Unset | SearchPlaylistsSearchTarget = UNSET,
    sort: Unset | str = UNSET,
    host: Unset | str = UNSET,
    uuids: Unset | Any = UNSET,
) -> Response[Any | SearchPlaylistsResponse200]:
    """Search playlists

    Args:
        search (str): Search query filter.
        start (Union[Unset, int]): Starting index for pagination.
        count (Union[Unset, int]):  Default: 15.
        search_target (Union[Unset, SearchPlaylistsSearchTarget]): Search filter for target.
        sort (Union[Unset, str]):  Example: -createdAt.
        host (Union[Unset, str]): Parameter for host.
        uuids (Union[Unset, Any]): Parameter for uuids.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, SearchPlaylistsResponse200]]
    """

    kwargs = _get_kwargs(
        search=search,
        start=start,
        count=count,
        search_target=search_target,
        sort=sort,
        host=host,
        uuids=uuids,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    search: str,
    start: Unset | int = UNSET,
    count: Unset | int = 15,
    search_target: Unset | SearchPlaylistsSearchTarget = UNSET,
    sort: Unset | str = UNSET,
    host: Unset | str = UNSET,
    uuids: Unset | Any = UNSET,
) -> Any | SearchPlaylistsResponse200 | None:
    """Search playlists

    Args:
        search (str): Search query filter.
        start (Union[Unset, int]): Starting index for pagination.
        count (Union[Unset, int]):  Default: 15.
        search_target (Union[Unset, SearchPlaylistsSearchTarget]): Search filter for target.
        sort (Union[Unset, str]):  Example: -createdAt.
        host (Union[Unset, str]): Parameter for host.
        uuids (Union[Unset, Any]): Parameter for uuids.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, SearchPlaylistsResponse200]
    """

    return sync_detailed(
        client=client,
        search=search,
        start=start,
        count=count,
        search_target=search_target,
        sort=sort,
        host=host,
        uuids=uuids,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    search: str,
    start: Unset | int = UNSET,
    count: Unset | int = 15,
    search_target: Unset | SearchPlaylistsSearchTarget = UNSET,
    sort: Unset | str = UNSET,
    host: Unset | str = UNSET,
    uuids: Unset | Any = UNSET,
) -> Response[Any | SearchPlaylistsResponse200]:
    """Search playlists

    Args:
        search (str): Search query filter.
        start (Union[Unset, int]): Starting index for pagination.
        count (Union[Unset, int]):  Default: 15.
        search_target (Union[Unset, SearchPlaylistsSearchTarget]): Search filter for target.
        sort (Union[Unset, str]):  Example: -createdAt.
        host (Union[Unset, str]): Parameter for host.
        uuids (Union[Unset, Any]): Parameter for uuids.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, SearchPlaylistsResponse200]]
    """

    kwargs = _get_kwargs(
        search=search,
        start=start,
        count=count,
        search_target=search_target,
        sort=sort,
        host=host,
        uuids=uuids,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    search: str,
    start: Unset | int = UNSET,
    count: Unset | int = 15,
    search_target: Unset | SearchPlaylistsSearchTarget = UNSET,
    sort: Unset | str = UNSET,
    host: Unset | str = UNSET,
    uuids: Unset | Any = UNSET,
) -> Any | SearchPlaylistsResponse200 | None:
    """Search playlists

    Args:
        search (str): Search query filter.
        start (Union[Unset, int]): Starting index for pagination.
        count (Union[Unset, int]):  Default: 15.
        search_target (Union[Unset, SearchPlaylistsSearchTarget]): Search filter for target.
        sort (Union[Unset, str]):  Example: -createdAt.
        host (Union[Unset, str]): Parameter for host.
        uuids (Union[Unset, Any]): Parameter for uuids.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, SearchPlaylistsResponse200]
    """

    return (
        await asyncio_detailed(
            client=client,
            search=search,
            start=start,
            count=count,
            search_target=search_target,
            sort=sort,
            host=host,
            uuids=uuids,
        )
    ).parsed
