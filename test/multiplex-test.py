from tescan.can import hexstr2bytes

messsages = """3F2080A2313204B4001
3F209FDFD09709E6900
3F20A28C51270363A01
3F20BABCD0940DD6700
3F200B9952700000000
3F2010D2F1A00000000
3F202A8880D00000000
3F203D53C4200000000
3F2080A2313204B4001
3F209FDFD09709E6900
3F20A28C51270363A01
3F20BABCD0940DD6700
3F200B9952700000000
3F2010D2F1A00000000
3F202A8880D00000000
3F203D53C4200000000
3F2080A2313204B4001
3F209FDFD09709E6900
3F20A28C51270363A01
3F20BABCD0940DD6700
3F200B9952700000000
3F2010D2F1A00000000
3F202A8880D00000000
3F203D53C4200000000
3F2080B2313204B4001
3F209FDFD09709E6900
3F20A29C51270363A01
3F20BABCD0940DD6700
3F200B9952700000000
3F2010D2F1A00000000
""".split('\n')

import cantools

db = cantools.db.load_file('../dbc/Model3CAN.dbc')

for chunk in messsages:
    hex_id = chunk[0:3]

    if not hex_id:
        continue

    frame_id = int(hex_id, 16)

    hexstr = chunk[3:]
    assert len(hexstr) % 2 == 0, "hexstr len not mod 2"
    bytes = hexstr2bytes(hexstr)

    msg = db.get_message_by_frame_id(frame_id)
    signals: dict = msg.decode(bytes, decode_choices=True, scaling=True)

    print(chunk, signals)
    if msg.is_multiplexed():
        pass
    else:
        pass

print(messsages)
