""":mod:`libfeedly.subscription`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
from stream import Stream


class Subscription(object):

    def __init__(self, api, id, categories=None, **kwds):
        self.api = api
        self.id = id
        self.categories = map(
            lambda x: x if isinstance(x, basestring) else
                      x.get('label') if isinstance(x, dict) else unicode(x),
            categories or []
        )
        for k, v in kwds.iteritems():
            self.__setattr__(k, v)

    @property
    def stream(self):
        return Stream(self.id, api=self.api, count=40)

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

