"""
bench_all.py — Rerun every benchmark and rewrite results.csv.

Prerequisites:
  - Lemonade app/server running on http://localhost:13305
  - Models already pulled: user.gpt2xl, Qwen3-0.6B-GGUF
"""

import re
import subprocess
import csv
from datetime import date
from pathlib import Path

SERVER_URL = "http://localhost:13305"
BENCH_CONFIG = "10iter-5warmup-64prompt-32out"
CSV_PATH = Path(__file__).parent / "results.csv"

# (display_name, model_id, backend_or_None)
RUNS = [
    ("GPT-2 XL", "user.gpt2xl", "cpu"),
    ("Qwen3-0.6B", "Qwen3-0.6B-GGUF", "cpu"),
    ("Qwen3-0.6B", "Qwen3-0.6B-GGUF", None),  # None = default GPU backend
]

MODEL_META = {
    "GPT-2 XL": {"year": "2019", "params": "1.5B", "maker": "OpenAI"},
    "Qwen3-0.6B": {"year": "2025", "params": "0.6B", "maker": "Alibaba"},
}


def run_bench(model_id: str, backend: str | None) -> dict:
    """Run lemonade-eval bench and return parsed metrics."""
    cmd = [
        "lemonade-eval",
        "-i", model_id,
        "load",
        "--server-url", SERVER_URL,
    ]
    if backend is not None:
        cmd += ["--llamacpp-backend", backend]
    cmd.append("bench")

    print(f"  Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    output = result.stdout + "\n" + result.stderr

    metrics = {}
    for line in output.splitlines():
        if "Backend:" in line:
            m = re.search(r"Backend:\s*(.+)", line)
            if m:
                metrics["backend"] = m.group(1).strip()
        if "Token Generation Tokens Per Second:" in line:
            m = re.search(r"Token Generation Tokens Per Second:\s*([\d.]+)", line)
            if m:
                metrics["tokens_per_sec"] = float(m.group(1))
        if "Seconds To First Token:" in line:
            m = re.search(r"Seconds To First Token:\s*([\d.]+)", line)
            if m:
                metrics["ttft_sec"] = float(m.group(1))
        if "Max Memory Used Gbyte:" in line:
            m = re.search(r"Max Memory Used Gbyte:\s*([\d.]+)", line)
            if m:
                metrics["peak_mem_gb"] = float(m.group(1))

    return metrics


def main():
    today = date.today().isoformat()
    rows = []

    for display_name, model_id, backend in RUNS:
        label = f"{display_name} on {backend or 'gpu (default)'}"
        print(f"\n{'='*60}\nBenchmarking: {label}\n{'='*60}")

        metrics = run_bench(model_id, backend)
        meta = MODEL_META[display_name]

        detected_backend = metrics.get("backend", backend or "gpu")
        row = {
            "model": display_name,
            "year": meta["year"],
            "params": meta["params"],
            "maker": meta["maker"],
            "backend": detected_backend,
            "tokens_per_sec": metrics.get("tokens_per_sec", ""),
            "ttft_sec": metrics.get("ttft_sec", ""),
            "peak_mem_gb": metrics.get("peak_mem_gb", ""),
            "bench_config": BENCH_CONFIG,
            "date": today,
        }
        rows.append(row)

    # Write results.csv
    fieldnames = [
        "model", "year", "params", "maker", "backend",
        "tokens_per_sec", "ttft_sec", "peak_mem_gb", "bench_config", "date",
    ]
    with open(CSV_PATH, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\n{'='*60}")
    print(f"Results written to {CSV_PATH}")
    print(f"{'='*60}\n")

    # Summary table
    print(f"{'Model':<14} {'Backend':<8} {'tok/s':<10} {'TTFT(s)':<10} {'Mem(GB)':<10}")
    print("-" * 52)
    for r in rows:
        tps = f"{r['tokens_per_sec']:.3f}" if r["tokens_per_sec"] else "n/a"
        ttft = f"{r['ttft_sec']:.3f}" if r["ttft_sec"] else "n/a"
        mem = f"{r['peak_mem_gb']:.2f}" if r["peak_mem_gb"] else "n/a"
        print(f"{r['model']:<14} {r['backend']:<8} {tps:<10} {ttft:<10} {mem:<10}")


if __name__ == "__main__":
    main()
