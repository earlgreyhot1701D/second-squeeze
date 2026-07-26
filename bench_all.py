#!/usr/bin/env python3
"""Second Squeeze benchmark runner.

Reruns every Lemonade `bench` measurement and writes results.csv.
Requires the Lemonade server running (default http://localhost:13305)
and the models already pulled (user.gpt2xl, Qwen3-0.6B-GGUF).

Usage:
    python bench_all.py
    python bench_all.py --iterations 20 --warmup 5
"""
import argparse
import csv
import datetime
import re
import subprocess
import sys

# server model id -> descriptive metadata
MODELS = {
    "user.gpt2xl":     {"name": "GPT-2 XL",   "year": 2019, "params": "1.5B", "maker": "OpenAI"},
    "Qwen3-0.6B-GGUF": {"name": "Qwen3-0.6B", "year": 2025, "params": "0.6B", "maker": "Alibaba"},
}

# (server model id, llamacpp backend). None = the server's default backend (GPU here).
RUNS = [
    ("user.gpt2xl",     "cpu"),
    ("Qwen3-0.6B-GGUF", "cpu"),
    ("Qwen3-0.6B-GGUF", None),
]

# result key -> (regex against bench output, converter)
PATTERNS = {
    "backend":        (r"Backend:\s*(.+)",                                str),
    "ttft_sec":       (r"Seconds To First Token:\s*([\d.]+)",             float),
    "tokens_per_sec": (r"Token Generation Tokens Per Second:\s*([\d.]+)", float),
    "peak_mem_gb":    (r"Max Memory Used Gbyte:\s*([\d.]+)",              float),
}
REQUIRED = list(PATTERNS.keys())


def parse_metrics(output):
    """Pull metrics out of a Lemonade `bench` run.

    Raises ValueError if any required metric is missing, so a changed output
    format fails loudly instead of writing a blank cell.
    """
    output = re.sub(r"\x1b\[[0-9;]*m", "", output)  # strip ANSI color codes
    metrics = {}
    for key, (pattern, conv) in PATTERNS.items():
        m = re.search(pattern, output)
        if m:
            metrics[key] = conv(m.group(1).strip())
    missing = [k for k in REQUIRED if k not in metrics]
    if missing:
        raise ValueError(
            "Could not parse {} from bench output. "
            "Lemonade's output labels may have changed.".format(missing)
        )
    return metrics


def run_bench(model_id, backend, args):
    """Run one benchmark and return its parsed metrics. Exit loudly on any failure."""
    cmd = ["lemonade-eval", "-i", model_id, "load", "--server-url", args.server_url]
    if backend is not None:
        cmd += ["--llamacpp-backend", backend]
    cmd += ["bench",
            "--iterations", str(args.iterations),
            "--warmup-iterations", str(args.warmup),
            "--prompts", str(args.prompt_tokens),
            "--output-tokens", str(args.output_tokens)]

    print("  running {} on {} ...".format(model_id, backend or "default(GPU)"))
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=args.timeout)
    except FileNotFoundError:
        sys.exit("ERROR: 'lemonade-eval' not found. Activate your venv and pip install it first.")
    except subprocess.TimeoutExpired:
        sys.exit("ERROR: bench timed out after {}s for {} ({}).".format(args.timeout, model_id, backend))

    if result.returncode != 0:
        sys.stderr.write(result.stdout + "\n" + result.stderr + "\n")
        sys.exit(
            "ERROR: bench failed for {} ({}), exit code {}. "
            "Is the Lemonade server running at {} and the model pulled?".format(
                model_id, backend, result.returncode, args.server_url)
        )

    return parse_metrics(result.stdout)


def main():
    ap = argparse.ArgumentParser(
        description="Rerun Second Squeeze benchmarks and write results.csv")
    ap.add_argument("--server-url", default="http://localhost:13305")
    ap.add_argument("--iterations", type=int, default=10)
    ap.add_argument("--warmup", type=int, default=5)
    ap.add_argument("--prompt-tokens", type=int, default=64)
    ap.add_argument("--output-tokens", type=int, default=32)
    ap.add_argument("--timeout", type=int, default=1200, help="per-benchmark timeout in seconds")
    ap.add_argument("--out", default="results.csv")
    args = ap.parse_args()

    bench_config = "{}iter-{}warmup-{}prompt-{}out".format(
        args.iterations, args.warmup, args.prompt_tokens, args.output_tokens)
    today = datetime.date.today().isoformat()

    # Run everything first; only write the CSV if all runs succeed (no partial data).
    rows = []
    for model_id, backend in RUNS:
        meta = MODELS[model_id]
        m = run_bench(model_id, backend, args)
        rows.append({
            "model": meta["name"], "year": meta["year"], "params": meta["params"],
            "maker": meta["maker"], "backend": m["backend"],
            "tokens_per_sec": m["tokens_per_sec"], "ttft_sec": m["ttft_sec"],
            "peak_mem_gb": m["peak_mem_gb"], "bench_config": bench_config, "date": today,
        })

    fields = ["model", "year", "params", "maker", "backend",
              "tokens_per_sec", "ttft_sec", "peak_mem_gb", "bench_config", "date"]
    with open(args.out, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    print("\nWrote {} rows to {}:".format(len(rows), args.out))
    for r in rows:
        print("  {:<12} {:<14} {:>9} tok/s  {:>6}s first token".format(
            r["model"], r["backend"], r["tokens_per_sec"], r["ttft_sec"]))


if __name__ == "__main__":
    main()
