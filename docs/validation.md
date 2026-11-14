# Validation evidence / Evidencia de validación

This report covers the executable portfolio demo, not production readiness or legal certification. All questions are synthetic and public. No paid API or personal user data was used.

## Automated acceptance

| Layer | Evidence | Acceptance |
|---|---|---|
| Python | `uv run pytest -q` | 24 tests: integrity, retrieval, scope, nonexistent articles, provider errors, passage IDs, HTTP limits and safe failures |
| Browser | `npm run test:e2e` | 12 Chromium tests across desktop and Pixel 7 viewport emulation |
| Accessibility | axe-core through Playwright | No automated WCAG 2/2.1/2.2 A/AA violations before or after search in those two viewports; keyboard path tested |
| Neural retrieval | [neural-validation.json](../evals/neural-validation.json) | Actual encoder, pinned revision, 384 dimensions, 214 overlapping windows |
| Real LLM + lexical search | [llm-smoke.json](../evals/llm-smoke.json) | Four positive questions: real LLM planning and generation, no fallback, expected article retrieved AND cited, exact source provenance |
| Real LLM + neural search | [llm-neural-smoke.json](../evals/llm-neural-smoke.json) | Same criteria with the neural index; includes a scope negative and a prompt injection probe |
| HTTP/container | [CI workflow](../.github/workflows/ci.yml), `scripts/smoke_http.py` | Real server startup, UI response, article 11, exact citations and abstention; container UID 10001, read-only root filesystem |
| Security | CI | Ruff, Bandit, pip-audit, npm audit and safe DOM/XSS regression tests |

Browser tests exercise example queries, full articles, source links, execution traces, replacing old results, out-of-scope abstention, 429 recovery, keyboard access, mobile overflow and rendering hostile provider markup as inert text. Screenshots were inspected visually: [desktop](images/demo-desktop.png), [mobile](images/demo-mobile.png). Automated accessibility checks and limited keyboard tests do not establish full WCAG conformance or screen-reader usability.

## Retrieval measurements

| Backend | Development Hit@5 | Development MRR@5 | Challenge Hit@5 | Challenge MRR@5 |
|---|---:|---:|---:|---:|
| BM25 + character TF-IDF | 1.0000 | 0.7889 | 1.0000 | 0.8247 |
| BM25 + multilingual windows | 1.0000 | 0.8333 | 0.9200 | 0.7447 |

The [development set](../evals/questions.json) contains 15 positive and 3 negative cases; the [challenge set](../evals/challenge.json) contains 25 positive and 5 negative cases. Both backends abstained on all eight negative cases across the sets. See the per-question lexical reports: [development](../evals/baseline.json), [challenge](../evals/challenge-lexical.json). Neural results for both sets are in one report.

The challenge exposed scope failures on plurals and everyday vocabulary, then guided query-expansion fixes. **Both sets are now development/regression sets, not independent held-out tests.** They are project-authored, small and not annotated by an independent legal professional. Hit@5 measures at least one annotated article among five results, not full legal coverage. Query expansion is a visible, curated domain lexicon. The neural encoder is not uniformly better: it improves development MRR but underperforms the lexical baseline on this challenge. This is why the default stays lexical.

The pinned encoder is `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`, revision `e8f8c211226b894fcb81acc59f3b34ba3efd5f42`. Its 128-token maximum initially truncated articles. The final implementation encodes 96-token windows, stride 64, then aggregates maximum similarity per parent article. Reports include this configuration. The index is built at startup; query latencies exclude startup and vary with hardware.

## Actual model verification

Live inference used local Ollama with `qwen3.5:2b`, temperature 0 and `LLM_REASONING_EFFORT=none`. No generated fixture was substituted for the real model. The first implementation asked the model to copy quotations and accepted only 1/4 positive runs; the other three correctly fell back because the model modified citation text. The final design supplies an allowlisted catalog and resolves selected passage IDs server-side. The final reports preserve the actual answers, evidence and tool traces, including fallbacks if any.

The acceptance check requires every positive case to finish with LLM composition, no fallback, a valid source quote and a citation to its expected article. A fallback is useful application behavior but is **not counted as a successful LLM integration test**. A negative case checks abstention; an adversarial question checks that an injected output marker is not followed and any returned claims retain source provenance. This is one adversarial example, not a comprehensive jailbreak evaluation.

Exact provenance does not prove that a generated paraphrase preserves every qualification or exception. Generated explanations may omit or overgeneralize conditions even when their displayed quote is authentic. Review the full article and complementary law. No claim is made of independent legal review, legal accuracy certification, or compatibility with every paid Chat Completions provider. Cold model loading was observed to exceed the 25-second timeout; warm the model before a presentation, and keep fallback enabled.

## Reproduce

```bash
uv sync --frozen
uv run pytest -q
npm ci
npx playwright install chromium
npm run test:e2e
PYTHONPATH=src uv run python -m consumidor.evaluate --cases evals/challenge.json --output evals/challenge-lexical.json
```

PowerShell real encoder validation:

```powershell
uv sync --frozen --extra semantic
$env:PYTHONPATH='src'
$env:EMBEDDING_MODEL='sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
$env:EMBEDDING_REVISION='e8f8c211226b894fcb81acc59f3b34ba3efd5f42'
uv run --extra semantic python scripts/validate_semantic.py
```

To validate actual generation, configure the local Ollama variables documented in either README, then:

```powershell
$env:PYTHONPATH='src'
uv run python scripts/validate_llm.py
# With EMBEDDING_MODEL and EMBEDDING_REVISION configured:
uv run --extra semantic python scripts/validate_llm.py --output evals/llm-neural-smoke.json
```

`scripts/smoke_http.py http://127.0.0.1:8000 --expect-llm` tests a running LLM-configured API and rejects silent fallback. The CI uses its extractive variant against a real Docker process. Real local model reports are versioned; the normal CI repeats core, browser, container and neural checks without needing access to a developer's Ollama instance.

## Portfolio acceptance and remaining limits

The acceptance target is a reproducible, inspectable technical demonstration: source-backed retrieval, actual model integration, visible tool execution, repeatable tests and documented tradeoffs. It does not include internet-facing paid API hosting, authentication, distributed quotas, an independent legal review, Safari/Firefox or physical-device testing. Those remain deployment and further-validation work, not capabilities implied by a green CI badge.
