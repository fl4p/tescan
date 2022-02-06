import can
bus = can.interface.Bus(channel='can0', bustype='socketcan_native')
#notifier = can.Notifier(bus, [can.Printer()])

import time

while True:
    r = bus.recv()
    print('R', r.arbitration_id, r.channel, r.data, str(r))
    # time.sleep(1)

can.Message

#msg = can.Message(arbitration_id=0x7de,
#data=[0, 25, 0, 1, 3, 1, 4, 1],
#extended_id=False)