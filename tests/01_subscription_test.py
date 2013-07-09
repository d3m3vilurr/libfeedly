import pytest
import pydeely
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

def test_subscribe(api):
    subscription = api.subscribe(TEST_FEED['feed_uri'])
    assert subscription.id == TEST_FEED['feed_id']
    assert subscription.title == TEST_FEED['feed_title']
    assert subscription.website == TEST_FEED['site_uri']
    assert subscription.api == api

def test_category(api):
    subscription = api.subscribe(TEST_FEED['feed_uri'], categories=['a', 'b'])
    assert len(subscription.categories) == 2
    assert subscription.categories[0]['label'] == 'a'
    assert subscription.categories[0]['id'] == \
           'user/%s/category/a' % ACCOUNT_ID 

def test_unsubscribe(api):
    assert api.unsubscribe(TEST_FEED['feed_uri'])

