import telnetlib
import os

from sqlite3 import *

serv = telnetlib.Telnet('192.168.42.242')

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




if __name__ == "__main__":
    db = MembersDB('leloop_members_db.sqlite')

    serv.write("I\n")
    while True:
        time.sleep(0.5)
        ret_str = serv.read_some()
        ret_str = ret_str.strip()
        if len(ret_str) != 0 and ret_str[:5] == "CARD ":
            nick = db.get_user(ret_str[5:])
            print ret_str[5:], nick
            if nick is None:
                serv.write("0\n")
            else:
                serv.write("1\n")
            

