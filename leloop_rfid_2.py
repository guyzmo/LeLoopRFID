import telnetlib
import time

serv = telnetlib.Telnet('192.168.42.242')

if __name__ == "__main__":
    while True:
        serv.write('\n')
        ret_str = serv.read_lazy()
        time.sleep(0.5)
        print ret_str
        if ret_str != '':
            serv.write('1\n')
