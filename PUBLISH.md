# How to publish this (5 minutes)

## 1. Make the repo
```
cd second-squeeze
git init
git add .
git commit -m "Second Squeeze: initial scaffold"
```
Create an empty repo on GitHub named `second-squeeze`, then:
```
git remote add origin https://github.com/<you>/second-squeeze.git
git branch -M main
git push -u origin main
```

## 2. Turn on the dashboard (GitHub Pages)
On GitHub: repo → **Settings** → **Pages** → Source = **Deploy from a branch**, branch = **main**, folder = **/ (root)** → Save.
After a minute your live dashboard is at:
`https://<you>.github.io/second-squeeze/`
That link is your Discord submission's front door.

## 3. Drop in your real numbers
Everything except the 2019 paper column is placeholder. When you have results:
- Open `index.html`, find the `DATA` block near the bottom, replace the numbers, set `placeholder: false`. Every chart and table re-draws. No build step.
- Fill `results.csv` (the machine-readable copy).
- Fill `environment.md` (versions, so it actually reproduces).
- `git commit` and `git push` — Pages updates itself.

## Files
- `index.html` — the live dashboard (edit only the `DATA` block).
- `results.csv` — the raw receipt, machine-readable.
- `environment.md` — versions pinned, so a stranger can reproduce.
- `README.md` — the story, the decisions, the claim, the control.
- `LICENSE` — MIT (required by the challenge).
