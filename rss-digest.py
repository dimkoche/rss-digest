from optparse import OptionParser
from rssdigest.db import DB
from rssdigest.mailer import Mailer
from cfg import db_path, mailgun

db = DB(db_path)
mailer = Mailer(mailgun, db)


def main():
    usage = """usage: %prog command

Commands:
    init
    update
    send
"""
    parser = OptionParser(usage)

    (_, args) = parser.parse_args()
    if len(args) != 1:
        parser.print_usage()
        return False

    command = args[0]
    commands = ['init', 'update', 'show', 'send']
    if command not in commands:
        parser.print_usage()
        return False

    if command == 'init':
        db.create_db()
    elif command == 'update':
        db.update()
    elif command == 'show':
        mailer.show()
    elif command == 'send':
        mailer.send()


if __name__ == "__main__":
    main()
