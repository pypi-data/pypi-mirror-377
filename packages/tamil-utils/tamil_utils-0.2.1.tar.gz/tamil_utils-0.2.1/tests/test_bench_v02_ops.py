from tamil_utils import word_counts, transliterate_iso15919, sort_tamil

def test_bench_word_counts_unigram(benchmark):
    base = "இது ஒரு சோதனை. தமிழ் உரை பகுப்பாய்வு பயன்பாடுகள். "
    text = base * 400
    benchmark(word_counts, text, rmstop=True, preset="ta", n=1, top=None)

def test_bench_word_counts_bigrams(benchmark):
    base = "தமிழ் NLP தமிழ் பயன்பாடு தமிழ் NLP "
    text = base * 400
    benchmark(word_counts, text, rmstop=False, n=2, top=10)

def test_bench_transliterate_iso(benchmark):
    text = ("ஆதி இலங்கை மொழி தொழில்நுட்பம் " * 600).strip()
    benchmark(transliterate_iso15919, text)

def test_bench_sort_tamil(benchmark):
    words = ["இலங்கை", "ஆதி", "அடி", "தமிழ்", "எழில்", "வேங்கை", "நாடு", "நீலம்"]
    benchmark(sort_tamil, words * 1000)
