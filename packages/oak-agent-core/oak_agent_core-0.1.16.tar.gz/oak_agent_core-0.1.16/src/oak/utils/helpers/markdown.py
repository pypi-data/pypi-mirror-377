import re

def remove_html_markers(text: str) -> str:
    pattern = r"^``````$"
    match = re.match(pattern, text, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return text.strip()