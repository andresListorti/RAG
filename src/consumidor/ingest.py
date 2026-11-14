"""Download only the allowlisted official source; preserve article boundaries."""

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
SOURCE = "https://www.argentina.gob.ar/normativa/nacional/ley-24240-638/actualizacion"
ARTICLE = re.compile(
    r"^ART[IÍ]CULO\s+(\d+)[º°.]?\s*(bis|ter|qu[aá]ter)?(?=\s|[:.\-—])",
    re.IGNORECASE | re.MULTILINE,
)


def parse_articles(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()
    # The official page contains historical amendments after the law. Stop there.
    text = soup.get_text("\n", strip=True).replace("\xa0", " ")
    text = re.split(r"Archivos anexos|Antecedentes Normativos", text, flags=re.I)[0]
    matches = list(ARTICLE.finditer(text))
    records = []
    seen = set()
    for i, match in enumerate(matches):
        article = match.group(1) + (f" {match.group(2).lower()}" if match.group(2) else "")
        if article in seen:
            # Infoleg explicitly documents two article 66s. Preserve both.
            if article == "66" and "Comuníquese" in text[match.start() : match.start() + 100]:
                article = "66 cierre"
            else:
                raise ValueError(f"Duplicate article {article}; source markup needs review")
        seen.add(article)
        body = text[match.start() : matches[i + 1].start() if i + 1 < len(matches) else len(text)]
        body = re.split(r"(?m)^(?:CAP[IÍ]TULO|T[IÍ]TULO)\s+[IVX]+", body)[0]
        records.append(
            {
                "id": f"ley24240-art-{article.replace(' ', '-')}",
                "article": article,
                "text": body.strip(),
                "source": SOURCE,
            }
        )
    if len(records) < 60 or not {"1", "11", "34", "66"}.issubset(seen):
        raise ValueError(f"Unexpected source structure: {len(records)} articles")
    return records


def main():
    request = Request(SOURCE, headers={"User-Agent": "ConsumidorRAG/0.1 (educational portfolio)"})
    # B310: SOURCE is a fixed HTTPS constant, never supplied by a user.
    with urlopen(request, timeout=30) as response:  # nosec B310
        if response.url != SOURCE:
            raise ValueError("Source redirected; review URL before ingestion")
        raw = response.read(4_000_001)
    if len(raw) > 4_000_000:
        raise ValueError("Source exceeds size limit")
    DATA.mkdir(exist_ok=True)
    (DATA / "raw").mkdir(exist_ok=True)
    (DATA / "raw" / "ley24240.html").write_bytes(raw)
    records = parse_articles(raw.decode("utf-8"))
    corpus = "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in records)
    metadata = {
        "source": SOURCE,
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "corpus_sha256": hashlib.sha256(corpus.encode()).hexdigest(),
        "articles": len(records),
        "parser_version": 1,
        "scope": "Ley 24.240; texto actualizado recuperado, sin garantía de vigencia futura",
    }
    (DATA / "articles.jsonl").write_bytes(corpus.encode("utf-8"))
    (DATA / "manifest.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(metadata, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
