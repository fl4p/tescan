from typing import List

import can

class CanSocket():
    def __init__(self, channel='can0'):
        self.bus = can.interface.Bus(channel=channel, bustype='socketcan_native')

    def monitor(self, send_only=False):
        pass

    def set_filters(self, filters: List[int]):
        pass

    def send(self, command):
        raise NotImplementedError()

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
        #print('data', data)

        if expect:
            excp = bytes(expect, 'ascii')
            assert data == excp, f"expected {excp}, got {data}"

        if fail:
            fail = bytes(fail, 'ascii')
            assert data != fail, "fail"

        return data

    def recv(self):
        return self.bus.recv()
        pass