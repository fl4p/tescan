import socket
# Device specific information

from tescan.obd import ObdSocket
from tescan.can import CANMonitor


def main():
    m5stick_addr = '00:04:3E:96:97:47'
    port = 1  # This needs to match M5Stick setting

    s = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
    s.connect((m5stick_addr, port))

    obd = ObdSocket(s)
    mon = CANMonitor(obd, dbc='dbc/Model3CAN.dbc')

    mon.monitor(monitor_ids=(306, 599, 1010, 950, 850, 658, 978, 609, 692, 826, 708, 548, 532, 541, 612, 647, 691))


main()
