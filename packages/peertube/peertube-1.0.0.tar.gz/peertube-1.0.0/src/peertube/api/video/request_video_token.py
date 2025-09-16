from http import HTTPStatus
from typing import Any, cast
from uuid import UUID

import httpx

from peertube import errors
from peertube.client import AuthenticatedClient, Client
from peertube.models.video_token_response import VideoTokenResponse
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
        "method": "post",
        "url": f"/api/v1/videos/{id}/token",
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | VideoTokenResponse | None:
    if response.status_code == 200:
        response_200 = VideoTokenResponse.from_dict(response.json())

        return response_200

    if response.status_code == 400:
        response_400 = cast("Any", None)
        return response_400

    if response.status_code == 404:
        response_404 = cast("Any", None)
        return response_404

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Any | VideoTokenResponse]:
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
    x_peertube_video_password: Unset | str = UNSET,
) -> Response[Any | VideoTokenResponse]:
    """Request video token

     Request special tokens that expire quickly to use them in some context (like accessing private
    static files)

    Args:
        id (Union[UUID, int, str]): Unique identifier for the entity.
        x_peertube_video_password (Union[Unset, str]): Video-related parameter.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, VideoTokenResponse]]
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
    client: AuthenticatedClient,
    x_peertube_video_password: Unset | str = UNSET,
) -> Any | VideoTokenResponse | None:
    """Request video token

     Request special tokens that expire quickly to use them in some context (like accessing private
    static files)

    Args:
        id (Union[UUID, int, str]): Unique identifier for the entity.
        x_peertube_video_password (Union[Unset, str]): Video-related parameter.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, VideoTokenResponse]
    """

    return sync_detailed(
        id=id,
        client=client,
        x_peertube_video_password=x_peertube_video_password,
    ).parsed


async def asyncio_detailed(
    id: UUID | int | str,
    *,
    client: AuthenticatedClient,
    x_peertube_video_password: Unset | str = UNSET,
) -> Response[Any | VideoTokenResponse]:
    """Request video token

     Request special tokens that expire quickly to use them in some context (like accessing private
    static files)

    Args:
        id (Union[UUID, int, str]): Unique identifier for the entity.
        x_peertube_video_password (Union[Unset, str]): Video-related parameter.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, VideoTokenResponse]]
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
    client: AuthenticatedClient,
    x_peertube_video_password: Unset | str = UNSET,
) -> Any | VideoTokenResponse | None:
    """Request video token

     Request special tokens that expire quickly to use them in some context (like accessing private
    static files)

    Args:
        id (Union[UUID, int, str]): Unique identifier for the entity.
        x_peertube_video_password (Union[Unset, str]): Video-related parameter.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, VideoTokenResponse]
    """

    return (
        await asyncio_detailed(
            id=id,
            client=client,
            x_peertube_video_password=x_peertube_video_password,
        )
    ).parsed
