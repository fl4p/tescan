from collections import defaultdict
from threading import Thread

import cantools
import cantools.database

from tescan.obd import ObdSocket


def hexstr2bytes(payload):
    bytes = [int(payload[i:i + 2], 16) for i in range(0, len(payload), 2)]
    return bytes


class CANMonitor():
    def __init__(self, obd: ObdSocket, dbc):
        self.obd = obd
        self.db = cantools.db.load_file(dbc)

        self._total_recv_frames = 0
        self._total_recv_signals = 0

        self.signal_values = defaultdict(dict)
        self._thread = None

    def get_message(self, frame_id_or_name) -> cantools.database.Message:
        if not isinstance(frame_id_or_name, str):
            message = self.db.get_message_by_frame_id(frame_id_or_name)
        else:
            message = self.db.get_message_by_name(frame_id_or_name)
        return message

    def vin(self):
        try:
            sig = self.signal_values['ID405VIN']
            vin1 = int(sig['VINA405']).to_bytes(8, 'little')
            assert vin1.startswith(b'\x00\x00\x00')
            vin = vin1 + int(sig['VINB405']).to_bytes(8, 'little')+ int(sig['VINC405']).to_bytes(8, 'little')
            vin = vin.replace(b'\x00', b'')
            return vin.decode('ascii')
        except KeyError:
            return None

    def _monitor_thread(self):
        obd = self.obd

        buf = b""
        while True:
            buf += obd.soc.recv(1024)
            if b'\r' in buf:

                chunks = buf.split(b'\r')
                for chunk in chunks:
                    try:
                        hex_id = chunk[0:3]

                        if not hex_id:
                            continue

                        frame_id = int(hex_id, 16)

                        hexstr = chunk[3:]
                        assert len(hexstr) % 2 == 0, "hexstr len not mod 2"
                        bytes = hexstr2bytes(hexstr)

                        msg = self.get_message(frame_id)

                        signals: dict = msg.decode(bytes, decode_choices=True, scaling=True)

                        self.signal_values[msg.name].update(signals)
                        self._total_recv_frames += 1
                        self._total_recv_signals += len(signals)

                        # print(frame_id, hexstr, msg)
                    except Exception as e:
                        pass
                        # print('failed to decode CAN chunk', chunk, e)

                buf = b""

    def monitor(self, monitor_ids):
        monitor_ids = [self.get_message(id).frame_id for id in monitor_ids]

        obd = self.obd
        obd.monitor()  # send STM before setting filters
        obd.set_filters(monitor_ids)
        obd.monitor(send_only=True)

        self._total_recv_frames = 0
        self._total_recv_signals = 0
        self.signal_values.clear()

        if not self._thread:
            print('starting monitor threadx')
            self._thread = Thread(target=self._monitor_thread, daemon=True)
            self._thread.start()


