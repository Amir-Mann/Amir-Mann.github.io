# Amir Mann — Homepage Plan

## Goal
A personal academic homepage at **https://amir-mann.github.io/**, styled after
`orlitany.github.io` and the existing `ResearchCV.pdf`, where the *only*
maintenance task is editing `data/data.json`. Everything else (webpage +
CV PDF) is generated from that one file.

## URL
GitHub Pages serves user sites from a repo literally named `<username>.github.io`.
Your username is `Amir-Mann`, so the repo must be named `Amir-Mann.github.io`
(confirmed available). Final URL: `https://amir-mann.github.io/`.

## Architecture
Single source of truth: `data/data.json`.

```
Amir-Mann.github.io/
├── index.html              # static shell, loads data.json client-side
├── assets/
│   ├── css/style.css        # visual style (Barron/Litany-inspired, minimal)
│   ├── js/render.js         # fetches data.json, renders all sections
│   └── img/profile.jpg      # your photo (add this yourself)
├── data/
│   └── data.json            # <-- THE FILE YOU EDIT to update the site + CV
├── cv/
│   ├── generate_cv.py       # data.json -> LaTeX -> Amir_Mann_CV.pdf
│   └── Amir_Mann_CV.pdf     # generated output, linked from the site
├── .github/workflows/
│   └── build-cv.yml         # CI: rebuild CV PDF when data.json changes
├── .gitignore
├── README.md
└── PLAN.md                  # this file
```

No build step is needed for the webpage itself — `index.html` fetches
`data/data.json` with `fetch()` and renders it in the browser. This works
natively on GitHub Pages with zero configuration.

The CV PDF *does* need a build step (LaTeX compilation), so a GitHub Actions
workflow (`build-cv.yml`) regenerates and commits `cv/Amir_Mann_CV.pdf`
automatically whenever `data/data.json` (or the generator script) changes on
`main`. You never run LaTeX by hand.

## Data model (`data/data.json`)
Top-level keys: `name`, `tagline`, `email`, `phone`, `links` (scholar/github/
linkedin/cv), `photo`, `bio`, `self_author_matches` (name variants of you to
bold in author lists), and these list sections — each renders as a webpage
section AND a CV section, in this order:
`education`, `honors`, `research_experience`, `publications`, `teaching`,
`projects`, `other_experience`.

To add a new publication/degree/honor: append one object to the matching
array in `data.json`, commit, push. The site and the PDF both update.

Each publication/project's `links.project` field (its `<name>.github.io`
project page) is treated as first-class: it renders as a clickable
"Project Page" button on the site and as a `[Project Page]` bracket link
next to the venue in the CV. Currently wired up:
- VideoMDM → https://videomdm.github.io/
- SpectralSplats → https://avigailco.github.io/SpectralSplats/
- Time-to-Move → https://time-to-move.github.io/

`arxiv` links are left blank for now (`data.json`) pending the links you're
sending over.

**Note on the phone number**: `data.json` currently includes your phone
number, which shows up both on the public webpage and in the CV PDF anyone
can download from it. That's a step more exposed than a CV you hand out
directly. Worth a conscious decision — remove it from `data.json`, or leave
it if you're fine with it being public.

## Steps to get this live (things only you can do)
1. **Add a photo (optional)**: drop a square-ish image at `assets/img/profile.jpg`.
2. **Send over your social/arXiv links** so I can fill in the remaining
   blanks in `data.json` (`links.scholar`, `links.linkedin`, each
   publication's `links.arxiv`).
3. **Create the GitHub repo** named exactly `Amir-Mann.github.io` (public).
   I can do this for you via `gh repo create` once you confirm — say the word.
4. **Push the code** (already committed locally; pushing needs your go-ahead).
5. **Enable GitHub Pages**: Settings → Pages → Source: "Deploy from a branch"
   → Branch `main` / folder `/ (root)`. (For a `username.github.io` repo,
   Pages is often auto-enabled on the first push — worth checking first.)
6. **Wait ~1 minute**, then visit `https://amir-mann.github.io/`.
7. **Ongoing use**: whenever you get a new publication/honor/degree, edit
   `data/data.json`, commit, push. That's the entire workflow.

## Design reference
- Layout/tone: minimal, text-first, like `orlitany.github.io` (name + links
  header, bio, then stacked sections; publications get title/authors/venue/
  links).
- Visual language for section headers / rules: mirrors `ResearchCV.pdf`
  (small-caps section labels, hairline rules, right-aligned dates).
- The generated CV PDF reuses the same LaTeX visual style as your current
  `ResearchCV 2026.05.15.pdf` (two-column: label column + content column,
  hairline rules between sections).
