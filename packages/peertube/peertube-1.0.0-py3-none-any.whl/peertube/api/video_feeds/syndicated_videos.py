import json
from http import HTTPStatus
from typing import Any, cast

import httpx

from peertube import errors
from peertube.client import AuthenticatedClient, Client
from peertube.models.get_syndicated_videos_format import GetSyndicatedVideosFormat
from peertube.models.get_syndicated_videos_include import GetSyndicatedVideosInclude
from peertube.models.get_syndicated_videos_nsfw import GetSyndicatedVideosNsfw
from peertube.models.video_privacy_set import VideoPrivacySet
from peertube.models.videos_for_xml_item import VideosForXMLItem
from peertube.types import UNSET, Response, Unset


def _get_kwargs(
    format_: GetSyndicatedVideosFormat,
    *,
    account_id: Unset | str = UNSET,
    account_name: Unset | str = UNSET,
    video_channel_id: Unset | str = UNSET,
    video_channel_name: Unset | str = UNSET,
    sort: Unset | str = UNSET,
    nsfw: Unset | GetSyndicatedVideosNsfw = UNSET,
    is_local: Unset | bool = UNSET,
    include: Unset | GetSyndicatedVideosInclude = UNSET,
    privacy_one_of: Unset | VideoPrivacySet = UNSET,
    has_hls_files: Unset | bool = UNSET,
    has_web_video_files: Unset | bool = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["accountId"] = account_id

    params["accountName"] = account_name

    params["videoChannelId"] = video_channel_id

    params["videoChannelName"] = video_channel_name

    params["sort"] = sort

    json_nsfw: Unset | str = UNSET
    if not isinstance(nsfw, Unset):
        json_nsfw = nsfw.value

    params["nsfw"] = json_nsfw

    params["isLocal"] = is_local

    json_include: Unset | int = UNSET
    if not isinstance(include, Unset):
        json_include = include.value

    params["include"] = json_include

    json_privacy_one_of: Unset | int = UNSET
    if not isinstance(privacy_one_of, Unset):
        json_privacy_one_of = privacy_one_of.value

    params["privacyOneOf"] = json_privacy_one_of

    params["hasHLSFiles"] = has_hls_files

    params["hasWebVideoFiles"] = has_web_video_files

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/feeds/videos.{format_}",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | list["VideosForXMLItem"] | None:
    if response.status_code == 200:
        response_200 = []
        _response_200 = json.loads(response.text)
        for componentsschemas_videos_for_xml_item_data in _response_200:
            componentsschemas_videos_for_xml_item = VideosForXMLItem.from_dict(
                componentsschemas_videos_for_xml_item_data
            )

            response_200.append(componentsschemas_videos_for_xml_item)

        return response_200

    if response.status_code == 404:
        response_404 = cast("Any", None)
        return response_404

    if response.status_code == 406:
        response_406 = cast("Any", None)
        return response_406

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Any | list["VideosForXMLItem"]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    format_: GetSyndicatedVideosFormat,
    *,
    client: AuthenticatedClient | Client,
    account_id: Unset | str = UNSET,
    account_name: Unset | str = UNSET,
    video_channel_id: Unset | str = UNSET,
    video_channel_name: Unset | str = UNSET,
    sort: Unset | str = UNSET,
    nsfw: Unset | GetSyndicatedVideosNsfw = UNSET,
    is_local: Unset | bool = UNSET,
    include: Unset | GetSyndicatedVideosInclude = UNSET,
    privacy_one_of: Unset | VideoPrivacySet = UNSET,
    has_hls_files: Unset | bool = UNSET,
    has_web_video_files: Unset | bool = UNSET,
) -> Response[Any | list["VideosForXMLItem"]]:
    """Common videos feeds

    Args:
        format_ (GetSyndicatedVideosFormat): Parameter for format (underscore avoids keyword conflict).
        account_id (Union[Unset, str]): Parameter for account id.
        account_name (Union[Unset, str]): Parameter for account name.
        video_channel_id (Union[Unset, str]): Video-related parameter.
        video_channel_name (Union[Unset, str]): Video-related parameter.
        sort (Union[Unset, str]):  Example: -createdAt.
        nsfw (Union[Unset, GetSyndicatedVideosNsfw]): Parameter for nsfw.
        is_local (Union[Unset, bool]): Parameter for is local.
        include (Union[Unset, GetSyndicatedVideosInclude]): Parameter for include.
        privacy_one_of (Union[Unset, VideoPrivacySet]): privacy id of the video (see
            [/videos/privacies](#operation/getVideoPrivacyPolicies))
        has_hls_files (Union[Unset, bool]): Parameter for has hls files.
        has_web_video_files (Union[Unset, bool]): Video-related parameter.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, list['VideosForXMLItem']]]
    """

    kwargs = _get_kwargs(
        format_=format_,
        account_id=account_id,
        account_name=account_name,
        video_channel_id=video_channel_id,
        video_channel_name=video_channel_name,
        sort=sort,
        nsfw=nsfw,
        is_local=is_local,
        include=include,
        privacy_one_of=privacy_one_of,
        has_hls_files=has_hls_files,
        has_web_video_files=has_web_video_files,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    format_: GetSyndicatedVideosFormat,
    *,
    client: AuthenticatedClient | Client,
    account_id: Unset | str = UNSET,
    account_name: Unset | str = UNSET,
    video_channel_id: Unset | str = UNSET,
    video_channel_name: Unset | str = UNSET,
    sort: Unset | str = UNSET,
    nsfw: Unset | GetSyndicatedVideosNsfw = UNSET,
    is_local: Unset | bool = UNSET,
    include: Unset | GetSyndicatedVideosInclude = UNSET,
    privacy_one_of: Unset | VideoPrivacySet = UNSET,
    has_hls_files: Unset | bool = UNSET,
    has_web_video_files: Unset | bool = UNSET,
) -> Any | list["VideosForXMLItem"] | None:
    """Common videos feeds

    Args:
        format_ (GetSyndicatedVideosFormat): Parameter for format (underscore avoids keyword conflict).
        account_id (Union[Unset, str]): Parameter for account id.
        account_name (Union[Unset, str]): Parameter for account name.
        video_channel_id (Union[Unset, str]): Video-related parameter.
        video_channel_name (Union[Unset, str]): Video-related parameter.
        sort (Union[Unset, str]):  Example: -createdAt.
        nsfw (Union[Unset, GetSyndicatedVideosNsfw]): Parameter for nsfw.
        is_local (Union[Unset, bool]): Parameter for is local.
        include (Union[Unset, GetSyndicatedVideosInclude]): Parameter for include.
        privacy_one_of (Union[Unset, VideoPrivacySet]): privacy id of the video (see
            [/videos/privacies](#operation/getVideoPrivacyPolicies))
        has_hls_files (Union[Unset, bool]): Parameter for has hls files.
        has_web_video_files (Union[Unset, bool]): Video-related parameter.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, list['VideosForXMLItem']]
    """

    return sync_detailed(
        format_=format_,
        client=client,
        account_id=account_id,
        account_name=account_name,
        video_channel_id=video_channel_id,
        video_channel_name=video_channel_name,
        sort=sort,
        nsfw=nsfw,
        is_local=is_local,
        include=include,
        privacy_one_of=privacy_one_of,
        has_hls_files=has_hls_files,
        has_web_video_files=has_web_video_files,
    ).parsed


