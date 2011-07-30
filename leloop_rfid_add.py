
import sys, os
from sqlite3 import *

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

if __name__ ==  "__main__":
    db = MembersDB('leloop_members_db.sqlite')

    nick = sys.argv[1]
    rfid = sys.argv[2]

    db.add_user(nick,rfid)
    

