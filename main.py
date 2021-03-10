# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.

import bluetooth

from util import setup_custom_logger

logger = setup_custom_logger('bt')


def print_hi(name):
    # devices = bluetooth.discover_devices()
    # search for the SampleServer service
    uuid = "00001101-0000-1000-8000-00805f9b34fb"
    addr = '00:04:3E:96:97:47'

    logger.info('Finding service %s on device %s', uuid, addr)

    service_matches = bluetooth.find_service(uuid=uuid, address=addr)

    for serv in service_matches:
        logger.info('Bt service %(host)s %(name)s port %(port)s', serv)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
