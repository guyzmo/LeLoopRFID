
import socket

def open_door():
    door = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    door.connect(("192.168.42.242", 4242))
    door.send("1\n")
    door.close()

def deny_entrance():
    door = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    door.connect(("192.168.42.242", 4242))
    door.send("0\n")

if __name__ == "__main__":
    open_door()
