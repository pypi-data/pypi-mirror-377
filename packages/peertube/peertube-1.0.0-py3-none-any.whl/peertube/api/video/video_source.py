from http import HTTPStatus
from typing import Any
from uuid import UUID

import httpx

from peertube import errors
from peertube.client import AuthenticatedClient, Client
from peertube.models.video_source import VideoSource
from peertube.types import Response


def _get_kwargs(
    id: UUID | int | str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/api/v1/videos/{id}/source",
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> VideoSource | None:
    if response.status_code == 200:
        response_200 = VideoSource.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[VideoSource]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    id: UUID | int | str,
    *,
    client: AuthenticatedClient,
) -> Response[VideoSource]:
    """Get video source file metadata

     Get metadata and download link of original video file

    Args:
        id (Union[UUID, int, str]): Unique identifier for the entity.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[VideoSource]
    """

    kwargs = _get_kwargs(
        id=id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    id: UUID | int | str,
    *,
    client: AuthenticatedClient,
) -> VideoSource | None:
    """Get video source file metadata

     Get metadata and download link of original video file

    Args:
        id (Union[UUID, int, str]): Unique identifier for the entity.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        VideoSource
    """

    return sync_detailed(
        id=id,
        client=client,
    ).parsed


async def asyncio_detailed(
    id: UUID | int | str,
    *,
    client: AuthenticatedClient,
) -> Response[VideoSource]:
    """Get video source file metadata

     Get metadata and download link of original video file

    Args:
        id (Union[UUID, int, str]): Unique identifier for the entity.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[VideoSource]
    """

    kwargs = _get_kwargs(
        id=id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    id: UUID | int | str,
    *,
    client: AuthenticatedClient,
) -> VideoSource | None:
    """Get video source file metadata

     Get metadata and download link of original video file

    Args:
        id (Union[UUID, int, str]): Unique identifier for the entity.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        VideoSource
    """

    return (
        await asyncio_detailed(
            id=id,
            client=client,
        )
    ).parsed
