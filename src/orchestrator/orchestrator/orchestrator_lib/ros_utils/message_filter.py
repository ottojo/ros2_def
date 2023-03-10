import sys
from typing import Any, List, Mapping
from threading import Lock
from message_filters import SimpleFilter, ApproximateTimeSynchronizer


# I guess this wont work below 3.7 anyways, but this file in particular makes use of
# map iteration, which is only guarenteed to be in insertion order starting with 3.7
# https://docs.python.org/3/library/stdtypes.html#dictionary-view-objects
assert sys.version_info >= (3, 7)


class ApproximateTimeSynchronizerTracker:
    """
    This wraps an ApproximateTimeSynchronizer without requiring actual subscriptions,
    and provides feedback wether the combined callback was executed or not
    """

    def __init__(self, topic_names: List[str], queue_size: int, slop: float) -> None:
        self._filters: Mapping[str, SimpleFilter] = {}
        for topic_name in topic_names:
            assert topic_name not in self._filters
            self._filters[topic_name] = SimpleFilter()
        self._time_synchronizer = ApproximateTimeSynchronizer(self._filters.values(), queue_size, slop)
        self._was_called: bool = False
        self._lock = Lock()
        self._time_synchronizer.registerCallback(self.__callback)

    def __callback(self, *_msgs):
        self._was_called = True

    def test_input(self, topic_name: str, msg: Any) -> bool:
        """
        Test if input causes time-synchronizer callback

        Note that this modifies the internal state, and calling this should always
        happen in sync with actually publishing the message to the node
        """
        with self._lock:
            self._was_called = False
            self._filters[topic_name].signalMessage(msg)
            was_called: bool = self._was_called
        return was_called
