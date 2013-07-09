import pytest
import pydeely
from pydeely.stream import Stream
from travis_test_set import TEST_FEED, ACCOUNT_ID

TEST_TOKEN = None

@pytest.fixture
def api():
    global TEST_TOKEN
    if not TEST_TOKEN:
        with open('TEST_TOKEN') as r:
            TEST_TOKEN = r.read()
    api = pydeely.api.API()
    api.auth_key = TEST_TOKEN
    return api

def test_profile(api):
    assert api.profile
    assert api.profile['id'] == ACCOUNT_ID

def test_user_id(api):
    assert api.user_id == 'user/%s' % ACCOUNT_ID
    
def test_subscribe(api):
    subscription = api.subscribe(TEST_FEED['feed_uri'])
    assert subscription.id == TEST_FEED['feed_id']
    assert subscription.title == TEST_FEED['feed_title']
    assert subscription.website == TEST_FEED['site_uri']
    assert subscription.api == api

def test_update_feed_category(api):
    subscription = api.subscribe(TEST_FEED['feed_uri'], categories=['a', 'b'])
    assert len(subscription.categories) == 2
    assert subscription.categories[0]['label'] == 'a'
    assert subscription.categories[0]['id'] == \
           'user/%s/category/a' % ACCOUNT_ID 

def test_categories(api):
    categories = api.categories
    assert categories['a']
    assert len(filter(lambda x: x.id == TEST_FEED['feed_id'],
                      categories['a']['subscriptions']))
    
def test_stream_properties(api):
    assert isinstance(api.all, Stream)
    assert api.all.stream_id == 'user/%s/category/global.all' %  ACCOUNT_ID
    assert isinstance(api.saved, Stream)
    assert api.saved.stream_id == 'user/%s/tag/global.saved' %  ACCOUNT_ID

def test_unsubscribe(api):
    assert api.unsubscribe(TEST_FEED['feed_uri'])
