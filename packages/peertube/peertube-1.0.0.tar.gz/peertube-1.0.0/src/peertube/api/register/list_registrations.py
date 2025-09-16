from http import HTTPStatus
from typing import Any

import httpx

from peertube import errors
from peertube.client import AuthenticatedClient, Client
from peertube.models.list_registrations_response_200 import ListRegistrationsResponse200
from peertube.models.list_registrations_sort import ListRegistrationsSort
from peertube.types import UNSET, Response, Unset


def _get_kwargs(
    *,
    start: Unset | int = UNSET,
    count: Unset | int = 15,
    search: Unset | str = UNSET,
    sort: Unset | ListRegistrationsSort = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["start"] = start

    params["count"] = count

    params["search"] = search

    json_sort: Unset | str = UNSET
    if not isinstance(sort, Unset):
        json_sort = sort.value

    params["sort"] = json_sort

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/users/registrations",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ListRegistrationsResponse200 | None:
    if response.status_code == 200:
        response_200 = ListRegistrationsResponse200.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[ListRegistrationsResponse200]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    start: Unset | int = UNSET,
    count: Unset | int = 15,
    search: Unset | str = UNSET,
    sort: Unset | ListRegistrationsSort = UNSET,
) -> Response[ListRegistrationsResponse200]:
    """List registrations

    Args:
        start (Union[Unset, int]): Starting index for pagination.
        count (Union[Unset, int]):  Default: 15.
        search (Union[Unset, str]): Search query filter.
        client: Authenticated HTTP client for API requests.
        sort (Union[Unset, ListRegistrationsSort]): Sorting criteria for results.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ListRegistrationsResponse200]
    """

    kwargs = _get_kwargs(
        start=start,
        count=count,
        search=search,
        sort=sort,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    start: Unset | int = UNSET,
    count: Unset | int = 15,
    search: Unset | str = UNSET,
    sort: Unset | ListRegistrationsSort = UNSET,
) -> ListRegistrationsResponse200 | None:
    """List registrations

    Args:
        start (Union[Unset, int]): Starting index for pagination.
        count (Union[Unset, int]):  Default: 15.
        search (Union[Unset, str]): Search query filter.
        client: Authenticated HTTP client for API requests.
        sort (Union[Unset, ListRegistrationsSort]): Sorting criteria for results.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ListRegistrationsResponse200
    """

    return sync_detailed(
        client=client,
        start=start,
        count=count,
        search=search,
        sort=sort,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    start: Unset | int = UNSET,
    count: Unset | int = 15,
    search: Unset | str = UNSET,
    sort: Unset | ListRegistrationsSort = UNSET,
) -> Response[ListRegistrationsResponse200]:
    """List registrations

    Args:
        start (Union[Unset, int]): Starting index for pagination.
        count (Union[Unset, int]):  Default: 15.
        search (Union[Unset, str]): Search query filter.
        client: Authenticated HTTP client for API requests.
        sort (Union[Unset, ListRegistrationsSort]): Sorting criteria for results.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ListRegistrationsResponse200]
    """

    kwargs = _get_kwargs(
        start=start,
        count=count,
        search=search,
        sort=sort,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    start: Unset | int = UNSET,
    count: Unset | int = 15,
    search: Unset | str = UNSET,
    sort: Unset | ListRegistrationsSort = UNSET,
) -> ListRegistrationsResponse200 | None:
    """List registrations

    Args:
        start (Union[Unset, int]): Starting index for pagination.
        count (Union[Unset, int]):  Default: 15.
        search (Union[Unset, str]): Search query filter.
        client: Authenticated HTTP client for API requests.
        sort (Union[Unset, ListRegistrationsSort]): Sorting criteria for results.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ListRegistrationsResponse200
    """

    return (
        await asyncio_detailed(
            client=client,
            start=start,
            count=count,
            search=search,
            sort=sort,
        )
    ).parsed
