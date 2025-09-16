# sea-snake
sea-snake is a small Python library generating PlantUML sequence diagrams.
Decorate any function with `snakebite` to record a call stack and produce both a
`trace.log` and a `trace_diagram.puml` file.

## Features

- Tracing decorator: add `@snakebite` to capture call sequences.
- Clean diagrams: filter with `include_prefixes` and `ignore_prefixes` (list/tuple).
- Depth control: limit with `max_depth` for concise flows.
- Optional per-line logging: `log_lines` with `sample_lines` for sampling.
- Multiprocessing: per‑process logs + safe parent‑side merge into a single diagram.
  - Workers: `@snakebite(multiprocess=True)` writes `trace-<session>-<pid>.log`.
  - Parent: `enable_auto_multiprocess_merge()` merges to one diagram at exit.
  - Identical flows de‑duplicated; different flows render in parallel arms.
- Coverage/debugger friendly: chains prior tracers when safe and restores them.
- Outputs: `trace.log` and `trace_diagram.puml` with sensible defaults.

## Installation

```bash
pip install --pre seasnake-bite
```

## Quick start

```python
from seasnake import snakebite

@snakebite
def greet(name: str) -> None:
    print(f"Hello, {name}!")

if __name__ == "__main__":
    greet("Slytherin")
```

Running the script will create `trace.log` and `trace_diagram.puml` in the
current directory, capturing the call sequence.

Advanced: control depth and filter modules

```python
from seasnake import snakebite

# Only trace calls in your app, skip vendor code, and cap depth
@snakebite(
    max_depth=2,
    include_prefixes=["myapp."],
    ignore_prefixes=["myapp.vendor", "thirdparty"],
)
def run():
    ...  # your code

if __name__ == "__main__":
    run()
```

## Filtering & Options

- include_prefixes / ignore_prefixes: focus tracing on your modules and filter noise. Accepts tuple or list of string prefixes. Example: `@snakebite(include_prefixes=["myapp."], ignore_prefixes=["myapp.vendor"])`.
- log_lines: generic per-line logs are off by default. Enable with `log_lines=True` only when debugging.
- sample_lines: when `log_lines=True`, you can reduce volume with `sample_lines=N` to log every Nth execution line.
- max_depth: limit call depth recorded from the decorated entrypoint.
- multiprocess: set `@snakebite(multiprocess=True)` to write per‑process logs and defer diagram generation to a single merge step.
  - Alias: `auto_multiprocess=True` is accepted for backward compatibility.
- log_file / output_puml_file: optionally set custom paths. With `multiprocess=True`, each process writes `trace-<session>-<pid>.log`.

These options are applied consistently during capture and when parsing the log to produce the diagram.

## Logging behavior

- The trace logger writes to `trace.log`. Console logging is opt-in; by default, sea-snake avoids printing to stdout/stderr.
- PUML generation (`trace_diagram.puml`) runs after tracing stops, and the logger is flushed to ensure no events are missed.
- Log lines include the process ID as a prefix (e.g., `[pid=12345] ...`) to help with multiprocessing post-processing.

## Multiprocessing

When using multiprocessing, each process is a separate Python interpreter and needs its own tracer. The simplest approach is to decorate the function each worker executes with `@snakebite`.

Options to present results:

- Single representative (identical flows): run one worker with `@snakebite` and use its diagram. Add a note (e.g., “Executed in N worker processes”).
- Per‑process diagrams: run each worker independently, then keep each `trace_diagram.puml` (use separate working directories or rename files after each run).
- Combined diagram (recommended): merge multiple per‑process logs into a single PUML using a helper:

```python
from seasnake.log_to_puml import merge_tracelogs_to_puml

# After running workers and saving their logs to unique files
merge_tracelogs_to_puml([
    "worker-1.log",
    "worker-2.log",
    # ... more logs
], output_puml_file="trace_diagram.puml")
```

Behavior of `merge_tracelogs_to_puml`:

- If all logs have identical call flows, it emits a single sequence with a summary note like “Executed in N worker processes”.
- If flows differ, it emits PlantUML parallel blocks using `par`/`else` arms — one arm per log — so concurrency is explicit.

Recommended: parent merge + worker decorator

```python
import multiprocessing as mp
from seasnake.decorators import snakebite, enable_auto_multiprocess_merge

@snakebite(multiprocess=True)
def worker_task(n: int) -> int:
    s = 0
    for i in range(n):
        s += i
    return s

def main():
    enable_auto_multiprocess_merge(output_puml_file="trace_diagram.puml")
    try:
        mp.set_start_method("spawn", force=True)
    except Exception:
        pass
    procs = [mp.Process(target=worker_task, args=(3,)) for _ in range(2)]
    [p.start() for p in procs]; [p.join() for p in procs]

if __name__ == "__main__":
    main()
```

Details:
- Workers write `trace-<session>-<pid>.log` and log messages include `[pid=...]`.
- Parent produces a single `trace_diagram.puml` at process exit by merging worker logs.

Practical tips:

- Ensure each worker’s `trace.log` is saved with a unique name before merging (e.g., copy `trace.log` to `worker-<id>.log`).
- Use `include_prefixes`/`ignore_prefixes` to focus on your app modules and reduce noise at scale.
- On macOS/Windows, prefer the `spawn` start method to avoid inheriting tracer state: `multiprocessing.set_start_method("spawn", force=True)`.

## Coverage & Test Interop

sea-snake uses Python tracing APIs and is designed to coexist with coverage/debuggers. If you use coverage in tests and encounter empty logs in subprocesses, open an issue with a minimal repro. The library chains existing tracers where safe and restores them after completion.

## Known Limitations

- Async functions: the decorator isn’t async-aware yet; wrap a sync entrypoint or await inside a traced sync wrapper.
- If/elif/else rendering: control-flow isn’t yet modeled as a single alt/else chain.
- Exceptions: exception events aren’t captured/rendered in diagrams yet.
- Participant names: not quoted/aliased; unusual characters may render oddly.
- Threads: tracer installs for new threads; no per-thread lanes/toggle in diagrams yet.
- Coverage interop: chaining preserves coverage in main pytest; subprocess coverage can affect performance.
- Performance: generic line logs are off by default; enable with `log_lines=True`, and consider `sample_lines=N` for large traces.
- Multiprocessing: merged diagrams approximate concurrency (parallel arms) but do not infer true cross‑process causality or ordering.

## Explore further

Run the test suite to see additional examples:

```bash
pytest
```

More information on contributing and project structure can be found in the
[CONTRIBUTING.md](CONTRIBUTING.md) and the `tests/` directory.

Disclaimer: This software is provided “as is” without warranty of any kind. Use at your own risk. The authors and contributors are not liable for any claim, damages, or other liability arising from use of this project. See the LICENSE file for details.
