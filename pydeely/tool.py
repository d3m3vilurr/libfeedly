import sys
import os
from api import API
try:
    import cPickle as pickle
except ImportError:
    import pickle
try:
    import html2text
    def strip(html):
        return html2text.html2text(html)
except ImportError:
    def strip(html):
        return html

LOCAL = {}
api = API()

def auth():
    print 'Authorization'
    print 
    print '1. Make auth code'
    print '2. Generate Token File'
    print '3. Load Token'
    print '4. Refresh Token'
    print '0. Back'
    print
    v = input('> ')
    print
    if v == 1:
        print 'Open this URL on Internet browser'
        print api.make_auth_url()
        i = raw_input('End URI > ')
        LOCAL['code'] = api.split_auth_code(i)
        print 'CODE: %s' % LOCAL['code']
    elif v == 2:
        if not LOCAL.get('code'):
            LOCAL['code'] = raw_input('CODE> ')
        tokens = api.create_token(LOCAL['code'])
        with open('TOKEN', 'w') as w:
            w.write(pickle.dumps(tokens))
        api.auth_key = tokens['access_token']
        return 0
    elif v == 3:
        with open('TOKEN') as r:
            tokens = pickle.load(r)
            api.auth_key = tokens['access_token']
        return 0
    elif v == 4:
        refresh_token = None
        if not os.path.exists('TOKEN'):
            refresh_token = raw_input('REFRESH TOKEN> ')
        else:
            with open('TOKEN') as r:
                tokens = pickle.load(r)
                refresh_token = tokens['refresh_token']
        tokens = api.refresh_token(refresh_token)
        tokens['refresh_token'] = refresh_token
        api.auth_key = tokens['access_token']
        with open('TOKEN', 'w') as w:
            w.write(pickle.dumps(tokens))
        api.auth_key = tokens['access_token']
        return 0
    return v
    
def print_item(item):
    while True:
        print item.title
        print item.href
        print '=' * len(item.title)
        print strip(item.html)
        print '=' * 80
        print 'Author: %s' % item.author
        print 'Date: %s' % (item.published_date or item.crawled_date)
        print
        print item.unread and '1. Mark as read' or '1. Keep unread'
        print item.saved_for_later and '2. Unsave' or '2. Save'
        print '3. Next'
        print '4. Prev'
        print '0. Return stream list'
        print
        try:
            v = input('> ')
            if v == 1:
                if item.unread:
                    item.mark_as_read()
                else:
                    item.keep_unread()
            elif v == 2:
                item.saved_for_later = not item.saved_for_later
            elif v in [3, 4]:
                return v
            elif v == 0:
                return
        except Exception:
            continue

def print_items(items):
    while True:
        print "Stream list"
        print
        for i, item in enumerate(items):
            print '%d. %s' % (i + 1, item.title)
        print "0. back"
        print
        try:
            v = input('> ')
            if v == 0:
                return 0
            while True:
                _ = print_item(items[v - 1])
                if not _:
                    break
                if _ == 3:
                    v += 1
                if _ == 4:
                    v -= 1
                if v < 1 or v > 9:
                    break
        except Exception:
            return -1

def print_streams(stream):
    items = []
    for i, item in enumerate(stream.unread_items):
        items.append(item)
        if len(items) == 9:
            if print_items(items) == 0:
                return
            items = []
    if len(items):
        print_items(items)

def print_subscription(subscription):
    while True:
        print subscription.title
        print
        print '1. substream'
        print '2. mark as read'
        print '3. unsubscribe'
        print '0. back'
        print
        try:
            v = input('> ')
            if v == 0:
                return
            if v == 1:
                print_stream(subscription.stream)
            elif v == 2:
                api.all_mark_as_read([subscription.id])
            elif v == 3:
                api.unsubscribe(subscription.feed_uri)
                return 'removed'
        except Exception:
            pass

def print_subscriptions(label, subscriptions):
    while True:
        print "%s's subscriptions" % label
        print
        for i, subscription in enumerate(subscriptions):
            print "%3d. %s" % (i + 1, subscription.title)
        print "  0. back"
        print
        try:
            v = input('> ')
            if v == 0:
                return
            if v < 1 or v > len(subscriptions):
                continue
            if print_subscription(subscriptions[v - 1]) == 'removed':
                subscriptions.remove(subscriptions[v - 1])
        except Exception:
            pass

def print_category(label, data):
    while True:
        print label
        if data.get('id'):
            print "1. Category stream" 
        print "2. Subscription lists"
        print "3. Mark as read"
        print "0. back"
        print
        try:
            v = input('> ')
            if v == 0:
                return
            elif v == 1:
                if data.get('id'):
                    print_streams(api.category(label))
            elif v == 2:
                print_subscriptions(label, data['subscriptions'])
            elif v == 3:
                feed_ids = map(lambda x: x.id, data['subscriptions'])
                api.all_mark_as_read(feed_ids)
        except Exception:
            pass

def categories():
    categories = list(api.categories.iteritems())
    while True:
        print "Categories"
        print
        for i, (label, data) in enumerate(categories):
            print "%3d. %s" % (i + 1, label)
        print "  0. back"
        print
        try:
            v = input('> ')
            if v == 0:
                return
            if v < 1 or v > len(categories):
                continue
            print_category(*categories[v - 1])
        except Exception:
            pass

def new_subscribe():
    uri = raw_input('FEED URI >')
    categories = raw_input('CATEGORIES >')
    categories = filter(lambda x: x.strip(), categories.split(','))
    if raw_input("Add (type 'yes') >").lower() == 'yes':
        api.subscribe(uri, categories)

def menu():
    print 'Feedly terminal client'
    print 
    print '1. AUTH'
    if api.auth_key:
        print '2. ALL'
        print '3. SAVED FOR LATER'
        print '4. CATEGORIES'
        print '5. SUBSCRIBE'
    print '0. Quit'
    print
    try:
        v = input('> ')
        if v == 1:
            while True:
               if auth() == 0:
                   return
        elif v == 0:
            sys.exit(0)
        if api.auth_key:
            if v == 2:
                print_streams(api.all)
            elif v == 3:
                print_streams(api.saved)
            elif v == 4:
                categories()
            elif v == 5:
                new_subscribe()
    except Exception:
        pass

while True:
    menu()
