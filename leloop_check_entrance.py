import SocketServer
from leloop_rfid import MembersDB
from leloop_rfid_open_door import open_door, deny_entrance

global db
class DoorRequestHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        data = self.request.recv(1024).strip()
#        socket = self.request[1]
        if data.startswith('CARD '):
            token = data[5:]
            nick = db.get_user(token)
            print data.strip(), nick
            if nick is None:
                deny_entrance()
            else:
                open_door()
        

if __name__ == "__main__":
    db = MembersDB('leloop_members_db.sqlite')
    server = SocketServer.TCPServer(("192.168.42.42",4242), DoorRequestHandler)

    server.serve_forever()


