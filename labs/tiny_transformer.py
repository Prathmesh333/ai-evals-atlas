"""Educational byte transformer. CPU default; no downloaded datasets or weights."""
import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
import torch
from torch import nn
from torch.nn import functional as F

HERE = Path(__file__).resolve().parent


class TinyTransformer(nn.Module):
    def __init__(self, context=64, width=64):
        super().__init__()
        self.context = context
        self.token = nn.Embedding(256, width)
        self.position = nn.Embedding(context, width)
        self.layers = nn.ModuleList([
            nn.TransformerEncoderLayer(width, 4, width * 4, dropout=0.1,
                                       batch_first=True, norm_first=True)
            for _ in range(2)
        ])
        self.norm = nn.LayerNorm(width)
        self.head = nn.Linear(width, 256)

    def forward(self, tokens):
        length = tokens.shape[1]
        hidden = self.token(tokens) + self.position(torch.arange(length, device=tokens.device))
        mask = torch.triu(torch.ones(length, length, device=tokens.device, dtype=torch.bool), diagonal=1)
        for layer in self.layers:
            hidden = layer(hidden, src_mask=mask)
        return self.head(self.norm(hidden))


@torch.no_grad()
def evaluate(model, data):
    model.eval()
    total, count = 0.0, 0
    for start in range(0, len(data) - 1, model.context):
        seq = data[start:start + model.context + 1]
        if len(seq) < 2:
            continue
        logits = model(seq[:-1].unsqueeze(0))
        total += F.cross_entropy(logits.reshape(-1, 256), seq[1:], reduction="sum").item()
        count += len(seq) - 1
    return total / count


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--steps", type=int, default=200)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--data", type=Path, default=HERE / "data")
    parser.add_argument("--output", type=Path, default=HERE / "runs")
    args = parser.parse_args()
    if args.steps < 1:
        parser.error("--steps must be positive")
    torch.manual_seed(args.seed)
    torch.set_num_threads(2)
    raw = {name: (args.data / f"{name}.txt").read_bytes() for name in ("train", "validation", "test")}
    if any(len(v) < 65 for v in raw.values()):
        parser.error("Each file needs at least 65 bytes")
    if len(set(raw.values())) != 3:
        parser.error("Splits must not have identical contents")
    data = {k: torch.tensor(list(v), dtype=torch.long) for k, v in raw.items()}
    model = TinyTransformer()
    optimizer = torch.optim.AdamW(model.parameters(), lr=3e-4)
    best_loss = evaluate(model, data["validation"])
    best_state = copy.deepcopy(model.state_dict())
    history = [{"step": 0, "validation_nll": best_loss}]
    for step in range(1, args.steps + 1):
        model.train()
        starts = torch.randint(len(data["train"]) - model.context, (8,))
        batch = torch.stack([data["train"][int(s):int(s) + model.context + 1] for s in starts])
        logits = model(batch[:, :-1])
        loss = F.cross_entropy(logits.reshape(-1, 256), batch[:, 1:].reshape(-1))
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        if step % 25 == 0 or step == args.steps:
            val = evaluate(model, data["validation"])
            history.append({"step": step, "train_nll": loss.item(), "validation_nll": val})
            print(f"step={step} train={loss.item():.3f} validation={val:.3f}")
            if val < best_loss:
                best_loss, best_state = val, copy.deepcopy(model.state_dict())
    model.load_state_dict(best_state)
    test_loss = evaluate(model, data["test"])
    model.eval()
    sequence = torch.tensor([[ord("A")]], dtype=torch.long)
    with torch.no_grad():
        for _ in range(120):
            logits = model(sequence[:, -model.context:])[:, -1, :]
            token = torch.multinomial(F.softmax(logits, dim=-1), num_samples=1)
            sequence = torch.cat((sequence, token), dim=1)
    report = {"description": "Educational smoke experiment, not a trained assistant",
        "torch_version": torch.__version__, "seed": args.seed, "steps": args.steps,
        "config": {"layers": 2, "heads": 4, "width": 64, "context_bytes": 64, "batch": 8, "learning_rate": 3e-4},
        "parameters": sum(p.numel() for p in model.parameters()),
        "sha256": {k: hashlib.sha256(v).hexdigest() for k, v in raw.items()},
        "history": history, "test_nll_nats_per_byte": test_loss, "test_perplexity": math.exp(test_loss),
        "sample": bytes(sequence[0].tolist()).decode("utf-8", errors="replace")}
    args.output.mkdir(parents=True, exist_ok=True)
    torch.save(best_state, args.output / "tiny-transformer.pt")
    (args.output / "tiny-transformer.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
