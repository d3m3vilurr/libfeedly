# -*- coding: utf-8 -*-
import pytest
import pydeely
import pydeely.util as util

def test_user_id():
    assert util.user_id('00000000-0000-0000-0000-000000000000') \
           == 'user/00000000-0000-0000-0000-000000000000'

def test_feed_id():
    assert util.feed_id('http://some/rss') == 'feed/http://some/rss'
    assert util.feed_id('http://some/rss', escape=True) \
           == 'feed%2Fhttp%3A%2F%2Fsome%2Frss'

def test_category_id():
    assert util.category_id('user/abc', 'a') == 'user/abc/category/a'
    assert util.category_id('user/abc', u'가나다') \
           == u'user/abc/category/가나다'
    assert util.category_id('user/abc', u'가나다', escape=True) \
           == 'user%2Fabc%2Fcategory%2F%EA%B0%80%EB%82%98%EB%8B%A4'

def test_tag_id():
    assert util.tag_id('user/abc', 'a') == 'user/abc/tag/a'
    assert util.tag_id('user/abc', u'가나다') \
           == u'user/abc/tag/가나다'
    assert util.tag_id('user/abc', u'가나다', escape=True) \
           == 'user%2Fabc%2Ftag%2F%EA%B0%80%EB%82%98%EB%8B%A4'

def test_parse_oauth_code():
    assert util.parse_oauth_code('http://some/?code=abcde&scope=') == 'abcde'
    assert util.parse_oauth_code('http://some/?code=abc%20de&scope=') \
           == 'abc%20de'
    assert util.parse_oauth_code('http://some/?code=abc+de&scope=') \
           == 'abc+de'
    assert util.parse_oauth_code('http://some/?scope=&code=abcde') \
           == 'abcde'
    assert util.parse_oauth_code('http://some/?code=abcde') \
           == 'abcde'
    assert util.parse_oauth_code('http://some/?code=abcde&s1=1&s2=2') \
           == 'abcde'
    assert not util.parse_oauth_code('http://some/')
