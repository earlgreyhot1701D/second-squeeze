![Second Squeeze Banner](banner.png)

# Second Squeeze

*Squeeze a 2019 model and a 2025 model on the same laptop and see what actually changed.* Model archaeology, run entirely on Lemonade.

**Live dashboard:** https://earlgreyhot1701d.github.io/second-squeeze/

## The thing most people have backwards

You can run real AI on a laptop now. Almost everyone assumes that's because the hardware got fast enough. Run the receipts and it's the opposite: the models got radically more efficient. A 2025 model that is **smaller** than a 2019 one (0.6B vs 1.5B parameters) generates tokens about **297× faster on the exact same CPU**, and actually answers the question instead of producing gibberish. The leap was design, not silicon.

That is the non-obvious claim. "Newer is faster" is boring and expected. "A smaller newer model laps a bigger older one by 300× on identical hardware, so the revolution was efficiency, not your chip" is the part worth measuring.

And you can't even see it clearly unless you measure carefully, which is the other half of this project.

## The numbers (same CPU, six years apart)

| Model | Year | Params | tokens/sec (CPU) | First token |
|-------|------|--------|------------------|-------------|
| GPT-2 XL | 2019 | 1.5B | 0.31 | 3.80 s |
| Qwen3-0.6B | 2025 | 0.6B | 90.85 | 0.07 s |

Smaller model, same processor, ~297× faster generation and ~55× quicker to start. Add the GPU and the 2025 model jumps to 359 tok/s (a 4× lift). The 2019 model can't use the GPU at all, its architecture isn't supported on the modern backend, so it's stuck on the CPU it already crawls on.

## Twice, the number tried to fool me (the real spine)

The point of this project isn't the speed. It's how easy it is to measure it wrong:

1. **The backend confound.** My first run compared GPT-2 on CPU to Qwen on GPU and showed a ~1000× gap. Most of that was hardware, not the models. Holding the backend fixed (both on CPU) gives the honest ~297× model gap. One uncontrolled variable, a 3× lie.
2. **The metric wall.** This started as an accuracy project, re-checking GPT-2's famous LAMBADA score. But that benchmark's number depends entirely on how you score it (OpenAI's method vs the standard method differ by ~15 points on the same model), and worse, it can't run through Lemonade at all because Lemonade's API doesn't expose token log-probabilities. So I pivoted to what Lemonade measures cleanly: speed and capability.

Control your variables or the benchmark lies to you. That's the transferable lesson, and I hit it twice with my own hands.

## Two findings I wasn't looking for

- **The 2019 model is so slow it breaks modern software.** At 0.3 tok/s, GPT-2 XL times out the chat interface mid-answer ("network error"). It can't finish a sentence before a modern UI gives up. That's a usability cliff, not a gradient.
- **The 2025 model reasons.** Qwen3-0.6B runs a short "thinking" pass before answering. A 0.6B model out-thinking a 1.5B one.

## Same prompt, different decade

Asked to complete "The capital of France is": GPT-2 (a base model) emits chat-template tokens and Dart import statements. Qwen answers "Paris." See the dashboard.

## The logprobs finding (reported back)

Lemonade's own docs state token log-probabilities aren't available on its API yet, so loglikelihood/multiple-choice evals (LAMBADA, MMLU) can't run through it. That's a concrete gap in the local-eval story, surfaced by actually trying to use it, and filed as a feature request.

## Why this exists

I went to AMD's Advancing AI 2026 summit. The vibecoding lab was built around Lemonade, the first time I'd seen it. I had never run anything locally before, everything I'd built talked to a cloud API with a key. Watching a model answer from a laptop with nothing leaving the machine reframed what "using AI" even means for me. Then I found the Lemonade Developer Challenge, and this is me following that spark to a submission.

Origin recap: https://dev.to/earlgreyhot1701d/amd-advancing-ai-2026-software-hardware-framework-unified-2d2j

## How it was measured

All speed numbers come from Lemonade's `bench` tool: 5 warmup + 10 timed runs, a 64-token prompt, 32 tokens out, identical for every model, backend held fixed for the era comparison. Full versions and exact commands in `environment.md`. Not a reproduction of the original 2019 lab, quantized weights on today's runtime aren't the original setup; every difference (quantization, backend, prompt, hardware) is named on purpose.

## Files
- `index.html` — the live dashboard (GitHub Pages). Edit only the `DATA` block.
- `results.csv` — the raw measurements.
- `environment.md` — versions and commands, so it reproduces.
- `PUBLISH.md` — how to push and turn on Pages.
- `LICENSE` — MIT.

## Measured on
Lenovo IdeaPad Pro 5i, Intel Core Ultra 9 285H, NVIDIA RTX 5050, 32 GB RAM, Windows 11. Lemonade 11.5.0. An AMD-GPU run is possible future work; the challenge allows any hardware.
