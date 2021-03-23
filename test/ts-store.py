from tescan.record import now
from tescan.store import TimeSeriesStore

tss = TimeSeriesStore()
tss.write('test', now(), {'tag0': 'abc'}, {'a': 1, 'b': 0})

print('flush..')
tss.flush()