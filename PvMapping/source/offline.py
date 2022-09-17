import time

import pandas as pd

from PvMapping.source import SourceThread, SourceItem


class OfflineSourceThread(SourceThread):
    def run(self) -> None:
        df = pd.read_pickle("/home/mathis/Downloads/2022-08.pkl")
        for timestamp in df.index:

            if self._should_stop:
                break

            row = df.loc[timestamp].dropna()
            sample = row.sample()
            name, power_kw = sample.index[0], sample.values[0]
            item = SourceItem(timestamp=timestamp, power_kw=power_kw, name=name)
            self._queue.put(item)

            time.sleep(1.0)
