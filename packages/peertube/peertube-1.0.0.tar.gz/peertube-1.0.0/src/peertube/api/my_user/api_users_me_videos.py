from http import HTTPStatus
from typing import Any

import httpx

from peertube import errors
from peertube.client import AuthenticatedClient, Client
from peertube.models.get_api_v1_users_me_videos_include import (
    GetApiV1UsersMeVideosInclude,
)
from peertube.models.get_api_v1_users_me_videos_nsfw import GetApiV1UsersMeVideosNsfw
from peertube.models.get_api_v1_users_me_videos_skip_count import (
    GetApiV1UsersMeVideosSkipCount,
)
from peertube.models.get_api_v1_users_me_videos_sort import GetApiV1UsersMeVideosSort
from peertube.models.nsfw_flag import NSFWFlag
from peertube.models.video_list_response import VideoListResponse
from peertube.models.video_privacy_set import VideoPrivacySet
from peertube.types import UNSET, Response, Unset


def _get_kwargs(
    *,
    channel_name_one_of: Unset | list[str] | str = UNSET,
    start: Unset | int = UNSET,
    count: Unset | int = 15,
    skip_count: Unset
    | GetApiV1UsersMeVideosSkipCount = GetApiV1UsersMeVideosSkipCount.FALSE,
    sort: Unset | GetApiV1UsersMeVideosSort = UNSET,
    nsfw: Unset | GetApiV1UsersMeVideosNsfw = UNSET,
    nsfw_flags_included: Unset | NSFWFlag = UNSET,
    nsfw_flags_excluded: Unset | NSFWFlag = UNSET,
    is_live: Unset | bool = UNSET,
    include_scheduled_live: Unset | bool = UNSET,
    category_one_of: Unset | int | list[int] = UNSET,
    licence_one_of: Unset | int | list[int] = UNSET,
    language_one_of: Unset | list[str] | str = UNSET,
    tags_one_of: Unset | list[str] | str = UNSET,
    tags_all_of: Unset | list[str] | str = UNSET,
    is_local: Unset | bool = UNSET,
    include: Unset | GetApiV1UsersMeVideosInclude = UNSET,
    has_hls_files: Unset | bool = UNSET,
    has_web_video_files: Unset | bool = UNSET,
    host: Unset | str = UNSET,
    auto_tag_one_of: Unset | list[str] | str = UNSET,
    privacy_one_of: Unset | VideoPrivacySet = UNSET,
    exclude_already_watched: Unset | bool = UNSET,
    search: Unset | str = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_channel_name_one_of: Unset | list[str] | str
    if isinstance(channel_name_one_of, Unset):
        json_channel_name_one_of = UNSET
    elif isinstance(channel_name_one_of, list):
        json_channel_name_one_of = channel_name_one_of

    else:
        json_channel_name_one_of = channel_name_one_of
    params["channelNameOneOf"] = json_channel_name_one_of

    params["start"] = start

    params["count"] = count

    json_skip_count: Unset | str = UNSET
    if not isinstance(skip_count, Unset):
        json_skip_count = skip_count.value

    params["skipCount"] = json_skip_count

    json_sort: Unset | str = UNSET
    if not isinstance(sort, Unset):
        json_sort = sort.value

    params["sort"] = json_sort

    json_nsfw: Unset | str = UNSET
    if not isinstance(nsfw, Unset):
        json_nsfw = nsfw.value

    params["nsfw"] = json_nsfw

    json_nsfw_flags_included: Unset | int = UNSET
    if not isinstance(nsfw_flags_included, Unset):
        json_nsfw_flags_included = nsfw_flags_included.value

    params["nsfwFlagsIncluded"] = json_nsfw_flags_included

    json_nsfw_flags_excluded: Unset | int = UNSET
    if not isinstance(nsfw_flags_excluded, Unset):
        json_nsfw_flags_excluded = nsfw_flags_excluded.value

    params["nsfwFlagsExcluded"] = json_nsfw_flags_excluded

    params["isLive"] = is_live

    params["includeScheduledLive"] = include_scheduled_live

    json_category_one_of: Unset | int | list[int]
    if isinstance(category_one_of, Unset):
        json_category_one_of = UNSET
    elif isinstance(category_one_of, list):
        json_category_one_of = category_one_of

    else:
        json_category_one_of = category_one_of
    params["categoryOneOf"] = json_category_one_of

    json_licence_one_of: Unset | int | list[int]
    if isinstance(licence_one_of, Unset):
        json_licence_one_of = UNSET
    elif isinstance(licence_one_of, list):
        json_licence_one_of = licence_one_of

    else:
        json_licence_one_of = licence_one_of
    params["licenceOneOf"] = json_licence_one_of

    json_language_one_of: Unset | list[str] | str
    if isinstance(language_one_of, Unset):
        json_language_one_of = UNSET
    elif isinstance(language_one_of, list):
        json_language_one_of = language_one_of

    else:
        json_language_one_of = language_one_of
    params["languageOneOf"] = json_language_one_of

    json_tags_one_of: Unset | list[str] | str
    if isinstance(tags_one_of, Unset):
        json_tags_one_of = UNSET
    elif isinstance(tags_one_of, list):
        json_tags_one_of = tags_one_of

    else:
        json_tags_one_of = tags_one_of
    params["tagsOneOf"] = json_tags_one_of

    json_tags_all_of: Unset | list[str] | str
    if isinstance(tags_all_of, Unset):
        json_tags_all_of = UNSET
    elif isinstance(tags_all_of, list):
        json_tags_all_of = tags_all_of

    else:
        json_tags_all_of = tags_all_of
    params["tagsAllOf"] = json_tags_all_of

    params["isLocal"] = is_local

    json_include: Unset | int = UNSET
    if not isinstance(include, Unset):
        json_include = include.value

    params["include"] = json_include

    params["hasHLSFiles"] = has_hls_files

    params["hasWebVideoFiles"] = has_web_video_files

    params["host"] = host

    json_auto_tag_one_of: Unset | list[str] | str
    if isinstance(auto_tag_one_of, Unset):
        json_auto_tag_one_of = UNSET
    elif isinstance(auto_tag_one_of, list):
        json_auto_tag_one_of = auto_tag_one_of

    else:
        json_auto_tag_one_of = auto_tag_one_of
    params["autoTagOneOf"] = json_auto_tag_one_of

    json_privacy_one_of: Unset | int = UNSET
    if not isinstance(privacy_one_of, Unset):
        json_privacy_one_of = privacy_one_of.value

    params["privacyOneOf"] = json_privacy_one_of

    params["excludeAlreadyWatched"] = exclude_already_watched

    params["search"] = search

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/users/me/videos",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> VideoListResponse | None:
    if response.status_code == 200:
        response_200 = VideoListResponse.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[VideoListResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    channel_name_one_of: Unset | list[str] | str = UNSET,
    start: Unset | int = UNSET,
    count: Unset | int = 15,
    skip_count: Unset
    | GetApiV1UsersMeVideosSkipCount = GetApiV1UsersMeVideosSkipCount.FALSE,
    sort: Unset | GetApiV1UsersMeVideosSort = UNSET,
    nsfw: Unset | GetApiV1UsersMeVideosNsfw = UNSET,
    nsfw_flags_included: Unset | NSFWFlag = UNSET,
    nsfw_flags_excluded: Unset | NSFWFlag = UNSET,
    is_live: Unset | bool = UNSET,
    include_scheduled_live: Unset | bool = UNSET,
    category_one_of: Unset | int | list[int] = UNSET,
    licence_one_of: Unset | int | list[int] = UNSET,
    language_one_of: Unset | list[str] | str = UNSET,
    tags_one_of: Unset | list[str] | str = UNSET,
    tags_all_of: Unset | list[str] | str = UNSET,
    is_local: Unset | bool = UNSET,
    include: Unset | GetApiV1UsersMeVideosInclude = UNSET,
    has_hls_files: Unset | bool = UNSET,
    has_web_video_files: Unset | bool = UNSET,
    host: Unset | str = UNSET,
    auto_tag_one_of: Unset | list[str] | str = UNSET,
    privacy_one_of: Unset | VideoPrivacySet = UNSET,
    exclude_already_watched: Unset | bool = UNSET,
    search: Unset | str = UNSET,
) -> Response[VideoListResponse]:
    """List videos of my user

    Args:
        channel_name_one_of (Union[Unset, list[str], str]): Channel-related parameter.
        start (Union[Unset, int]): Starting index for pagination.
        count (Union[Unset, int]):  Default: 15.
        skip_count (Union[Unset, GetApiV1UsersMeVideosSkipCount]):  Default:
            GetApiV1UsersMeVideosSkipCount.FALSE.
        sort (Union[Unset, GetApiV1UsersMeVideosSort]): Sort videos by criteria (prefixing with
            `-` means `DESC` order):
              * `hot` - Adaptation of Reddit "hot" algorithm taking into account video views, likes,
            dislikes and comments and publication date
              * `best` - Same than `hot`, but also takes into account user video history
              * `trending` - Sort videos by recent views ("recent" is defined by the admin)
              * `views` - Sort videos using their `views` counter
              * `publishedAt` - Sort by video publication date (when it became publicly available)
        nsfw (Union[Unset, GetApiV1UsersMeVideosNsfw]): Parameter for nsfw.
        nsfw_flags_included (Union[Unset, NSFWFlag]): Parameter for nsfw flags included.
            NSFW flags (can be combined using bitwise or operator)
            - `0` NONE
            - `1` VIOLENT
            - `2` EXPLICIT_SEX
        nsfw_flags_excluded (Union[Unset, NSFWFlag]): Parameter for nsfw flags excluded.
            NSFW flags (can be combined using bitwise or operator)
            - `0` NONE
            - `1` VIOLENT
            - `2` EXPLICIT_SEX
        is_live (Union[Unset, bool]): Parameter for is live.
        include_scheduled_live (Union[Unset, bool]): Parameter for include scheduled live.
        category_one_of (Union[Unset, int, list[int]]): Parameter for category one of.
        licence_one_of (Union[Unset, int, list[int]]): Parameter for licence one of.
        language_one_of (Union[Unset, list[str], str]): Parameter for language one of.
        tags_one_of (Union[Unset, list[str], str]): Parameter for tags one of.
        tags_all_of (Union[Unset, list[str], str]): Parameter for tags all of.
        is_local (Union[Unset, bool]): Parameter for is local.
        include (Union[Unset, GetApiV1UsersMeVideosInclude]): Parameter for include.
        has_hls_files (Union[Unset, bool]): Parameter for has hls files.
        has_web_video_files (Union[Unset, bool]): Video-related parameter.
        host (Union[Unset, str]): Parameter for host.
        auto_tag_one_of (Union[Unset, list[str], str]): Parameter for auto tag one of.
        privacy_one_of (Union[Unset, VideoPrivacySet]): privacy id of the video (see
            [/videos/privacies](#operation/getVideoPrivacyPolicies))
        exclude_already_watched (Union[Unset, bool]): Parameter for exclude already watched.
        search (Union[Unset, str]): Search query filter.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[VideoListResponse]
    """

    kwargs = _get_kwargs(
        channel_name_one_of=channel_name_one_of,
        start=start,
        count=count,
        skip_count=skip_count,
        sort=sort,
        nsfw=nsfw,
        nsfw_flags_included=nsfw_flags_included,
        nsfw_flags_excluded=nsfw_flags_excluded,
        is_live=is_live,
        include_scheduled_live=include_scheduled_live,
        category_one_of=category_one_of,
        licence_one_of=licence_one_of,
        language_one_of=language_one_of,
        tags_one_of=tags_one_of,
        tags_all_of=tags_all_of,
        is_local=is_local,
        include=include,
        has_hls_files=has_hls_files,
        has_web_video_files=has_web_video_files,
        host=host,
        auto_tag_one_of=auto_tag_one_of,
        privacy_one_of=privacy_one_of,
        exclude_already_watched=exclude_already_watched,
        search=search,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    channel_name_one_of: Unset | list[str] | str = UNSET,
    start: Unset | int = UNSET,
    count: Unset | int = 15,
    skip_count: Unset
    | GetApiV1UsersMeVideosSkipCount = GetApiV1UsersMeVideosSkipCount.FALSE,
    sort: Unset | GetApiV1UsersMeVideosSort = UNSET,
    nsfw: Unset | GetApiV1UsersMeVideosNsfw = UNSET,
    nsfw_flags_included: Unset | NSFWFlag = UNSET,
    nsfw_flags_excluded: Unset | NSFWFlag = UNSET,
    is_live: Unset | bool = UNSET,
    include_scheduled_live: Unset | bool = UNSET,
    category_one_of: Unset | int | list[int] = UNSET,
    licence_one_of: Unset | int | list[int] = UNSET,
    language_one_of: Unset | list[str] | str = UNSET,
    tags_one_of: Unset | list[str] | str = UNSET,
    tags_all_of: Unset | list[str] | str = UNSET,
    is_local: Unset | bool = UNSET,
    include: Unset | GetApiV1UsersMeVideosInclude = UNSET,
    has_hls_files: Unset | bool = UNSET,
    has_web_video_files: Unset | bool = UNSET,
    host: Unset | str = UNSET,
    auto_tag_one_of: Unset | list[str] | str = UNSET,
    privacy_one_of: Unset | VideoPrivacySet = UNSET,
    exclude_already_watched: Unset | bool = UNSET,
    search: Unset | str = UNSET,
) -> VideoListResponse | None:
    """List videos of my user

    Args:
        channel_name_one_of (Union[Unset, list[str], str]): Channel-related parameter.
        start (Union[Unset, int]): Starting index for pagination.
        count (Union[Unset, int]):  Default: 15.
        skip_count (Union[Unset, GetApiV1UsersMeVideosSkipCount]):  Default:
            GetApiV1UsersMeVideosSkipCount.FALSE.
        sort (Union[Unset, GetApiV1UsersMeVideosSort]): Sort videos by criteria (prefixing with
            `-` means `DESC` order):
              * `hot` - Adaptation of Reddit "hot" algorithm taking into account video views, likes,
            dislikes and comments and publication date
              * `best` - Same than `hot`, but also takes into account user video history
              * `trending` - Sort videos by recent views ("recent" is defined by the admin)
              * `views` - Sort videos using their `views` counter
              * `publishedAt` - Sort by video publication date (when it became publicly available)
        nsfw (Union[Unset, GetApiV1UsersMeVideosNsfw]): Parameter for nsfw.
        nsfw_flags_included (Union[Unset, NSFWFlag]): Parameter for nsfw flags included.
            NSFW flags (can be combined using bitwise or operator)
            - `0` NONE
            - `1` VIOLENT
            - `2` EXPLICIT_SEX
        nsfw_flags_excluded (Union[Unset, NSFWFlag]): Parameter for nsfw flags excluded.
            NSFW flags (can be combined using bitwise or operator)
            - `0` NONE
            - `1` VIOLENT
            - `2` EXPLICIT_SEX
        is_live (Union[Unset, bool]): Parameter for is live.
        include_scheduled_live (Union[Unset, bool]): Parameter for include scheduled live.
        category_one_of (Union[Unset, int, list[int]]): Parameter for category one of.
        licence_one_of (Union[Unset, int, list[int]]): Parameter for licence one of.
        language_one_of (Union[Unset, list[str], str]): Parameter for language one of.
        tags_one_of (Union[Unset, list[str], str]): Parameter for tags one of.
        tags_all_of (Union[Unset, list[str], str]): Parameter for tags all of.
        is_local (Union[Unset, bool]): Parameter for is local.
        include (Union[Unset, GetApiV1UsersMeVideosInclude]): Parameter for include.
        has_hls_files (Union[Unset, bool]): Parameter for has hls files.
        has_web_video_files (Union[Unset, bool]): Video-related parameter.
        host (Union[Unset, str]): Parameter for host.
        auto_tag_one_of (Union[Unset, list[str], str]): Parameter for auto tag one of.
        privacy_one_of (Union[Unset, VideoPrivacySet]): privacy id of the video (see
            [/videos/privacies](#operation/getVideoPrivacyPolicies))
        exclude_already_watched (Union[Unset, bool]): Parameter for exclude already watched.
        search (Union[Unset, str]): Search query filter.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        VideoListResponse
    """

    return sync_detailed(
        client=client,
        channel_name_one_of=channel_name_one_of,
        start=start,
        count=count,
        skip_count=skip_count,
        sort=sort,
        nsfw=nsfw,
        nsfw_flags_included=nsfw_flags_included,
        nsfw_flags_excluded=nsfw_flags_excluded,
        is_live=is_live,
        include_scheduled_live=include_scheduled_live,
        category_one_of=category_one_of,
        licence_one_of=licence_one_of,
        language_one_of=language_one_of,
        tags_one_of=tags_one_of,
        tags_all_of=tags_all_of,
        is_local=is_local,
        include=include,
        has_hls_files=has_hls_files,
        has_web_video_files=has_web_video_files,
        host=host,
        auto_tag_one_of=auto_tag_one_of,
        privacy_one_of=privacy_one_of,
        exclude_already_watched=exclude_already_watched,
        search=search,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    channel_name_one_of: Unset | list[str] | str = UNSET,
    start: Unset | int = UNSET,
    count: Unset | int = 15,
    skip_count: Unset
    | GetApiV1UsersMeVideosSkipCount = GetApiV1UsersMeVideosSkipCount.FALSE,
    sort: Unset | GetApiV1UsersMeVideosSort = UNSET,
    nsfw: Unset | GetApiV1UsersMeVideosNsfw = UNSET,
    nsfw_flags_included: Unset | NSFWFlag = UNSET,
    nsfw_flags_excluded: Unset | NSFWFlag = UNSET,
    is_live: Unset | bool = UNSET,
    include_scheduled_live: Unset | bool = UNSET,
    category_one_of: Unset | int | list[int] = UNSET,
    licence_one_of: Unset | int | list[int] = UNSET,
    language_one_of: Unset | list[str] | str = UNSET,
    tags_one_of: Unset | list[str] | str = UNSET,
    tags_all_of: Unset | list[str] | str = UNSET,
    is_local: Unset | bool = UNSET,
    include: Unset | GetApiV1UsersMeVideosInclude = UNSET,
    has_hls_files: Unset | bool = UNSET,
    has_web_video_files: Unset | bool = UNSET,
    host: Unset | str = UNSET,
    auto_tag_one_of: Unset | list[str] | str = UNSET,
    privacy_one_of: Unset | VideoPrivacySet = UNSET,
    exclude_already_watched: Unset | bool = UNSET,
    search: Unset | str = UNSET,
) -> Response[VideoListResponse]:
    """List videos of my user

    Args:
        channel_name_one_of (Union[Unset, list[str], str]): Channel-related parameter.
        start (Union[Unset, int]): Starting index for pagination.
        count (Union[Unset, int]):  Default: 15.
        skip_count (Union[Unset, GetApiV1UsersMeVideosSkipCount]):  Default:
            GetApiV1UsersMeVideosSkipCount.FALSE.
        sort (Union[Unset, GetApiV1UsersMeVideosSort]): Sort videos by criteria (prefixing with
            `-` means `DESC` order):
              * `hot` - Adaptation of Reddit "hot" algorithm taking into account video views, likes,
            dislikes and comments and publication date
              * `best` - Same than `hot`, but also takes into account user video history
              * `trending` - Sort videos by recent views ("recent" is defined by the admin)
              * `views` - Sort videos using their `views` counter
              * `publishedAt` - Sort by video publication date (when it became publicly available)
        nsfw (Union[Unset, GetApiV1UsersMeVideosNsfw]): Parameter for nsfw.
        nsfw_flags_included (Union[Unset, NSFWFlag]): Parameter for nsfw flags included.
            NSFW flags (can be combined using bitwise or operator)
            - `0` NONE
            - `1` VIOLENT
            - `2` EXPLICIT_SEX
        nsfw_flags_excluded (Union[Unset, NSFWFlag]): Parameter for nsfw flags excluded.
            NSFW flags (can be combined using bitwise or operator)
            - `0` NONE
            - `1` VIOLENT
            - `2` EXPLICIT_SEX
        is_live (Union[Unset, bool]): Parameter for is live.
        include_scheduled_live (Union[Unset, bool]): Parameter for include scheduled live.
        category_one_of (Union[Unset, int, list[int]]): Parameter for category one of.
        licence_one_of (Union[Unset, int, list[int]]): Parameter for licence one of.
        language_one_of (Union[Unset, list[str], str]): Parameter for language one of.
        tags_one_of (Union[Unset, list[str], str]): Parameter for tags one of.
        tags_all_of (Union[Unset, list[str], str]): Parameter for tags all of.
        is_local (Union[Unset, bool]): Parameter for is local.
        include (Union[Unset, GetApiV1UsersMeVideosInclude]): Parameter for include.
        has_hls_files (Union[Unset, bool]): Parameter for has hls files.
        has_web_video_files (Union[Unset, bool]): Video-related parameter.
        host (Union[Unset, str]): Parameter for host.
        auto_tag_one_of (Union[Unset, list[str], str]): Parameter for auto tag one of.
        privacy_one_of (Union[Unset, VideoPrivacySet]): privacy id of the video (see
            [/videos/privacies](#operation/getVideoPrivacyPolicies))
        exclude_already_watched (Union[Unset, bool]): Parameter for exclude already watched.
        search (Union[Unset, str]): Search query filter.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[VideoListResponse]
    """

    kwargs = _get_kwargs(
        channel_name_one_of=channel_name_one_of,
        start=start,
        count=count,
        skip_count=skip_count,
        sort=sort,
        nsfw=nsfw,
        nsfw_flags_included=nsfw_flags_included,
        nsfw_flags_excluded=nsfw_flags_excluded,
        is_live=is_live,
        include_scheduled_live=include_scheduled_live,
        category_one_of=category_one_of,
        licence_one_of=licence_one_of,
        language_one_of=language_one_of,
        tags_one_of=tags_one_of,
        tags_all_of=tags_all_of,
        is_local=is_local,
        include=include,
        has_hls_files=has_hls_files,
        has_web_video_files=has_web_video_files,
        host=host,
        auto_tag_one_of=auto_tag_one_of,
        privacy_one_of=privacy_one_of,
        exclude_already_watched=exclude_already_watched,
        search=search,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    channel_name_one_of: Unset | list[str] | str = UNSET,
    start: Unset | int = UNSET,
    count: Unset | int = 15,
    skip_count: Unset
    | GetApiV1UsersMeVideosSkipCount = GetApiV1UsersMeVideosSkipCount.FALSE,
    sort: Unset | GetApiV1UsersMeVideosSort = UNSET,
    nsfw: Unset | GetApiV1UsersMeVideosNsfw = UNSET,
    nsfw_flags_included: Unset | NSFWFlag = UNSET,
    nsfw_flags_excluded: Unset | NSFWFlag = UNSET,
    is_live: Unset | bool = UNSET,
    include_scheduled_live: Unset | bool = UNSET,
    category_one_of: Unset | int | list[int] = UNSET,
    licence_one_of: Unset | int | list[int] = UNSET,
    language_one_of: Unset | list[str] | str = UNSET,
    tags_one_of: Unset | list[str] | str = UNSET,
    tags_all_of: Unset | list[str] | str = UNSET,
    is_local: Unset | bool = UNSET,
    include: Unset | GetApiV1UsersMeVideosInclude = UNSET,
    has_hls_files: Unset | bool = UNSET,
    has_web_video_files: Unset | bool = UNSET,
    host: Unset | str = UNSET,
    auto_tag_one_of: Unset | list[str] | str = UNSET,
    privacy_one_of: Unset | VideoPrivacySet = UNSET,
    exclude_already_watched: Unset | bool = UNSET,
    search: Unset | str = UNSET,
) -> VideoListResponse | None:
    """List videos of my user

    Args:
        channel_name_one_of (Union[Unset, list[str], str]): Channel-related parameter.
        start (Union[Unset, int]): Starting index for pagination.
        count (Union[Unset, int]):  Default: 15.
        skip_count (Union[Unset, GetApiV1UsersMeVideosSkipCount]):  Default:
            GetApiV1UsersMeVideosSkipCount.FALSE.
        sort (Union[Unset, GetApiV1UsersMeVideosSort]): Sort videos by criteria (prefixing with
            `-` means `DESC` order):
              * `hot` - Adaptation of Reddit "hot" algorithm taking into account video views, likes,
            dislikes and comments and publication date
              * `best` - Same than `hot`, but also takes into account user video history
              * `trending` - Sort videos by recent views ("recent" is defined by the admin)
              * `views` - Sort videos using their `views` counter
              * `publishedAt` - Sort by video publication date (when it became publicly available)
        nsfw (Union[Unset, GetApiV1UsersMeVideosNsfw]): Parameter for nsfw.
        nsfw_flags_included (Union[Unset, NSFWFlag]): Parameter for nsfw flags included.
            NSFW flags (can be combined using bitwise or operator)
            - `0` NONE
            - `1` VIOLENT
            - `2` EXPLICIT_SEX
        nsfw_flags_excluded (Union[Unset, NSFWFlag]): Parameter for nsfw flags excluded.
            NSFW flags (can be combined using bitwise or operator)
            - `0` NONE
            - `1` VIOLENT
            - `2` EXPLICIT_SEX
        is_live (Union[Unset, bool]): Parameter for is live.
        include_scheduled_live (Union[Unset, bool]): Parameter for include scheduled live.
        category_one_of (Union[Unset, int, list[int]]): Parameter for category one of.
        licence_one_of (Union[Unset, int, list[int]]): Parameter for licence one of.
        language_one_of (Union[Unset, list[str], str]): Parameter for language one of.
        tags_one_of (Union[Unset, list[str], str]): Parameter for tags one of.
        tags_all_of (Union[Unset, list[str], str]): Parameter for tags all of.
        is_local (Union[Unset, bool]): Parameter for is local.
        include (Union[Unset, GetApiV1UsersMeVideosInclude]): Parameter for include.
        has_hls_files (Union[Unset, bool]): Parameter for has hls files.
        has_web_video_files (Union[Unset, bool]): Video-related parameter.
        host (Union[Unset, str]): Parameter for host.
        auto_tag_one_of (Union[Unset, list[str], str]): Parameter for auto tag one of.
        privacy_one_of (Union[Unset, VideoPrivacySet]): privacy id of the video (see
            [/videos/privacies](#operation/getVideoPrivacyPolicies))
        exclude_already_watched (Union[Unset, bool]): Parameter for exclude already watched.
        search (Union[Unset, str]): Search query filter.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        VideoListResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            channel_name_one_of=channel_name_one_of,
            start=start,
            count=count,
            skip_count=skip_count,
            sort=sort,
            nsfw=nsfw,
            nsfw_flags_included=nsfw_flags_included,
            nsfw_flags_excluded=nsfw_flags_excluded,
            is_live=is_live,
            include_scheduled_live=include_scheduled_live,
            category_one_of=category_one_of,
            licence_one_of=licence_one_of,
            language_one_of=language_one_of,
            tags_one_of=tags_one_of,
            tags_all_of=tags_all_of,
            is_local=is_local,
            include=include,
            has_hls_files=has_hls_files,
            has_web_video_files=has_web_video_files,
            host=host,
            auto_tag_one_of=auto_tag_one_of,
            privacy_one_of=privacy_one_of,
            exclude_already_watched=exclude_already_watched,
            search=search,
        )
    ).parsed
