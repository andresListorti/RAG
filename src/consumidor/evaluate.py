"""Small, transparent regression set. Not a legal or production benchmark."""

import json
from pathlib import Path

from .agent import Agent
from .ingest import ROOT
from .retrieval import Retriever


def evaluate():
    agent = Agent(Retriever())
    cases = json.loads((ROOT / "evals/questions.json").read_text(encoding="utf-8"))
    rows = []
    reciprocal, hits, relevant_count, negatives, abstained = 0, 0, 0, 0, 0
    for case in cases:
        result = agent.run(case["question"])
        retrieved = [d["article"] for d in result["evidence"]]
        relevant = case["relevant"]
        if relevant:
            relevant_count += 1
            ranks = [retrieved.index(a) + 1 for a in relevant if a in retrieved]
            hits += bool(ranks)
            reciprocal += 1 / min(ranks) if ranks else 0
        else:
            negatives += 1
            abstained += not result["claims"]
        rows.append({**case, "retrieved": retrieved, "latency_ms": result["latency_ms"]})
    return {
        "backend": agent.retriever.backend,
        "corpus_sha256": agent.retriever.manifest["corpus_sha256"],
        "cases": len(cases),
        "hit_at_5": round(hits / relevant_count, 4),
        "mrr_at_5": round(reciprocal / relevant_count, 4),
        "out_of_scope_abstention": round(abstained / negatives, 4),
        "results": rows,
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = evaluate()
    encoded = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded, encoding="utf-8")
    print(encoded)
