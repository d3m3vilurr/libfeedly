import pytest
import os

def test_cleanup():
    os.path.exists('TEST_TOKEN') and os.remove('TEST_TOKEN')
