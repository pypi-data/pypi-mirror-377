from http import HTTPStatus
from typing import Any, cast

import httpx

from peertube import errors
from peertube.client import AuthenticatedClient, Client
from peertube.models.post_api_v1_users_me_avatar_pick_body import (
    PostApiV1UsersMeAvatarPickBody,
)
from peertube.models.post_api_v1_users_me_avatar_pick_response_200 import (
    PostApiV1UsersMeAvatarPickResponse200,
)
from peertube.types import Response


def _get_kwargs(
    *,
    body: PostApiV1UsersMeAvatarPickBody,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/v1/users/me/avatar/pick",
    }

    _kwargs["files"] = body.to_multipart()

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | PostApiV1UsersMeAvatarPickResponse200 | None:
    if response.status_code == 200:
        response_200 = PostApiV1UsersMeAvatarPickResponse200.from_dict(response.json())

        return response_200

    if response.status_code == 413:
        response_413 = cast("Any", None)
        return response_413

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Any | PostApiV1UsersMeAvatarPickResponse200]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    body: PostApiV1UsersMeAvatarPickBody,
) -> Response[Any | PostApiV1UsersMeAvatarPickResponse200]:
    """Update my user avatar

    Args:
        body (PostApiV1UsersMeAvatarPickBody): Request body data.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, PostApiV1UsersMeAvatarPickResponse200]]
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
    client: AuthenticatedClient,
    body: PostApiV1UsersMeAvatarPickBody,
) -> Any | PostApiV1UsersMeAvatarPickResponse200 | None:
    """Update my user avatar

    Args:
        body (PostApiV1UsersMeAvatarPickBody): Request body data.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, PostApiV1UsersMeAvatarPickResponse200]
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: PostApiV1UsersMeAvatarPickBody,
) -> Response[Any | PostApiV1UsersMeAvatarPickResponse200]:
    """Update my user avatar

    Args:
        body (PostApiV1UsersMeAvatarPickBody): Request body data.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, PostApiV1UsersMeAvatarPickResponse200]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    body: PostApiV1UsersMeAvatarPickBody,
) -> Any | PostApiV1UsersMeAvatarPickResponse200 | None:
    """Update my user avatar

    Args:
        body (PostApiV1UsersMeAvatarPickBody): Request body data.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, PostApiV1UsersMeAvatarPickResponse200]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
