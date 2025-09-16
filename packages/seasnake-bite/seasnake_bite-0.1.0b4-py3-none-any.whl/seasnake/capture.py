import linecache
import os
import sys
import threading

from .dispatcher import TraceDispatcher
from .noisy_config import NOISY_MODULE_PREFIXES


class TraceManager:
    _active_count = 0
    _prev_sys_trace = None
    _prev_thread_trace = None

    def __init__(
        self,
        dispatcher=None,
        max_depth=3,
        log_lines=False,
        noisy_modules=NOISY_MODULE_PREFIXES,
        include_prefixes=None,
    ):
        self.dispatcher = dispatcher or TraceDispatcher()
        self.max_depth = max_depth
        self.log_lines = log_lines

        # Normalize prefix collections so str.startswith works reliably
        def _norm(prefixes, default=None):
            if prefixes is None:
                return default
            if isinstance(prefixes, str):
                return (prefixes,)
            if isinstance(prefixes, tuple):
                return prefixes
            try:
                return tuple(prefixes)
            except TypeError:
                return (prefixes,)

        self.noisy_modules = _norm(noisy_modules, default=NOISY_MODULE_PREFIXES)
        self.include_prefixes = _norm(include_prefixes)
        self.logged_loops = set()
        self.base_frame = None

    def get_depth(self, frame):
        depth = 0
        current = frame
        while current:
            if current == self.base_frame:
                return depth
            current = current.f_back
            depth += 1
        # Fallback: if base frame not found (e.g., due to tracer interactions),
        # treat as immediate child to avoid over-filtering legitimate calls.
        return 1

    def log_event(self, event_type, detail, frame, depth):
        if not self.dispatcher:
            return
        module = frame.f_globals.get("__name__", "<unknown>")
        payload = {
            "detail": detail,
            "module": module,
            "function": frame.f_code.co_name,
            "depth": depth,
        }
        self.dispatcher.notify(event_type, payload)

    def is_noisy(self, module_name):
        return any(module_name.startswith(prefix) for prefix in self.noisy_modules)

    def trace_func(self, frame, event, arg):
        module = frame.f_globals.get("__name__", "")
        if not module:
            return
        if module.startswith(self.noisy_modules):
            return
        # If include_prefixes is specified, only trace matching modules
        if self.include_prefixes and not module.startswith(self.include_prefixes):
            return

        depth = self.get_depth(frame)
        if depth > self.max_depth:
            return

        if event == "call":
            self.handle_call_event(frame, depth)
            return self.trace_func
        elif event == "return":
            self.handle_return_event(frame, depth)
        elif event == "line":
            self.handle_line_event(frame, depth)

        return self.trace_func

    def handle_call_event(self, frame, depth):
        module = frame.f_globals.get("__name__", "<unknown>")
        self.log_event(
            "Entering function", f"{module}.{frame.f_code.co_name}", frame, depth
        )

    def handle_return_event(self, frame, depth):
        module = frame.f_globals.get("__name__", "<unknown>")
        self.log_event(
            "Exiting function", f"{module}.{frame.f_code.co_name}", frame, depth
        )

    def handle_line_event(self, frame, depth):
        filename = frame.f_globals.get("__file__", None)
        if not filename:
            return

        line_no = frame.f_lineno
        linecache.checkcache(filename)
        line = linecache.getline(filename, line_no).strip()
        key = (filename, line_no)
        structure = self.classify_line(line)

        if structure == "loop" and key not in self.logged_loops:
            self.log_event(
                "Control flow", f"Loop header: Line {line_no}: {line}", frame, depth
            )
            self.logged_loops.add(key)
        elif structure == "conditional":
            self.log_event(
                "Control flow", f"Conditional: Line {line_no}: {line}", frame, depth
            )
        elif structure == "jump":
            self.log_event(
                "Control flow",
                f"Control statement: Line {line_no}: {line}",
                frame,
                depth,
            )
        else:
            # Only log generic execution lines if enabled
            if self.log_lines:
                self.log_event("Execution", f"Line {line_no}: {line}", frame, depth)

    def classify_line(self, line):
        line = line.strip()
        if "for " in line or "while " in line:
            return "loop"
        if "if " in line or "elif " in line or "else:" in line:
            return "conditional"
        if "break" in line or "continue" in line:
            return "jump"
        return "execution"

    def start(self):
        # If this is the first active tracer, install and save previous tracers
        if TraceManager._active_count == 0:
            self.base_frame = sys._getframe(1)
            try:
                TraceManager._prev_sys_trace = sys.gettrace()
            except Exception:
                TraceManager._prev_sys_trace = None
            try:
                # threading.gettrace may not exist in some Python versions
                TraceManager._prev_thread_trace = getattr(
                    threading, "gettrace", lambda: None
                )()
            except Exception:
                TraceManager._prev_thread_trace = None

            # Decide whether to chain or replace previous tracer
            # (keeps subprocess coverage safe)
            def _should_chain(prev):
                if prev is None:
                    return False
                typ = type(prev)
                mod = getattr(typ, "__module__", "")
                name = getattr(typ, "__name__", "")
                # Avoid chaining coverage C tracer
                # or when subprocess coverage is enabled
                if "coverage" in mod or name.lower().startswith("ctracer"):
                    return False
                # Coverage enables subprocess tracing via this env var
                if os.environ.get("COVERAGE_PROCESS_START"):
                    return False
                return True

            if _should_chain(TraceManager._prev_sys_trace):
                sys_tracer = self._combine_tracers(
                    TraceManager._prev_sys_trace, self.trace_func
                )
            else:
                sys_tracer = self.trace_func
            sys.settrace(sys_tracer)
            try:
                if _should_chain(TraceManager._prev_thread_trace):
                    thread_tracer = self._combine_tracers(
                        TraceManager._prev_thread_trace, self.trace_func
                    )
                else:
                    thread_tracer = self.trace_func
                threading.settrace(thread_tracer)
            except Exception:
                pass
        TraceManager._active_count += 1

    def stop(self):
        # If no active tracers, retain previous behavior: clear tracing
        if TraceManager._active_count == 0:
            sys.settrace(None)
            try:
                threading.settrace(None)
            except Exception:
                pass
            return

        TraceManager._active_count -= 1
        if TraceManager._active_count == 0:
            # Restore previous tracers
            sys.settrace(TraceManager._prev_sys_trace)
            try:
                threading.settrace(TraceManager._prev_thread_trace)
            except Exception:
                pass
            TraceManager._prev_sys_trace = None
            TraceManager._prev_thread_trace = None

    @staticmethod
    def _combine_tracers(prev, current):
        """Combine two trace functions into one that calls both.

        Respects per-frame return behavior by creating a local tracer that
        continues to call each tracer only if it previously returned a
        callable for that frame.
        """
        if prev is None and current is None:
            return None
        if prev is None:
            return current
        if current is None:
            return prev

        def combined(frame, event, arg):
            # Call both tracers defensively; if one fails, keep the other
            try:
                ra = prev(frame, event, arg)
            except Exception:
                ra = None
            try:
                rb = current(frame, event, arg)
            except Exception:
                rb = None

            # If neither returned a local tracer, short-circuit
            if ra is None and rb is None:
                return None

            def local(frame2, event2, arg2):
                nonlocal ra, rb
                if ra is not None:
                    try:
                        ra = ra(frame2, event2, arg2)
                    except Exception:
                        ra = None
                if rb is not None:
                    try:
                        rb = rb(frame2, event2, arg2)
                    except Exception:
                        rb = None
                if ra is None and rb is None:
                    return None
                return local

            return local

        return combined
