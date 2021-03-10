import cantools

db = cantools.db.load_file('./dbc/Model3CAN.dbc')

msg = db.get_message_by_frame_id(306)
print(len(msg.signals))

#msg =  db.decode_message(306, b'C695150064402B00')
#print(msg)

def payload2bytes(payload):
    bytes = [int(payload[i:i+2], 16) for i in range(0, len(payload), 2)]
    return bytes

print(db.decode_message(306, payload2bytes(b'9F9218006640DD00'.replace(b' ', b''))))
print(db.decode_message(306, payload2bytes(b'70 96 0E FF 5C 26 FF 0F'.replace(b' ', b''))))
print(db.decode_message(306, payload2bytes(b'7592D1FFE23FF00F'.replace(b' ', b''))))





fn = lambda bytes: (bytes[0] + (bytes[1] << 8)) / 100.0

print(fn(payload2bytes(b'70 96 AE FF 5C 26 FF 0F'.replace(b' ', b''))))
