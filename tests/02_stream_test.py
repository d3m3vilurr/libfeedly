import pytest
import pydeely

SUBSCRIPTION = None

@pytest.fixture
def subscription():
    global SUBSCRIPTION
    if not SUBSCRIPTION:
        with open('TEST_TOKEN') as r:
            TEST_TOKEN = r.read()
            api = pydeely.api.API()
            api.auth_key = TEST_TOKEN
            SUBSCRIPTION = api.subscribe('https://news.ycombinator.com/rss')
    return SUBSCRIPTION

def test_stream(subscription):
    items, cont = subscription.api.contents(subscription.id, count=2) 
    items_0 = list(items)
    assert len(items_0) == 2
    assert cont
    items, cont = subscription.api.contents(subscription.id, count=2,
                                            continuation=cont) 
    items_1 = list(items)
    assert items_0[0].id != items_1[0].id

def test_mark_as_read(subscription):
    item = subscription.stream.unread_items.next()
    assert item.unread
    item.mark_as_read()
    item2 = subscription.stream.unread_items.next()
    assert item2.unread
    assert item.id != item2.id

def test_keep_unread(subscription):
    item = subscription.stream.items.next()
    assert not item.unread
    item.keep_unread()
    item = subscription.stream.items.next()
    assert item.unread
    
def test_save(subscription):
    item = subscription.stream.items.next()
    item.saved_for_later = False
    assert not item.saved_for_later
    item.saved_for_later = True
    item = subscription.stream.items.next()
    assert len(item.tags)
    assert item.saved_for_later
    item.saved_for_later = False
    item = subscription.stream.items.next()
    assert not item.saved_for_later

def test_global_stream(subscription):
    item = subscription.api.all.items.next()
    assert item
    item.saved_for_later = True
    assert len(list(subscription.api.saved.items))
    for item in subscription.api.saved.items:
        item.saved_for_later = False

def test_all_mark_as_read(subscription):
    subscription.api.all_mark_as_read([subscription.id])
    assert not len(list(subscription.stream.unread_items))
    
def test_teardown(subscription):
    subscription.unsubscribe()
