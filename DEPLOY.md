# Deploy on Streamlit Community Cloud (free)

1. Create a GitHub repo and push this folder so that `app.py`, `requirements.txt`, `src/` and `data/corpus.csv`
   are at the repo root (data/corpus.csv must be committed: the app reads it at start-up).
   ```
   git init && git add . && git commit -m "Lab 02 Smart Keyboard V1"
   git branch -M main
   git remote add origin https://github.com/<you>/smart-keyboard-v1.git
   git push -u origin main
   ```
2. Go to https://share.streamlit.io, sign in with GitHub, click "Create app".
3. Pick the repo, branch `main`, main file path `app.py`, then "Deploy".
4. Wait for the build (installs requirements.txt). Copy the public URL `https://<name>.streamlit.app` into your report.

Vercel is not a good fit: Streamlit needs a long-running server and websockets, which Vercel's serverless functions do not provide.
