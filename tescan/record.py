import datetime
import time
import traceback
from threading import Thread
from typing import Dict

import pytz
from influxdb import InfluxDBClient

from tescan.can import CANMonitor
from tescan.util import setup_custom_logger

logger = setup_custom_logger('rec')


def is_near(a, b, eps):
    return a == b or (abs(a - b) / abs(a or b) < eps)


def now():
    return datetime.datetime.utcnow().replace(tzinfo=pytz.utc)


class TimeSeriesStore():
    def __init__(self):
        self.client = InfluxDBClient('influx.fabi.me', 8086, 'tescan', 't3sc4n', 'tescan_mon', ssl=True)

    def write(self, measurement, time: datetime.datetime, tags, data):
        points = [
            {
                "measurement": measurement,
                "tags": tags,
                "time": time.isoformat(),
                "fields": data,
            }
        ]
        self.client.write_points(points, time_precision='ms')
        print('tss wrote', len(data))


class Recorder:

    def __init__(self, can: CANMonitor, signals: Dict[str, set]):
        self.can = can
        self.signals = signals
        self.last_sample = {}
        self.eps = 1e-4
        self.interval = 8

        self.tss = TimeSeriesStore()

    def sample(self):
        vin = self.can.vin()
        if vin is None:
            logger.warn('No VIN yet, skip sample')
            return

        if not self.last_sample:
            logger.warn('VIN #%s', vin)

        sample = {}
        for frame_name, signal_names in self.signals.items():
            frame_signals = self.can.signal_values[frame_name]
            sample.update({k: v for k, v in frame_signals.items() if k in signal_names or signal_names == '*'})

        last = self.last_sample
        for k in list(sample.keys()):
            if k in last and is_near(last[k], sample[k], self.eps):
                del sample[k]

        self.last_sample.update(sample)

        print('sample', time.time(), sample)
        self.tss.write('sample', now(), tags={'vin': vin}, data=sample)

    def start(self):
        self.thread = Thread(target=self._thread_body, daemon=True)
        self.thread.start()

    def _thread_body(self):
        time.sleep(max(2, self.interval / 4))
        while True:
            try:
                self.sample()
            except Exception as e:
                logger.error('Error sampling: %s %s', e, traceback.format_exc())
            time.sleep(self.interval)
