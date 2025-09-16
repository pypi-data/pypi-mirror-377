from http import HTTPStatus
from typing import Any

import httpx

from peertube import errors
from peertube.client import AuthenticatedClient, Client
from peertube.models.post_api_v1_watched_words_accounts_account_name_lists_body import (
    PostApiV1WatchedWordsAccountsAccountNameListsBody,
)
from peertube.models.post_api_v1_watched_words_accounts_account_name_lists_response_200 import (
    PostApiV1WatchedWordsAccountsAccountNameListsResponse200,
)
from peertube.types import Response


def _get_kwargs(
    account_name: str,
    *,
    body: PostApiV1WatchedWordsAccountsAccountNameListsBody,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/api/v1/watched-words/accounts/{account_name}/lists",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> PostApiV1WatchedWordsAccountsAccountNameListsResponse200 | None:
    if response.status_code == 200:
        response_200 = (
            PostApiV1WatchedWordsAccountsAccountNameListsResponse200.from_dict(
                response.json()
            )
        )

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[PostApiV1WatchedWordsAccountsAccountNameListsResponse200]:
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
    body: PostApiV1WatchedWordsAccountsAccountNameListsBody,
) -> Response[PostApiV1WatchedWordsAccountsAccountNameListsResponse200]:
    """Add account watched words

     **PeerTube >= 6.2**

    Args:
        account_name (str): Parameter for account name.
        body (PostApiV1WatchedWordsAccountsAccountNameListsBody): Request body data.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PostApiV1WatchedWordsAccountsAccountNameListsResponse200]
    """

    kwargs = _get_kwargs(
        account_name=account_name,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    account_name: str,
    *,
    client: AuthenticatedClient,
    body: PostApiV1WatchedWordsAccountsAccountNameListsBody,
) -> PostApiV1WatchedWordsAccountsAccountNameListsResponse200 | None:
    """Add account watched words

     **PeerTube >= 6.2**

    Args:
        account_name (str): Parameter for account name.
        body (PostApiV1WatchedWordsAccountsAccountNameListsBody): Request body data.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PostApiV1WatchedWordsAccountsAccountNameListsResponse200
    """

    return sync_detailed(
        account_name=account_name,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    account_name: str,
    *,
    client: AuthenticatedClient,
    body: PostApiV1WatchedWordsAccountsAccountNameListsBody,
) -> Response[PostApiV1WatchedWordsAccountsAccountNameListsResponse200]:
    """Add account watched words

     **PeerTube >= 6.2**

    Args:
        account_name (str): Parameter for account name.
        body (PostApiV1WatchedWordsAccountsAccountNameListsBody): Request body data.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PostApiV1WatchedWordsAccountsAccountNameListsResponse200]
    """

    kwargs = _get_kwargs(
        account_name=account_name,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    account_name: str,
    *,
    client: AuthenticatedClient,
    body: PostApiV1WatchedWordsAccountsAccountNameListsBody,
) -> PostApiV1WatchedWordsAccountsAccountNameListsResponse200 | None:
    """Add account watched words

     **PeerTube >= 6.2**

    Args:
        account_name (str): Parameter for account name.
        body (PostApiV1WatchedWordsAccountsAccountNameListsBody): Request body data.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PostApiV1WatchedWordsAccountsAccountNameListsResponse200
    """

    return (
        await asyncio_detailed(
            account_name=account_name,
            client=client,
            body=body,
        )
    ).parsed
