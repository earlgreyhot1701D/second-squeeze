![Second Squeeze Banner](banner.png)

# Second Squeeze

*Squeeze a 2019 model and a 2025 model on the same laptop and see what actually changed.* Model archaeology, run entirely on Lemonade.

**Live dashboard:** https://earlgreyhot1701d.github.io/second-squeeze/

## The thing most people have backwards

You can run real AI on a laptop now. Almost everyone assumes that's because the hardware got fast enough. Run the receipts and the bigger driver is the software: six years of progress across the whole local-AI stack, smaller models, better quantization, instruction tuning, and runtime support, stacked together. A 2025 model that is **smaller** than a 2019 one (0.6B vs 1.5B) generates tokens about **11× faster on the exact same CPU** and actually answers the question. This isn't an isolation of any single cause, it's the practical 2019 stack versus the practical 2025 stack. That gap, not "newer is faster," is what's worth measuring.

## The numbers (same CPU, six years apart)

| Model | Year | Params | tokens/sec (CPU) | First token |
|-------|------|--------|------------------|-------------|
| GPT-2 XL | 2019 | 1.5B | 8.50 | 1.69 s |
| Qwen3-0.6B | 2025 | 0.6B | 90.85 | 0.07 s |

Smaller model, same processor, ~11× faster generation and ~24× quicker to start. Add the GPU and the 2025 model jumps to 347 tok/s (~4× lift). The 2019 model can't use the GPU at all, its architecture isn't supported on the modern backend.

## The number that lied (why this project rebuilt its own headline)

My first GPT-2 XL run measured **0.31 tok/s**, which made the era gap look like **~297×**. Before publishing that, I wrote `bench_all.py` to make every measurement reproducible with one command. The rerun measured **8.5 tok/s**, an **~11×** gap.

The 0.31 was a contaminated first run: the GPU backend was still downloading and the 6.8 GB model was cold off disk while it was timing itself. Qwen, by contrast, reproduced almost exactly (90.845 → 90.853), which proved the harness was stable and the GPT-2 number really had moved. The reproducible ~11× is what's reported here.

The tool I built to make the project rigorous immediately caught the project's own headline. That is the entire thesis of Second Squeeze in one incident: **control your variables and re-run, or the benchmark fools you.**

## Two more ways the number tried to fool me

1. **The backend confound.** An even earlier run compared GPT-2 on CPU to Qwen on GPU and showed a ~1000× gap. Most of that was hardware, not the models. Holding the backend fixed (both on CPU) gives the honest model gap.
2. **The metric wall.** This started as an accuracy project, re-checking GPT-2's famous LAMBADA score. But that benchmark's number depends on how you score it (OpenAI's method vs the standard method differ by ~15 points on the same model), and it can't run through Lemonade at all because Lemonade's API doesn't expose token log-probabilities. So I pivoted to what Lemonade measures cleanly: speed and capability.

## Same prompt, different decade

Asked to complete "The capital of France is": GPT-2 (a base model with no instruction-following) emits chat-template tokens and Dart import statements. Qwen returns a clean, usable answer, "Paris," and even shows a short reasoning pass on the way. GPT-2 can't follow an instruction at all. See the dashboard.

## The logprobs finding (reported back)

Lemonade's own docs state token log-probabilities aren't available on its API yet, so loglikelihood/multiple-choice evals (LAMBADA, MMLU) can't run through it. That's a concrete gap in the local-eval story, surfaced by actually trying to use it, and filed as a feature request.

## Why this exists

I went to AMD's Advancing AI 2026 summit. The vibecoding lab was built around Lemonade, the first time I'd seen it. I had never run anything locally before, everything I'd built talked to a cloud API with a key. Watching a model answer from a laptop with nothing leaving the machine reframed what "using AI" even means for me. Then I found the Lemonade Developer Challenge, and this is me following that spark to a submission.

Origin recap: https://dev.to/earlgreyhot1701d/amd-advancing-ai-2026-software-hardware-framework-unified-2d2j

## Reproduce

Start the Lemonade app (server on `localhost:13305`) with the models pulled, then, inside the project's `.venv`:

```
python bench_all.py             # reruns every benchmark, rewrites results.csv
python -m unittest test_parser  # verifies the output parser (5 tests)
```

`bench_all.py` fails loudly if the server is down, a model is missing, the run errors, or the output format changed. It never writes a partial CSV. Benchmark settings: 5 warmup + 10 timed runs, 64-token prompt, 32 tokens out, backend held fixed for the era comparison. Versions and exact commands in `environment.md`.

## What this is not

Not a reproduction of the original 2019 lab. Quantized weights on today's runtime aren't the original setup. Every difference (parameters, quantization, backend, prompt, hardware) is named on purpose. The gap between "what was claimed" and "what you can verify now" is the story.

## Files
- `index.html` — the live dashboard (GitHub Pages). Edit only the `DATA` block.
- `bench_all.py` — reruns all benchmarks and writes `results.csv`.
- `test_parser.py` — unit tests for the output parser.
- `results.csv` — the raw measurements.
- `environment.md` — versions and commands, so it reproduces.
- `PUBLISH.md` — how to push and turn on Pages.
- `LICENSE` — MIT.

## Measured on
Lenovo IdeaPad Pro 5i, Intel Core Ultra 9 285H, NVIDIA RTX 5050, 32 GB RAM, Windows 11. Lemonade 11.5.0. An AMD-GPU run is possible future work; the challenge allows any hardware.

---

*AI Assisted. Human Reviewed. Powered by NLP.*
