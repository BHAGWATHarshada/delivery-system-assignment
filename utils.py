import json
import math
import re


def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    try:
        return json.loads(text)
    except Exception:

        # Replacing single quotes , removing commas at the end , fixing duplicate words

        t = text
        t = t.replace("'", '"')
        t = re.sub(r",\s*([}\]])", r"\1", t)
        t = re.sub(r'"(\\w+)"\s+"\1"\s*:', r'"\1":', t)
        t = re.sub(r',\s*,+', ',', t)

        # lading  json
        try:
            return json.loads(t)
        except Exception as e:
            raise ValueError(f"failed to parse json ({path}): {e}")


# finding distance between two points using euclidean formulaa
def euclidean(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])
