"""BM25 + character TF-IDF (offline) or multilingual neural dense retrieval.

Rankings are fused with reciprocal rank fusion. Scores are ranks, not confidence.
"""

import hashlib
import json
import math
import os
import re
import unicodedata
from collections import Counter

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

from .ingest import DATA

STOP = set("a al con de del el en es la las lo los me mi o para por que se si sin su un una y".split())


def normalize(text):
    return "".join(c for c in unicodedata.normalize("NFD", text.lower()) if unicodedata.category(c) != "Mn")


def tokens(text):
    return [w for w in re.findall(r"[a-z0-9]+", normalize(text)) if w not in STOP and len(w) > 1]


def requested_article(query):
    match = re.search(r"art(?:iculo|\.)?\s*(\d+)(?:\s+(bis|ter|quater))?", normalize(query))
    return match[1] + (" " + match[2] if match[2] else "") if match else None


class Retriever:
    def __init__(self, embedding_model=None):
        corpus = (DATA / "articles.jsonl").read_bytes()
        self.manifest = json.loads((DATA / "manifest.json").read_text(encoding="utf-8"))
        if hashlib.sha256(corpus).hexdigest() != self.manifest["corpus_sha256"]:
            raise ValueError("Corpus integrity check failed; re-run ingestion")
        self.docs = [json.loads(line) for line in corpus.decode().splitlines()]
        self.counts = [Counter(tokens(d["text"])) for d in self.docs]
        self.lengths = np.array([sum(c.values()) for c in self.counts])
        self.avg_length = self.lengths.mean()
        df = Counter(t for c in self.counts for t in c)
        self.idf = {t: math.log(1 + (len(self.docs) - n + 0.5) / (n + 0.5)) for t, n in df.items()}
        model = embedding_model or os.getenv("EMBEDDING_MODEL")
        self.encoder = None
        if model:
            from sentence_transformers import SentenceTransformer

            revision = os.getenv("EMBEDDING_REVISION")
            self.encoder = SentenceTransformer(model, revision=revision, trust_remote_code=False)
            # Encode overlapping windows, so long articles are not silently truncated.
            window = min(96, self.encoder.max_seq_length - 2)
            stride = max(1, window * 2 // 3)
            chunks, parents = [], []
            for parent, doc in enumerate(self.docs):
                ids = self.encoder.tokenizer.encode(doc["text"], add_special_tokens=False, verbose=False)
                for offset in range(0, len(ids), stride):
                    chunks.append(self.encoder.tokenizer.decode(ids[offset : offset + window]))
                    parents.append(parent)
                    if offset + window >= len(ids):
                        break
            self.parents = np.array(parents)
            self.matrix = self.encoder.encode(chunks, normalize_embeddings=True)
            self.backend = f"bm25+neural:{model}"
            self.embedding_metadata = {
                "model": model,
                "requested_revision": revision,
                "max_seq_length": self.encoder.max_seq_length,
                "dimension": self.matrix.shape[1],
                "chunks": len(chunks),
                "window_tokens": window,
                "stride_tokens": stride,
                "aggregation": "maximum child-window cosine per parent article",
            }
        else:
            self.vectorizer = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), strip_accents="unicode")
            self.matrix = self.vectorizer.fit_transform(d["text"] for d in self.docs)
            self.backend = "bm25+char-tfidf (lexical, no neural embeddings)"

    def search(self, query, k=5):
        label = requested_article(query)
        exact = next((i for i, d in enumerate(self.docs) if normalize(d["article"]) == label), None)
        if label and exact is None:
            return []
        words = tokens(query)
        lexical = np.zeros(len(self.docs))
        for word in set(words):
            tf = np.array([c[word] for c in self.counts])
            lexical += (
                self.idf.get(word, 0) * tf * 2.5 / (tf + 1.5 * (0.25 + 0.75 * self.lengths / self.avg_length))
            )
        if self.encoder:
            chunk_scores = self.matrix @ self.encoder.encode(query, normalize_embeddings=True)
            dense = np.full(len(self.docs), -1.0)
            np.maximum.at(dense, self.parents, chunk_scores)
        else:
            dense = (self.matrix @ self.vectorizer.transform([query]).T).toarray().ravel()
        # Require lexical support; avoids presenting unrelated nearest neighbours as evidence.
        eligible = set(np.flatnonzero(lexical > 0).tolist())
        if not eligible:
            return []
        fused = np.zeros(len(self.docs))
        for scores in (lexical, dense):
            for rank, idx in enumerate(np.argsort(-scores)[:20]):
                if idx in eligible:
                    fused[idx] += 1 / (60 + rank + 1)
        if exact is not None:
            fused[exact] += 1
        return [
            {**self.docs[i], "score": round(float(fused[i]), 6)}
            for i in np.argsort(-fused)[:k]
            if fused[i] > 0
        ]
