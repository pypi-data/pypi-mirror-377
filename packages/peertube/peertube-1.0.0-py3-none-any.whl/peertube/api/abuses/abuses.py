from http import HTTPStatus
from typing import Any

import httpx

from peertube import errors
from peertube.client import AuthenticatedClient, Client
from peertube.models.abuse_state_set import AbuseStateSet
from peertube.models.get_abuses_filter import GetAbusesFilter
from peertube.models.get_abuses_sort import GetAbusesSort
from peertube.models.get_abuses_video_is import GetAbusesVideoIs
from peertube.models.predefined_abuse_reasons_item import PredefinedAbuseReasonsItem
from peertube.types import UNSET, Response, Unset


def _get_kwargs(
    *,
    id: Unset | int = UNSET,
    predefined_reason: Unset | list[PredefinedAbuseReasonsItem] = UNSET,
    search: Unset | str = UNSET,
    state: Unset | AbuseStateSet = UNSET,
    search_reporter: Unset | str = UNSET,
    search_reportee: Unset | str = UNSET,
    search_video: Unset | str = UNSET,
    search_video_channel: Unset | str = UNSET,
    video_is: Unset | GetAbusesVideoIs = UNSET,
    filter_: Unset | GetAbusesFilter = UNSET,
    start: Unset | int = UNSET,
    count: Unset | int = 15,
    sort: Unset | GetAbusesSort = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["id"] = id

    json_predefined_reason: Unset | list[str] = UNSET
    if not isinstance(predefined_reason, Unset):
        json_predefined_reason = []
        for componentsschemas_predefined_abuse_reasons_item_data in predefined_reason:
            componentsschemas_predefined_abuse_reasons_item = (
                componentsschemas_predefined_abuse_reasons_item_data.value
            )
            json_predefined_reason.append(
                componentsschemas_predefined_abuse_reasons_item
            )

    params["predefinedReason"] = json_predefined_reason

    params["search"] = search

    json_state: Unset | int = UNSET
    if not isinstance(state, Unset):
        json_state = state.value

    params["state"] = json_state

    params["searchReporter"] = search_reporter

    params["searchReportee"] = search_reportee

    params["searchVideo"] = search_video

    params["searchVideoChannel"] = search_video_channel

    json_video_is: Unset | str = UNSET
    if not isinstance(video_is, Unset):
        json_video_is = video_is.value

    params["videoIs"] = json_video_is

    json_filter_: Unset | str = UNSET
    if not isinstance(filter_, Unset):
        json_filter_ = filter_.value

    params["filter"] = json_filter_

    params["start"] = start

    params["count"] = count

    json_sort: Unset | str = UNSET
    if not isinstance(sort, Unset):
        json_sort = sort.value

    params["sort"] = json_sort

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/abuses",
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
    id: Unset | int = UNSET,
    predefined_reason: Unset | list[PredefinedAbuseReasonsItem] = UNSET,
    search: Unset | str = UNSET,
    state: Unset | AbuseStateSet = UNSET,
    search_reporter: Unset | str = UNSET,
    search_reportee: Unset | str = UNSET,
    search_video: Unset | str = UNSET,
    search_video_channel: Unset | str = UNSET,
    video_is: Unset | GetAbusesVideoIs = UNSET,
    filter_: Unset | GetAbusesFilter = UNSET,
    start: Unset | int = UNSET,
    count: Unset | int = 15,
    sort: Unset | GetAbusesSort = UNSET,
) -> Response[Any]:
    """List abuses

    Args:
        id (Union[Unset, int]): Unique identifier for the entity.
        predefined_reason (Union[Unset, list[PredefinedAbuseReasonsItem]]): Reason categories that
            help triage reports
        search (Union[Unset, str]): Search query filter.
        state (Union[Unset, AbuseStateSet]): The abuse state (Pending = `1`, Rejected = `2`,
            Accepted = `3`)
        search_reporter (Union[Unset, str]): Search filter for reporter.
        search_reportee (Union[Unset, str]): Search filter for reportee.
        search_video (Union[Unset, str]): Search filter for video.
        search_video_channel (Union[Unset, str]): Search filter for video_channel.
        video_is (Union[Unset, GetAbusesVideoIs]): Video-related parameter.
        filter_ (Union[Unset, GetAbusesFilter]): Filter criteria for results.
        start (Union[Unset, int]): Starting index for pagination.
        count (Union[Unset, int]):  Default: 15.
        client: Authenticated HTTP client for API requests.
        sort (Union[Unset, GetAbusesSort]): Sorting criteria for results.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        id=id,
        predefined_reason=predefined_reason,
        search=search,
        state=state,
        search_reporter=search_reporter,
        search_reportee=search_reportee,
        search_video=search_video,
        search_video_channel=search_video_channel,
        video_is=video_is,
        filter_=filter_,
        start=start,
        count=count,
        sort=sort,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    id: Unset | int = UNSET,
    predefined_reason: Unset | list[PredefinedAbuseReasonsItem] = UNSET,
    search: Unset | str = UNSET,
    state: Unset | AbuseStateSet = UNSET,
    search_reporter: Unset | str = UNSET,
    search_reportee: Unset | str = UNSET,
    search_video: Unset | str = UNSET,
    search_video_channel: Unset | str = UNSET,
    video_is: Unset | GetAbusesVideoIs = UNSET,
    filter_: Unset | GetAbusesFilter = UNSET,
    start: Unset | int = UNSET,
    count: Unset | int = 15,
    sort: Unset | GetAbusesSort = UNSET,
) -> Response[Any]:
    """List abuses

    Args:
        id (Union[Unset, int]): Unique identifier for the entity.
        predefined_reason (Union[Unset, list[PredefinedAbuseReasonsItem]]): Reason categories that
            help triage reports
        search (Union[Unset, str]): Search query filter.
        state (Union[Unset, AbuseStateSet]): The abuse state (Pending = `1`, Rejected = `2`,
            Accepted = `3`)
        search_reporter (Union[Unset, str]): Search filter for reporter.
        search_reportee (Union[Unset, str]): Search filter for reportee.
        search_video (Union[Unset, str]): Search filter for video.
        search_video_channel (Union[Unset, str]): Search filter for video_channel.
        video_is (Union[Unset, GetAbusesVideoIs]): Video-related parameter.
        filter_ (Union[Unset, GetAbusesFilter]): Filter criteria for results.
        start (Union[Unset, int]): Starting index for pagination.
        count (Union[Unset, int]):  Default: 15.
        client: Authenticated HTTP client for API requests.
        sort (Union[Unset, GetAbusesSort]): Sorting criteria for results.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        id=id,
        predefined_reason=predefined_reason,
        search=search,
        state=state,
        search_reporter=search_reporter,
        search_reportee=search_reportee,
        search_video=search_video,
        search_video_channel=search_video_channel,
        video_is=video_is,
        filter_=filter_,
        start=start,
        count=count,
        sort=sort,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)
