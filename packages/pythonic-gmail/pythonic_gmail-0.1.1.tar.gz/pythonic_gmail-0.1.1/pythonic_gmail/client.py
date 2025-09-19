# -*- coding: utf-8 -*-

"""
Gmail API List and Batch Utilities

This module provides utilities for paginating Gmail API list operations and
efficiently retrieving multiple messages or threads using batch requests.
It abstracts page token handling and batch processing, offering unified iterator
and batch interfaces for different Gmail API endpoints.
"""

import typing as T

from .paginate import paginate
from .batch import batch_get

from .iterator import ListMessagesResponseIterProxy
from .iterator import ListThreadsResponseIterProxy

from .model import Message

if T.TYPE_CHECKING:
    from googleapiclient._apis.gmail.v1 import GmailResource


def pagi_list_messages(
    gmail: "GmailResource",
    kwargs: dict[str, T.Any] | None = None,
    page_size: int = 100,
    max_items: int = 1000,
) -> "ListMessagesResponseIterProxy":
    """
    Paginate Gmail messages list with automatic token handling.

    Returns an iterator proxy that yields Gmail API responses containing batches
    of messages. The proxy supports both response-level iteration and individual
    message iteration through the iter_items() method.

    :param gmail: Gmail API client resource
    :param kwargs: Parameters for Gmail's messages.list API call
    :param page_size: Number of messages per API request (maxResults)
    :param max_items: Maximum total messages to return across all pages

    :returns: Iterator proxy that yields :class:`~pythonic_gmail.model.ListMessagesResponse` objects

    **Examples**:
        Iterate over API responses::

            iterproxy = pagi_list_messages(
                gmail_client,
                kwargs={"userId": "me"},
                page_size=2,
                max_items=6
            )
            for i, res in enumerate(iterproxy):
                print(f"Response {i}: {res}")

        Iterate over individual messages::

            iterproxy = pagi_list_messages(
                gmail_client,
                kwargs={"userId": "me"},
                page_size=2,
                max_items=6
            )
            for i, msg in enumerate(iterproxy.iter_items()):
                print(f"Message {i}: {msg.id}")

    .. note::
        This function returns message metadata only (ID and threadId).
        Use :func:`batch_get_messages` to retrieve full message content.

    .. seealso::
        :func:`pagi_list_threads` for thread pagination and
        :func:`batch_get_messages` for retrieving full message content.
    """
    return ListMessagesResponseIterProxy.from_paginator(
        paginator=paginate(
            method=gmail.users().messages().list,
            items_field="messages",
            kwargs=kwargs,
            page_size=page_size,
            max_items=max_items,
        )
    )


def pagi_list_threads(
    gmail: "GmailResource",
    kwargs: dict[str, T.Any] | None = None,
    page_size: int = 100,
    max_items: int = 1000,
) -> "ListThreadsResponseIterProxy":
    """
    Paginate Gmail threads list with automatic token handling.

    Returns an iterator proxy that yields Gmail API responses containing batches
    of threads. The proxy supports both response-level iteration and individual
    thread iteration through the iter_items() method.

    :param gmail: Gmail API client resource
    :param kwargs: Parameters for Gmail's threads.list API call
    :param page_size: Number of threads per API request (maxResults)
    :param max_items: Maximum total threads to return across all pages

    :returns: Iterator proxy that yields :class:`~pythonic_gmail.model.ListThreadsResponse` objects

    **Examples**:
        Iterate over API responses::

            iterproxy = pagi_list_threads(
                gmail_client,
                kwargs={"userId": "me"},
                page_size=2,
                max_items=6
            )
            for i, res in enumerate(iterproxy):
                print(f"Response {i}: {res}")

        Iterate over individual threads::

            iterproxy = pagi_list_threads(
                gmail_client,
                kwargs={"userId": "me"},
                page_size=2,
                max_items=6
            )
            for i, thread in enumerate(iterproxy.iter_items()):
                print(f"Thread {i}: {thread.id}")

    .. note::
        This function returns thread metadata only (ID and snippet).
        Use :func:`batch_get_threads` to retrieve full thread content.

    .. seealso::
        :func:`pagi_list_messages` for message pagination and
        :func:`batch_get_threads` for retrieving full thread content.
    """
    return ListThreadsResponseIterProxy.from_paginator(
        paginator=paginate(
            method=gmail.users().threads().list,
            items_field="threads",
            kwargs=kwargs,
            page_size=page_size,
            max_items=max_items,
        )
    )


