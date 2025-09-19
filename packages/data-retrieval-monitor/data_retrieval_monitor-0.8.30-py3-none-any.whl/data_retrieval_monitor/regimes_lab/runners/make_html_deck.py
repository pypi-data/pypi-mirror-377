#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Updated: Combines selected Plotly HTML plots into an interactive Reveal.js-based PPT.
- Picks first N files (default 2) from STATS_FIG_DIR.
- Adds intro slide.
- Splits into multiple decks if more than max_per_deck (default 10) slides.
Assumes input files are in STATS_FIG_DIR, named like 'cumret_multi_{factor}_h{horizon}.html'.
Output: interactive_ppt_deck{num}.html (open in browser for slideshow).
"""

import os
import glob
from pathlib import Path
from datetime import datetime

# Update this to your STATS_FIG_DIR path
STATS_FIG_DIR = '/path/to/your/STATS_FIG_DIR'  # e.g., './stats_fig_dir'

# Config
NUM_FILES_TO_USE = 2  # Number of files to pick (first N sorted)
MAX_PER_DECK = 10     # Split into new deck if more slides

# Get all HTML plot files (sorted for consistent order)
html_files = sorted(glob.glob(os.path.join(STATS_FIG_DIR, 'cumret_multi_*.html')))

if not html_files:
    print(f"No 'cumret_multi_*.html' files found in {STATS_FIG_DIR}. Exiting.")
    exit(1)

# Pick first N files
selected_files = html_files[:NUM_FILES_TO_USE]
print(f"Selected {len(selected_files)} files: {[os.path.basename(f) for f in selected_files]}")

# Reveal.js template (with escaped {{ }} for JS code to avoid .format() issues)
reveal_template = """
<!doctype html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">

    <title>Interactive Regime Plots PPT - Deck {deck_num}</title>

    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/reveal.js/4.6.0/reveal.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/reveal.js/4.6.0/theme/white.min.css" id="theme">
    <style>
        .reveal iframe {{
            width: 100%;
            height: 90vh;  /* Adjust height as needed; leaves room for title */
            border: none;
            background: white;
        }}
        .reveal section {{
            text-align: center;
            padding: 20px;
        }}
        .reveal h1, .reveal h2 {{
            margin-bottom: 10px;
            color: #333;
        }}
        .reveal p {{
            font-size: 1.2em;
            color: #666;
        }}
        /* Fullscreen mode for better plot viewing */
        .reveal .slides section > iframe {{
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }}
        /* Intro slide styling */
        .intro {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }}
        .intro h1 {{
            color: white;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        .intro p {{
            color: #f0f0f0;
        }}
    </style>
</head>
<body>
    <div class="reveal">
        <div class="slides">
{slides}
        </div>
    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/reveal.js/4.6.0/reveal.min.js"></script>
    <script>
        Reveal.initialize({{
            hash: true,
            transition: 'slide',  // Or 'fade', 'zoom', etc.
            backgroundTransition: 'fade',
            width: '100%',
            height: '100%',
            margin: 0.1,
            // Enable overview mode (Esc key)
            overview: true,
            // Keyboard shortcuts: arrows, PgUp/Dn, etc.
            keyboard: true
        }});
    </script>
</body>
</html>
"""

# Build intro slide
current_date = datetime.now().strftime("%B %d, %Y")
intro_slide = f"""
        <section class="intro">
            <h1>Interactive Regime Plots Presentation</h1>
            <p>Generated on {current_date}</p>
            <p>Explore cumulative returns with regime shading and controls.</p>
            <p>Use arrow keys to navigate | Press 'O' for overview</p>
        </section>
"""

def build_deck_slides(files_slice, deck_num):
    """Build slides for one deck: intro + selected files."""
    slides_html = intro_slide
    for html_file in files_slice:
        # Extract a readable title from filename (e.g., "Cumret Multi Factor H1")
        title = Path(html_file).stem.replace('_', ' ').title()
        rel_path = os.path.basename(html_file)  # Relative path for iframe src
        slide = f"""
                <section data-background="#f8f9fa">
                    <h2>{title}</h2>
                    <iframe src="{rel_path}" allowfullscreen></iframe>
                </section>
        """
        slides_html += slide
    return slides_html

# Split selected files into decks
decks = []
for i in range(0, len(selected_files), MAX_PER_DECK):
    deck_files = selected_files[i:i + MAX_PER_DECK]
    deck_num = (i // MAX_PER_DECK) + 1
    slides = build_deck_slides(deck_files, deck_num)
    full_html = reveal_template.format(deck_num=deck_num, slides=slides)
    output_ppt = os.path.join(STATS_FIG_DIR, f'interactive_ppt_deck{deck_num}.html')
    with open(output_ppt, 'w', encoding='utf-8') as f:
        f.write(full_html)
    decks.append(output_ppt)

print(f"Generated {len(decks)} deck(s):")
for ppt in decks:
    print(f"  - {ppt}")
print("\nTips:")
print("- Open in browser and use arrow keys to navigate.")
print("- Press 'O' for overview of all slides.")
print("- Press 'Esc' to enter/exit overview.")
print("- Each slide's plot remains fully interactive (checkboxes, buttons, etc.).")
print("- All individual HTML files must be in the same directory as the PPT for iframes to load.")
print("- Customize: Edit NUM_FILES_TO_USE or MAX_PER_DECK at the top of this script.")