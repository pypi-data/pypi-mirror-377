from http import HTTPStatus
from typing import Any

import httpx

from peertube import errors
from peertube.client import AuthenticatedClient, Client
from peertube.models.get_api_v1_users_me_subscriptions_exist_response_200 import (
    GetApiV1UsersMeSubscriptionsExistResponse200,
)
from peertube.types import UNSET, Response


def _get_kwargs(
    *,
    uris: list[str],
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_uris = uris

    params["uris"] = json_uris

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/users/me/subscriptions/exist",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> GetApiV1UsersMeSubscriptionsExistResponse200 | None:
    if response.status_code == 200:
        response_200 = GetApiV1UsersMeSubscriptionsExistResponse200.from_dict(
            response.json()
        )

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[GetApiV1UsersMeSubscriptionsExistResponse200]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    uris: list[str],
) -> Response[GetApiV1UsersMeSubscriptionsExistResponse200]:
    """Get if subscriptions exist for my user

    Args:
        uris (list[str]): Parameter for uris.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetApiV1UsersMeSubscriptionsExistResponse200]
    """

    kwargs = _get_kwargs(
        uris=uris,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    uris: list[str],
) -> GetApiV1UsersMeSubscriptionsExistResponse200 | None:
    """Get if subscriptions exist for my user

    Args:
        uris (list[str]): Parameter for uris.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetApiV1UsersMeSubscriptionsExistResponse200
    """

    return sync_detailed(
        client=client,
        uris=uris,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    uris: list[str],
) -> Response[GetApiV1UsersMeSubscriptionsExistResponse200]:
    """Get if subscriptions exist for my user

    Args:
        uris (list[str]): Parameter for uris.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetApiV1UsersMeSubscriptionsExistResponse200]
    """

    kwargs = _get_kwargs(
        uris=uris,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    uris: list[str],
) -> GetApiV1UsersMeSubscriptionsExistResponse200 | None:
    """Get if subscriptions exist for my user

    Args:
        uris (list[str]): Parameter for uris.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetApiV1UsersMeSubscriptionsExistResponse200
    """

    return (
        await asyncio_detailed(
            client=client,
            uris=uris,
        )
    ).parsed
