"""Collect one response per case from a compatible chat-completions endpoint.

This client is deliberately non-streaming and sequential. It measures request
duration, not time to first token or throughput. Expected answers are never sent.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, HTTPRedirectHandler, build_opener

from evaluate import load_cases

HERE = Path(__file__).resolve().parent
SYSTEM = "Follow the user's output format exactly. Return only the requested answer."


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def endpoint_url(base_url):
    parts = urlsplit(base_url)
    if parts.username or parts.password or parts.query or parts.fragment:
        raise ValueError("Base URL must not contain credentials, a query, or a fragment")
    local = parts.hostname in {"localhost", "127.0.0.1", "::1"}
    if not parts.hostname or parts.scheme not in {"http", "https"} or (parts.scheme == "http" and not local):
        raise ValueError("Use HTTPS for remote endpoints; HTTP is allowed only for localhost")
    return base_url.rstrip("/") + "/chat/completions"


def collect(cases, model, base_url, api_key="", timeout=60, max_tokens=128):
    if not model.strip():
        raise ValueError("Model name is required")
    if not math.isfinite(timeout) or timeout <= 0 or max_tokens < 1:
        raise ValueError("Timeout and output budget must be positive")
    url = endpoint_url(base_url)
    opener = build_opener(NoRedirect)
    predictions, attempts = {}, []
    for case in cases:
        payload = {"model": model, "messages": [{"role": "system", "content": SYSTEM},
                    {"role": "user", "content": case["input"]}],
                    "temperature": 0, "max_tokens": max_tokens, "stream": False}
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = "Bearer " + api_key
        request = Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
        started = time.perf_counter()
        record = {"id": case["id"], "status": "failed"}
        try:
            with opener.open(request, timeout=timeout) as response:
                raw = response.read(16 * 1024 * 1024 + 1)
                if len(raw) > 16 * 1024 * 1024:
                    raise ValueError("Response exceeds the 16 MiB limit")
                result = json.loads(raw)
            answer = result["choices"][0]["message"]["content"]
            if not isinstance(answer, str):
                raise ValueError("Expected a string in choices[0].message.content")
            predictions[case["id"]] = answer
            record.update(status="ok", returned_model=result.get("model"), usage=result.get("usage"),
                          finish_reason=result["choices"][0].get("finish_reason"))
        except HTTPError as error:
            # Do not log response bodies, credentials, or server-provided error text.
            record["error"] = f"HTTP {error.code}"
        except (URLError, TimeoutError, OSError):
            record["error"] = "Connection error or timeout"
        except (ValueError, KeyError, IndexError, TypeError):
            record["error"] = "Response does not match the required completion schema"
        record["request_seconds"] = time.perf_counter() - started
        attempts.append(record)
    return predictions, attempts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", required=True)
    parser.add_argument("--base-url", default="http://127.0.0.1:1234/v1")
    parser.add_argument("--cases", type=Path, default=HERE / "data" / "cases.jsonl")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--timeout", type=float, default=60)
    parser.add_argument("--max-tokens", type=int, default=128)
    args = parser.parse_args()
    if (args.output / "predictions.json").exists() or (args.output / "manifest.json").exists():
        parser.error("Output already contains a run. Choose a new directory to preserve the existing evidence.")
    try:
        cases = load_cases(args.cases)
        predictions, attempts = collect(cases, args.model, args.base_url,
            os.environ.get("AI_EVAL_API_KEY", ""), args.timeout, args.max_tokens)
    except (ValueError, OSError) as error:
        parser.error(str(error))
    manifest = {"created_utc": datetime.now(timezone.utc).isoformat(), "requested_model": args.model,
        "endpoint": endpoint_url(args.base_url), "system_instruction": SYSTEM,
        "settings": {"temperature": 0, "max_tokens": args.max_tokens, "stream": False,
                     "timeout_seconds": args.timeout, "attempts_per_case": 1, "concurrency": 1},
        "cases_sha256": hashlib.sha256(args.cases.read_bytes()).hexdigest(),
        "case_count": len(cases), "successful_responses": len(predictions), "attempts": attempts,
        "timing_scope": "Non-streaming client request duration; not first-token latency or server-only compute"}
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "predictions.json").write_text(json.dumps(predictions, indent=2, ensure_ascii=False), encoding="utf-8")
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Saved {len(predictions)}/{len(cases)} responses. Failed requests remain missing predictions and count as failed tasks.")
    print(f"Run files: {args.output}")


if __name__ == "__main__":
    main()
