from http import HTTPStatus
from typing import Any

import httpx

from peertube import errors
from peertube.client import AuthenticatedClient, Client
from peertube.models.post_api_v1_runners_register_body import (
    PostApiV1RunnersRegisterBody,
)
from peertube.models.post_api_v1_runners_register_response_200 import (
    PostApiV1RunnersRegisterResponse200,
)
from peertube.types import Response


def _get_kwargs(
    *,
    body: PostApiV1RunnersRegisterBody,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/v1/runners/register",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> PostApiV1RunnersRegisterResponse200 | None:
    if response.status_code == 200:
        response_200 = PostApiV1RunnersRegisterResponse200.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[PostApiV1RunnersRegisterResponse200]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: PostApiV1RunnersRegisterBody,
) -> Response[PostApiV1RunnersRegisterResponse200]:
    """Register a new runner

     API used by PeerTube runners

    Args:
        body (PostApiV1RunnersRegisterBody): Request body data.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PostApiV1RunnersRegisterResponse200]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    body: PostApiV1RunnersRegisterBody,
) -> PostApiV1RunnersRegisterResponse200 | None:
    """Register a new runner

     API used by PeerTube runners

    Args:
        body (PostApiV1RunnersRegisterBody): Request body data.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PostApiV1RunnersRegisterResponse200
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: PostApiV1RunnersRegisterBody,
) -> Response[PostApiV1RunnersRegisterResponse200]:
    """Register a new runner

     API used by PeerTube runners

    Args:
        body (PostApiV1RunnersRegisterBody): Request body data.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PostApiV1RunnersRegisterResponse200]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: PostApiV1RunnersRegisterBody,
) -> PostApiV1RunnersRegisterResponse200 | None:
    """Register a new runner

     API used by PeerTube runners

    Args:
        body (PostApiV1RunnersRegisterBody): Request body data.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PostApiV1RunnersRegisterResponse200
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
