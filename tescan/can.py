import cantools

from tescan.obd import ObdSocket


def hexstr2bytes(payload):
    bytes = [int(payload[i:i + 2], 16) for i in range(0, len(payload), 2)]
    return bytes


class CANMonitor():
    def __init__(self, obd: ObdSocket, dbc):
        self.obd = obd
        self.db = cantools.db.load_file(dbc)

        self._num_frames = 0
        self._num_signals = 0

    def get_message(self, frame_id_or_name) -> cantools.db.Message:
        try:
            message = self.db.get_message_by_frame_id(frame_id_or_name)
        except KeyError:
            message = self.db.get_message_by_name(frame_id_or_name)
        return message

    def monitor(self, monitor_ids):
        filters = [self.get_message(id).frame_id for id in monitor_ids]

        obd = self.obd
        obd.monitor()  # send STM before setting filters
        obd.set_filters(filters)
        obd.monitor(send_only=True)

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
                        msg: dict = self.db.decode_message(frame_id, bytes)

                        self._num_frames += 1
                        self._num_signals += len(msg)

                        print(frame_id, hexstr, msg)
                    except Exception as e:
                        print('failed to decode CAN chunk', chunk, e)

                buf = b""
