from html.parser import HTMLParser

class HTMLValidator(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack = []
        self.is_valid = True

    def handle_starttag(self, tag, attrs):
        # Push start tag onto stack
        self.stack.append(tag)

    def handle_endtag(self, tag):
        if not self.stack or self.stack[-1] != tag:
            self.is_valid = False
        else:
            self.stack.pop()

def is_valid_html(html_str: str) -> bool:
    parser = HTMLValidator()
    parser.feed(html_str)
    # HTML is valid if no mismatches and stack empty
    return parser.is_valid and len(parser.stack) == 0