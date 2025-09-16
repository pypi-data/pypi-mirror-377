from http import HTTPStatus
from typing import Any

import httpx

from peertube import errors
from peertube.client import AuthenticatedClient, Client
from peertube.models.get_api_v1_server_followers_actor_type import (
    GetApiV1ServerFollowersActorType,
)
from peertube.models.get_api_v1_server_followers_response_200 import (
    GetApiV1ServerFollowersResponse200,
)
from peertube.models.get_api_v1_server_followers_state import (
    GetApiV1ServerFollowersState,
)
from peertube.types import UNSET, Response, Unset


def _get_kwargs(
    *,
    state: Unset | GetApiV1ServerFollowersState = UNSET,
    actor_type: Unset | GetApiV1ServerFollowersActorType = UNSET,
    start: Unset | int = UNSET,
    count: Unset | int = 15,
    sort: Unset | str = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_state: Unset | str = UNSET
    if not isinstance(state, Unset):
        json_state = state.value

    params["state"] = json_state

    json_actor_type: Unset | str = UNSET
    if not isinstance(actor_type, Unset):
        json_actor_type = actor_type.value

    params["actorType"] = json_actor_type

    params["start"] = start

    params["count"] = count

    params["sort"] = sort

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/server/followers",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> GetApiV1ServerFollowersResponse200 | None:
    if response.status_code == 200:
        response_200 = GetApiV1ServerFollowersResponse200.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[GetApiV1ServerFollowersResponse200]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    state: Unset | GetApiV1ServerFollowersState = UNSET,
    actor_type: Unset | GetApiV1ServerFollowersActorType = UNSET,
    start: Unset | int = UNSET,
    count: Unset | int = 15,
    sort: Unset | str = UNSET,
) -> Response[GetApiV1ServerFollowersResponse200]:
    """List instances following the server

    Args:
        state (Union[Unset, GetApiV1ServerFollowersState]): Current state or status filter.
        actor_type (Union[Unset, GetApiV1ServerFollowersActorType]): Parameter for actor type.
        start (Union[Unset, int]): Starting index for pagination.
        count (Union[Unset, int]):  Default: 15.
        sort (Union[Unset, str]):  Example: -createdAt.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetApiV1ServerFollowersResponse200]
    """

    kwargs = _get_kwargs(
        state=state,
        actor_type=actor_type,
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
    client: AuthenticatedClient | Client,
    state: Unset | GetApiV1ServerFollowersState = UNSET,
    actor_type: Unset | GetApiV1ServerFollowersActorType = UNSET,
    start: Unset | int = UNSET,
    count: Unset | int = 15,
    sort: Unset | str = UNSET,
) -> GetApiV1ServerFollowersResponse200 | None:
    """List instances following the server

    Args:
        state (Union[Unset, GetApiV1ServerFollowersState]): Current state or status filter.
        actor_type (Union[Unset, GetApiV1ServerFollowersActorType]): Parameter for actor type.
        start (Union[Unset, int]): Starting index for pagination.
        count (Union[Unset, int]):  Default: 15.
        sort (Union[Unset, str]):  Example: -createdAt.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetApiV1ServerFollowersResponse200
    """

    return sync_detailed(
        client=client,
        state=state,
        actor_type=actor_type,
        start=start,
        count=count,
        sort=sort,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    state: Unset | GetApiV1ServerFollowersState = UNSET,
    actor_type: Unset | GetApiV1ServerFollowersActorType = UNSET,
    start: Unset | int = UNSET,
    count: Unset | int = 15,
    sort: Unset | str = UNSET,
) -> Response[GetApiV1ServerFollowersResponse200]:
    """List instances following the server

    Args:
        state (Union[Unset, GetApiV1ServerFollowersState]): Current state or status filter.
        actor_type (Union[Unset, GetApiV1ServerFollowersActorType]): Parameter for actor type.
        start (Union[Unset, int]): Starting index for pagination.
        count (Union[Unset, int]):  Default: 15.
        sort (Union[Unset, str]):  Example: -createdAt.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetApiV1ServerFollowersResponse200]
    """

    kwargs = _get_kwargs(
        state=state,
        actor_type=actor_type,
        start=start,
        count=count,
        sort=sort,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    state: Unset | GetApiV1ServerFollowersState = UNSET,
    actor_type: Unset | GetApiV1ServerFollowersActorType = UNSET,
    start: Unset | int = UNSET,
    count: Unset | int = 15,
    sort: Unset | str = UNSET,
) -> GetApiV1ServerFollowersResponse200 | None:
    """List instances following the server

    Args:
        state (Union[Unset, GetApiV1ServerFollowersState]): Current state or status filter.
        actor_type (Union[Unset, GetApiV1ServerFollowersActorType]): Parameter for actor type.
        start (Union[Unset, int]): Starting index for pagination.
        count (Union[Unset, int]):  Default: 15.
        sort (Union[Unset, str]):  Example: -createdAt.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetApiV1ServerFollowersResponse200
    """

    return (
        await asyncio_detailed(
            client=client,
            state=state,
            actor_type=actor_type,
            start=start,
            count=count,
            sort=sort,
        )
    ).parsed
