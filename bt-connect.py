import sys

import bluetooth

print(sys.argv[1])

uuid = "00001101-0000-1000-8000-00805f9b34fb"
addr = sys.argv[1]

print('Finding service %s on device %s' % (uuid, addr))

service_matches = bluetooth.find_service(uuid=uuid, address=addr)

for serv in service_matches:
    print('Bt service %(host)s %(name)s port %(port)s' % serv)

first_match = service_matches[0]
port = first_match["port"]
name = first_match["name"]
host = first_match["host"]

print("Connecting to \"{}\" on {}".format(name, host))

sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
sock.connect((host, port))

print("Connected. Type something...")
exit(0)
while True:
    data = input()
    if not data:
        break
    sock.send(data)

# sock.close()