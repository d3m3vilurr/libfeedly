import os
import pytest
import json
import time
import datetime
import requests
import libfeedly.api
from libfeedly.utils import *
from libfeedly.compat import urlparse, quote_plus, xlist, dict_iter
from libfeedly.subscription import Subscription
from libfeedly.stream import Stream


SAMPLE_PATH = os.path.dirname(__file__) + '/samples'
URL_PREFIX = 'http://cloud.feedly.com/v3'


class MocKRequestSession(requests.Session):

    def __init__(self):
        super(MocKRequestSession, self).__init__()
        self.history = []

    def get(self, *args, **kwds):
        self.history.append(('GET', args[0], kwds))
        return StubResp('GET', args[0])

    def post(self, *args, **kwds):
        self.history.append(('POST', args[0], kwds))
        return StubResp('POST', args[0])

    def put(self, *args, **kwds):
        self.history.append(('PUT', args[0], kwds))
        return StubResp('PUT', args[0])

    def delete(self, *args, **kwds):
        self.history.append(('DELETE', args[0], kwds))
        return StubResp('DELETE', args[0])


class StubResp(object):

    def __init__(self, method, url):
        self.status_code = 200
        self.data = None
        self.url = None
        # /v3/{api_type}/....
        path = urlparse(url).path
        paths = path.split('/')
        if paths[-1] == 'contents':
            api_type = 'contents'
        else:
            api_type = paths[2]
        with open('%s/%s_%s' % (SAMPLE_PATH, method, api_type)) as f:
            try:
                self.data = json.load(f)
            except ValueError:
                pass

    def json(self):
        return self.data


@pytest.fixture
def api():
    api = libfeedly.api.API()
    api._session = MocKRequestSession()
    api.history = api._session.history
    return api

def test_make_auth_url(api):
    api.make_auth_url()
    expect = 'GET', URL_PREFIX + '/auth/auth'
    assert api.history[0][:2] == expect

def test_create_token(api):
    # If use real API, this testcase broken
    # else If use mock version API, api may cause :exc:`KeyError`
    code = 'TEST_CODE'
    try:
        api.create_token(code)
    except KeyError:
        pass
    expect = 'POST', URL_PREFIX + '/auth/token'
    assert api.history[0][:2] == expect
    assert (api.history[0][2]['headers']['content-type'] ==
            'application/x-www-form-urlencoded')
    data = api.history[0][2]['data']
    assert data['grant_type'] == 'authorization_code'
    assert data['redirect_uri'] == 'http://www.feedly.com/feedly.html'
    assert data['code'] == code

def test_refresh_token(api):
    refresh_token = 'AQAARgF7InUiOiIxMDc5MDE4Mjc5MTIw' \
                    'MTEwNjE1MTYiLCJpIjoiN2NiYmVkYmMt' \
                    'MzZiYi00YzA0LTk1N2YtN2RlMzU3Y2Vl' \
                    'OWVkIiwicCI6MSwiYSI6ImZlZWRseSIs' \
                    'InYiOiJwcm9kdWN0aW9uIiwibiI6ImVW' \
                    'YjlnOTJmRDVhSEh1cDYifQ=='
    token_info = api.refresh_token(refresh_token)
    expect = 'POST', URL_PREFIX + '/auth/token'
    assert api.history[0][:2] == expect
    assert (api.history[0][2]['headers']['content-type'] ==
            'application/x-www-form-urlencoded')
    #assert token_info['id'] == '7cbbedbc-36bb-4c04-957f-7de357cee9ed'
    #assert token_info['access_token']
    #assert token_info['expire'] > time.time()

def test_profile(api):
    assert api.profile
    assert api.history[0][:2] == ('GET', URL_PREFIX + '/profile')
    assert api.user_id == 'user/7cbbedbc-36bb-4c04-957f-7de357cee9ed'

