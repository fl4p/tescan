from tescan.record import TimeSeriesStore, now

tss = TimeSeriesStore()
tss.write('test', now(), {'tag0': 'abc'}, {'a': 1, 'b': 0})