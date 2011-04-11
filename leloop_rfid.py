#!/usr/bin/env python2.6
import sys, os
import logging
from sqlite3 import *

### RESTful service routing
from optparse import OptionParser
from bottle import route, run, debug

### IRC
from ircbot import Bot

CHANNEL='#leloop-test'

def irc_connect(nick, channels):
    bot = Bot(nick=nick, channels=channels)

    def bye(m, origin, args, text, bot=bot):
        if origin.nick in ['guyzmo', 'ToMPouce']:
            bot.todo(['QUIT'], 'FOAD!')
        else:
            bot.msg(origin.nick, 'Who are you to talk to me like that ?')
    bot.rule(bye, 'bye', r''+nick+'.*casse-toi.*')
    
    return bot

import threading
def irc_spawn(bot, host, port):
    class MyThread ( threading.Thread ):
        def run (self):
            bot.run(host, port)
    MyThread().start()


class MembersDB:
    _schema = '''
CREATE TABLE member (
    id INTEGER primary key,
    uid TEXT,
    nickname TEXT
);
'''

    def __init__(self, db_name):
        def dict_factory(cursor, row):
            d = {}
            for idx,col in enumerate(cursor.description):
                d[col[0]] = row[idx]
            return d
        if not os.path.exists(db_name):
            self.conn = connect(db_name)
            curs = self.conn.cursor()
            curs.executescript(self._schema)
            curs.close()
        else:
            self.conn = connect(db_name)
        self.conn.row_factory = dict_factory

    def add_user(self, nickname, uid):
        self.conn.cursor().execute("INSERT INTO member VALUES (NULL, ?, ?)", [uid, nickname])
        self.conn.commit()

    def get_user(self, uid):
        curs = self.conn.cursor()
        curs.execute("SELECT nickname FROM member WHERE uid=?;", [uid])
        try:
            return curs.fetchone()['nickname']
        except:
            return None

@route('uid/:uid', method='GET')
def validate_uid(uid):
    log.debug("validate uid: "+ uid)
    nick = db.get_user(uid)
    log.debug("nick is: "+str(nick))
    if nick is None:
        log.debug("return 0")
        return '0'
    else:
        log.debug("return 1")
        bot.msg('ChanServ', CHANNEL+' voice '+nick)
        return '1'

def init_service(host_addr='0.0.0.0', host_port=42000, dbg=True):
    global db
    db = MembersDB('leloop_members_db.sqlite')
    debug(dbg)
    try:
        run(host=host_addr, port=host_port)
    finally:
        bot.todo(['QUIT'], "Omar m'a tuer")

if __name__ == '__main__':
    global log
    global bot

    parser = OptionParser()
    parser.add_option("-H", "--host", dest="hostname",
                    help="IP address to start the service on", metavar="HOST", default="0.0.0.0")
    parser.add_option("-p", "--port", dest="port",
                    help="Port to start the service on", metavar="PORT", default="42000")
    parser.add_option("-v", "--verbose",
                    action="store_true", dest="verbose", default=False,
                    help="print more information messages to stdout")
    parser.add_option("-i", "--irc",
                    action="store_true", dest="irc", default=False)

    (options, args) = parser.parse_args()

    if options.verbose == True : level=logging.DEBUG
    else:                        level=logging.ERROR

    logging.basicConfig(stream=sys.stdout, level=level)
    log = logging.getLogger('rfid')
    
    log.debug("connecting to IRC...")
    bot = irc_connect('loop_break', [CHANNEL])
    irc_spawn(bot, 'barjavel.freenode.net', 6667)

    log.debug("starting service...")
    init_service(options.hostname, options.port, dbg=options.verbose)
