import pytest
import pydeely

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
    subscription = api.subscribe('https://news.ycombinator.com/rss')    
    assert subscription.id == 'feed/https://news.ycombinator.com/rss'
    assert subscription.title == 'Hacker News'
    assert subscription.website == 'https://news.ycombinator.com/'
    assert subscription.api == api
    assert len(list(api.subscriptions)) == 1

def test_category(api):
    api.subscribe('https://news.ycombinator.com/rss', categories=['a', 'b'])
    subscription = api.subscriptions.next()
    assert len(subscription.categories) == 2
    assert subscription.categories[0]['label'] == 'a'
    assert subscription.categories[0]['id'] == \
           'user/7cbbedbc-36bb-4c04-957f-7de357cee9ed/category/a'

def test_unsubscribe(api):
    assert api.unsubscribe('https://news.ycombinator.com/rss')

