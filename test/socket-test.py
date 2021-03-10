import socket
import time
from time import sleep

# Device specific information
from typing import List

m5stick_addr = '00:04:3E:96:97:47'
port = 1 # This needs to match M5Stick setting

# Establish connection and setup serial communication
s = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
s.connect((m5stick_addr, port))

class ObdSocket():
    def __init__(self, socket):
        self.soc:socket.socket = socket
        obd = self

        self.obd_interface_name = obd.query("ATZ") # reset
        # print('OBD Interface ', obd_interface_name)

        obd.query("ATE0", expect="OK")
        # print("Connecting car ...")
        obd.query("ATSP0", expect="OK")
        obd.query("ATH1", expect="OK") # headers
        obd.query("ATS0", expect="OK")
        obd.query("ATCAF0", expect="OK")


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

    #def monitor_all(self):
    #    print('Monitor all')
    #    self.send("STMA" if self.st_commands else "ATMA")

    def monitor(self, send_only=False):
        print('Monitor')
        if send_only:
            self.send("STM")
        else:
            return self.query("STM")
        #self.send("STM" if self.st_commands else "ATM")
        #data = s.recv(1024)
        #print('recv', data)
        #return data


    def set_filters(self, filters:List[str]):
        self.query("STFCP", expect="OK")
        for f in filters:
          self.query("STFAP " + f.upper().rjust(3, '0')[-3:] + ",7FF", expect="OK")


    def send(self, command):
        b = bytes(command + '\r', 'ascii')
        print('send', b)
        self.soc.sendall(b)
        return b

    def query(self, command:str, expect=None, fail=None):
        b = self.send(command)
        data = s.recv(1024)
        print('recv', data)

        if data.startswith(b):
            data = data[len(b):]

        data = data.lstrip(b'\r')
        while not data.endswith(b'>'):
            r = s.recv(1024)
            print('recv', r)
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



obd = ObdSocket(s)

class Field:
    def __init__(self, name, unit, func):
        self.name = name
        self.unit = unit
        self.func = func

    def update(self, bytes):
        self.value = self.func(bytes)
        return self.value

class Packet:
    def __init__(self, id:int, fields:List[Field]):
        self.id = id
        self.fields:List[Field] = fields




packets = [
    Packet(id=306, fields=[
        Field("bat_voltage", "V", lambda bytes: (bytes[0] + (bytes[1] << 8)) / 100.0),
        Field("bat_current", "A", lambda bytes: (int(bytes[2]) + (int(bytes[3]) << 8)) / 10.0),
    ])
]

packets_by_hex = {bytes(hex(p.id)[2:],'ascii'):p for p in packets}

def get_can_filter(packets:List[Packet]):
    ids = set()
    for p in packets:
        ids.add(p.id)
    return [hex(id) for id in ids]

filters = get_can_filter(packets)

obd.monitor() # send STM before setting filters
obd.set_filters(filters)

obd.monitor(send_only=True)

buf = b""
while True:
    buf += obd.soc.recv(1024)
    if b'\r' in buf:
        # print('mon data', buf)

        chunks = buf.split(b'\r')
        for chunk in chunks:
            hex_id = chunk[0:3]

            if not hex_id:
                continue

            p: Packet = packets_by_hex.get(hex_id)

            if p:
                payload = chunk[3:]
                print('new packet data', p.id, payload, [f.name for f in p.fields])
                assert len(payload) % 2 == 0, "payload len not mod 2"
                bytes = [int(payload[i:i+2], 16) for i in range(0, len(payload), 2)]
                for f in p.fields:
                    f.update(bytes)
                    print('update field', f.name, f.value)
            else:
                print('unknown packet hex id', hex_id)

        buf = b""








