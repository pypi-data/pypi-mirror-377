from http import HTTPStatus
from typing import Any
from uuid import UUID

import httpx

from peertube import errors
from peertube.client import AuthenticatedClient, Client
from peertube.types import UNSET, File, Response


def _get_kwargs(
    id: UUID | int | str,
    *,
    body: File,
    upload_id: str,
    content_range: str,
    content_length: float,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    headers["Content-Range"] = content_range

    headers["Content-Length"] = str(content_length)

    params: dict[str, Any] = {}

    params["upload_id"] = upload_id

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": f"/api/v1/videos/{id}/source/replace-resumable",
        "params": params,
    }

    _kwargs["content"] = body.payload

    headers["Content-Type"] = "application/octet-stream"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | None:
    if response.status_code == 204:
        return None

    if response.status_code == 308:
        return None

    if response.status_code == 403:
        return None

    if response.status_code == 404:
        return None

    if response.status_code == 409:
        return None

    if response.status_code == 422:
        return None

    if response.status_code == 429:
        return None

    if response.status_code == 503:
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
    body: File,
    upload_id: str,
    content_range: str,
    content_length: float,
) -> Response[Any]:
    """Send chunk for the resumable replacement of a video

     **PeerTube >= 6.0** Uses [a resumable protocol](https://github.com/kukhariev/node-
    uploadx/blob/master/proto.md) to continue, pause or resume the replacement of a video

    Args:
        id (Union[UUID, int, str]): Unique identifier for the entity.
        upload_id (str): Parameter for upload id.
        content_range (str):  Example: bytes 0-262143/2469036.
        content_length (float):  Example: 262144.
        body (File): Request body data.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        id=id,
        body=body,
        upload_id=upload_id,
        content_range=content_range,
        content_length=content_length,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


async def asyncio_detailed(
    id: UUID | int | str,
    *,
    client: AuthenticatedClient,
    body: File,
    upload_id: str,
    content_range: str,
    content_length: float,
) -> Response[Any]:
    """Send chunk for the resumable replacement of a video

     **PeerTube >= 6.0** Uses [a resumable protocol](https://github.com/kukhariev/node-
    uploadx/blob/master/proto.md) to continue, pause or resume the replacement of a video

    Args:
        id (Union[UUID, int, str]): Unique identifier for the entity.
        upload_id (str): Parameter for upload id.
        content_range (str):  Example: bytes 0-262143/2469036.
        content_length (float):  Example: 262144.
        body (File): Request body data.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        id=id,
        body=body,
        upload_id=upload_id,
        content_range=content_range,
        content_length=content_length,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)
