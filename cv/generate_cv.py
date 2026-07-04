#!/usr/bin/env python3
"""
Generate Amir_Mann_CV.pdf from data/data.json.

Usage:
    python3 cv/generate_cv.py

Reads ../data/data.json (relative to this file), renders a .tex file in the
same two-column / hairline-rule visual style as the original ResearchCV.pdf,
and compiles it with pdflatex into cv/Amir_Mann_CV.pdf.

This is the ONLY place that needs to know LaTeX. To change CV content, edit
data/data.json -- do not edit the generated .tex/.pdf by hand.
"""
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "data" / "data.json"
OUTPUT_PDF = Path(__file__).resolve().parent / "Amir_Mann_CV.pdf"

LINK_LABELS = {
    "scholar": "Google Scholar",
    "github": "GitHub",
    "linkedin": "LinkedIn",
    "arxiv": "arXiv",
    "project": "Project Page",
    "code": "Code",
    "pdf": "PDF",
}

_LATEX_SPECIAL = {
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
    "\\": r"\textbackslash{}",
}
_UNICODE_SUBS = {
    "—": "---",
    "–": "--",
    "’": "'",
    "‘": "`",
    "“": "``",
    "”": "''",
    "×": r"$\times$",
    "†": r"$^{\dagger}$",
}

_MD_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


def esc(text):
    """Escape a plain string for LaTeX. Supports inline [text](url) markdown links."""
    if not text:
        return ""

    def esc_plain(s):
        out = []
        for ch in s:
            if ch in _LATEX_SPECIAL:
                out.append(_LATEX_SPECIAL[ch])
            elif ch in _UNICODE_SUBS:
                out.append(_UNICODE_SUBS[ch])
            else:
                out.append(ch)
        return "".join(out)

    parts = []
    last = 0
    for m in _MD_LINK_RE.finditer(text):
        parts.append(esc_plain(text[last:m.start()]))
        label, url = m.group(1), m.group(2)
        parts.append(r"\href{%s}{%s}" % (url, esc_plain(label)))
        last = m.end()
    parts.append(esc_plain(text[last:]))
    return "".join(parts)


def bracket_links(links):
    """Render {'arxiv': 'url', ...} as '[arXiv] [Project Page]' with real hyperlinks."""
    items = [(k, v) for k, v in (links or {}).items() if v]
    if not items:
        return ""
    return " ".join(
        r"[\href{%s}{%s}]" % (url, LINK_LABELS.get(key, key.title()))
        for key, url in items
    )


def bold_self(authors, self_matches):
    rendered = []
    for a in authors:
        bare = a.rstrip("†")
        if bare in self_matches:
            rendered.append(r"\textbf{%s}" % esc(a))
        else:
            rendered.append(esc(a))
    return ", ".join(rendered)


def row(label, content):
    return r"\textbf{\scshape %s} & %s \\" % (esc(label), content)


# NOTE: inside a tabular/longtable cell, "\\" always ends the table ROW, even
# inside a p{} column. To break a line *within* a cell you must use
# \newline instead, and \par (+ \vspace) to separate stacked entries.
LINE = r"\newline" + "\n"


def join_lines(lines):
    return LINE.join(lines)


def join_entries(blocks, gap="5pt"):
    return (r"\par\vspace{%s}" % gap + "\n").join(blocks)


def hline():
    return r"\noalign{\vskip 4pt}\hline\noalign{\vskip 4pt}" + "\n"


def build_education(items):
    blocks = []
    for e in items:
        lines = [r"\textbf{%s} \hfill {\color{muted}%s}" % (esc(e["degree"]), esc(e.get("dates", "")))]
        lines.append(esc(e["institution"]))
        details = e.get("details") or []
        if details:
            lines.append(r"{\footnotesize %s}" % esc("; ".join(details)))
        blocks.append(join_lines(lines))
    return join_entries(blocks)


def build_honors(items):
    lines = []
    for h in items:
        if h.get("dates"):
            lines.append(r"%s \hfill {\color{muted}%s}" % (esc(h["title"]), esc(h["dates"])))
        else:
            lines.append(esc(h["title"]))
    return join_lines(lines)


def build_research_experience(items):
    blocks = []
    for r_ in items:
        lines = [r"\textbf{%s --- %s} \hfill {\color{muted}%s}" % (esc(r_["org"]), esc(r_["role"]), esc(r_.get("dates", "")))]
        if r_.get("description"):
            lines.append(r"{\footnotesize %s}" % esc(r_["description"]))
        blocks.append(join_lines(lines))
    return join_entries(blocks)


def build_publications(items, self_matches):
    blocks = []
    for p in items:
        lines = [r"\textbf{%s}" % esc(p["title"])]
        authors_line = bold_self(p["authors"], self_matches)
        if p.get("note"):
            authors_line += " (%s)" % esc(p["note"])
        lines.append(authors_line)
        links = bracket_links(p.get("links"))
        tail = " ".join(filter(None, [esc(p.get("year", "")), links]))
        lines.append(r"{\slshape %s} \hfill %s" % (esc(p.get("venue", "")), tail))
        blocks.append(join_lines(lines))
    return join_entries(blocks)


