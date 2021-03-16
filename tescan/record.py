import datetime
import queue
import time
import traceback
from threading import Thread
from typing import Dict

import pytz
from influxdb import InfluxDBClient

from tescan.can import CANMonitor
from tescan.util import setup_custom_logger, exit_process

logger = setup_custom_logger('rec')


def is_near(a, b, eps):
    return a == b or (abs(a - b) / abs(a or b)) < eps


def now():
    return datetime.datetime.utcnow().replace(tzinfo=pytz.utc)


class TimeSeriesStore():
    def __init__(self, write_interval=20):
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        self.client = InfluxDBClient('influx.fabi.me', 8086, 'tescan', 't3sc4n', 'tescan_mon', ssl=True)
        self.queue = queue.Queue()
        self.write_interval = write_interval
        self._write_thread = Thread(target=self._write_loop, daemon=True)
        self._write_thread.start()

    def write(self, measurement, time: datetime.datetime, tags, data):
        if not data:
            return False
        self.queue.put({
            "measurement": measurement,
            "tags": tags,
            "time": time.isoformat(),
            "fields": data,
        })
        return True

    def _write_loop(self):
        while True:
            points = []
            while not self.queue.empty() and len(points) < 20_000:
                points.append(self.queue.get())
            try:
                if points:
                    self.client.write_points(points, time_precision='ms')
                    print('tss wrote', len(points), 'points with', sum(map(len, points)), 'fields')
            except (Exception, IOError) as e:
                print(type(e), 'error writing', len(points), 'points', e)
                for p in points:
                    self.queue.put(p)
                print('re-queued', len(points), 'points, qsize=', self.queue.qsize())
                time.sleep(self.write_interval * 4)
            time.sleep(self.write_interval)


class Recorder:

    def __init__(self, can: CANMonitor, signals: Dict[str, set]):
        self.can = can
        self.signals = signals
        self.last_sample = {}
        self.eps = 1e-4
        self.interval = 1

        self.last_change_time = time.time()

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

        if sample:
            self.last_change_time = time.time()
            print('sample', time.time(), len(sample), str(sample)[:60])
            self.last_sample.update(sample)
            self.tss.write('sample', now(), tags={'vin': vin}, data=sample)
        else:
            print('EMPTY sample, last change', round(time.time() - self.last_change_time), 's ago')

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

            if (time.time() - self.last_change_time) > 30:
                logger.error('No data change for 30s! EXITING PROCESS')
                exit_process()
                # raise Exception('Sample timeout')

            time.sleep(self.interval)
