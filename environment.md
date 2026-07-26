# Environment (for reproduction)

## Versions
- Lemonade: 11.5.0
- lm-eval-harness: 0.4.12
- Python: 3.12.10 (in .venv)
- OS: Windows 11
- lemonade-eval commit: run `git -C lemonade-eval rev-parse --short HEAD` and paste it here

## Hardware / backends
- Machine: Lenovo IdeaPad Pro 5i, Intel Core Ultra 9 285H, NVIDIA RTX 5050, 32 GB RAM
- Era comparison backend: `llamacpp cpu` (held fixed for fairness)
- Hardware comparison: `llamacpp cpu` vs `llamacpp gpu` (NVIDIA CUDA)
- Phase 2 (pending): AMD GPU via ROCm

## Models
- GPT-2 XL (2019, 1.5B): `QuantFactory/gpt2-xl-GGUF:Q8_0` (pulled file gpt2-xl.Q8_0.gguf, ~6.8 GB)
- Qwen3-0.6B (2025, 0.6B): `Qwen3-0.6B-GGUF` (built-in, Q4_0, ~365 MB)

## Benchmark settings (identical for every model)
Lemonade `bench`: 5 warmup + 10 timed iterations, 64-token prompt, 32 output tokens.

## Exact commands
Register GPT-2 XL:
```
lemonade pull user.gpt2xl --checkpoint main "QuantFactory/gpt2-xl-GGUF:Q8_0" --recipe llamacpp
```
Era comparison (both on CPU):
```
lemonade-eval -i user.gpt2xl load --server-url http://localhost:13305 --llamacpp-backend cpu bench
lemonade-eval -i Qwen3-0.6B-GGUF load --server-url http://localhost:13305 --llamacpp-backend cpu bench
```
Hardware comparison (GPU):
```
lemonade-eval -i Qwen3-0.6B-GGUF load --server-url http://localhost:13305 bench
```

## Note on accuracy benchmarks
LAMBADA and other loglikelihood evals can't run through Lemonade: its API doesn't expose token logprobs. See README for the finding.
