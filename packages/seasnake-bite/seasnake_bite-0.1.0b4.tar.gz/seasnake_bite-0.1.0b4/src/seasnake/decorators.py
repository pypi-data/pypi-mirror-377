import atexit
import functools
import glob
import logging
import os
import uuid

from .capture import TraceManager
from .dispatcher import TraceDispatcher
from .log_to_puml import merge_tracelogs_to_puml, tracelog_to_puml
from .observers import get_trace_observer


def trace_log(_func=None, *, max_depth=3):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            tracer = TraceManager(dispatcher=TraceDispatcher(), max_depth=max_depth)
            tracer.dispatcher.register(get_trace_observer())
            tracer.start()
            try:
                return func(*args, **kwargs)
            finally:
                tracer.stop()

        return wrapper

    return decorator if _func is None else decorator(_func)


def sequence_puml(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        # Flush the trace logger's handlers to ensure all events are written
        try:
            observer = get_trace_observer()
            for handler in getattr(observer.logger, "handlers", []):
                try:
                    handler.flush()
                except Exception:
                    pass
        except Exception:
            # In case observer/logger isn't available, fall back silently
            pass
        try:
            tracelog_to_puml(
                log_file="trace.log", output_puml_file="trace_diagram.puml"
            )
        except Exception as e:
            logging.warning(f"Failed to generate PUML: {e}")
        return result

    return wrapper


def snakebite(
    _func=None,
    *,
    max_depth=3,
    include_prefixes=None,
    ignore_prefixes=None,
    auto_multiprocess=False,
    multiprocess=None,
    log_file=None,
    output_puml_file="trace_diagram.puml",
):
    def decorator(func):
        # If multiprocess is enabled, register a parent-side merge at import time
        # so users don't need an explicit enable call in the parent process.
        _auto_mp_flag = bool(auto_multiprocess or (multiprocess is True))
        if _auto_mp_flag:
            session_id = os.environ.get("SEASNAKE_SESSION_ID")
            if not session_id:
                session_id = str(uuid.uuid4())
                os.environ["SEASNAKE_SESSION_ID"] = session_id
                os.environ["SEASNAKE_ROOT_PID"] = str(os.getpid())

                def _merge_at_exit():
                    try:
                        pattern = f"trace-{session_id}-*.log"
                        files = sorted(glob.glob(pattern))
                        if not files:
                            # Fallback: pick up any per-process trace logs in cwd
                            files = sorted(glob.glob("trace-*.log"))
                        if files:
                            merge_tracelogs_to_puml(
                                files, output_puml_file=output_puml_file
                            )
                    except Exception as e:
                        logging.warning(f"Failed to merge PUML: {e}")

                atexit.register(_merge_at_exit)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Configure auto-multiprocess session and per-process log files
            session_id = None
            effective_log_file = log_file or "trace.log"
            # Support alias: multiprocess=True is equivalent to auto_multiprocess
            _auto_mp = _auto_mp_flag
            if _auto_mp:
                session_id = os.environ.get("SEASNAKE_SESSION_ID")
                if not session_id:
                    session_id = str(uuid.uuid4())
                    os.environ["SEASNAKE_SESSION_ID"] = session_id
                    os.environ["SEASNAKE_ROOT_PID"] = str(os.getpid())

                    def _merge_at_exit():
                        try:
                            pattern = f"trace-{session_id}-*.log"
                            files = sorted(glob.glob(pattern))
                            if files:
                                merge_tracelogs_to_puml(
                                    files, output_puml_file=output_puml_file
                                )
                        except Exception as e:
                            logging.warning(f"Failed to merge PUML: {e}")

                    atexit.register(_merge_at_exit)
                # Per-process log file
                effective_log_file = f"trace-{session_id}-{os.getpid()}.log"

            tracer = TraceManager(
                dispatcher=TraceDispatcher(),
                max_depth=max_depth,
                noisy_modules=ignore_prefixes if ignore_prefixes is not None else None,
                include_prefixes=include_prefixes,
            )
            observer = get_trace_observer(
                log_file=effective_log_file, session_id=session_id
            )
            tracer.dispatcher.register(observer)
            tracer.start()
            try:
                return func(*args, **kwargs)
            finally:
                # Ensure tracing is stopped before generating PUML
                tracer.stop()
                # Flush the trace logger so all events are on disk
                try:
                    for handler in getattr(observer.logger, "handlers", []):
                        try:
                            handler.flush()
                        except Exception:
                            pass
                except Exception:
                    pass
                if not _auto_mp:
                    try:
                        tracelog_to_puml(
                            log_file=effective_log_file,
                            output_puml_file=output_puml_file,
                        )
                    except Exception as e:
                        logging.warning(f"Failed to generate PUML: {e}")

        return wrapper

    return decorator if _func is None else decorator(_func)


def enable_auto_multiprocess_merge(output_puml_file: str = "trace_diagram.puml"):
    """Enable auto-merge of per-process trace logs at parent process exit.

    Creates a session id if missing and registers an atexit hook that merges
    all trace-<session>-*.log files into a single PUML using
    merge_tracelogs_to_puml.
    """
    session_id = os.environ.get("SEASNAKE_SESSION_ID")
    if not session_id:
        session_id = str(uuid.uuid4())
        os.environ["SEASNAKE_SESSION_ID"] = session_id
        os.environ["SEASNAKE_ROOT_PID"] = str(os.getpid())

    def _merge_at_exit():
        try:
            pattern = f"trace-{session_id}-*.log"
            files = sorted(glob.glob(pattern))
            if not files:
                files = sorted(glob.glob("trace-*.log"))
            if files:
                merge_tracelogs_to_puml(files, output_puml_file=output_puml_file)
        except Exception as e:
            logging.warning(f"Failed to merge PUML: {e}")

    atexit.register(_merge_at_exit)
