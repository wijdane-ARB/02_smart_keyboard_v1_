# Lab 02 — Smart Keyboard V1 (report)

## Live demo

**App:** https://YOUR-APP-NAME.streamlit.app  <!-- replace with the link given by Streamlit Community Cloud -->

## Run it
```
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python data/make_data.py        # corpus (fixed seed 42)
python -m src.evaluate          # all numbers below -> results/
streamlit run app.py            # live suggestions
```

## 1. Evaluation output
See `results/run_log.txt` (copy of the console output), `results/metrics.json`,
`results/failures.txt`, `results/ngram_results.png`.

| model | perplexity | zero-prob tokens | top-3 |
|---|---|---|---|
| unigram (k=1) | 24.96 | 0.0% | 48.0% |
| bigram (k=1) | 6.43 | 0.0% | 60.9% |
| trigram (k=1) | 8.30 | 0.0% | 64.1% |
| trigram (k=0.1) | 5.06 | 0.0% | 64.1% |
| trigram unsmoothed (k=0) | inf | 4.6% | 64.1% |
| interpolated 3/2/1 (k=0.1) | 5.15 | 0.0% | 64.7% |

Hard back-off (3→2→1, k=0.1): 64.2% top-3.

## 2. Split by document (explained)
The 1,200 sentences form 60 documents of 20 sentences. The last 20% of documents (12) are the test set:
960 train / 240 test sentences. Sentences of one document share topic words; a split by sentence would
leak that vocabulary and context into training and make scores look better than they are.

## 3. Answer in 5 lines
1. The trigram with small smoothing (k=0.1) is the best single model: perplexity 5.06 vs 24.96 for the unigram (about 5x lower) and 6.43 for the bigram (k=1).
2. Top-3 accuracy rises from 48.0% (unigram) to 60.9% (bigram) to 64.1% (trigram); interpolation is marginally best (64.7%).
3. Perplexity is the model's effective branching factor: 5.06 means it is about as unsure as a uniform choice among 5 words (a uniform guess over this vocabulary would be about 61).
4. Without smoothing (k=0), 4.6% of test tokens have probability 0, so log P = -inf and perplexity is infinite: one unseen n-gram ruins the score.
5. Add-k reserves a little probability mass for unseen sequences; but k must be small: k=1 on a trigram spreads k·V over every context and raises perplexity to 8.30.

## 4. Smoothing sweep (60-min track)
Trigram perplexity: k=0.001: 4.96, **k=0.01: 4.63**, k=0.1: 5.06, k=0.5: 6.79, k=1: 8.30, k=2: 10.57, k=5: 15.07.
The curve is U-shaped: too little smoothing makes rare/unseen events too improbable, too much flattens the real
distribution. The best value tried is k≈0.01. The bigram is flatter (best ≈ 5.08 at k=0.01) because its contexts
are denser. Caveat: k was chosen on the test set, which is only acceptable for teaching; a real study needs a
separate validation split and a single final test run (Lab 09). Top-3 accuracy does not change with k inside a
seen context, because k shifts all candidates equally and the ranking stays the same.

## 5. Failure analysis
| type | example | explanation | proposed fix |
|---|---|---|---|
| Ambiguity at sentence start | `the` → *foxes* (suggested doctors, teachers, girls) | After "the" about 20 nouns are almost equally likely; 3 guesses cannot cover them | Show more candidates, or add context (previous sentence / topic of the document) |
| Unseen context | `lazy soup`, `happy bread`, `brave girls` (9 test positions) | The grammar combination never appeared in training, so the trigram has no counts | Back-off / interpolation to the bigram (implemented: `backoff_top_k`, `InterpolatedModel`), or Kneser-Ney |
| Semantic choice | `the foxes eat the` → *cakes* (suggested bread, apples, soup) | Foods are about equally likely; an n-gram has no notion of meaning | Word embeddings / neural model (Lab 07) or more data |

Chosen failure with fix: unseen context `lazy soup`. The trigram context is unseen, so its distribution is
nearly uniform (only k counts). Hard back-off to the bigram `soup` context, or interpolation, recovers
sensible suggestions; the app already does this and displays which order was used.

## 6. Reflection questions
1. **Why is trigram (k=1) worse than bigram (k=1) but better with k=0.1?** Trigram contexts are far more numerous and each has few counts. With k=1 the added k·V (V≈62) in the denominator is large compared with a context's few observations, so the real counts are drowned out. With k=0.1 the correction is small and the more specific trigram information wins.
2. **Would a 5-gram help on 960 sentences?** Unlikely. The number of possible contexts explodes, most test contexts would never be seen (data sparsity), and the grammar only needs short-range dependencies. It would need heavy back-off/interpolation and much more data.
3. **Why is perplexity not comparable between word-level and character-level models?** Perplexity is per token, and the units differ (a word carries many characters and has a far larger vocabulary), so the averaging unit and the branching factor are different. Compare with bits per character or the likelihood of the same text instead.
4. **Privacy:** run the model on-device (the Streamlit app can run locally, the model is a small count table), do not log or send typed text, and keep any personalization local.

## 7. Limits and ethics
Data are synthetic and grammatical by construction (61 word types, regular grammar): perplexities here are far
lower than on real text, where 100+ is normal. Any personal text (e.g. a WhatsApp export) must only be used with
consent and never shared.