def build_teaching(items):
    blocks = []
    for t in items:
        course = esc(t["course"])
        if t.get("course_number"):
            course += " (%s)" % esc(t["course_number"])
        lines = [r"\textbf{%s --- %s} \hfill {\color{muted}%s}" % (esc(t["role"]), course, esc(t.get("dates", "")))]
        lines.append(esc(t["org"]))
        blocks.append(join_lines(lines))
    return join_entries(blocks)


def build_projects(items):
    blocks = []
    for p in items:
        lines = [r"\textbf{%s} \hfill {\color{muted}%s}" % (esc(p["title"]), esc(p.get("dates", "")))]
        lines.append(esc(p["org"]))
        desc = p.get("description", "")
        links = bracket_links(p.get("links"))
        tail = " ".join(filter(None, [esc(desc), links]))
        if tail:
            lines.append(r"{\footnotesize %s}" % tail)
        blocks.append(join_lines(lines))
    return join_entries(blocks)


def build_other_experience(items):
    blocks = []
    for o in items:
        lines = [r"\textbf{%s --- %s} \hfill {\color{muted}%s}" % (esc(o["role"]), esc(o["org"]), esc(o.get("dates", "")))]
        if o.get("description"):
            lines.append(r"{\footnotesize %s}" % esc(o["description"]))
        blocks.append(join_lines(lines))
    return join_entries(blocks)


SECTIONS = [
    ("Education", "education", lambda d: build_education(d["education"])),
    ("Awards & Honors", "honors", lambda d: build_honors(d["honors"])),
    ("Research Experience", "research_experience", lambda d: build_research_experience(d["research_experience"])),
    ("Publications", "publications", lambda d: build_publications(d["publications"], d.get("self_author_matches", []))),
    ("Teaching", "teaching", lambda d: build_teaching(d["teaching"])),
    ("Academic Projects", "projects", lambda d: build_projects(d["projects"])),
    ("Other Experience", "other_experience", lambda d: build_other_experience(d["other_experience"])),
]

PREAMBLE = r"""
\documentclass[10pt]{article}
\usepackage[letterpaper,margin=0.7in]{geometry}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{times}
\usepackage{textcomp}
\usepackage{xcolor}
\usepackage{longtable}
\usepackage{array}
\usepackage{hyperref}
\hypersetup{colorlinks=true, urlcolor=blue, linkcolor=blue}
\definecolor{muted}{gray}{0.45}
\setlength{\arrayrulewidth}{0.3pt}
\renewcommand{\arraystretch}{1.0}
\pagestyle{empty}
\setlength{\parindent}{0pt}
"""


def build_tex(data):
    name = esc(data["name"])
    contact_bits = []
    if data.get("email"):
        contact_bits.append(r"\href{mailto:%s}{%s}" % (data["email"], esc(data["email"])))
    if data.get("phone"):
        contact_bits.append(esc(data["phone"]))
    for key, url in (data.get("links") or {}).items():
        if not url or key == "cv":
            continue
        contact_bits.append(r"\href{%s}{%s}" % (url, LINK_LABELS.get(key, key.title())))
    contact_line = r" \textbar\ ".join(contact_bits)

    rows = []
    for title, key, builder in SECTIONS:
        items = data.get(key)
        if not items:
            continue
        rows.append(row(title, builder(data)))
    body_rows = ("\n" + hline()).join(rows)

    tex = PREAMBLE + r"""
\begin{document}
\begin{center}
{\Huge \textbf{%(name)s}}\\[4pt]
%(contact)s
\end{center}
\vspace{6pt}

\begin{longtable}{@{}p{0.16\textwidth}@{\hspace{10pt}}p{0.80\textwidth}@{}}
%(rows)s
\end{longtable}

\end{document}
""" % {"name": name, "contact": contact_line, "rows": body_rows}
    return tex


def compile_pdf(tex_source, output_pdf):
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        tex_file = tmp / "cv.tex"
        tex_file.write_text(tex_source, encoding="utf-8")
        for _ in range(2):  # run twice to settle hyperref references
            result = subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", tex_file.name],
                cwd=tmp,
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                log = (tmp / "cv.log")
                print(result.stdout[-4000:])
                print(result.stderr[-2000:])
                if log.exists():
                    print(log.read_text(encoding="utf-8", errors="ignore")[-4000:])
                raise RuntimeError("pdflatex failed, see log above")
        shutil.copy(tmp / "cv.pdf", output_pdf)


def main():
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    tex = build_tex(data)
    debug_tex = Path(__file__).resolve().parent / "_last_build.tex"
    debug_tex.write_text(tex, encoding="utf-8")
    compile_pdf(tex, OUTPUT_PDF)
    print(f"Wrote {OUTPUT_PDF}")


if __name__ == "__main__":
    sys.exit(main())
