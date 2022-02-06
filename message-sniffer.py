
import can
import cantools

bus = can.interface.Bus(channel='can0', bustype='socketcan_native')

db = cantools.db.load_file('./dbc/Model3CAN.dbc')

num_total_message = 0

printing_new_messages = False
known_message_ids = set()

import threading

def input_thread():
    global printing_new_messages
    while True:
        c = input()
        if c == 's':
            printing_new_messages = True
            print('Printing new messages enabled')

        if c == 't':
            # 1294 False
            msg = can.Message(arbitration_id=1294, is_extended_id=False, data=bytearray(b'F\x00P\x00\x00\x00\x00\x00'))
            print('sending', msg)
            r = bus.send(msg)
            print('sent', r)

t = threading.Thread(target=input_thread, daemon=True)
t.start()


while True:

    r = bus.recv()

    if printing_new_messages:
        if r.arbitration_id not in known_message_ids:
            print('new msg', r.arbitration_id, r.is_extended_id, r.data)
            print(r)
            try:
                decoded = db.decode_message(r.arbitration_id, r.data)
                print(decoded)
            except Exception as e:
                print('error decoding', type(e), e)
    #else:
    known_message_ids.add(r.arbitration_id)
    num_total_message += 1

    if num_total_message % 1000 == 0:
        print('total messages=%d, known_ids=%d' % (num_total_message, len(known_message_ids)))


