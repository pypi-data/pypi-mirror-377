# -*- coding: utf-8 -*-

"""
Gmail API Pagination Utilities

This module provides pagination utilities for Gmail API list operations.
It abstracts the complexity of handling pageToken and nextPageToken to
provide a simple iterator interface for paginated API responses.

The module follows the adapter pattern to handle different Gmail API
endpoints (messages, threads) with a unified pagination mechanism.
"""

import typing as T

from .type_hint import T_KWARGS, T_RESPONSE


def default_set_page_size(
    request_kwargs: T_KWARGS,
    page_size: int,
):
    """
    Set maxResults in request parameters for page size.

    Default implementation for Gmail API's pagination mechanism where
    page size is controlled by the maxResults parameter.

    :param request_kwargs: Request parameters dictionary to modify
    :param page_size: Number of items to request per page
    """
    request_kwargs["maxResults"] = page_size


def default_get_next_token(
    response: T_RESPONSE,
) -> str | None:
    """
    Extract nextPageToken from Gmail API response.

    Default implementation for Gmail API's pagination mechanism where
    the next page token is provided in the nextPageToken field.

    :param response: API response dictionary

    :returns: Next page token if available, None if no more pages
    """
    return response.get("nextPageToken")


def default_set_next_token(
    request_kwargs: T_KWARGS,
    next_token: str,
):
    """
    Set pageToken in request parameters for next API call.

    Default implementation for Gmail API's pagination mechanism where
    the page token is passed via the pageToken parameter.

    :param request_kwargs: Request parameters dictionary to modify
    :param next_token: Token for the next page to retrieve
    """
    request_kwargs["pageToken"] = next_token


def paginate(
    method: T.Callable,
    items_field: str,
    page_size: int,
    max_items: int,
    kwargs: dict[str, T.Any] | None = None,
    set_page_size: T.Callable[[T_KWARGS, int], None] = default_set_page_size,
    get_next_token: T.Callable[[T_RESPONSE], str | None] = default_get_next_token,
    set_next_token: T.Callable[[T_KWARGS, str], None] = default_set_next_token,
) -> T.Iterator[dict[str, T.Any]]:
    """
    Core pagination engine for Gmail API list methods.

    Provides the underlying pagination mechanism used by :func:`~pythonic_gmail.client.pagi_list_messages`
    and :func:`~pythonic_gmail.client.pagi_list_threads`. Handles nextPageToken
    management and respects item count limits across multiple API calls.

    :param method: Gmail API method that returns a Resource for execution
    :param items_field: Field name in API response containing the list of items
    :param page_size: Number of items per API request (sets maxResults)
    :param max_items: Maximum total items to return across all pages
    :param kwargs: Initial parameters for the API call
    :param set_page_size: Function to set page size in request parameters
    :param get_next_token: Function to extract nextPageToken from API response
    :param set_next_token: Function to set pageToken in request parameters

    :yields: API response dictionaries containing paginated results

    **Examples**:
        Direct usage with messages list API::

            for response in paginate(
                method=gmail_client.users().messages().list,
                items_field="messages",
                page_size=50,
                max_items=100,
                kwargs={"userId": "me"}
            ):
                messages = response.get("messages", [])
                print(f"Got {len(messages)} messages")

        Direct usage with threads list API::

            for response in paginate(
                method=gmail_client.users().threads().list,
                items_field="threads",
                page_size=25,
                max_items=75,
                kwargs={"userId": "me"}
            ):
                threads = response.get("threads", [])
                print(f"Got {len(threads)} threads")

    .. note::
        This is a low-level function. Most users should use
        :func:`~pythonic_gmail.client.pagi_list_messages` or
        :func:`~pythonic_gmail.client.pagi_list_threads` instead.

    .. seealso::
        :func:`~pythonic_gmail.client.pagi_list_messages` and
        :func:`~pythonic_gmail.client.pagi_list_threads` for high-level interfaces.
    """
    items_returned = 0
    if kwargs is None:
        kwargs = {}
    set_page_size(kwargs, page_size)

    while True:
        # Execute the API call
        response = method(**kwargs).execute()
        items_in_response = len(response.get(items_field, []))
        items_returned += items_in_response

        yield response

        # Check if we've reached the maximum items limit
        if items_returned >= max_items:
            break

        # Get next page token for pagination
        next_token = get_next_token(response)
        if next_token is None:
            break  # No more pages available
        else:
            set_next_token(kwargs, next_token)
