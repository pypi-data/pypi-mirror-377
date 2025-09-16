from .log_parser import LogParser
from .puml_generator import PUMLGenerator


def tracelog_to_puml(log_file="trace.log", output_puml_file="trace_diagram.puml"):
    # Parse the log file
    parser = LogParser(log_file)
    parser.parse()

    # Generate PUML
    generator = PUMLGenerator(output_puml_file)
    generator.write_puml(parser.interactions, parser.functions)


def merge_tracelogs_to_puml(
    log_files,
    output_puml_file="trace_diagram.puml",
    label="Worker",
    dedupe_identical=True,
):
    """
    Merge multiple trace logs into a single PUML.

    - If all logs produce identical interaction sequences and dedupe_identical=True,
      emits a single flow with a note indicating number of workers.
    - Otherwise, wraps each process flow in a PlantUML parallel (par/else) block.
    """
    parsed = []
    all_functions = set()
    for lf in log_files:
        p = LogParser(lf)
        p.parse()
        parsed.append(p)
        all_functions |= set(p.functions)

    if not parsed:
        # Nothing to do, write an empty skeleton
        PUMLGenerator(output_puml_file).write_puml([], set())
        return

    # Check if all interactions are identical
    first_seq = parsed[0].interactions
    all_same = dedupe_identical and all(p.interactions == first_seq for p in parsed)

    interactions = []
    if all_same:
        # Single flow; add a summary note first
        count = len(parsed)
        if count > 1:
            interactions.append(
                f"note over Main : Executed in {count} worker processes"
            )
        interactions.extend(first_seq)
    else:
        # Emit parallel blocks per log file
        for idx, p in enumerate(parsed):
            if idx == 0:
                interactions.append(f"par {label} {idx+1}")
            else:
                interactions.append(f"else {label} {idx+1}")
            interactions.extend(p.interactions)
        interactions.append("end")

    PUMLGenerator(output_puml_file).write_puml(interactions, all_functions)
