# amir-mann.github.io

Personal academic homepage, live at **https://amir-mann.github.io/**.

The entire site (and the downloadable CV PDF) is generated from a single
file: [`data/data.json`](data/data.json). See [`PLAN.md`](PLAN.md) for the
full design rationale.

## Updating the site

1. Edit [`data/data.json`](data/data.json) — add a publication, honor,
   degree, whatever changed.
2. Commit and push to `main`.
3. The webpage updates immediately (it reads `data.json` at load time).
   A GitHub Action rebuilds `cv/Amir_Mann_CV.pdf` from the same file and
   commits it automatically within a minute or two.

No HTML/CSS/LaTeX editing required for routine updates.

## Local development

```bash
# serve the site locally
python3 -m http.server 8000
# then open http://localhost:8000/

# regenerate the CV PDF (requires a TeX Live install: pdflatex)
python3 cv/generate_cv.py
```

## Structure

- `index.html`, `assets/` — the static site shell + styling + renderer
  (`assets/js/render.js` fetches `data/data.json` and builds the DOM).
- `data/data.json` — single source of truth for site content and CV.
- `cv/generate_cv.py` — renders `data.json` into LaTeX and compiles it
  with `pdflatex` into `cv/Amir_Mann_CV.pdf`.
- `.github/workflows/build-cv.yml` — CI job that reruns the CV generator
  whenever `data.json` changes on `main`.
