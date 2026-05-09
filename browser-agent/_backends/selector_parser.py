import re

def parse_selector(selector):
    if not selector or not isinstance(selector, str):
        return selector

    parts = selector.split(":", 1)
    if len(parts) != 2:
        return selector

    prefix, value = parts
    if not value:
        return selector

    if prefix == "label":
        return f'[aria-label="{value}"]'
    elif prefix == "placeholder":
        return f'[placeholder="{value}"]'
    elif prefix == "role":
        return f'[{value}]'
    elif prefix == "name":
        return f'[name="{value}"]'

    return selector