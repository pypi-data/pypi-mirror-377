from http import HTTPStatus
from typing import Any

import httpx

from peertube import errors
from peertube.client import AuthenticatedClient, Client
from peertube.models.get_mirrored_videos_sort import GetMirroredVideosSort
from peertube.models.get_mirrored_videos_target import GetMirroredVideosTarget
from peertube.models.video_redundancy import VideoRedundancy
from peertube.types import UNSET, Response, Unset


def _get_kwargs(
    *,
    target: GetMirroredVideosTarget,
    start: Unset | int = UNSET,
    count: Unset | int = 15,
    sort: Unset | GetMirroredVideosSort = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_target = target.value
    params["target"] = json_target

    params["start"] = start

    params["count"] = count

    json_sort: Unset | str = UNSET
    if not isinstance(sort, Unset):
        json_sort = sort.value

    params["sort"] = json_sort

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/server/redundancy/videos",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> list["VideoRedundancy"] | None:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = VideoRedundancy.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[list["VideoRedundancy"]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    target: GetMirroredVideosTarget,
    start: Unset | int = UNSET,
    count: Unset | int = 15,
    sort: Unset | GetMirroredVideosSort = UNSET,
) -> Response[list["VideoRedundancy"]]:
    """List videos being mirrored

    Args:
        target (GetMirroredVideosTarget): Parameter for target.
        start (Union[Unset, int]): Starting index for pagination.
        count (Union[Unset, int]):  Default: 15.
        sort (Union[Unset, GetMirroredVideosSort]): Sorting criteria for results.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['VideoRedundancy']]
    """

    kwargs = _get_kwargs(
        target=target,
        start=start,
        count=count,
        sort=sort,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    target: GetMirroredVideosTarget,
    start: Unset | int = UNSET,
    count: Unset | int = 15,
    sort: Unset | GetMirroredVideosSort = UNSET,
) -> list["VideoRedundancy"] | None:
    """List videos being mirrored

    Args:
        target (GetMirroredVideosTarget): Parameter for target.
        start (Union[Unset, int]): Starting index for pagination.
        count (Union[Unset, int]):  Default: 15.
        sort (Union[Unset, GetMirroredVideosSort]): Sorting criteria for results.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['VideoRedundancy']
    """

    return sync_detailed(
        client=client,
        target=target,
        start=start,
        count=count,
        sort=sort,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    target: GetMirroredVideosTarget,
    start: Unset | int = UNSET,
    count: Unset | int = 15,
    sort: Unset | GetMirroredVideosSort = UNSET,
) -> Response[list["VideoRedundancy"]]:
    """List videos being mirrored

    Args:
        target (GetMirroredVideosTarget): Parameter for target.
        start (Union[Unset, int]): Starting index for pagination.
        count (Union[Unset, int]):  Default: 15.
        sort (Union[Unset, GetMirroredVideosSort]): Sorting criteria for results.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['VideoRedundancy']]
    """

    kwargs = _get_kwargs(
        target=target,
        start=start,
        count=count,
        sort=sort,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    target: GetMirroredVideosTarget,
    start: Unset | int = UNSET,
    count: Unset | int = 15,
    sort: Unset | GetMirroredVideosSort = UNSET,
) -> list["VideoRedundancy"] | None:
    """List videos being mirrored

    Args:
        target (GetMirroredVideosTarget): Parameter for target.
        start (Union[Unset, int]): Starting index for pagination.
        count (Union[Unset, int]):  Default: 15.
        sort (Union[Unset, GetMirroredVideosSort]): Sorting criteria for results.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['VideoRedundancy']
    """

    return (
        await asyncio_detailed(
            client=client,
            target=target,
            start=start,
            count=count,
            sort=sort,
        )
    ).parsed
