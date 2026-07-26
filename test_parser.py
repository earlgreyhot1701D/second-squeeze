"""Unit tests for the bench-output parser.

Run:  python -m unittest test_parser

These guard against Lemonade silently changing its output labels: if a metric
can no longer be found, parse_metrics raises instead of writing a blank cell.
"""
import unittest

from bench_all import parse_metrics

# A real captured Qwen3-0.6B GPU benchmark output.
SAMPLE_GPU = """
Qwen3-0.6B-GGUF:
        Checkpoint:                         Qwen3-0.6B-GGUF
        Backend:                            llamacpp gpu
        Seconds To First Token:             0.015
        Std Dev Seconds To First Token:     0.002
        Token Generation Tokens Per Second: 358.662
        Std Dev Tokens Per Second:          6.915
        Prefill Tokens Per Second:          4165.663
        Max Memory Used Gbyte:              9.361
"""

# A real captured GPT-2 XL CPU benchmark output.
SAMPLE_CPU = """
user.gpt2xl:
        Backend:                            llamacpp cpu
        Seconds To First Token:             3.798
        Token Generation Tokens Per Second: 0.306
        Max Memory Used Gbyte:              8.382
"""


class TestParseMetrics(unittest.TestCase):
    def test_parses_gpu_output(self):
        m = parse_metrics(SAMPLE_GPU)
        self.assertEqual(m["backend"], "llamacpp gpu")
        self.assertAlmostEqual(m["tokens_per_sec"], 358.662)
        self.assertAlmostEqual(m["ttft_sec"], 0.015)
        self.assertAlmostEqual(m["peak_mem_gb"], 9.361)

    def test_parses_cpu_output(self):
        m = parse_metrics(SAMPLE_CPU)
        self.assertEqual(m["backend"], "llamacpp cpu")
        self.assertAlmostEqual(m["tokens_per_sec"], 0.306)

    def test_does_not_confuse_prefill_with_generation(self):
        # "Prefill Tokens Per Second" must not be picked up as the generation rate.
        m = parse_metrics(SAMPLE_GPU)
        self.assertNotAlmostEqual(m["tokens_per_sec"], 4165.663)

    def test_strips_ansi_color_codes(self):
        # Lemonade colorizes output; the reset code must not end up in the CSV.
        colored = "Backend:                            llamacpp cpu\x1b[0m\n" \
                  "Seconds To First Token:             1.689\n" \
                  "Token Generation Tokens Per Second: 8.499\n" \
                  "Max Memory Used Gbyte:              9.703\n"
        m = parse_metrics(colored)
        self.assertEqual(m["backend"], "llamacpp cpu")

    def test_raises_when_metric_missing(self):
        with self.assertRaises(ValueError):
            parse_metrics("Backend: llamacpp cpu\n(no speed metrics here)")


if __name__ == "__main__":
    unittest.main()
