"""Train and evaluate an inspectable character LM. Python standard library only."""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path
import random

HERE = Path(__file__).resolve().parent


def fit(text):
    vocab = sorted(set(text)) + ["<UNK>"]
    counts = defaultdict(Counter)
    for a, b in zip(text, text[1:]):
        counts[a][b] += 1
    return vocab, counts, Counter(text)


def evaluate(text, vocab, counts, unigram, alpha, order=2):
    known = set(vocab)
    tokens = [c if c in known else "<UNK>" for c in text]
    if len(tokens) < 2:
        raise ValueError("Each split needs at least two characters")
    losses = []
    for previous, target in zip(tokens, tokens[1:]):
        row = counts.get(previous, {}) if order == 2 else unigram
        probability = (row.get(target, 0) + alpha) / (sum(row.values()) + alpha * len(vocab))
        losses.append(-math.log(probability))
    loss = sum(losses) / len(losses)
    return {"nll_nats_per_character": loss, "perplexity": math.exp(loss),
            "scored_characters": len(losses), "unknown_rate": tokens.count("<UNK>") / len(tokens)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("train", "validation", "test"):
        parser.add_argument(f"--{name}", type=Path, default=HERE / "data" / f"{name}.txt")
    parser.add_argument("--output", type=Path, default=HERE / "runs" / "tiny-lm.json")
    args = parser.parse_args()
    splits = {name: getattr(args, name).read_text(encoding="utf-8") for name in ("train", "validation", "test")}
    if any(len(value) < 2 for value in splits.values()):
        parser.error("Each split needs at least two characters")
    if len(set(splits.values())) != 3:
        parser.error("Splits must not have identical contents")
    vocab, counts, unigram = fit(splits["train"])
    candidates = [0.01, 0.1, 0.5, 1.0]
    reports = {}
    for order in (1, 2):
        scores = {alpha: evaluate(splits["validation"], vocab, counts, unigram, alpha, order)["nll_nats_per_character"] for alpha in candidates}
        chosen = min(scores, key=scores.get)
        reports[f"order_{order}"] = {"alpha": chosen, "validation_losses": scores,
            "test": evaluate(splits["test"], vocab, counts, unigram, chosen, order)}
    rng = random.Random(42)
    current = splits["train"][0]
    generated = current
    alpha = reports["order_2"]["alpha"]
    for _ in range(200):
        row = counts.get(current, {})
        current = rng.choices(vocab, weights=[row.get(c, 0) + alpha for c in vocab])[0]
        generated += current
    report = {"description": "Synthetic teaching experiment; not a capability benchmark", "seed": 42,
        "sha256": {k: hashlib.sha256(v.encode()).hexdigest() for k, v in splits.items()},
        "vocabulary_size": len(vocab), "models": reports, "sample": generated}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
