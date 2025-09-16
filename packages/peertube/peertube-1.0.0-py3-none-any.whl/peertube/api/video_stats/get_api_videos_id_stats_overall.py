import datetime
from http import HTTPStatus
from typing import Any
from uuid import UUID

import httpx

from peertube import errors
from peertube.client import AuthenticatedClient, Client
from peertube.models.video_stats_overall import VideoStatsOverall
from peertube.types import UNSET, Response, Unset


def _get_kwargs(
    id: UUID | int | str,
    *,
    start_date: Unset | datetime.datetime = UNSET,
    end_date: Unset | datetime.datetime = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_start_date: Unset | str = UNSET
    if not isinstance(start_date, Unset):
        json_start_date = start_date.isoformat()
    params["startDate"] = json_start_date

    json_end_date: Unset | str = UNSET
    if not isinstance(end_date, Unset):
        json_end_date = end_date.isoformat()
    params["endDate"] = json_end_date

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/api/v1/videos/{id}/stats/overall",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> VideoStatsOverall | None:
    if response.status_code == 200:
        response_200 = VideoStatsOverall.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[VideoStatsOverall]:
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
    start_date: Unset | datetime.datetime = UNSET,
    end_date: Unset | datetime.datetime = UNSET,
) -> Response[VideoStatsOverall]:
    """Get overall stats of a video

    Args:
        id (Union[UUID, int, str]): Unique identifier for the entity.
        start_date (Union[Unset, datetime.datetime]): Parameter for start date.
        end_date (Union[Unset, datetime.datetime]): Parameter for end date.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[VideoStatsOverall]
    """

    kwargs = _get_kwargs(
        id=id,
        start_date=start_date,
        end_date=end_date,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    id: UUID | int | str,
    *,
    client: AuthenticatedClient,
    start_date: Unset | datetime.datetime = UNSET,
    end_date: Unset | datetime.datetime = UNSET,
) -> VideoStatsOverall | None:
    """Get overall stats of a video

    Args:
        id (Union[UUID, int, str]): Unique identifier for the entity.
        start_date (Union[Unset, datetime.datetime]): Parameter for start date.
        end_date (Union[Unset, datetime.datetime]): Parameter for end date.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        VideoStatsOverall
    """

    return sync_detailed(
        id=id,
        client=client,
        start_date=start_date,
        end_date=end_date,
    ).parsed


async def asyncio_detailed(
    id: UUID | int | str,
    *,
    client: AuthenticatedClient,
    start_date: Unset | datetime.datetime = UNSET,
    end_date: Unset | datetime.datetime = UNSET,
) -> Response[VideoStatsOverall]:
    """Get overall stats of a video

    Args:
        id (Union[UUID, int, str]): Unique identifier for the entity.
        start_date (Union[Unset, datetime.datetime]): Parameter for start date.
        end_date (Union[Unset, datetime.datetime]): Parameter for end date.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[VideoStatsOverall]
    """

    kwargs = _get_kwargs(
        id=id,
        start_date=start_date,
        end_date=end_date,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    id: UUID | int | str,
    *,
    client: AuthenticatedClient,
    start_date: Unset | datetime.datetime = UNSET,
    end_date: Unset | datetime.datetime = UNSET,
) -> VideoStatsOverall | None:
    """Get overall stats of a video

    Args:
        id (Union[UUID, int, str]): Unique identifier for the entity.
        start_date (Union[Unset, datetime.datetime]): Parameter for start date.
        end_date (Union[Unset, datetime.datetime]): Parameter for end date.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        VideoStatsOverall
    """

    return (
        await asyncio_detailed(
            id=id,
            client=client,
            start_date=start_date,
            end_date=end_date,
        )
    ).parsed