def test_feed(api):
    rss_url = 'http://news.ycombinator.com/rss'
    feed_info = api.feed(rss_url)
    escaped_id = feed_id(rss_url, escape=True)
    expect = 'GET', URL_PREFIX + '/feeds/%s' % escaped_id
    assert api.history[0][:2] == expect
    expect_feed_info = dict(id=feed_id(rss_url),
                            title='Hacker News',
                            website='https://news.ycombinator.com/')
    header = api.history[0][2]
    for k, v in dict_iter(expect_feed_info):
        assert feed_info[k] == v

def test_subscribe(api):
    rss_url = 'http://news.ycombinator.com/rss'
    escaped_id = feed_id(rss_url, escape=True)
    subscription = api.subscribe(rss_url)
    expects = (
        ('GET', URL_PREFIX + '/feeds/%s' % escaped_id),
        ('POST', URL_PREFIX + '/subscriptions'),
    )
    for idx, history in enumerate(api.history):
        assert history[:2] == expects[idx]
    header = api.history[-1][2]
    expect_feed_info = dict(id=feed_id(rss_url),
                            title='Hacker News',
                            website='https://news.ycombinator.com/')
    assert header["data"]["id"] == expect_feed_info["id"]
    categories = header["data"]["categories"]
    categories = xlist(categories)
    assert categories == []
    assert header["data"]["title"] == expect_feed_info["title"]
    assert isinstance(subscription, Subscription)
    assert subscription.id == expect_feed_info["id"]
    assert subscription.title == expect_feed_info["title"]
    assert subscription.website == expect_feed_info["website"]

def test_unsubscribe(api):
    rss_url = 'http://news.ycombinator.com/rss'
    escaped_id = feed_id(rss_url, escape=True)
    api.unsubscribe(rss_url)
    expect = 'DELETE', URL_PREFIX + '/subscriptions/' + escaped_id
    assert api.history[-1][:2] == expect

def test_update_feed_category(api):
    rss_url = 'http://news.ycombinator.com/rss'
    subscription = api.subscribe(rss_url, categories=['test'])
    expect_header_categories = [
        dict(id=category_id(api.user_id, 'test'), label='test')
    ]
    categories = api.history[-1][2]["data"]["categories"]
    categories = xlist(categories)
    assert categories == expect_header_categories
    

def test_subscriptions(api):
    subscriptions = list(api.subscriptions)
    assert len(subscriptions)
    assert api.history[0][:2] == ('GET', URL_PREFIX + '/subscriptions')

def test_categories(api):
    categories = api.categories
    assert categories
    assert sorted(categories.keys()) == ['global.uncategorized', 'test']
    assert not len(categories['global.uncategorized']['subscriptions'])
    assert len(categories['test']['subscriptions'])

def test_contents(api):
    fid = feed_id('http://news.ycombinator.com/rss')
    escaped_id = feed_id('http://news.ycombinator.com/rss', escape=True)
    items, continuation = api.contents(fid)
    expect = ('GET', URL_PREFIX + '/streams/%s/contents' % escaped_id)
    assert api.history[0][:2] == expect
    assert items

def test_category(api):
    stream = api.category('test')
    escaped_id = category_id(api.user_id, 'test', escape=True)
    assert isinstance(stream, Stream)
    item = stream.items[0]
    expects = (
        ('GET', URL_PREFIX + '/profile'),
        ('GET', URL_PREFIX + '/stream/%s/contents' % escaped_id)
    )
    for idx, history in enumerate(api.history):
        history[:2] == expects[idx]

@pytest.fixture
def stream(api):
    return api.all

def test_stream(stream):
    item = stream.items[0]
    escaped_id = category_id(item.api.user_id, 'global.all', escape=True)
    expect = 'GET', URL_PREFIX + '/streams/%s/contents' % escaped_id
    assert item.api.history[-1][:2] == expect
    params = item.api.history[-1][2]["params"]
    assert params['ranked'] == 'newest'
    assert params['unreadOnly'] == 'false'
    item = stream.unread_items[0]
    params = item.api.history[-1][2]["params"]
    assert params['ranked'] == 'newest'
    assert params['unreadOnly'] == 'true'
    

