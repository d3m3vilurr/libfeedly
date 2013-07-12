""":mod:`libfeedly.stream`
~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
import urllib
from item import Item


class Stream(object):

    def __init__(self, stream_id, api, count=20, ranked='newest', limit=None):
        self.stream_id = stream_id
        self.api = api
        self.count = count
        self.ranked = ranked
        self.limit = limit
        # TODO: preload stream info

    @property
    def items(self):
        api = self.api
        cont = None
        i = 0
        while True:
            items, cont = api.contents(self.stream_id, count=self.count,
                                       unread_only=False, ranked=self.ranked,
                                       continuation=cont)
            for item in items:
                yield item
                i += 1
                if self.limit and self.limit >= i:
                    raise StopIteration
            if not cont:
                raise StopIteration

    @property
    def unread_items(self):
        api = self.api
        cont = None
        i = 0
        while True:
            items, cont = api.contents(self.stream_id, count=self.count,
                                       unread_only=True, ranked=self.ranked,
                                       continuation=cont)
            for item in items:
                yield item
                i += 1
                if self.limit and self.limit >= i:
                    raise StopIteration
            if not cont:
                raise StopIteration
