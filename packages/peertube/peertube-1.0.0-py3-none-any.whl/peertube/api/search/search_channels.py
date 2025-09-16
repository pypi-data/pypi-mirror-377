from http import HTTPStatus
from typing import Any

import httpx

from peertube import errors
from peertube.client import AuthenticatedClient, Client
from peertube.models.search_channels_search_target import SearchChannelsSearchTarget
from peertube.types import UNSET, Response, Unset


def _get_kwargs(
    *,
    search: str,
    start: Unset | int = UNSET,
    count: Unset | int = 15,
    search_target: Unset | SearchChannelsSearchTarget = UNSET,
    sort: Unset | str = UNSET,
    host: Unset | str = UNSET,
    handles: Unset | Any = UNSET,
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

    params["handles"] = handles

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/search/video-channels",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | None:
    if response.status_code == 500:
        return None

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Any]:
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
    search_target: Unset | SearchChannelsSearchTarget = UNSET,
    sort: Unset | str = UNSET,
    host: Unset | str = UNSET,
    handles: Unset | Any = UNSET,
) -> Response[Any]:
    """Search channels

    Args:
        search (str): Search query filter.
        start (Union[Unset, int]): Starting index for pagination.
        count (Union[Unset, int]):  Default: 15.
        search_target (Union[Unset, SearchChannelsSearchTarget]): Search filter for target.
        sort (Union[Unset, str]):  Example: -createdAt.
        host (Union[Unset, str]): Parameter for host.
        handles (Union[Unset, Any]): Parameter for handles.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        search=search,
        start=start,
        count=count,
        search_target=search_target,
        sort=sort,
        host=host,
        handles=handles,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    search: str,
    start: Unset | int = UNSET,
    count: Unset | int = 15,
    search_target: Unset | SearchChannelsSearchTarget = UNSET,
    sort: Unset | str = UNSET,
    host: Unset | str = UNSET,
    handles: Unset | Any = UNSET,
) -> Response[Any]:
    """Search channels

    Args:
        search (str): Search query filter.
        start (Union[Unset, int]): Starting index for pagination.
        count (Union[Unset, int]):  Default: 15.
        search_target (Union[Unset, SearchChannelsSearchTarget]): Search filter for target.
        sort (Union[Unset, str]):  Example: -createdAt.
        host (Union[Unset, str]): Parameter for host.
        handles (Union[Unset, Any]): Parameter for handles.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        search=search,
        start=start,
        count=count,
        search_target=search_target,
        sort=sort,
        host=host,
        handles=handles,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)
