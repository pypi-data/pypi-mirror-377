import re

from .noisy_config import NOISY_MODULE_PREFIXES


class LogParser:
    def __init__(self, log_file, ignore_prefixes=None, include_prefixes=None):
        self.log_file = log_file

        # Default to the same noisy module prefixes as the tracer
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

        self.ignore_prefixes = _norm(ignore_prefixes, default=NOISY_MODULE_PREFIXES)
        # Optional include filter; when set, only matching prefixes are parsed
        self.include_prefixes = _norm(include_prefixes)
        self.call_stack = ["Main"]  # Initialize with Main
        self.interactions = []  # Store parsed interactions
        self.functions = set()  # Track all participants
        self.control_flow_stack = []  # Stack to track control flow blocks
        self.function_blocks = {}  # Map functions to their control flow blocks

        # Regex patterns for parsing logs
        # Match anywhere in line; prefixes (timestamp, logger, pid) may vary
        self.enter_pattern = r"Entering function: ([\w\.]+)"
        self.exit_pattern = r"Exiting function: ([\w\.]+)"
        self.loop_pattern = r"Control flow: Loop header: Line (\d+): (.+)"
        self.control_flow_pattern = r"Control flow: Conditional: Line (\d+): (.+)"

    def simplify_name(self, name):
        """Simplify participant names for clarity."""
        parts = name.split(".")
        return f"{parts[-2]}.{parts[-1]}" if len(parts) > 2 else name

    def parse(self):
        """Parse the log file and update interactions."""
        with open(self.log_file, "r") as file:
            for line in file:
                # Match entering function call
                enter_match = re.search(self.enter_pattern, line)
                if enter_match:
                    self.handle_function_entry(enter_match.group(1))
                    continue

                # Match exiting function call
                exit_match = re.search(self.exit_pattern, line)
                if exit_match:
                    self.handle_function_exit(exit_match.group(1))
                    continue

                # Match loop events
                loop_match = re.search(self.loop_pattern, line)
                if loop_match:
                    line_no, loop_header = loop_match.groups()
                    self.handle_loop_event(line_no, loop_header)
                    continue

                # Match control flow events
                control_flow_match = re.search(self.control_flow_pattern, line)
                if control_flow_match:
                    line_no, source_line = control_flow_match.groups()
                    self.handle_control_flow(line_no, source_line)
                    continue

        # Close any remaining control flow blocks
        self.close_all_control_flows()

    def handle_function_entry(self, function_name):
        """Handle entering a function."""
        # Check ignore before simplifying name so module prefixes remain intact
        if function_name.startswith(self.ignore_prefixes):
            return
        # If includes specified, skip non-matching prefixes
        if self.include_prefixes and not function_name.startswith(
            self.include_prefixes
        ):
            return
        function_name = self.simplify_name(function_name)

        # Determine caller
        caller = self.call_stack[-1]

        # Log the function call
        self.interactions.append(f"{caller} -> {function_name} : Call {function_name}")
        self.call_stack.append(function_name)
        self.functions.add(function_name)

        # Initialize function's control flow blocks
        self.function_blocks[function_name] = []

    def handle_function_exit(self, function_name):
        """Handle exiting a function."""
        # Check ignore before simplifying name so module prefixes remain intact
        if function_name.startswith(self.ignore_prefixes):
            return
        # If includes specified, skip non-matching prefixes
        if self.include_prefixes and not function_name.startswith(
            self.include_prefixes
        ):
            return
        function_name = self.simplify_name(function_name)
        if self.call_stack and self.call_stack[-1] == function_name:
            # Close any control flow blocks started within this function
            self.close_blocks_for_function(function_name)

            self.call_stack.pop()
            # Determine where to return
            caller = self.call_stack[-1]
            self.interactions.append(
                f"{function_name} --> {caller} : Return from {function_name}"
            )

            # Remove function's control flow blocks
            del self.function_blocks[function_name]
        else:
            # Handle unexpected function exit (should not happen in well-formed logs)
            pass

    def handle_loop_event(self, line_no, loop_header):
        """Handle loop events."""
        # Start a new loop block
        self.interactions.append(f"loop {loop_header.strip()}")
        current_function = self.call_stack[-1]
        self.interactions.append(
            f"    note right of {current_function} : Loop at line {line_no}"
        )
        self.control_flow_stack.append("loop")

        # Add to current function's blocks, ensure key exists
        self.function_blocks.setdefault(current_function, []).append("loop")

    def handle_control_flow(self, line_no, source_line):
        """Handle control flow events like 'if', 'else', etc."""
        condition = source_line.strip()
        if condition.startswith("if "):
            self.interactions.append(f"alt {condition}")
        elif condition.startswith("elif "):
            self.interactions.append(f"alt {condition}")
        elif condition.startswith("else"):
            self.interactions.append("else")
        else:
            self.interactions.append(f"alt {condition}")

        current_function = self.call_stack[-1]
        self.interactions.append(
            f"    note right of {current_function} : Control flow at line {line_no}"
        )
        self.control_flow_stack.append("alt")

        # Add to current function's blocks, ensure key exists
        self.function_blocks.setdefault(current_function, []).append("alt")

    def close_blocks_for_function(self, function_name):
        """Closes any control flow blocks started within the given function."""
        # Close control flow blocks in reverse order
        for _ in self.function_blocks[function_name]:
            self.control_flow_stack.pop()
            self.interactions.append("end")

    def close_all_control_flows(self):
        """Close any remaining control flow blocks."""
        while self.control_flow_stack:
            self.interactions.append("end")
            self.control_flow_stack.pop()
