import datetime
import time
import traceback
from threading import Thread
from typing import Dict

import pytz

from tescan.can import CANMonitor
from tescan.store import TimeSeriesStore
from tescan.util import setup_custom_logger

logger = setup_custom_logger('rec')


def is_near(a, b, eps):
    return a == b or (abs(a - b) / abs(a or b)) < eps


def now():
    return datetime.datetime.utcnow().replace(tzinfo=pytz.utc)


class Recorder:

    def __init__(self, can: CANMonitor, signals: Dict[str, set], on_timeout=None):
        self.thread = Thread(target=self._thread_body, daemon=True)
        self.can = can
        self.signals = signals

        self.last_sample = {}
        self.last_ts = None
        self.last_vehicle_status = None

        self.eps = 1e-4
        self.interval = 1

        self.timeout_timer = time.time() + 30

        self.on_timeout = on_timeout

        self.tss = TimeSeriesStore()

    def flush(self):
        self.tss.flush()

    def sample(self):
        vin = self.can.vin()
        if vin is None:
            logger.warn('No VIN yet, skip sample')
            return

        if not self.last_sample:
            time.sleep(.2)
            logger.warn('VIN #%s  UnixTime=%s Status=%s', vin, self.can.unix_time(), self.can.vehicle_status())

        sample = {}
        for frame_name, signal_names in self.signals.items():
            frame_signals = self.can.signal_values[frame_name]
            sample.update({k: v for k, v in frame_signals.items() if k in signal_names or signal_names == '*'})

        ts = self.can.unix_time()
        last = self.last_sample
        for k in list(sample.keys()):
            if k in last and is_near(last[k], sample[k], self.eps):
                del sample[k]

        if not ts or ts == self.last_ts:
            print('NO timestamp, skip sample', ts, self.last_ts)
        elif sample:
            self.timeout_timer = time.time() + 30
            # print('sample', time.time(), len(sample), str(sample)[:60])
            self.last_sample.update(sample)
            self.last_ts = ts
            self.tss.write('sample', ts, tags={'vin': vin}, data=sample)
        else:
            print('EMPTY sample, timeout', self.timeout_timer, 's ago')

        vehicle_status = self.can.vehicle_status()
        if vehicle_status != self.last_vehicle_status:
            logger.warn('Flushing tss on status change %s -> %s', self.last_vehicle_status, vehicle_status)
            self.tss.flush()
            self.last_vehicle_status = vehicle_status

    def start(self):
        self.thread.start()

    def _thread_body(self):
        time.sleep(max(2, self.interval / 4))
        while True:
            try:
                self.sample()
            except Exception as e:
                logger.error('Error sampling: %s %s', e, traceback.format_exc())

            if time.time() > self.timeout_timer:
                logger.error('No data change for 30s!')
                self.on_timeout and self.on_timeout()
                self.timeout_timer = time.time() + 30

            time.sleep(self.interval)
