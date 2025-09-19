#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Create a Beamer (LaTeX) slide deck from a subset of generated PNGs.

Usage:
  python -m regimes_lab.runners.make_beamer_from_figs \
      --title "Regime Results" \
      --output ./regimes_lab/output/stats/figures/RegimeDeck.tex \
      ./regimes_lab/output/stats/figures/cumret_multi_Factor_01.png \
      ./regimes_lab/output/stats/figures/cumret_multi_Factor_03.png

Notes:
- This expects PNGs written by run_shifted_bands_plotly (install kaleido).
- Compile with: pdflatex RegimeDeck.tex
"""

import os, argparse, textwrap

TEX_HEADER = r"""
\documentclass{beamer}
\usepackage[utf8]{inputenc}
\usepackage{graphicx}
\usetheme{Madrid}
\title{%s}
\author{Regimes Lab}
\date{\today}
\begin{document}
\frame{\titlepage}
"""

TEX_FOOTER = r"""
\end{document}
"""

FRAME_TPL = r"""
\begin{frame}{%s}
\begin{center}
\includegraphics[width=\linewidth]{%s}
\end{center}
\end{frame}
"""

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--title", type=str, default="Regime Shading Results")
    ap.add_argument("--output", type=str, required=True, help="Path to .tex output")
    ap.add_argument("images", nargs="+", help="PNG images to include (one per slide)")
    args = ap.parse_args()

    out_dir = os.path.dirname(os.path.abspath(args.output))
    os.makedirs(out_dir, exist_ok=True)

    frames = []
    for img in args.images:
        if not os.path.exists(img):
            print(f"[beamer] WARN: missing image {img}, skipping.")
            continue
        title = os.path.splitext(os.path.basename(img))[0].replace("_", r"\_")
        frames.append(FRAME_TPL % (title, img))

    tex = TEX_HEADER % args.title + "\n".join(frames) + TEX_FOOTER
    with open(args.output, "w", encoding="utf-8") as fh:
        fh.write(tex)
    print(f"[beamer] wrote {args.output}")
    print("Compile with: pdflatex", args.output)

if __name__ == "__main__":
    main()