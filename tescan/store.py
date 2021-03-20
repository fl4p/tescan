import datetime
import os
import pickle
import queue
import time
import uuid
from threading import Thread

from influxdb import InfluxDBClient


class TimeSeriesStore():
    def __init__(self, write_interval=20):
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        self.client = InfluxDBClient('influx.fabi.me', 8086, 'tescan', 't3sc4n', 'tescan_mon', ssl=True)
        self.queue = queue.Queue()
        self.write_interval = write_interval
        self._write_thread = Thread(target=self._write_loop, daemon=True)
        self._write_thread.start()

        self._num_write_errors = 0
        self.fallback = FallbackStore()

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
                    self._num_write_errors = 0
            except (Exception, IOError) as e:
                self._num_write_errors += 1
                print(type(e), 'error writing', len(points), 'points', e, 'num err', self._num_write_errors)

                if self._num_write_errors > 2:
                    print('fallback store', len(points), 'points')
                    self.fallback.write(points)
                else:
                    for p in points:
                        self.queue.put(p)
                    print('re-queued', len(points), 'points, qsize=', self.queue.qsize(), 'ne=', self._num_write_errors)

                time.sleep(self.write_interval * 4)
            time.sleep(self.write_interval)

    def flush(self):
        points = []
        while not self.queue.empty():
            points.append(self.queue.get())

        print('flushing', len(points), 'points')

        if points:
            try:
                self.client.write_points(points, time_precision='ms')
            except:
                self.fallback.write(points, sync=True)


class FallbackStore():
    def __init__(self, dir='data/fbs'):
        self.dir = os.path.abspath(dir)
        os.makedirs(self.dir, exist_ok=True)

        import glob

        pickles = glob.glob(self.dir + '/*.pkl')

        print('Found ', len(pickles), 'pkl files')

        for pkl in pickles:
            with open(pkl, 'rb') as fh:
                d = pickle.load(fh)
                print(pkl, len(d), type(d))

    def write(self, points, sync=False):
        uid = str(uuid.uuid4()).split('-')[-1]
        fp = os.path.join(self.dir, str(time.time()) + uid + '.pkl')
        with open(fp , 'wb') as fh:
            pickle.dump(points, fh, pickle.HIGHEST_PROTOCOL)

        if sync:
            os.sync()
