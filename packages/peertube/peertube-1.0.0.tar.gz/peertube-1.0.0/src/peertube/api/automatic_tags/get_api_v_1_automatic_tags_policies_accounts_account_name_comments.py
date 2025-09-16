from http import HTTPStatus
from typing import Any

import httpx

from peertube import errors
from peertube.client import AuthenticatedClient, Client
from peertube.models.comment_auto_tag_policies import CommentAutoTagPolicies
from peertube.types import Response


def _get_kwargs(
    account_name: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/api/v1/automatic-tags/policies/accounts/{account_name}/comments",
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> CommentAutoTagPolicies | None:
    if response.status_code == 200:
        response_200 = CommentAutoTagPolicies.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[CommentAutoTagPolicies]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    account_name: str,
    *,
    client: AuthenticatedClient,
) -> Response[CommentAutoTagPolicies]:
    """Get account auto tag policies on comments

     **PeerTube >= 6.2**

    Args:
        account_name (str): Parameter for account name.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CommentAutoTagPolicies]
    """

    kwargs = _get_kwargs(
        account_name=account_name,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    account_name: str,
    *,
    client: AuthenticatedClient,
) -> CommentAutoTagPolicies | None:
    """Get account auto tag policies on comments

     **PeerTube >= 6.2**

    Args:
        account_name (str): Parameter for account name.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CommentAutoTagPolicies
    """

    return sync_detailed(
        account_name=account_name,
        client=client,
    ).parsed


async def asyncio_detailed(
    account_name: str,
    *,
    client: AuthenticatedClient,
) -> Response[CommentAutoTagPolicies]:
    """Get account auto tag policies on comments

     **PeerTube >= 6.2**

    Args:
        account_name (str): Parameter for account name.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CommentAutoTagPolicies]
    """

    kwargs = _get_kwargs(
        account_name=account_name,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    account_name: str,
    *,
    client: AuthenticatedClient,
) -> CommentAutoTagPolicies | None:
    """Get account auto tag policies on comments

     **PeerTube >= 6.2**

    Args:
        account_name (str): Parameter for account name.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CommentAutoTagPolicies
    """

    return (
        await asyncio_detailed(
            account_name=account_name,
            client=client,
        )
    ).parsed
