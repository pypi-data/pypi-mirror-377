# observers.py
import os

from .logging_config import setup_trace_logger

_trace_observer = None
_session_id = None


def get_trace_observer(log_file=None, session_id=None):
    global _trace_observer, _session_id
    if _trace_observer is None:
        import uuid

        _session_id = session_id or str(uuid.uuid4())
        if log_file is None:
            logger = setup_trace_logger("trace_logger", session_id=_session_id)
        else:
            logger = setup_trace_logger(
                "trace_logger", session_id=_session_id, log_file=log_file
            )
        _trace_observer = SeaSnakeObserver(logger)
    return _trace_observer


class TraceObserver:
    def on_event(self, event_type, payload):
        raise NotImplementedError


class SeaSnakeObserver(TraceObserver):
    def __init__(self, logger):
        self.logger = logger

    def on_event(self, event_type, payload):
        pid = os.getpid()
        self.logger.info(f"[pid={pid}] {event_type}: {payload['detail']}")
