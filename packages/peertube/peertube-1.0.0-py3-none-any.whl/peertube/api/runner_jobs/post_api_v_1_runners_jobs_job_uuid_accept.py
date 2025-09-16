from http import HTTPStatus
from typing import Any
from uuid import UUID

import httpx

from peertube import errors
from peertube.client import AuthenticatedClient, Client
from peertube.models.post_api_v1_runners_jobs_job_uuid_accept_body import (
    PostApiV1RunnersJobsJobUUIDAcceptBody,
)
from peertube.models.post_api_v1_runners_jobs_job_uuid_accept_response_200 import (
    PostApiV1RunnersJobsJobUUIDAcceptResponse200,
)
from peertube.types import Response


def _get_kwargs(
    job_uuid: UUID,
    *,
    body: PostApiV1RunnersJobsJobUUIDAcceptBody,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/api/v1/runners/jobs/{job_uuid}/accept",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> PostApiV1RunnersJobsJobUUIDAcceptResponse200 | None:
    if response.status_code == 200:
        response_200 = PostApiV1RunnersJobsJobUUIDAcceptResponse200.from_dict(
            response.json()
        )

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[PostApiV1RunnersJobsJobUUIDAcceptResponse200]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    job_uuid: UUID,
    *,
    client: AuthenticatedClient | Client,
    body: PostApiV1RunnersJobsJobUUIDAcceptBody,
) -> Response[PostApiV1RunnersJobsJobUUIDAcceptResponse200]:
    """Accept job

     API used by PeerTube runners

    Args:
        job_uuid (UUID):  Example: 9c9de5e8-0a1e-484a-b099-e80766180a6d.
        body (PostApiV1RunnersJobsJobUUIDAcceptBody): Request body data.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PostApiV1RunnersJobsJobUUIDAcceptResponse200]
    """

    kwargs = _get_kwargs(
        job_uuid=job_uuid,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    job_uuid: UUID,
    *,
    client: AuthenticatedClient | Client,
    body: PostApiV1RunnersJobsJobUUIDAcceptBody,
) -> PostApiV1RunnersJobsJobUUIDAcceptResponse200 | None:
    """Accept job

     API used by PeerTube runners

    Args:
        job_uuid (UUID):  Example: 9c9de5e8-0a1e-484a-b099-e80766180a6d.
        body (PostApiV1RunnersJobsJobUUIDAcceptBody): Request body data.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PostApiV1RunnersJobsJobUUIDAcceptResponse200
    """

    return sync_detailed(
        job_uuid=job_uuid,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    job_uuid: UUID,
    *,
    client: AuthenticatedClient | Client,
    body: PostApiV1RunnersJobsJobUUIDAcceptBody,
) -> Response[PostApiV1RunnersJobsJobUUIDAcceptResponse200]:
    """Accept job

     API used by PeerTube runners

    Args:
        job_uuid (UUID):  Example: 9c9de5e8-0a1e-484a-b099-e80766180a6d.
        body (PostApiV1RunnersJobsJobUUIDAcceptBody): Request body data.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PostApiV1RunnersJobsJobUUIDAcceptResponse200]
    """

    kwargs = _get_kwargs(
        job_uuid=job_uuid,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    job_uuid: UUID,
    *,
    client: AuthenticatedClient | Client,
    body: PostApiV1RunnersJobsJobUUIDAcceptBody,
) -> PostApiV1RunnersJobsJobUUIDAcceptResponse200 | None:
    """Accept job

     API used by PeerTube runners

    Args:
        job_uuid (UUID):  Example: 9c9de5e8-0a1e-484a-b099-e80766180a6d.
        body (PostApiV1RunnersJobsJobUUIDAcceptBody): Request body data.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PostApiV1RunnersJobsJobUUIDAcceptResponse200
    """

    return (
        await asyncio_detailed(
            job_uuid=job_uuid,
            client=client,
            body=body,
        )
    ).parsed
