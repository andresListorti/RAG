"""Real HTTP smoke test for a running local app/container, using only stdlib."""

import json
import sys
import time
from urllib.error import URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

base = sys.argv[1].rstrip("/")
if urlparse(base).hostname != "127.0.0.1":
    raise ValueError("Smoke tests target loopback only")


def fetch(path, payload=None):
    request = Request(
        base + path,
        data=json.dumps(payload).encode() if payload else None,
        headers={"Content-Type": "application/json"},
    )
    with urlopen(request, timeout=60 if "--expect-llm" in sys.argv else 5) as response:  # nosec B310 -- loopback validated above
        return response.read()


for attempt in range(30):
    try:
        health = json.loads(fetch("/health"))
        if health["status"] != "ok" or health["corpus"]["articles"] != 75:
            raise ValueError("Invalid health response")
        break
    except URLError:
        if attempt == 29:
            raise
        time.sleep(1)
assert b"Consumidor" in fetch("/")
result = json.loads(fetch("/api/ask", {"question": "¿Qué garantía legal tiene un producto nuevo?"}))
assert result["claims"]
if "--expect-llm" in sys.argv:
    assert result["mode"] == "llm" and not result["fallback"]
    assert result["trace"][-1]["method"] == "llm"
assert "11" in {doc["article"] for doc in result["evidence"]}
docs = {doc["id"]: doc for doc in result["evidence"]}
assert all(claim["quote"] in docs[claim["evidence_id"]]["text"] for claim in result["claims"])
outside = json.loads(fetch("/api/ask", {"question": "¿Cómo se calcula la órbita de Marte?"}))
assert not outside["claims"]
print("PASS: real HTTP startup, UI, warranty retrieval, exact citations and abstention")
