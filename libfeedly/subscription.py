""":mod:`libfeedly.subscription`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
from .stream import Stream
from .compat import dict_iter, xmap

__all__ = 'Subscription',


class Subscription(Stream):

    def __init__(self, api, id, categories=None, **kwds):
        self.api = api
        self.id = id
        self.categories = xmap(
            lambda x: x if isinstance(x, str) else
                      x.get('label') if isinstance(x, dict) else unicode(x),
            categories or []
        )
        for k, v in dict_iter(kwds):
            self.__setattr__(k, v)
        super(Subscription, self).__init__(self.id, self.api)

    @property
    def feed_uri(self):
        return self.id.strip('feed/')

    def subscribe(self):
        _ = self.api.subscribe(self.feed_uri, self.categories)
        self.title = _.title
        self.categories = _.categories
        self.website = _.website
        self.categories = _.categories

    def unsubscribe(self):
        return self.api.unsubscribe(self.feed_uri)

    def mark_as_read(self):
        return self.api.all_mark_as_read([self.id])

