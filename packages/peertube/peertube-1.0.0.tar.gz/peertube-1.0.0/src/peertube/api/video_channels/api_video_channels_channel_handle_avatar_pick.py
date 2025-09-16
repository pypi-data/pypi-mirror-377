from http import HTTPStatus
from typing import Any, cast

import httpx

from peertube import errors
from peertube.client import AuthenticatedClient, Client
from peertube.models.post_api_v1_video_channels_channel_handle_avatar_pick_body import (
    PostApiV1VideoChannelsChannelHandleAvatarPickBody,
)
from peertube.models.post_api_v1_video_channels_channel_handle_avatar_pick_response_200 import (
    PostApiV1VideoChannelsChannelHandleAvatarPickResponse200,
)
from peertube.types import Response


def _get_kwargs(
    channel_handle: str,
    *,
    body: PostApiV1VideoChannelsChannelHandleAvatarPickBody,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/api/v1/video-channels/{channel_handle}/avatar/pick",
    }

    _kwargs["files"] = body.to_multipart()

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | PostApiV1VideoChannelsChannelHandleAvatarPickResponse200 | None:
    if response.status_code == 200:
        response_200 = (
            PostApiV1VideoChannelsChannelHandleAvatarPickResponse200.from_dict(
                response.json()
            )
        )

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
) -> Response[Any | PostApiV1VideoChannelsChannelHandleAvatarPickResponse200]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    channel_handle: str,
    *,
    client: AuthenticatedClient,
    body: PostApiV1VideoChannelsChannelHandleAvatarPickBody,
) -> Response[Any | PostApiV1VideoChannelsChannelHandleAvatarPickResponse200]:
    """Update channel avatar

    Args:
        channel_handle (str):  Example: my_username | my_username@example.com.
        body (PostApiV1VideoChannelsChannelHandleAvatarPickBody): Request body data.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, PostApiV1VideoChannelsChannelHandleAvatarPickResponse200]]
    """

    kwargs = _get_kwargs(
        channel_handle=channel_handle,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    channel_handle: str,
    *,
    client: AuthenticatedClient,
    body: PostApiV1VideoChannelsChannelHandleAvatarPickBody,
) -> Any | PostApiV1VideoChannelsChannelHandleAvatarPickResponse200 | None:
    """Update channel avatar

    Args:
        channel_handle (str):  Example: my_username | my_username@example.com.
        body (PostApiV1VideoChannelsChannelHandleAvatarPickBody): Request body data.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, PostApiV1VideoChannelsChannelHandleAvatarPickResponse200]
    """

    return sync_detailed(
        channel_handle=channel_handle,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    channel_handle: str,
    *,
    client: AuthenticatedClient,
    body: PostApiV1VideoChannelsChannelHandleAvatarPickBody,
) -> Response[Any | PostApiV1VideoChannelsChannelHandleAvatarPickResponse200]:
    """Update channel avatar

    Args:
        channel_handle (str):  Example: my_username | my_username@example.com.
        body (PostApiV1VideoChannelsChannelHandleAvatarPickBody): Request body data.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, PostApiV1VideoChannelsChannelHandleAvatarPickResponse200]]
    """

    kwargs = _get_kwargs(
        channel_handle=channel_handle,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    channel_handle: str,
    *,
    client: AuthenticatedClient,
    body: PostApiV1VideoChannelsChannelHandleAvatarPickBody,
) -> Any | PostApiV1VideoChannelsChannelHandleAvatarPickResponse200 | None:
    """Update channel avatar

    Args:
        channel_handle (str):  Example: my_username | my_username@example.com.
        body (PostApiV1VideoChannelsChannelHandleAvatarPickBody): Request body data.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, PostApiV1VideoChannelsChannelHandleAvatarPickResponse200]
    """

    return (
        await asyncio_detailed(
            channel_handle=channel_handle,
            client=client,
            body=body,
        )
    ).parsed
