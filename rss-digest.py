from optparse import OptionParser
from rssdigest.db import DB

db = DB()

def main():
    usage = """usage: %prog command

Commands:
    init
    update
    send
"""
    parser = OptionParser(usage)

    (options, args) = parser.parse_args()
    if len(args) != 1:
        parser.print_usage()
        return False

    command = args[0]
    commands = ['init', 'update', 'send']
    if command not in commands:
        parser.print_usage()
        return False

    if command == 'init':
        db.create_db()
    elif command == 'update':
        db.update()
    elif command == 'send':
        db.send()


if __name__ == "__main__":
    main()
