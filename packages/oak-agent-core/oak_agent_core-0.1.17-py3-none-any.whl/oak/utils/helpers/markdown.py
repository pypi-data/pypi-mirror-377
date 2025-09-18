import re

def remove_html_markers(text: str) -> str:
    """
    Removes specific HTML code block markers from the start and end of a string,
    including trailing newlines after the closing marker.
    """
    pattern = r"^```html\s*(.*?)```\s*$"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text.strip()