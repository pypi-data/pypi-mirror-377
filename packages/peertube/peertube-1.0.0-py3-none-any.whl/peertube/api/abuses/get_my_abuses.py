from http import HTTPStatus
from typing import Any

import httpx

from peertube import errors
from peertube.client import AuthenticatedClient, Client
from peertube.models.abuse_state_set import AbuseStateSet
from peertube.models.get_my_abuses_sort import GetMyAbusesSort
from peertube.types import UNSET, Response, Unset


def _get_kwargs(
    *,
    id: Unset | int = UNSET,
    state: Unset | AbuseStateSet = UNSET,
    sort: Unset | GetMyAbusesSort = UNSET,
    start: Unset | int = UNSET,
    count: Unset | int = 15,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["id"] = id

    json_state: Unset | int = UNSET
    if not isinstance(state, Unset):
        json_state = state.value

    params["state"] = json_state

    json_sort: Unset | str = UNSET
    if not isinstance(sort, Unset):
        json_sort = sort.value

    params["sort"] = json_sort

    params["start"] = start

    params["count"] = count

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/users/me/abuses",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | None:
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
    client: AuthenticatedClient,
    id: Unset | int = UNSET,
    state: Unset | AbuseStateSet = UNSET,
    sort: Unset | GetMyAbusesSort = UNSET,
    start: Unset | int = UNSET,
    count: Unset | int = 15,
) -> Response[Any]:
    """List my abuses

    Args:
        id (Union[Unset, int]): Unique identifier for the entity.
        state (Union[Unset, AbuseStateSet]): The abuse state (Pending = `1`, Rejected = `2`,
            Accepted = `3`)
        sort (Union[Unset, GetMyAbusesSort]): Sorting criteria for results.
        start (Union[Unset, int]): Starting index for pagination.
        client: Authenticated HTTP client for API requests.
        count (Union[Unset, int]):  Default: 15.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        id=id,
        state=state,
        sort=sort,
        start=start,
        count=count,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    id: Unset | int = UNSET,
    state: Unset | AbuseStateSet = UNSET,
    sort: Unset | GetMyAbusesSort = UNSET,
    start: Unset | int = UNSET,
    count: Unset | int = 15,
) -> Response[Any]:
    """List my abuses

    Args:
        id (Union[Unset, int]): Unique identifier for the entity.
        state (Union[Unset, AbuseStateSet]): The abuse state (Pending = `1`, Rejected = `2`,
            Accepted = `3`)
        sort (Union[Unset, GetMyAbusesSort]): Sorting criteria for results.
        start (Union[Unset, int]): Starting index for pagination.
        client: Authenticated HTTP client for API requests.
        count (Union[Unset, int]):  Default: 15.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        id=id,
        state=state,
        sort=sort,
        start=start,
        count=count,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)
