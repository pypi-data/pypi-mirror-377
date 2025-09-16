from http import HTTPStatus
from typing import Any
from uuid import UUID

import httpx

from peertube import errors
from peertube.client import AuthenticatedClient, Client
from peertube.models.get_api_v1_videos_id_comment_threads_sort import (
    GetApiV1VideosIdCommentThreadsSort,
)
from peertube.types import UNSET, Response, Unset


def _get_kwargs(
    id: UUID | int | str,
    *,
    start: Unset | int = UNSET,
    count: Unset | int = 15,
    sort: Unset | GetApiV1VideosIdCommentThreadsSort = UNSET,
    x_peertube_video_password: Unset | str = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(x_peertube_video_password, Unset):
        headers["x-peertube-video-password"] = x_peertube_video_password

    params: dict[str, Any] = {}

    params["start"] = start

    params["count"] = count

    json_sort: Unset | str = UNSET
    if not isinstance(sort, Unset):
        json_sort = sort.value

    params["sort"] = json_sort

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/api/v1/videos/{id}/comment-threads",
        "params": params,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | None:
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
    client: AuthenticatedClient | Client,
    start: Unset | int = UNSET,
    count: Unset | int = 15,
    sort: Unset | GetApiV1VideosIdCommentThreadsSort = UNSET,
    x_peertube_video_password: Unset | str = UNSET,
) -> Response[Any]:
    """List threads of a video

    Args:
        id (Union[UUID, int, str]): Unique identifier for the entity.
        start (Union[Unset, int]): Starting index for pagination.
        count (Union[Unset, int]):  Default: 15.
        sort (Union[Unset, GetApiV1VideosIdCommentThreadsSort]): Sorting criteria for results.
        x_peertube_video_password (Union[Unset, str]): Video-related parameter.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        id=id,
        start=start,
        count=count,
        sort=sort,
        x_peertube_video_password=x_peertube_video_password,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


async def asyncio_detailed(
    id: UUID | int | str,
    *,
    client: AuthenticatedClient | Client,
    start: Unset | int = UNSET,
    count: Unset | int = 15,
    sort: Unset | GetApiV1VideosIdCommentThreadsSort = UNSET,
    x_peertube_video_password: Unset | str = UNSET,
) -> Response[Any]:
    """List threads of a video

    Args:
        id (Union[UUID, int, str]): Unique identifier for the entity.
        start (Union[Unset, int]): Starting index for pagination.
        count (Union[Unset, int]):  Default: 15.
        sort (Union[Unset, GetApiV1VideosIdCommentThreadsSort]): Sorting criteria for results.
        x_peertube_video_password (Union[Unset, str]): Video-related parameter.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        id=id,
        start=start,
        count=count,
        sort=sort,
        x_peertube_video_password=x_peertube_video_password,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)
