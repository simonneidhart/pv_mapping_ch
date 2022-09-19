from __future__ import annotations

import abc
import dataclasses
import queue
import threading

import numpy as np


@dataclasses.dataclass
class SourceItem:
    timestamp: np.datetime64
    power_kw: float
    meter_id: int


class SourceThread(threading.Thread, metaclass=abc.ABCMeta):
    """A thread which consumes real-time power production data and pushes this data into a queue.

    When the thread's stop() method is called, it must terminate.
    """

    def __init__(self, item_queue: queue.Queue) -> None:
        super().__init__()
        self._should_stop: bool = False
        self._queue: queue.Queue = item_queue

    def stop(self) -> None:
        self._should_stop = True
