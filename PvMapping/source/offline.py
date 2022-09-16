from PvMapping.source import SourceThread, SourceItem
import pandas as pd


class OfflineSourceThread(SourceThread):
    def run(self) -> None:

        df = pd.read_pickle("../../data/2022-08.pkl").reset_index().T

        for timestamp in df.index:
            if self._should_stop:
                break
            row = df.loc[timestamp].dropna()
            sample = row.sample()
            name, power_kw = sample.index[0], sample.values[0]
            item = SourceItem(timestamp=timestamp, power_kw=power_kw, name=name)
            self._queue.put(item)
