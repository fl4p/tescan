import obd


ports = obd.scan_serial()      # return list of valid USB or RF ports
print(ports)  # ['/dev/ttyUSB0', '/dev/ttyUSB1']
connection = obd.OBD(ports[0]) # conn# ect to the first port in the list

q = connection.query("ATZ")
print(q)