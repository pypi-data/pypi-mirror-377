import re

def fix_key(key: str) -> str:
    if not key.startswith("q"):
        print(
            f"[JotForm] Filter key '{key}' does not start with 'q', prepending 'q'."
        )
        # Try to extract number at start
        match = re.match(r"(\d+)(:.*)?", key)
        if match:
            new_key = f"q{match.group(1)}"
            if match.group(2):
                new_key += match.group(2)
            return new_key
        else:
            return "q" + key
    return key