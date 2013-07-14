""":mod:`libfeedly.stream`
~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
from .item import Item

__all__ = 'Stream',


class Stream(object):

    def __init__(self, stream_id, api, count=40, ranked='newest'):
        self.stream_id = stream_id
        self.api = api
        self.count = count
        self.ranked = ranked
        # TODO: preload stream info

    @property
    def items(self):
        return ItemContainer(self, unread_only=False)

    @property
    def unread_items(self):
        return ItemContainer(self, unread_only=True)


class ItemContainer(object):

    def __init__(self, stream, unread_only):
        self.stream = stream
        self.unread_only = unread_only
        self.reload()

    def reload(self):
        self._cache = []
        self._cont = None
        self._load()

    def _load(self):
        api = self.stream.api
        stream = self.stream
        items, self.cont = api.contents(stream.stream_id, count=stream.count,
                                        unread_only=self.unread_only,
                                        ranked=stream.ranked,
                                        continuation=self._cont)
        self._cache += items

    def __getitem__(self, index):
        while self._cont and \
              (index < 0 or index >= len(self._caches)):
            self.load()
        return self._cache[index]

    def __iter__(self):
        for x in self._cache:
            yield x
        while self._cont:
            start_idx = len(self._cache)
            self._load()
            for x in self._cache[start_idx:]:
                yield x
