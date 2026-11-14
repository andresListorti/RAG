"""Run a real encoder, fail on retrieval regression, and preserve its metadata."""

import json
import os
from pathlib import Path

from consumidor.evaluate import evaluate
from consumidor.ingest import ROOT
from consumidor.retrieval import Retriever

if not os.getenv("EMBEDDING_MODEL"):
    raise ValueError("An actual EMBEDDING_MODEL is required")
retriever = Retriever()
result = evaluate(retriever=retriever)
result["embedding"] = retriever.embedding_metadata
result["challenge"] = evaluate(ROOT / "evals/challenge.json", retriever=retriever)
Path("evals/neural-validation.json").write_text(
    json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n"
)
assert result["hit_at_5"] >= 0.8, result
assert result["out_of_scope_abstention"] == 1, result
assert result["challenge"]["hit_at_5"] >= 0.9, result["challenge"]
assert result["challenge"]["out_of_scope_abstention"] == 1
assert retriever.matrix.shape[1] > 0
print(json.dumps({k: v for k, v in result.items() if k not in {"results", "challenge"}}, indent=2))
