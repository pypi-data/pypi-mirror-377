# -*- coding: utf-8 -*-

"""
This module provides a core batch retrieval engine for the Gmail API,
enabling efficient fetching of multiple messages or threads in a single request
to minimize HTTP overhead and improve performance.
"""

import typing as T

try:
    from more_itertools import batched
except ImportError as e:
    from itertools import batched

if T.TYPE_CHECKING:
    from googleapiclient._apis.gmail.v1 import GmailResource


def batch_get(
    gmail: "GmailResource",
    method: T.Callable,
    ids: list[T.Any],
    id_arg_name: str,
    batch_size: int = 50,
    kwargs: dict[str, T.Any] | None = None,
):
    """
    Core batch retrieval engine for Gmail API get methods.

    Provides the underlying batch mechanism used by :func:`~pythonic_gmail.client.batch_get_messages`
    and :func:`~pythonic_gmail.client.batch_get_threads`. Groups multiple API calls
    into efficient batch requests to reduce HTTP overhead.

    :param gmail: Gmail API client resource
    :param method: Gmail API method that returns a Resource for execution
    :param ids: List of IDs to retrieve (message IDs or thread IDs)
    :param id_arg_name: Parameter name for the ID in the API method
    :param batch_size: Number of items to fetch per batch request
    :param kwargs: Additional parameters for the API call

    :returns: List of retrieved objects from the API responses

    **Examples**:
        Direct usage with messages get API::

            messages = batch_get(
                gmail=gmail_client,
                method=gmail_client.users().messages().get,
                ids=["msg1", "msg2", "msg3"],
                id_arg_name="id",
                batch_size=2,
                kwargs={"userId": "me", "format": "minimal"}
            )

        Direct usage with threads get API::

            threads = batch_get(
                gmail=gmail_client,
                method=gmail_client.users().threads().get,
                ids=["thread1", "thread2", "thread3"],
                id_arg_name="id",
                batch_size=2,
                kwargs={"userId": "me", "format": "minimal"}
            )

    .. note::
        This is a low-level function. Most users should use
        :func:`~pythonic_gmail.client.batch_get_messages` or
        :func:`~pythonic_gmail.client.batch_get_threads` instead.

        Uses Gmail's batch API for efficient retrieval. See the
        `batch guide <https://developers.google.com/workspace/gmail/api/guides/batch>`_
        for more details.

    .. seealso::
        :func:`~pythonic_gmail.client.batch_get_messages` and
        :func:`~pythonic_gmail.client.batch_get_threads` for high-level interfaces.
    """
    if kwargs is None:
        kwargs = {}

    items = list()

    def callback(
        request_id,
        response,
        exception,
    ):
        if exception is not None:
            print(f"Error for request {request_id}: {exception}")
        else:
            items.append(response)

    for sub_ids in batched(ids, batch_size):
        batch_request = gmail.new_batch_http_request()
        for id in sub_ids:
            kwargs[id_arg_name] = id
            batch_request.add(
                method(**kwargs),
                callback=callback,
            )
        batch_request.execute()

    return items
