""":mod:`libfeedly.api`
~~~~~~~~~~~~~~~~~~~~~~~
"""
import requests
import time
try:
    import simplejson as json
except ImportError:
    import json
from .subscription import Subscription
from .stream import Stream
from .item import Item
from .utils import user_id, tag_id, category_id, feed_id, escape
from .compat import xmap

__all__ = 'API',


class API(object):
    """
    """

    def __init__(self, prefix="http://cloud.feedly.com", version="v3"):
        self._prefix = prefix
        self._version = version
        self._session = requests.Session()
        self._session.headers['content-type'] = 'application/json'

    def raw_get(self, *args, **kwds):
        return self._session.get(*args, **kwds)

    def _wrap_data(self, kwds):
        if not kwds.get('data'):
            return
        sess = self._session
        content_type = kwds['headers'].get('content-type') or \
                       kwds['headers'].get('Content-Type') or \
                       sess.headers.get('content-type')
        if content_type == 'application/json':
            kwds['data'] = json.dumps(kwds['data'])

    def raw_post(self, *args, **kwds):
        self._wrap_data(kwds)
        return self._session.post(*args, **kwds)

    def raw_put(self, *args, **kwds):
        self._wrap_data(kwds)
        return self._session.put(*args, **kwds)

    def raw_delete(self, *args, **kwds):
        return self._session.delete(*args, **kwds)

    def get(self, uri_path, headers=None, params=None):
        headers = headers or {}
        params = params or {}
        _append_ck(params)
        uri = '%s/%s/%s' % (self._prefix, self._version, uri_path)
        return self.raw_get(uri, headers=headers, params=params)

    def post(self, uri_path, headers=None, params=None, data=None):
        headers = headers or {}
        params = params or {}
        data = data or {}
        _append_ck(params)
        uri = '%s/%s/%s' % (self._prefix, self._version, uri_path)
        return self.raw_post(uri, headers=headers, params=params, data=data)

    def put(self, uri_path, headers=None, params=None, data=None):
        headers = headers or {}
        params = params or {}
        data = data or {}
        _append_ck(params)
        uri = '%s/%s/%s' % (self._prefix, self._version, uri_path)
        return self.raw_put(uri, headers=headers, params=params, data=data)

    def delete(self, uri_path, headers=None, params=None):
        headers = headers or {}
        params = params or {}
        _append_ck(params)
        uri = '%s/%s/%s' % (self._prefix, self._version, uri_path)
        return self.raw_delete(uri, headers=headers, params=params)

    def feed(self, uri):
        uri_path = 'feeds/%s' % feed_id(uri, escape=True)
        resp = self.get(uri_path)
        if resp.status_code != 200:
            raise APIError('Invalid input')
        return resp.json()


    def make_auth_url(self, client_id='feedly',
                      redirect_uri='https://cloud.feedly.com/feedly.html',
                      scope='https://cloud.feedly.com/subscriptions',
                      response_type='code', provider='google'):
        params = dict(client_id=client_id, redirect_uri=redirect_uri,
                      scope=scope, response_type=response_type, provider=provider,
                      migrate='false')
        resp = self.get('auth/auth', params=params)
        if resp.status_code != 200:
            raise APIError('Not authorization')
        return resp.url

    def create_token(self, code,
                     client_id='feedly',
                     client_secret='0XP4XQ07VVMDWBKUHTJM4WUQ',
                     grant_type='authorization_code',
                     redirect_uri='http://www.feedly.com/feedly.html'):
        """
        """
        data = dict(client_id=client_id, client_secret=client_secret,
                    grant_type=grant_type, redirect_uri=redirect_uri,
                    code=code)
        headers = {'content-type': 'application/x-www-form-urlencoded'}
        resp = self.post('auth/token', headers=headers, data=data)
        if resp.status_code != 200:
            raise APIError('Not authorization')
        json = resp.json()
        return dict(id=json['id'], access_token=json['access_token'],
                    refresh_token=json['refresh_token'],
                    expire=int(time.time() + json['expires_in']))

    def refresh_token(self, refresh_token,
                      client_id='feedly',
                      client_secret='0XP4XQ07VVMDWBKUHTJM4WUQ',
                      grant_type='refresh_token'):
        print("DEBUG: %s" % refresh_token)
        headers = {'content-type': 'application/x-www-form-urlencoded'}
        data = dict(client_id=client_id, client_secret=client_secret,
                    grant_type='refresh_token', refresh_token=refresh_token)
        resp = self.post('auth/token', headers=headers, data=data)
        if resp.status_code != 200:
            raise APIError('Not authorization')
        json = resp.json()
        return dict(id=json['id'], access_token=json['access_token'],
                    expire=int(time.time() + json['expires_in']))

    @property
    def auth_key(self):
        return (self._session.headers or {}).get('Authorization', 'Oauth ')[6:]

    @auth_key.setter
    def auth_key(self, key):
        if getattr(self, '_profile', None):
            del self._profile
        if not key:
            del self._session.headers['Authorization']
            return
        self._session.headers['Authorization'] = 'OAuth %s' % key
        self.profile

    @property
    def profile(self):
        if getattr(self, '_profile', None):
            return self._profile
        resp = self.get('profile')
        if resp.status_code != 200:
            raise APIError('Not authorization')
        self._profile = resp.json()
        return self._profile

    @property
    def user_id(self):
        return user_id(self.profile['id'])

    @property
    def subscriptions(self):
        resp = self.get('subscriptions')
        if resp.status_code != 200:
            raise APIError('Not authorization')
        for subscription in resp.json():
            yield Subscription(api=self, **subscription)

    @property
    def categories(self):
        categories = {'global.uncategorized': dict(subscriptions=[])}
        for subscription in self.subscriptions:
            if not len(subscription.categories):
                categories['global.uncategorized']['subscriptions'].append(subscription)
            for label in subscription.categories:
                category = categories[label] = categories.get(
                    label,
                    dict(id=category_id(self.user_id, label),
                         subscriptions=[])
                )
                category['subscriptions'].append(subscription)
        return categories

    def subscribe(self, uri, categories=None):
        info = self.feed(uri)
        categories = xmap(self._category, categories or [])
        data = dict(id=info['id'], title=info['title'], categories=categories)
        resp = self.post('subscriptions', data=data)
        if resp.status_code != 200:
            raise APIError('Not authorization')
        data['website'] = info['website']
        return Subscription(api=self, **data)

    def unsubscribe(self, uri):
        resp = self.delete('subscriptions/%s' % feed_id(uri, escape=True))
        if resp.status_code != 200:
            raise APIError('Not authorization')
        return True

    def contents(self, stream_id, count=20, unread_only=False,
                        ranked='newest', continuation=None):
        stream_id = stream_id.encode('utf-8')
        uri_path = 'streams/%s/contents' % escape(stream_id)
        count = int(count) or 20
        if count < 0:
            count = 20
        if not isinstance(unread_only, bool):
            unread_only = False
        unread_only = str(unread_only).lower()
        if ranked not in ['newest', 'oldest']:
            ranked = 'newest'
        params = dict(count=count, unreadOnly=unread_only, ranked=ranked)
        if continuation:
            params['continuation'] = continuation
        resp = self.get(uri_path, params=params)
        if resp.status_code != 200:
            raise APIError('Not authorization')
        resp = resp.json()
        items = (Item(api=self, **item) for item in resp.get('items', []))
        return items, resp.get('continuation')

    def category(self, category):
        return Stream(category_id(self.user_id, category), api=self)

    def tag(self, tag):
        return Stream(tag_id(self.user_id, tag), api=self)

    @property
    def all(self):
        return self.category('global.all')

    @property
    def saved(self):
        return self.tag('global.saved')

    def mark_as_read(self, entry_ids):
        if not len(entry_ids):
            # TODO: throw invalid item_id
            return
        data = dict(action='markAsRead', type='entries', entryIds=entry_ids)
        resp = self.post('markers', data=data)
        if resp.status_code != 200:
            raise APIError

    def keep_unread(self, entry_ids):
        if not len(entry_ids):
            # TODO: throw invalid item_id
            return
        data = dict(action='keepUnread', type='entries', entryIds=entry_ids)
        resp = self.post('markers', data=data)
        if resp.status_code != 200:
            raise APIError

    def all_mark_as_read(self, feed_ids, asOf=None):
        if not len(feed_ids):
            # TODO: throw invalid item_id
            return
        if not asOf:
            asOf = int(time.time()) * 1000
        data = dict(action='markAsRead', type='feeds', feedIds=feed_ids,
                    asOf=asOf)
        resp = self.post('markers', data=data)
        if resp.status_code != 200:
            raise APIError

    def tagging(self, tag, item_id):
        tag = tag.encode('utf-8')
        uri_path = 'tags/%s' % tag_id(self.user_id, tag, escape=True)
        resp = self.put(uri_path, data=dict(entryId=item_id))
        if resp.status_code != 200:
            raise APIError

    def untagging(self, tag, item_id):
        uri_path = 'tags/%s/%s' % (tag_id(self.user_id, tag, escape=True),
                                   escape(item_id))
        resp = self.delete(uri_path)
        if resp.status_code != 200:
            raise APIError

    def _category(self, label):
        return dict(id=category_id(self.user_id, label), label=label)

def _append_ck(params):
    if not params.get('ck'):
        params['ck'] = int(time.time())
