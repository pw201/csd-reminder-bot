"""
Create a copy of config.py with all the quoted strings removed, as they contain passwords etc.
"""
import re

with open("config.py", "r") as config:
    with open("sample_config.py", "w") as sample:
        text = config.read()
        text = re.sub(r'"{3}.*?"{3}', '', text, flags=re.DOTALL)
        text = re.sub(r'"[^"]+"', '""', text, flags=re.DOTALL)
        text = re.sub(r"'[^']+'", "''", text, flags=re.DOTALL)
        sample.write('"""Copy me to config.py and fill in the blanks."""\n')
        sample.write(text)

