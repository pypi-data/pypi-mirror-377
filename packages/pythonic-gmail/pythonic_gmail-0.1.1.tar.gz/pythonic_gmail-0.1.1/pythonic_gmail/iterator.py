# -*- coding: utf-8 -*-

import typing as T

from iterproxy import IterProxy

from .model import (
    Message,
    ListMessagesResponse,
    Thread,
    ListThreadsResponse,
)


class ListMessagesResponseIterProxy(IterProxy[ListMessagesResponse]):
    @classmethod
    def from_paginator(
        cls,
        paginator: T.Iterable,
    ):
        return cls(
            (ListMessagesResponse.new(res) for res in paginator),
        )

    def iter_items(self) -> T.Iterator["Message"]:
        res: "ListMessagesResponse"
        message: "Message"
        for res in self:
            for message in res.messages:
                yield message


class ListThreadsResponseIterProxy(IterProxy[ListThreadsResponse]):
    @classmethod
    def from_paginator(
        cls,
        paginator: T.Iterable,
    ):
        return cls(
            (ListThreadsResponse.new(res) for res in paginator),
        )

    def iter_items(self) -> T.Iterator["Thread"]:
        res: "ListThreadsResponse"
        thread: "Thread"
        for res in self:
            for thread in res.threads:
                yield thread
