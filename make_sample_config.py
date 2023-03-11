"""
Create a copy of config.py with all the quoted strings removed, as they contain passwords etc.
"""
import re

in_function=False
with open("config.py", "r") as config:
    with open("sample_config.py", "w") as sample:
        sample.write("# Copy me to config.py and fill in the blanks.\n")
        for line in config.readlines():
            if line.startswith("#"):
                # A bit hacky: the next thing after a function is a comment
                # introducing the next setting, whereas the functions
                # themselves tend to contain multi-line text, so looking at
                # indentation doesn't help.
                in_function = False
            elif line.startswith("def "):
                in_function = True

            if not in_function:
                if not line.strip().startswith("#"):
                    # Empty out strings, double quoted first in case they contain
                    # apostrophes.
                    line = re.sub(r'"[^"]+"', '""', line)
                    line = re.sub(r"'[^']+'", "''", line)
                sample.write(line)

