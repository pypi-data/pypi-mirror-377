def html_output(func):
    original_func = getattr(func, "func", func)
    original_func.output_type = "html"
    return func