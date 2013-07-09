""":mod:`pydeely.tool`
~~~~~~~~~~~~~~~~~~~~~
"""
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

api = API()

def print_menu(title, menus, is_main=False):
    print
    if title:
        print title
        print
    for i, text in enumerate(menus):
        print '%3d. %s' % (i + 1, text)
    print
    if is_main:
        print '  0. Exit'
    else:
        print '  0. Back'
    print

def auth():
    menu = ['Generate Token', 'Load Token', 'Refresh Token']
    while True:
        print_menu('Authrization', menu)
        v = raw_input('> ')
        try:
            v = int(v):
        except ValueError:
            continue
        if not v:
            return 0
        if v == 1:
            print 'Open this URL on Internet browser'
            print api.make_auth_url()
            i = raw_input('Enter End URI> ')
            code = api.split_auth_code(i)
            tokens = api.create_token(code)
            with open('TOKEN', 'w') as w:
                w.write(pickle.dumps(tokens))
            api.auth_key = tokens['access_token']
            return 0
        elif v == 2:
            with open('TOKEN') as r:
                tokens = pickle.load(r)
                api.auth_key = tokens['access_token']
            return 0
        elif v == 3:
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
        return

def _print_item(item):
    print item.title
    print '    URL: %s' % item.href
    print '    Author: %s' % item.author
    print '    Date: %s' % (item.published_date or item.crawled_date)
    print '=' * len(item.title)
    print strip(item.html)

def print_item(item):
    while True:
        _print_item(item)
        print_menu(None, [item.unread and 'Mark as read' or 'Keep unread',
                          item.saved_for_later and 'Unsave' or 'Save',
                          'Next', 'Prev'])
        v = raw_input('> ')
        try:
            v = int(v):
        except ValueError:
            continue
        if not v:
            return
        if v == 1:
            if item.unread:
                item.mark_as_read()
            else:
                item.keep_unread()
        elif v == 2:
            item.saved_for_later = not item.saved_for_later
        elif v == 3:
            return 'next'
        elif v == 4:
            return 'prev'

def print_items(title, items):
    item_titles = map(lambda x: x.title, items)
    while True:
        print_menu(title, item_titles)
        v = raw_input('> ')
        try:
            v = int(v):
        except ValueError:
            continue
        if not v:
            return 0
        while True:
            if v < 1 or v > 9:
                break
            cont = print_item(items[v - 1])
            if not cont:
                break
            if cont == 'next':
                v += 1
            if cont == 'prev':
                v -= 1

def print_streams(title, stream):
    items = []
    for i, item in enumerate(stream.unread_items):
        items.append(item)
        if len(items) == 9:
            if print_items(items) == 0:
                return
            items = []
    if len(items):
        print_items(title, items)

def print_subscription(subscription):
    menus = ['Stream', 'Mark as read', 'Unsubscribe']
    while True:
        print_menu(subscription.title, menus)
        v = raw_input('> ')
        try:
            v = int(v):
        except ValueError:
            continue
        if not v:
            return
        if v == 1:
            print_streams(subscription.title, subscription.stream)
        elif v == 2:
            api.all_mark_as_read([subscription.id])
        elif v == 3:
            api.unsubscribe(subscription.feed_uri)
            return 'removed'

def print_subscriptions(label, subscriptions):
    title = "%s's feeds" % label
    while True:
        print_menu(title, (s.title for x in subscriptions))
        v = raw_input('> ')
        try:
            v = int(v):
        except ValueError:
            continue
        if not v:
            return
        if v < 1 or v > len(subscriptions):
            continue
        if print_subscription(subscriptions[v - 1]) == 'removed':
            subscriptions.remove(subscriptions[v - 1])

def print_category(label, data):
    menus = ['Stream', 'Detail feeds', 'Mark as read']
    while True:
        print_menu(label, menus)
        v = raw_input('> ')
        try:
            v = int(v):
        except ValueError:
            continue
        if not v:
            return
        elif v == 1:
            if data.get('id'):
                print_streams(label, api.category(label))
            else:
                print 'This category not provide stream'
        elif v == 2:
            print_subscriptions(label, data['subscriptions'])
        elif v == 3:
            feed_ids = map(lambda x: x.id, data['subscriptions'])
            api.all_mark_as_read(feed_ids)

def print_categories():
    categories = list(api.categories.iteritems())
    category_names = map(lambda (x, y): x, categories)
    while True:
        print_menu('Categories', category_names)
        v = raw_input('> ')
        try:
            v = int(v):
        except ValueError:
            continue
        if not v:
            return
        if v < 1 or v > len(categories):
            continue
        print_category(*categories[v - 1])

def new_subscribe():
    uri = raw_input('FEED URI> ')
    categories = raw_input('CATEGORIES> ')
    categories = filter(lambda x: x.strip(), categories.split(','))
    if raw_input("Add (type 'yes')> ").lower() == 'yes':
        api.subscribe(uri, categories)

def main_menu():
    menus = ['Auth', 'All unread items', 'Saved for later',
             'Categories', 'Add new feed']
    while True:
        print_menu('Feedly terminal client',
                   api.auth_key and menus or menus[:1],
                   is_main=True)
        v = raw_input('> ')
        if v == '0':
            sys.exit(0)
        if v == '1':
           auth()
        elif api.auth_key:
            if v == '2':
                print_streams('All unread items', api.all)
            elif v == '3':
                print_streams('Saved for later', api.saved)
            elif v == '4':
                print_categories()
            elif v == '5':
                new_subscribe()

if __name__ == '__main__':
    main_menu()
