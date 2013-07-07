import pytest
import pydeely
import time

ACCOUNT_ID = '7cbbedbc-36bb-4c04-957f-7de357cee9ed'
REFRESH_TOKEN = 'AQAARgF7InUiOiIxMDc5MDE4Mjc5MTIw' \
                'MTEwNjE1MTYiLCJpIjoiN2NiYmVkYmMt' \
                'MzZiYi00YzA0LTk1N2YtN2RlMzU3Y2Vl' \
                'OWVkIiwicCI6MSwiYSI6ImZlZWRseSIs' \
                'InYiOiJwcm9kdWN0aW9uIiwibiI6ImVW' \
                'YjlnOTJmRDVhSEh1cDYifQ=='

# TODO: test create token

def test_refresh_token():
    api = pydeely.api.API()
    token_info = api.refresh_token(REFRESH_TOKEN)
    assert token_info['id'] == ACCOUNT_ID
    assert token_info['access_token']
    assert token_info['expire'] > time.time()
    with open('TEST_TOKEN', 'w') as w:
        w.write(token_info['access_token'])
