import pytest
import pydeely
import time
from travis_test_set import REFRESH_TOKEN, ACCOUNT_ID

# TODO: test create token

def test_refresh_token():
    api = pydeely.api.API()
    token_info = api.refresh_token(REFRESH_TOKEN)
    assert token_info['id'] == ACCOUNT_ID
    assert token_info['access_token']
    assert token_info['expire'] > time.time()
    with open('TEST_TOKEN', 'w') as w:
        w.write(token_info['access_token'])