def batch_get_messages(
    gmail: "GmailResource",
    ids: list[str],
    batch_size: int = 100,
    kwargs: dict[str, T.Any] | None = None,
) -> list["Message"]:
    """
    Retrieve multiple Gmail messages using batch requests.

    Efficiently fetches multiple messages by batching API calls, reducing
    the number of HTTP requests compared to individual get operations.
    Useful for retrieving full message content after obtaining IDs from
    pagination functions.

    :param gmail: Gmail API client resource
    :param ids: List of message IDs to retrieve
    :param batch_size: Number of messages to fetch per batch request
    :param kwargs: Additional parameters for Gmail's messages.get API call

    :returns: List of :class:`~pythonic_gmail.model.Message` objects

    **Examples**:
        Basic message retrieval::

            ids = [
                "19959e8dc4ed58dc",
                "199599553c319566",
                "199598bcc7491337",
            ]
            messages = batch_get_messages(
                gmail_client,
                ids=ids,
                batch_size=2,
                kwargs={"userId": "me", "format": "minimal"}
            )
            for i, msg in enumerate(messages):
                print(f"Message {i}: {msg}")

    .. note::
        Uses Gmail's batch API for efficient retrieval.
        See `batch guide <https://developers.google.com/workspace/gmail/api/guides/batch>`_
        for more details.

    .. seealso::
        :func:`pagi_list_messages` for obtaining message IDs and
        :func:`batch_get_threads` for retrieving threads.
    """
    return batch_get(
        gmail=gmail,
        method=gmail.users().messages().get,
        ids=ids,
        id_arg_name="id",
        batch_size=batch_size,
        kwargs=kwargs,
    )


def batch_get_threads(
    gmail: "GmailResource",
    ids: list[str],
    batch_size: int = 100,
    kwargs: dict[str, T.Any] | None = None,
) -> list["Message"]:
    """
    Retrieve multiple Gmail threads using batch requests.

    Efficiently fetches multiple threads by batching API calls, reducing
    the number of HTTP requests compared to individual get operations.
    Useful for retrieving full thread content after obtaining IDs from
    pagination functions.

    :param gmail: Gmail API client resource
    :param ids: List of thread IDs to retrieve
    :param batch_size: Number of threads to fetch per batch request
    :param kwargs: Additional parameters for Gmail's threads.get API call

    :returns: List of thread objects (currently typed as :class:`~pythonic_gmail.model.Message`)

    **Examples**:
        Basic thread retrieval::

            ids = [
                "199599553c319566",
                "199598bcc7491337",
                "1995984aaf02e9ff",
            ]
            threads = batch_get_threads(
                gmail_client,
                ids=ids,
                batch_size=2,
                kwargs={"userId": "me", "format": "minimal"}
            )
            for i, thread in enumerate(threads):
                print(f"Thread {i}: {thread}")

    .. note::
        Uses Gmail's batch API for efficient retrieval.
        See `batch guide <https://developers.google.com/workspace/gmail/api/guides/batch>`_
        for more details.

    .. seealso::
        :func:`pagi_list_threads` for obtaining thread IDs and
        :func:`batch_get_messages` for retrieving messages.
    """
    return batch_get(
        gmail=gmail,
        method=gmail.users().threads().get,
        ids=ids,
        id_arg_name="id",
        batch_size=batch_size,
        kwargs=kwargs,
    )