async def asyncio_detailed(
    format_: GetSyndicatedVideosFormat,
    *,
    client: AuthenticatedClient | Client,
    account_id: Unset | str = UNSET,
    account_name: Unset | str = UNSET,
    video_channel_id: Unset | str = UNSET,
    video_channel_name: Unset | str = UNSET,
    sort: Unset | str = UNSET,
    nsfw: Unset | GetSyndicatedVideosNsfw = UNSET,
    is_local: Unset | bool = UNSET,
    include: Unset | GetSyndicatedVideosInclude = UNSET,
    privacy_one_of: Unset | VideoPrivacySet = UNSET,
    has_hls_files: Unset | bool = UNSET,
    has_web_video_files: Unset | bool = UNSET,
) -> Response[Any | list["VideosForXMLItem"]]:
    """Common videos feeds

    Args:
        format_ (GetSyndicatedVideosFormat): Parameter for format (underscore avoids keyword conflict).
        account_id (Union[Unset, str]): Parameter for account id.
        account_name (Union[Unset, str]): Parameter for account name.
        video_channel_id (Union[Unset, str]): Video-related parameter.
        video_channel_name (Union[Unset, str]): Video-related parameter.
        sort (Union[Unset, str]):  Example: -createdAt.
        nsfw (Union[Unset, GetSyndicatedVideosNsfw]): Parameter for nsfw.
        is_local (Union[Unset, bool]): Parameter for is local.
        include (Union[Unset, GetSyndicatedVideosInclude]): Parameter for include.
        privacy_one_of (Union[Unset, VideoPrivacySet]): privacy id of the video (see
            [/videos/privacies](#operation/getVideoPrivacyPolicies))
        has_hls_files (Union[Unset, bool]): Parameter for has hls files.
        has_web_video_files (Union[Unset, bool]): Video-related parameter.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, list['VideosForXMLItem']]]
    """

    kwargs = _get_kwargs(
        format_=format_,
        account_id=account_id,
        account_name=account_name,
        video_channel_id=video_channel_id,
        video_channel_name=video_channel_name,
        sort=sort,
        nsfw=nsfw,
        is_local=is_local,
        include=include,
        privacy_one_of=privacy_one_of,
        has_hls_files=has_hls_files,
        has_web_video_files=has_web_video_files,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    format_: GetSyndicatedVideosFormat,
    *,
    client: AuthenticatedClient | Client,
    account_id: Unset | str = UNSET,
    account_name: Unset | str = UNSET,
    video_channel_id: Unset | str = UNSET,
    video_channel_name: Unset | str = UNSET,
    sort: Unset | str = UNSET,
    nsfw: Unset | GetSyndicatedVideosNsfw = UNSET,
    is_local: Unset | bool = UNSET,
    include: Unset | GetSyndicatedVideosInclude = UNSET,
    privacy_one_of: Unset | VideoPrivacySet = UNSET,
    has_hls_files: Unset | bool = UNSET,
    has_web_video_files: Unset | bool = UNSET,
) -> Any | list["VideosForXMLItem"] | None:
    """Common videos feeds

    Args:
        format_ (GetSyndicatedVideosFormat): Parameter for format (underscore avoids keyword conflict).
        account_id (Union[Unset, str]): Parameter for account id.
        account_name (Union[Unset, str]): Parameter for account name.
        video_channel_id (Union[Unset, str]): Video-related parameter.
        video_channel_name (Union[Unset, str]): Video-related parameter.
        sort (Union[Unset, str]):  Example: -createdAt.
        nsfw (Union[Unset, GetSyndicatedVideosNsfw]): Parameter for nsfw.
        is_local (Union[Unset, bool]): Parameter for is local.
        include (Union[Unset, GetSyndicatedVideosInclude]): Parameter for include.
        privacy_one_of (Union[Unset, VideoPrivacySet]): privacy id of the video (see
            [/videos/privacies](#operation/getVideoPrivacyPolicies))
        has_hls_files (Union[Unset, bool]): Parameter for has hls files.
        has_web_video_files (Union[Unset, bool]): Video-related parameter.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, list['VideosForXMLItem']]
    """

    return (
        await asyncio_detailed(
            format_=format_,
            client=client,
            account_id=account_id,
            account_name=account_name,
            video_channel_id=video_channel_id,
            video_channel_name=video_channel_name,
            sort=sort,
            nsfw=nsfw,
            is_local=is_local,
            include=include,
            privacy_one_of=privacy_one_of,
            has_hls_files=has_hls_files,
            has_web_video_files=has_web_video_files,
        )
    ).parsed
