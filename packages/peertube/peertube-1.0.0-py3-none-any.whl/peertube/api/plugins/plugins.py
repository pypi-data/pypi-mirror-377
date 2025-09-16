from http import HTTPStatus
from typing import Any

import httpx

from peertube import errors
from peertube.client import AuthenticatedClient, Client
from peertube.models.plugin_response import PluginResponse
from peertube.types import UNSET, Response, Unset


def _get_kwargs(
    *,
    plugin_type: Unset | int = UNSET,
    uninstalled: Unset | bool = UNSET,
    start: Unset | int = UNSET,
    count: Unset | int = 15,
    sort: Unset | str = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["pluginType"] = plugin_type

    params["uninstalled"] = uninstalled

    params["start"] = start

    params["count"] = count

    params["sort"] = sort

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/plugins",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> PluginResponse | None:
    if response.status_code == 200:
        response_200 = PluginResponse.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[PluginResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    plugin_type: Unset | int = UNSET,
    uninstalled: Unset | bool = UNSET,
    start: Unset | int = UNSET,
    count: Unset | int = 15,
    sort: Unset | str = UNSET,
) -> Response[PluginResponse]:
    """List plugins

    Args:
        plugin_type (Union[Unset, int]): Parameter for plugin type.
        uninstalled (Union[Unset, bool]): Parameter for uninstalled.
        start (Union[Unset, int]): Starting index for pagination.
        count (Union[Unset, int]):  Default: 15.
        sort (Union[Unset, str]):  Example: -createdAt.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PluginResponse]
    """

    kwargs = _get_kwargs(
        plugin_type=plugin_type,
        uninstalled=uninstalled,
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
    plugin_type: Unset | int = UNSET,
    uninstalled: Unset | bool = UNSET,
    start: Unset | int = UNSET,
    count: Unset | int = 15,
    sort: Unset | str = UNSET,
) -> PluginResponse | None:
    """List plugins

    Args:
        plugin_type (Union[Unset, int]): Parameter for plugin type.
        uninstalled (Union[Unset, bool]): Parameter for uninstalled.
        start (Union[Unset, int]): Starting index for pagination.
        count (Union[Unset, int]):  Default: 15.
        sort (Union[Unset, str]):  Example: -createdAt.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PluginResponse
    """

    return sync_detailed(
        client=client,
        plugin_type=plugin_type,
        uninstalled=uninstalled,
        start=start,
        count=count,
        sort=sort,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    plugin_type: Unset | int = UNSET,
    uninstalled: Unset | bool = UNSET,
    start: Unset | int = UNSET,
    count: Unset | int = 15,
    sort: Unset | str = UNSET,
) -> Response[PluginResponse]:
    """List plugins

    Args:
        plugin_type (Union[Unset, int]): Parameter for plugin type.
        uninstalled (Union[Unset, bool]): Parameter for uninstalled.
        start (Union[Unset, int]): Starting index for pagination.
        count (Union[Unset, int]):  Default: 15.
        sort (Union[Unset, str]):  Example: -createdAt.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PluginResponse]
    """

    kwargs = _get_kwargs(
        plugin_type=plugin_type,
        uninstalled=uninstalled,
        start=start,
        count=count,
        sort=sort,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    plugin_type: Unset | int = UNSET,
    uninstalled: Unset | bool = UNSET,
    start: Unset | int = UNSET,
    count: Unset | int = 15,
    sort: Unset | str = UNSET,
) -> PluginResponse | None:
    """List plugins

    Args:
        plugin_type (Union[Unset, int]): Parameter for plugin type.
        uninstalled (Union[Unset, bool]): Parameter for uninstalled.
        start (Union[Unset, int]): Starting index for pagination.
        count (Union[Unset, int]):  Default: 15.
        sort (Union[Unset, str]):  Example: -createdAt.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PluginResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            plugin_type=plugin_type,
            uninstalled=uninstalled,
            start=start,
            count=count,
            sort=sort,
        )
    ).parsed
