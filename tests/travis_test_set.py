import sys

ACCOUNT_ID = '7cbbedbc-36bb-4c04-957f-7de357cee9ed'

def version():
    if 'PyPy'in sys.version:
        return 'pypy'
    return '%d.%d' % sys.version_info[:2]

VERSION = version()

_REFRESH_TOKENS = {
    '2.6': 'AQAARgF7InUiOiIxMDc5MDE4Mjc5MTIw' \
           'MTEwNjE1MTYiLCJpIjoiN2NiYmVkYmMt' \
           'MzZiYi00YzA0LTk1N2YtN2RlMzU3Y2Vl' \
           'OWVkIiwicCI6MSwiYSI6ImZlZWRseSIs' \
           'InYiOiJwcm9kdWN0aW9uIiwibiI6ImVW' \
           'YjlnOTJmRDVhSEh1cDYifQ==',
    '2.7': 'AQAAafN7InUiOiIxMDc5MDE4Mjc5MTIw' \
           'MTEwNjE1MTYiLCJpIjoiN2NiYmVkYmMt' \
           'MzZiYi00YzA0LTk1N2YtN2RlMzU3Y2Vl' \
           'OWVkIiwibiI6ImVWYjlnOTJmRDVhSEh1' \
           'cDYiLCJ2IjoicHJvZHVjdGlvbiIsInAi' \
           'OjEsImEiOiJmZWVkbHkifQ==',
    'pypy': 'AQAAyft7ImkiOiI3Y2JiZWRiYy0zNmJi' \
            'LTRjMDQtOTU3Zi03ZGUzNTdjZWU5ZWQi' \
            'LCJ1IjoiMTA3OTAxODI3OTEyMDExMDYx' \
            'NTE2IiwibiI6ImVWYjlnOTJmRDVhSEh1' \
            'cDYiLCJwIjoxLCJhIjoiZmVlZGx5Iiwi' \
            'diI6InByb2R1Y3Rpb24ifQ=='
}

_TEST_FEED = {
    '2.6': dict(feed_uri='http://rss.slashdot.org/Slashdot/slashdotLinux',
                feed_title='Slashdot: Linux',
                site_uri='http://linux.slashdot.org/',
                feed_id='feed/http://rss.slashdot.org/Slashdot/slashdotLinux'),
    '2.7': dict(feed_uri='http://rss.slashdot.org/Slashdot/slashdotGames',
                feed_title='Slashdot: Games',
                site_uri='http://games.slashdot.org/',
                feed_id='feed/http://rss.slashdot.org/Slashdot/slashdotGames'),
    'pypy': dict(feed_uri='http://rss.slashdot.org/Slashdot/slashdotDevelopers',
                 feed_title='Slashdot: Developers',
                 site_uri='http://developers.slashdot.org/',
                 feed_id='feed/http://rss.slashdot.org/Slashdot/slashdotDevelopers')
}

REFRESH_TOKEN = _REFRESH_TOKENS[VERSION]
TEST_FEED = _TEST_FEED[VERSION]
