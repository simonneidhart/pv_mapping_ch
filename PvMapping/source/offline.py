from PvMapping.source import SourceThread


class OfflineSourceThread(SourceThread):
    def run(self) -> None:
        while not self._should_stop:
            # TODO: Push SourceItems into queue
            pass
