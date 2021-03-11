import socket
from typing import List


class ObdSocket():
    def __init__(self, socket: socket.socket):
        self.soc = socket
        obd = self

        self.obd_interface_name = obd.query("ATZ")  # reset
        # print('OBD Interface ', obd_interface_name)

        obd.query("ATE0", expect="OK")
        # print("Connecting car ...")
        obd.query("ATSP0", expect="OK")
        obd.query("ATH1", expect="OK")  # enable headers
        obd.query("ATS0", expect="OK")
        obd.query("ATCAF0", expect="OK")


        # check for advanced ST1110 command set
        self.device_name = obd.query("STDI")
        if self.device_name != '?':
            print('device', self.device_name)
            self.st_commands = True
            print("Using ST1110 command set")

            # set UART baud rate ( https://www.scantool.net/downloads/98/stn1100-frpm.pdf )
            assert obd.query("STBR 2000000").startswith(b"OK")

        else:
            self.st_commands = False
            print("Using ELM327 command set")
            raise Exception('ST1110 command set currently required, ELM327-only is WIP')

    # def monitor_all(self):
    #    print('Monitor all')
    #    self.send("STMA" if self.st_commands else "ATMA")

    def monitor(self, send_only=False):
        print('Monitor')
        if send_only:
            self.send("STM")
        else:
            return self.query("STM")
        # self.send("STM" if self.st_commands else "ATM")
        # data = s.recv(1024)
        # print('recv', data)
        # return data

    def set_filters(self, filters: List[int]):
        filters = list(set(filters))
        self.query("STFCP", expect="OK")
        for f in filters:
            self.query("STFAP " + hex(f)[2:].upper().rjust(3, '0')[-3:] + ",7FF", expect="OK")

    def send(self, command):
        b = bytes(command + '\r', 'ascii')
        print('send', b)
        self.soc.sendall(b)
        return b

    def query(self, command: str, expect=None, fail=None):
        b = self.send(command)
        data = self.soc.recv(1024)
        # print('recv', data)

        if data.startswith(b):
            data = data[len(b):]

        data = data.lstrip(b'\r')
        while not data.endswith(b'>'):
            r = self.soc.recv(1024)
            # print('recv', r)
            data += r
            # print('data', data, not data.endswith(b'\r\r'))

        data = data[:-1].strip(b'\r')
        print('data', data)

        if expect:
            excp = bytes(expect, 'ascii')
            assert data == excp, f"expected {excp}, got {data}"

        if fail:
            fail = bytes(fail, 'ascii')
            assert data != fail, "fail"

        return data