def test_saved_feed(api):
    items = api.saved.items
    assert items
    item = items[0]
    escaped_id = tag_id(api.user_id, 'global.saved', escape=True)
    expect = 'GET', URL_PREFIX + '/streams/%s/contents' % escaped_id
    assert api.history[-1][:2] == expect

def test_items(stream):
    assert stream.items[0]
    assert len(list(stream.items))
    assert len(stream.items[:3]) == 3

@pytest.fixture
def item(stream):
    return stream.items[0]

def test_mark_as_read(item):
    assert item.unread
    item.mark_as_read()
    expect = 'POST', URL_PREFIX + '/markers'
    history = item.api.history[-1]
    assert history[:2] == expect
    assert history[2]["data"]["action"] == 'markAsRead'
    assert history[2]["data"]["type"] == 'entries'
    assert history[2]["data"]["entryIds"] == [item.id]
    assert not item.unread
    item.keep_unread()
    expect = 'POST', URL_PREFIX + '/markers'
    history = item.api.history[-1]
    assert history[:2] == expect
    assert history[2]["data"]["action"] == 'keepUnread'
    assert history[2]["data"]["type"] == 'entries'
    assert history[2]["data"]["entryIds"] == [item.id]
    assert item.unread

def test_all_mark_as_read(api):
    fid = feed_id('http://news.ycombinator.com/rss')
    api.all_mark_as_read([fid])
    expect = 'POST', URL_PREFIX + '/markers'
    api.history[-1][:2] == expect
    post_data = api.history[-1][2]["data"]
    assert post_data["action"] == 'markAsRead'
    assert post_data["type"] == 'feeds'
    assert post_data["feedIds"] == [fid]
    assert post_data["asOf"] < time.time() * 1000

def test_tagging(item):
    item.tagging('hn')
    tid = tag_id(item.api.user_id, 'hn')
    escaped_id = tag_id(item.api.user_id, 'hn', escape=True)
    expect = 'PUT', URL_PREFIX + '/tags/' + escaped_id
    assert item.api.history[-1][:2] == expect
    except_tag_info = dict(id=tid, label='hn')
    assert item.tags == [except_tag_info]
    item.untagging('hn')
    expect = ('DELETE',
              URL_PREFIX + '/tags/' + escaped_id + '/' + quote_plus(item.id))
    assert item.api.history[-1][:2] == expect
    assert item.tags == []

def test_item(item):
    date = item.published_date or item.crawled_date
    assert date
    assert isinstance(date, datetime.datetime) 

def test_item_save(item):
    assert not item.saved_for_later
    item.saved_for_later = True
    tid = tag_id(item.api.user_id, 'global.saved')
    assert item.tags == [dict(id=tid, label='global.saved')]
    item.saved_for_later = False
    assert item.tags == []
    assert item.href and item.html and item.text

@pytest.fixture
def subscription(api):
    rss_url = 'http://news.ycombinator.com/rss'
    return api.subscribe(rss_url, categories=['test'])

def test_subscription(subscription):
    assert subscription.feed_uri == 'http://news.ycombinator.com/rss'
    assert isinstance(subscription.stream, Stream)
    subscription.unsubscribe()
    escaped_id = feed_id(subscription.feed_uri, escape=True)
    expect = 'DELETE', URL_PREFIX + '/subscriptions/' + escaped_id
    assert subscription.api.history[-1][:2] == expect

def test_new_subscription(api):
    subscription = Subscription(api,
                                feed_id('http://news.ycombinator.com/rss'))
    subscription.subscribe()

def test_subscription_mark_as_read(subscription):
    subscription.mark_as_read()
    expect = 'POST', URL_PREFIX + '/markers'
    subscription.api.history[-1][:2] == expect
    post_data = subscription.api.history[-1][2]["data"]
    assert post_data["action"] == 'markAsRead'
    assert post_data["type"] == 'feeds'
    assert post_data["feedIds"] == [subscription.id]
    assert post_data["asOf"] < time.time() * 1000
