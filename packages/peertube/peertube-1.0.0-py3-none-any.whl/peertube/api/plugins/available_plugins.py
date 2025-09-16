from http import HTTPStatus
from typing import Any, cast

import httpx

from peertube import errors
from peertube.client import AuthenticatedClient, Client
from peertube.models.plugin_response import PluginResponse
from peertube.types import UNSET, Response, Unset


def _get_kwargs(
    *,
    search: Unset | str = UNSET,
    plugin_type: Unset | int = UNSET,
    current_peer_tube_engine: Unset | str = UNSET,
    start: Unset | int = UNSET,
    count: Unset | int = 15,
    sort: Unset | str = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["search"] = search

    params["pluginType"] = plugin_type

    params["currentPeerTubeEngine"] = current_peer_tube_engine

    params["start"] = start

    params["count"] = count

    params["sort"] = sort

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/plugins/available",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | PluginResponse | None:
    if response.status_code == 200:
        response_200 = PluginResponse.from_dict(response.json())

        return response_200

    if response.status_code == 503:
        response_503 = cast("Any", None)
        return response_503

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Any | PluginResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    search: Unset | str = UNSET,
    plugin_type: Unset | int = UNSET,
    current_peer_tube_engine: Unset | str = UNSET,
    start: Unset | int = UNSET,
    count: Unset | int = 15,
    sort: Unset | str = UNSET,
) -> Response[Any | PluginResponse]:
    """List available plugins

    Args:
        search (Union[Unset, str]): Search query filter.
        plugin_type (Union[Unset, int]): Parameter for plugin type.
        current_peer_tube_engine (Union[Unset, str]): Parameter for current peer tube engine.
        start (Union[Unset, int]): Starting index for pagination.
        count (Union[Unset, int]):  Default: 15.
        sort (Union[Unset, str]):  Example: -createdAt.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, PluginResponse]]
    """

    kwargs = _get_kwargs(
        search=search,
        plugin_type=plugin_type,
        current_peer_tube_engine=current_peer_tube_engine,
        start=start,
        count=count,
        sort=sort,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    search: Unset | str = UNSET,
    plugin_type: Unset | int = UNSET,
    current_peer_tube_engine: Unset | str = UNSET,
    start: Unset | int = UNSET,
    count: Unset | int = 15,
    sort: Unset | str = UNSET,
) -> Any | PluginResponse | None:
    """List available plugins

    Args:
        search (Union[Unset, str]): Search query filter.
        plugin_type (Union[Unset, int]): Parameter for plugin type.
        current_peer_tube_engine (Union[Unset, str]): Parameter for current peer tube engine.
        start (Union[Unset, int]): Starting index for pagination.
        count (Union[Unset, int]):  Default: 15.
        sort (Union[Unset, str]):  Example: -createdAt.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, PluginResponse]
    """

    return sync_detailed(
        client=client,
        search=search,
        plugin_type=plugin_type,
        current_peer_tube_engine=current_peer_tube_engine,
        start=start,
        count=count,
        sort=sort,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    search: Unset | str = UNSET,
    plugin_type: Unset | int = UNSET,
    current_peer_tube_engine: Unset | str = UNSET,
    start: Unset | int = UNSET,
    count: Unset | int = 15,
    sort: Unset | str = UNSET,
) -> Response[Any | PluginResponse]:
    """List available plugins

    Args:
        search (Union[Unset, str]): Search query filter.
        plugin_type (Union[Unset, int]): Parameter for plugin type.
        current_peer_tube_engine (Union[Unset, str]): Parameter for current peer tube engine.
        start (Union[Unset, int]): Starting index for pagination.
        count (Union[Unset, int]):  Default: 15.
        sort (Union[Unset, str]):  Example: -createdAt.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, PluginResponse]]
    """

    kwargs = _get_kwargs(
        search=search,
        plugin_type=plugin_type,
        current_peer_tube_engine=current_peer_tube_engine,
        start=start,
        count=count,
        sort=sort,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    search: Unset | str = UNSET,
    plugin_type: Unset | int = UNSET,
    current_peer_tube_engine: Unset | str = UNSET,
    start: Unset | int = UNSET,
    count: Unset | int = 15,
    sort: Unset | str = UNSET,
) -> Any | PluginResponse | None:
    """List available plugins

    Args:
        search (Union[Unset, str]): Search query filter.
        plugin_type (Union[Unset, int]): Parameter for plugin type.
        current_peer_tube_engine (Union[Unset, str]): Parameter for current peer tube engine.
        start (Union[Unset, int]): Starting index for pagination.
        count (Union[Unset, int]):  Default: 15.
        sort (Union[Unset, str]):  Example: -createdAt.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, PluginResponse]
    """

    return (
        await asyncio_detailed(
            client=client,
            search=search,
            plugin_type=plugin_type,
            current_peer_tube_engine=current_peer_tube_engine,
            start=start,
            count=count,
            sort=sort,
        )
    ).parsed
