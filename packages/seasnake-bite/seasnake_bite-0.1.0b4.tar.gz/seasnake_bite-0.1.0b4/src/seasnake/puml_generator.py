import os


class PUMLGenerator:
    def __init__(self, output_file):
        self.output_file = output_file

    def write_puml(self, interactions, functions):
        """Writes the interactions to a PUML file."""
        # Check if the output file already exists and remove it.
        try:
            os.remove(self.output_file)
        except FileNotFoundError:
            pass
        with open(self.output_file, "w") as file:
            file.write("@startuml\n")
            file.write("!theme amiga\n")
            file.write("participant Main\n")

            for func in sorted(functions):
                file.write(f"participant {func}\n")
            for interaction in interactions:
                file.write(interaction + "\n")
            file.write("@enduml\n")
