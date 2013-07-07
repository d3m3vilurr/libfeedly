""":mod:`pydeely.util`
~~~~~~~~~~~~~~~~~~~~~
"""
class APIError(IOError):
    pass


def user_id(uid):
    return 'user/%s' % uid

def feed_id(uri):
    return 'feed/%s' % uri

def category_id(user_id, label):
    return '%s/category/%s' % (user_id, label)

def tag_id(user_id, tag):
    return '%s/tag/%s' % (user_id, tag)

