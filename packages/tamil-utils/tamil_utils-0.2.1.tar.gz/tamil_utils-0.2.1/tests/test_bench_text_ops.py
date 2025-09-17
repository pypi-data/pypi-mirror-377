from tamil_utils import tokens, graphemes, sents

def test_bench_tokens(benchmark):
    text = "இது ஒரு சோதனை. இது மற்றொரு வரி! 👍🏽" * 100
    benchmark(tokens, text)

def test_bench_graphemes(benchmark):
    text = "👩🏽‍💻தமிழ்🙂" * 200
    benchmark(graphemes, text)

def test_bench_sents(benchmark):
    text = "இது ஒன்று. இது இரண்டு? சரி! " * 200
    benchmark(sents, text)
