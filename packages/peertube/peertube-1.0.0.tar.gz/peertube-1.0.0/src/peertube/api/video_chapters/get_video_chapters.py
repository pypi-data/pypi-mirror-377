from http import HTTPStatus
from typing import Any
from uuid import UUID

import httpx

from peertube import errors
from peertube.client import AuthenticatedClient, Client
from peertube.models.video_chapters import VideoChapters
from peertube.types import UNSET, Response, Unset


def _get_kwargs(
    id: UUID | int | str,
    *,
    x_peertube_video_password: Unset | str = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(x_peertube_video_password, Unset):
        headers["x-peertube-video-password"] = x_peertube_video_password

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/api/v1/videos/{id}/chapters",
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> VideoChapters | None:
    if response.status_code == 200:
        response_200 = VideoChapters.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[VideoChapters]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    id: UUID | int | str,
    *,
    client: AuthenticatedClient | Client,
    x_peertube_video_password: Unset | str = UNSET,
) -> Response[VideoChapters]:
    """Get chapters of a video

     **PeerTube >= 6.0**

    Args:
        id (Union[UUID, int, str]): Unique identifier for the entity.
        x_peertube_video_password (Union[Unset, str]): Video-related parameter.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[VideoChapters]
    """

    kwargs = _get_kwargs(
        id=id,
        x_peertube_video_password=x_peertube_video_password,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    id: UUID | int | str,
    *,
    client: AuthenticatedClient | Client,
    x_peertube_video_password: Unset | str = UNSET,
) -> VideoChapters | None:
    """Get chapters of a video

     **PeerTube >= 6.0**

    Args:
        id (Union[UUID, int, str]): Unique identifier for the entity.
        x_peertube_video_password (Union[Unset, str]): Video-related parameter.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        VideoChapters
    """

    return sync_detailed(
        id=id,
        client=client,
        x_peertube_video_password=x_peertube_video_password,
    ).parsed


async def asyncio_detailed(
    id: UUID | int | str,
    *,
    client: AuthenticatedClient | Client,
    x_peertube_video_password: Unset | str = UNSET,
) -> Response[VideoChapters]:
    """Get chapters of a video

     **PeerTube >= 6.0**

    Args:
        id (Union[UUID, int, str]): Unique identifier for the entity.
        x_peertube_video_password (Union[Unset, str]): Video-related parameter.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[VideoChapters]
    """

    kwargs = _get_kwargs(
        id=id,
        x_peertube_video_password=x_peertube_video_password,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    id: UUID | int | str,
    *,
    client: AuthenticatedClient | Client,
    x_peertube_video_password: Unset | str = UNSET,
) -> VideoChapters | None:
    """Get chapters of a video

     **PeerTube >= 6.0**

    Args:
        id (Union[UUID, int, str]): Unique identifier for the entity.
        x_peertube_video_password (Union[Unset, str]): Video-related parameter.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        VideoChapters
    """

    return (
        await asyncio_detailed(
            id=id,
            client=client,
            x_peertube_video_password=x_peertube_video_password,
        )
    ).parsed
