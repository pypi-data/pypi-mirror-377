from http import HTTPStatus
from typing import Any

import httpx

from peertube import errors
from peertube.client import AuthenticatedClient, Client
from peertube.types import UNSET, Response, Unset


def _get_kwargs(
    *,
    search: Unset | str = UNSET,
    search_account: Unset | str = UNSET,
    search_video: Unset | str = UNSET,
    video_id: Unset | int = UNSET,
    video_channel_id: Unset | int = UNSET,
    auto_tag_one_of: Unset | list[str] | str = UNSET,
    is_held_for_review: Unset | bool = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["search"] = search

    params["searchAccount"] = search_account

    params["searchVideo"] = search_video

    params["videoId"] = video_id

    params["videoChannelId"] = video_channel_id

    json_auto_tag_one_of: Unset | list[str] | str
    if isinstance(auto_tag_one_of, Unset):
        json_auto_tag_one_of = UNSET
    elif isinstance(auto_tag_one_of, list):
        json_auto_tag_one_of = auto_tag_one_of

    else:
        json_auto_tag_one_of = auto_tag_one_of
    params["autoTagOneOf"] = json_auto_tag_one_of

    params["isHeldForReview"] = is_held_for_review

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/users/me/videos/comments",
        "params": params,
    }

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
    *,
    client: AuthenticatedClient,
    search: Unset | str = UNSET,
    search_account: Unset | str = UNSET,
    search_video: Unset | str = UNSET,
    video_id: Unset | int = UNSET,
    video_channel_id: Unset | int = UNSET,
    auto_tag_one_of: Unset | list[str] | str = UNSET,
    is_held_for_review: Unset | bool = UNSET,
) -> Response[Any]:
    """List comments on user's videos

     **PeerTube >= 6.2**

    Args:
        search (Union[Unset, str]): Search query filter.
        search_account (Union[Unset, str]): Search filter for account.
        search_video (Union[Unset, str]): Search filter for video.
        video_id (Union[Unset, int]): Unique identifier for the video.
        video_channel_id (Union[Unset, int]): Video-related parameter.
        auto_tag_one_of (Union[Unset, list[str], str]): Parameter for auto tag one of.
        is_held_for_review (Union[Unset, bool]): Parameter for is held for review.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        search=search,
        search_account=search_account,
        search_video=search_video,
        video_id=video_id,
        video_channel_id=video_channel_id,
        auto_tag_one_of=auto_tag_one_of,
        is_held_for_review=is_held_for_review,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    search: Unset | str = UNSET,
    search_account: Unset | str = UNSET,
    search_video: Unset | str = UNSET,
    video_id: Unset | int = UNSET,
    video_channel_id: Unset | int = UNSET,
    auto_tag_one_of: Unset | list[str] | str = UNSET,
    is_held_for_review: Unset | bool = UNSET,
) -> Response[Any]:
    """List comments on user's videos

     **PeerTube >= 6.2**

    Args:
        search (Union[Unset, str]): Search query filter.
        search_account (Union[Unset, str]): Search filter for account.
        search_video (Union[Unset, str]): Search filter for video.
        video_id (Union[Unset, int]): Unique identifier for the video.
        video_channel_id (Union[Unset, int]): Video-related parameter.
        auto_tag_one_of (Union[Unset, list[str], str]): Parameter for auto tag one of.
        is_held_for_review (Union[Unset, bool]): Parameter for is held for review.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        search=search,
        search_account=search_account,
        search_video=search_video,
        video_id=video_id,
        video_channel_id=video_channel_id,
        auto_tag_one_of=auto_tag_one_of,
        is_held_for_review=is_held_for_review,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)
