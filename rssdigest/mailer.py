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
          <style type="text/css">
            * {font-family: Helvetica; padding: 0px; margin: 0px;}
            body {
                -webkit-font-smoothing: antialiased;
                -webkit-text-size-adjust: none;
                width: 100%!important;
                height: 100%;
                background-color: #f6f6f6;
            }
            h1 {padding-left: 7px; margin: 15px 0px 5px 0px;}
            ul {padding-left: 5px;}
            li {
                margin: 4px 5px 1px 5px;
                list-style-position: inside;
            }
            ul ul {
                margin-left: 10px;
            }

            li.source a:link {
                color: #000;
                text-decoration: none;
            }
            li.source a:visited {
                color: #000;
            }
            li.source a:hover {
                color: #000;
            }

            li.item a:link {
                color: #337ab7;
                text-decoration: none;
                border-bottom: 1px solid #337ab7;
            }
            li.item a:visited {
                color: #607;
                border-bottom: 1px solid #607;
            }
            li.item a:visited:hover {
                color: #000;
                border-bottom-color: #ed7e88;
            }
            li.item a:hover {
                color: #000;
                border-bottom-color: #ed7e88;
            }

            .source {
                margin-top: 10px;
            }
            #main {
                width:600px;
                margin: 10px auto;
                border: 1px solid;
                background-color: #ffffff;
                padding: 3px 10px 20px 10px;
            }
            #footer {
                width:600px;
                margin:0 auto;
                padding: 5px 0px 5px 0px;
                text-align: right;
                color: grey;
            }
          </style>

          <body>
              <div id="main">
                  <h1>{{greeting}}</h1>
                  <ul class="sources">
                  {{#sources}}
                      <li class="source">
                        <b><a href={{site_url}}>{{title}}</a></b>
                      </li>
                      <ul class="items">
                      {{#items}}
                        <li class="item"><a href={{url}}>{{title}}</a></li>
                      {{/items}}
                      </ul>
                  {{/sources}}
                  </ul>
              </div>
              <div id="footer">
                  <p>Created by {{information.product}}</p>
              </div>
          </body>
        '''

        context = {
            'greeting': 'Digest #%s' % datetime.datetime.now(),
            'information': {
                'product': 'RSS-Digest'
            },
            'sources': self.db.get_items()
        }

        return pystache.render(template, context)
