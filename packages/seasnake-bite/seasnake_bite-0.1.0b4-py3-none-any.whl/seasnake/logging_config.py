import logging
import os


def setup_trace_logger(
    name, log_file="trace.log", level=logging.INFO, session_id=None, console=False
):

    session_file = log_file + ".session"
    delete_log = False
    if session_id:
        if not os.path.exists(session_file):
            delete_log = True
        else:
            try:
                with open(session_file, "r") as f:
                    prev = f.read().strip()
                if prev != session_id:
                    delete_log = True
            except Exception:
                delete_log = True

    if delete_log:
        try:
            if os.path.exists(log_file):
                os.remove(log_file)
            with open(session_file, "w") as f:
                f.write(session_id)
        except Exception as e:
            logging.warning(f"Could not reset trace log: {e}")

    trace_logger = logging.getLogger(name + "_trace")
    trace_logger.setLevel(level)
    # Avoid duplicating to root handlers
    trace_logger.propagate = False

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Ensure a single FileHandler for the specified log_file
    has_file_handler = False
    for h in trace_logger.handlers:
        if isinstance(h, logging.FileHandler):
            # Some handlers may not have baseFilename in all environments
            base = getattr(h, "baseFilename", None)
            if base and os.path.abspath(base) == os.path.abspath(log_file):
                has_file_handler = True
                # Keep formatter consistent
                h.setFormatter(formatter)
                break
    if not has_file_handler:
        try:
            fh = logging.FileHandler(log_file, mode="a", encoding="utf-8")
            fh.setFormatter(formatter)
            trace_logger.addHandler(fh)
        except Exception as e:
            logging.warning(f"Could not set up file handler for trace log: {e}")

    # Add console handler only when explicitly requested
    if console:
        has_stream = any(
            isinstance(h, logging.StreamHandler)
            and not isinstance(h, logging.FileHandler)
            for h in trace_logger.handlers
        )
        if not has_stream:
            sh = logging.StreamHandler()
            sh.setFormatter(formatter)
            trace_logger.addHandler(sh)

    return trace_logger
