import datetime
import requests
import pystache


class Mailer:
    db = None
    cfg = None

    def __init__(self, cfg, db):
        self.cfg = cfg
        self.db = db

    def show(self):
        print(self.get_email_text())

    def send(self):
        txt = self.get_email_text()
        print(self.send_mailgun_message(self.cfg['to_email'], 'Hello', txt))

    def send_mailgun_message(self, to, subj, txt):
        return requests.post(
            "https://api.mailgun.net/v2/%s/messages" % self.cfg['domain'],
            auth=("api", self.cfg['api_key']),
            data={"from": self.cfg['from_email'],
                  "to": to,
                  "subject": subj,
                  "html": txt})

    def get_email_text(self):
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
            'sources': self.db.get_items()
        }

        return pystache.render(template, context)
