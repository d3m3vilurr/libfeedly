""":mod:`pydeely.subscription`
~~~~~~~~~~~~~~~~~~~~~
"""
from stream import Stream


class Subscription(object):

    def __init__(self, **kwds):
        for k, v in kwds.iteritems():
            self.__setattr__(k, v)

    @property
    def stream(self):
        return Stream(self.id, self.api, count=40)

    @property
    def feed_uri(self):
        return self.id.strip('feed/')

    def subscribe(self):
        _ = self.api.subscribe(self.feed_uri)
        self.title = _.title
        self.categories = _.categories
        self.website = _.website
        self.categories = _.categories

    def unsubscribe(self):
        return self.api.unsubscribe(self.feed_uri)

