import urllib.request as urllib2
import feedparser
import signal
import pystache
import os
import sqlite3
import datetime

db_path = 'db.sqlite'
timeout = 5

def get_http_response(url):
    req = urllib2.Request(url)
    try:
        signal.alarm(timeout)
        response = urllib2.urlopen(req)
        signal.alarm(0)
    except Exception as exc:
        print(exc)
        return False
    return response


class DB:
    db = None

    def __init__(self):
        self.db = sqlite3.connect(db_path)
        self.db.row_factory = sqlite3.Row

    def get_connection(self):
        return self.db.cursor()

    def create_db(self):
        #if os.path.exists(db_path):
        #    exit('DB file already exists: %s' % os.path.abspath(db_path))

        c = self.get_connection()
        c.executescript("""
            create table source(
                id integer primary key,
                url text
            );

            create table item(
                id integer primary key,
                source_id integer,
                url text,
                title text,
                sent_date text
            );

            insert into source(url)
            values
            ("http://avva.livejournal.com/data/rss"),
            ("http://grosslarnakh.livejournal.com/data/rss"),
            ("http://anykeen.net/rss");
            """)
        c.close()

    def send(self):
        template = '''
          {{greeting}}
          <ul>
          {{#sources}}
              <li><b><a href={{url}}>{{title}}</a></b></li>
              <ul>
              {{#items}}
                <li><a href={{url}}>{{title}}</a></li>
              {{/items}}
              </ul>
          {{/sources}}
          </ul>
           Created by {{information.product}}
        '''

        context = {
            'greeting': 'Digest #%s' % datetime.datetime.now(),
            'information': {
                'product': 'RSS-Digest'
            },
            'sources': self.get_items()
        }

        print(pystache.render(template, context))

    def update(self):
        sources = self.get_sources()
        if not sources:
            print("There is not sources for update")
            return False

        for source in sources:
            self.update_source(source)

    def get_sources(self):
        c = self.get_connection()
        c.execute('SELECT id, url FROM source')
        res = c.fetchall()
        c.close()
        return res

    def get_items(self):
        sql = '''
            select
                s.url as s_title, s.url as s_url, i.source_id, i.url, i.title
            from item i
            join source s on i.source_id=s.id
            where i.sent_date is null
            order by i.source_id'''
        c = self.get_connection()
        c.execute(sql)

        source_id = 0
        items = []
        res = []
        last_item = None
        for item in c:
            if item['source_id'] != source_id and source_id != 0:
                res.append({'title': last_item['s_title'], 'url': last_item['s_url'], 'items': items})
                items = []

            items.append({'title': item['title'], 'url': item['url']})

            source_id = item['source_id']
            last_item = item

        res.append({'title': last_item['s_title'], 'url': last_item['s_url'], 'items': items})
        c.close()
        return res


    def update_source(self, source):
        print('Updating:', source['url'])

        response = get_http_response(source[1])
        if not response:
            return False

        res = feedparser.parse(response)
        if res.bozo:
            return False

        for item in res['entries'][0:100]:
            try:
                self.handle_feed_item(item, source)
            except Exception as e:
                raise e
                break
        return False

    def handle_feed_item(self, item, source):
        url = item.link

        title = 'No title'
        if 'title' in item.keys():
            title = item.title

        existed_item = self.get_item_by_url(url)
        if not existed_item:
            item_id = self.insert_item(url, title, source[0])
            print(url, source['id'], '===>', item_id)
        else:
            print(url, source['id'], '===> Already exists')
            return False

    def insert_item(self, url, title, source_id):
        c = self.get_connection()
        c.execute("INSERT INTO item(url, title, source_id) VALUES (?, ?, ?)", (url, title, source_id))
        item_id = c.lastrowid
        self.db.commit()
        c.close()
        return item_id

    def get_item_by_url(self, url):
        c = self.get_connection()
        c.execute('''SELECT url,title,source_id,sent_date FROM item WHERE url = ?''', (url,))
        item = c.fetchone()
        c.close()
        return item
