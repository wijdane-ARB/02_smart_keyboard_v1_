# Lab 02 — Smart Keyboard V1 (report)

**Student:** Wijdane AARROUB

## Run it
```text
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python data/make_data.py
python -m src.evaluate
streamlit run app.py
```

## 1. Evaluation output

See `results/run_log.txt`, `results/metrics.json`, `results/failures.txt`, and
`results/ngram_results.png`.

| Model | Perplexity | Zero-probability tokens | Top-3 accuracy |
|---|---:|---:|---:|
| Unigram (`k=1`) | 24.96 | 0.0% | 48.0% |
| Bigram (`k=1`) | 6.43 | 0.0% | 60.9% |
| Trigram (`k=1`) | 8.30 | 0.0% | 64.1% |
| Trigram (`k=0.1`) | 5.06 | 0.0% | 64.1% |
| Unsmoothed trigram (`k=0`) | Infinite | 4.6% | 64.1% |
| Interpolated 3/2/1-gram (`k=0.1`) | 5.15 | 0.0% | 64.7% |

Hard back-off (3→2→1, `k=0.1`) achieves 64.2% top-3 accuracy.

## 2. Split by document

The 1,200 sentences form 60 documents of 20 sentences. The last 20% of
documents are the test set: 960 training sentences and 240 test sentences.
Splitting by document avoids leaking related vocabulary and contexts from the
test set into training.

## 3. Required five-line answer

1. The interpolated model has the best top-3 accuracy at 64.7%, while the trigram with `k=0.01` has the best measured perplexity at 4.63.
2. The trigram with `k=0.1` has perplexity 5.06 and top-3 accuracy 64.1%, much better than the unigram's perplexity of 24.96 and accuracy of 48.0%.
3. Perplexity is the model's effective branching factor: a value of 5.06 means it is approximately as uncertain as choosing uniformly among five words.
4. Without smoothing, 4.6% of test tokens have probability zero, so the log probability becomes negative infinity and perplexity is infinite.
5. Add-k smoothing gives unseen sequences nonzero probability, but `k` must remain small because excessive smoothing flattens the distribution and worsens perplexity.

## 4. Smoothing sweep

Trigram perplexity is 4.96 at `k=0.001`, **4.63 at `k=0.01`**, 5.06 at
`k=0.1`, 6.79 at `k=0.5`, 8.30 at `k=1`, 10.57 at `k=2`, and 15.07 at
`k=5`. The best tested value is therefore approximately `k=0.01`.

This sweep uses the test set for teaching purposes. A real study should tune
on a validation split and evaluate once on the final test set.

## 5. Failure analysis

| Failure type | Example | Explanation | Proposed fix |
|---|---|---|---|
| Ambiguity at sentence start | `the` → `foxes` | Many nouns are possible after “the”, so three suggestions cannot cover them all. | Show more candidates or add topic context. |
| Unseen context | `lazy soup`, `happy bread`, `brave girls` | The combination never appeared in training, so the trigram has no learned counts. | Back off to a lower-order model or use interpolation/Kneser-Ney smoothing. |
| Semantic choice | `the foxes eat the` → `cakes` | The n-gram model has no semantic knowledge and several foods are similarly likely. | Use more data or a semantic/neural model. |

For `lazy soup`, hard back-off to the bigram or interpolation provides a more
reliable distribution than relying on the unseen trigram context. The project
already implements both approaches.

## 6. Reflection

1. Trigram contexts are sparser than bigram contexts. With `k=1`, the added `k·V` term overwhelms the few trigram observations; with `k=0.1`, the correction is smaller and the extra context helps.
2. A 5-gram is unlikely to help on 960 training sentences because the number of possible contexts grows rapidly and data sparsity increases.
3. Word-level and character-level perplexities are not directly comparable because they average over different token units and vocabulary sizes.
4. The application can run locally on-device without logging or sending typed text to a server.

## 7. Limits and ethics

The corpus is synthetic and highly regular, so its perplexities are much lower
than those of real text. Personal text should only be used with consent and
must not be shared.
