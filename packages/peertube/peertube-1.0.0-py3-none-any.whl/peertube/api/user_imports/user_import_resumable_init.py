from http import HTTPStatus
from typing import Any

import httpx

from peertube import errors
from peertube.client import AuthenticatedClient, Client
from peertube.models.user_import_resumable import UserImportResumable
from peertube.types import Response


def _get_kwargs(
    user_id: int,
    *,
    body: UserImportResumable,
    x_upload_content_length: float,
    x_upload_content_type: str,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    headers["X-Upload-Content-Length"] = str(x_upload_content_length)

    headers["X-Upload-Content-Type"] = x_upload_content_type

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/api/v1/users/{user_id}/imports/import-resumable",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | None:
    if response.status_code == 201:
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
    user_id: int,
    *,
    client: AuthenticatedClient,
    body: UserImportResumable,
    x_upload_content_length: float,
    x_upload_content_type: str,
) -> Response[Any]:
    """Initialize the resumable user import

     **PeerTube >= 6.1** Uses [a resumable protocol](https://github.com/kukhariev/node-
    uploadx/blob/master/proto.md) to initialize the import of the archive

    Args:
        user_id (int):  Example: 42.
        x_upload_content_length (float):  Example: 2469036.
        x_upload_content_type (str):  Example: video/mp4.
        body (UserImportResumable): Request body data.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        user_id=user_id,
        body=body,
        x_upload_content_length=x_upload_content_length,
        x_upload_content_type=x_upload_content_type,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


async def asyncio_detailed(
    user_id: int,
    *,
    client: AuthenticatedClient,
    body: UserImportResumable,
    x_upload_content_length: float,
    x_upload_content_type: str,
) -> Response[Any]:
    """Initialize the resumable user import

     **PeerTube >= 6.1** Uses [a resumable protocol](https://github.com/kukhariev/node-
    uploadx/blob/master/proto.md) to initialize the import of the archive

    Args:
        user_id (int):  Example: 42.
        x_upload_content_length (float):  Example: 2469036.
        x_upload_content_type (str):  Example: video/mp4.
        body (UserImportResumable): Request body data.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        user_id=user_id,
        body=body,
        x_upload_content_length=x_upload_content_length,
        x_upload_content_type=x_upload_content_type,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)
