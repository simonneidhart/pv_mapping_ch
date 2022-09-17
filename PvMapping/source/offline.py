import os
import time

import dotenv
import pandas as pd

from PvMapping.source import SourceThread, SourceItem

dotenv.load_dotenv()


class OfflineSourceThread(SourceThread):
    def run(self) -> None:
        df = pd.read_pickle(os.environ.get("TIME_SERIES_FILE_PATH"))
        for timestamp in df.index:

            if self._should_stop:
                break

            row = df.loc[timestamp].dropna()
            sample = row.sample()
            meter_id, power_kw = sample.index[0], sample.values[0]
            item = SourceItem(
                timestamp=timestamp, power_kw=power_kw, meter_id=int(meter_id)
            )
            self._queue.put(item)

            time.sleep(1.0)
