""":mod:`libfeedly.item`
~~~~~~~~~~~~~~~~~~~~~~~~

"""
from .utils import tag_id, dict_iter
from datetime import datetime
from html2text import html2text


class Item(object):

    def __init__(self, api, **kwds):
        self.api = api
        for k, v in dict_iter(kwds):
            self.__setattr__(k, v)
        self.tags = getattr(self, 'tags', [])
        self.summary = getattr(self, 'summary', dict(content=''))
        self.author = getattr(self, 'author', '')

    def mark_as_read(self):
        # TODO: send api
        if not self.unread:
            return
        self.api.mark_as_read([self.id])
        self.unread = False

    def keep_unread(self):
        # TODO: send api
        if self.unread:
            return
        self.api.keep_unread([self.id])
        self.unread = True

    def tagging(self, tag):
        tid = tag_id(self.api.user_id, tag)
        for t in self.tags:
            if t['id'] == tid:
                return
        self.api.tagging(tag, self.id)
        tag_info = dict(id=tid, label=tag)
        self.tags.append(tag_info)

    def untagging(self, tag):
        tid = tag_id(self.api.user_id, tag)
        for tag_info in filter(lambda x: x['id'] == tid, self.tags):
            if tag_info['label'] == tag:
                self.api.untagging(tag, self.id)
                self.tags.remove(tag_info)

    @property
    def saved_for_later(self):
        tid = tag_id(self.api.user_id, 'global.saved')
        for t in self.tags:
            if t['id'] == tid:
                return True
        return False

    @saved_for_later.setter
    def saved_for_later(self, boolean):
        tag = 'global.saved'
        if boolean:
            return self.tagging(tag)
        return self.untagging(tag)

    @property
    def published_date(self):
        if not getattr(self, 'published', None):
            return
        return datetime.fromtimestamp(self.published / 1000)


    @property
    def crawled_date(self):
        if not getattr(self, 'crawled', None):
            return
        return datetime.fromtimestamp(self.crawled / 1000)

    @property
    def href(self):
        alternate = getattr(self, 'alternate', [])
        if len(alternate):
            return alternate[0]['href']
        return getattr(self, 'originId', None)

    @property
    def html(self):
        content = getattr(self, 'content', None) or \
                  getattr(self, 'summary', None) or dict(content='')
        return content['content']

    @property
    def text(self):
        return html2text(self.html)
