import logging
import time
import typing as tp

from kombu import Connection

from .base import IChecker


class BrokerChecker(IChecker):
    def __init__(self, broker_url: str, timeout: int = 3, retries: int = 3, delay: float = 0.5):
        self.broker_url = broker_url
        self.timeout = timeout
        self.retries = retries
        self.delay = delay

        self._logger = logging.getLogger(self.__class__.__name__)

    def name(self) -> str:
        return 'broker'

    def check(self) -> tp.Tuple[bool, float, tp.Optional[str]]:
        start = time.monotonic()
        last_error = None
        for i in range(1, self.retries + 1):
            try:
                with Connection(self.broker_url, connect_timeout=self.timeout) as conn:
                    conn.connect()
                    conn.release()
                latency = time.monotonic() - start
                return True, latency, None
            except Exception as e:
                last_error = str(e)
                self._logger.warning(f"Broker attempt {i} failed: {e}")
                time.sleep(self.delay * i)

        latency = time.monotonic() - start
        return False, latency, last_error
