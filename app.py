"""Lab 02 - Smart Keyboard V1 (Streamlit UI). Run:  streamlit run app.py"""
import pandas as pd
import streamlit as st

from src.pipeline import NGramModel, EOS, load_documents, backoff_top_k

st.set_page_config(page_title="Smart Keyboard V1", page_icon="⌨️", layout="centered")


@st.cache_resource
def get_models(k):
    docs = load_documents()
    sentences = [s for d in docs.values() for s in d]
    return [NGramModel(sentences, n, k) for n in (3, 2, 1)], len(sentences)


# ------------------------------------------------------------- sidebar
with st.sidebar:
    st.header("Settings")
    k = st.select_slider("Smoothing constant k", options=[0.001, 0.01, 0.1, 0.5, 1.0], value=0.1,
                         help="Add-k smoothing. Small k trusts the counts, large k flattens the distribution.")
    show_n = st.slider("Bars in the chart", 5, 15, 8)
    st.divider()
    st.markdown("**How it works**  \n"
                "Trigram model with add-k smoothing and hard back-off "
                "(3-gram → 2-gram → 1-gram when the context was never seen).")

(tri, bi, uni), n_sent = get_models(k)

# ------------------------------------------------------------- state
if "text" not in st.session_state:
    st.session_state.text = "the happy girls"


def pick(word):
    """Append the chosen suggestion to the text (like tapping a keyboard suggestion)."""
    st.session_state.text = (st.session_state.text.rstrip() + (" ." if word == EOS else " " + word)).strip()


def clear():
    st.session_state.text = ""


# ------------------------------------------------------------- main
st.title("⌨️ Smart Keyboard V1")
st.caption("Next-word suggestions from an n-gram language model. Tap a suggestion to add it to your sentence.")

st.text_input("Type the beginning of a sentence:", key="text")
words = st.session_state.text.lower().replace(".", " . ").split()
unknown = [w for w in words if w not in uni.vocab]

if unknown:
    st.warning(f"Not in the training vocabulary (treated as <unk>): {', '.join(unknown)}")
if not words:
    st.info("Type at least one word - showing how sentences usually start.")

suggestions, order = backoff_top_k(tri, bi, uni, words, 3)
st.subheader("Top-3 suggestions")
cols = st.columns(3)
for i, (col, (w, p)) in enumerate(zip(cols, suggestions)):
    label = "(end)" if w == EOS else w
    col.button(label, key=f"sug{i}", on_click=pick, args=(w,), use_container_width=True)
    col.caption(f"{p:.1%}")

c1, c2 = st.columns([3, 1])
c1.caption(f"Model used: **{order}** · k = {k}")
c2.button("Clear", on_click=clear, use_container_width=True)

with st.expander("Probability distribution"):
    top, _ = backoff_top_k(tri, bi, uni, words, show_n)
    series = pd.Series({("(end)" if w == EOS else w): p for w, p in top}, name="probability")
    st.bar_chart(series)

st.caption(f"Trained on {n_sent} synthetic sentences. Probabilities are model estimates on a tiny "
           "synthetic corpus - not real-world typing statistics.")
