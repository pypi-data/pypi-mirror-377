from http import HTTPStatus
from typing import Any
from uuid import UUID

import httpx

from peertube import errors
from peertube.client import AuthenticatedClient, Client
from peertube.models.video_replace_source_request_resumable import (
    VideoReplaceSourceRequestResumable,
)
from peertube.types import Response


def _get_kwargs(
    id: UUID | int | str,
    *,
    body: VideoReplaceSourceRequestResumable,
    x_upload_content_length: float,
    x_upload_content_type: str,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    headers["X-Upload-Content-Length"] = str(x_upload_content_length)

    headers["X-Upload-Content-Type"] = x_upload_content_type

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/api/v1/videos/{id}/source/replace-resumable",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | None:
    if response.status_code == 200:
        return None

    if response.status_code == 201:
        return None

    if response.status_code == 413:
        return None

    if response.status_code == 415:
        return None

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
    id: UUID | int | str,
    *,
    client: AuthenticatedClient,
    body: VideoReplaceSourceRequestResumable,
    x_upload_content_length: float,
    x_upload_content_type: str,
) -> Response[Any]:
    """Initialize the resumable replacement of a video

     **PeerTube >= 6.0** Uses [a resumable protocol](https://github.com/kukhariev/node-
    uploadx/blob/master/proto.md) to initialize the replacement of a video

    Args:
        id (Union[UUID, int, str]): Unique identifier for the entity.
        x_upload_content_length (float):  Example: 2469036.
        x_upload_content_type (str):  Example: video/mp4.
        body (VideoReplaceSourceRequestResumable): Request body data.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        id=id,
        body=body,
        x_upload_content_length=x_upload_content_length,
        x_upload_content_type=x_upload_content_type,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


async def asyncio_detailed(
    id: UUID | int | str,
    *,
    client: AuthenticatedClient,
    body: VideoReplaceSourceRequestResumable,
    x_upload_content_length: float,
    x_upload_content_type: str,
) -> Response[Any]:
    """Initialize the resumable replacement of a video

     **PeerTube >= 6.0** Uses [a resumable protocol](https://github.com/kukhariev/node-
    uploadx/blob/master/proto.md) to initialize the replacement of a video

    Args:
        id (Union[UUID, int, str]): Unique identifier for the entity.
        x_upload_content_length (float):  Example: 2469036.
        x_upload_content_type (str):  Example: video/mp4.
        body (VideoReplaceSourceRequestResumable): Request body data.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        id=id,
        body=body,
        x_upload_content_length=x_upload_content_length,
        x_upload_content_type=x_upload_content_type,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)
