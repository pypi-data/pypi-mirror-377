#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Serve and present interactive Plotly HTML figures with a landing page,
intro block, file browser, and a slideshow that embeds each HTML figure.

Run:
  python -m regimes_lab.runners.present --host 0.0.0.0 --port 5000

Keyboard in slideshow:
  ← / →  : previous / next
  S      : show files list
"""

import os
import argparse
from pathlib import Path
from flask import (
    Flask, send_from_directory, render_template_string,
    url_for, abort, request, redirect, jsonify
)

# Pull the output directory from your configs module
try:
    from regimes_lab.configs import STATS_FIG_DIR
except Exception:
    # Fallback if configs import fails; you can hardcode or adjust as needed
    STATS_FIG_DIR = "./regimes_lab/output/stats/figures"

APP_TITLE = "Interactive Figures"
AUTHOR = "Donggeun Kim"

app = Flask(__name__)

def _fig_dir() -> Path:
    return Path(STATS_FIG_DIR).resolve()

def _list_figs():
    d = _fig_dir()
    if not d.exists():
        return []
    # sort by name for determinism
    return sorted([f.name for f in d.iterdir() if f.suffix.lower() == ".html"])

INTRO_BLOCK = f"""
<div id="intro-block" style="font-family:Inter, system-ui, Arial, sans-serif; margin: 10px 0 14px 0; line-height:1.45;">
  <div style="font-size:22px; font-weight:800; margin-bottom:2px;">
    Regime Significance & Model-Generalization Lab
  </div>
  <div style="color:#333; font-size:14px;">
    Goal: identify <b>statistically significant regimes</b> and expand the module to automate which regimes
    matter by testing their dummies on residual factor-return data. Any predictive model can be treated as a
    regime generator (e.g., sign of predicted return ⇒ Long/Short regimes), so we test significance of
    <i>predictions-as-regimes</i> too. Significant components (classical alpha) can be included in the
    overall prediction stack.
  </div>
  <div style="margin-top:6px; font-size:13px; color:#555;">
    This presenter serves the generated interactive HTML figures directly for live, in-slide exploration.
  </div>
  <div style="margin-top:6px; font-size:13px; color:#555;">
    Author: <b>{AUTHOR}</b>
  </div>
  <hr style="border:none; height:1px; background:#eee; margin:12px 0 0 0;">
</div>
"""

INDEX_TMPL = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>{{ title }}</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <style>
    body { font-family: Inter, system-ui, Arial, sans-serif; margin: 18px; }
    .btn { display:inline-block; padding:8px 12px; border-radius:8px; border:1px solid #ccc; background:#fafafa; text-decoration:none; color:#222; font-size:14px; }
    .btn:hover { background:#f2f2f2; }
    .grid { display:grid; gap:8px; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); margin-top:10px; }
    .card { border:1px solid #eee; border-radius:10px; padding:10px 12px; background:#fff; }
    .name { font-weight:600; font-size:14px; margin-bottom:6px; }
    .sm { font-size:12px; color:#666; }
    .topbar { display:flex; align-items:center; gap:10px; margin-bottom:10px; }
  </style>
</head>
<body>
  {{ intro|safe }}

  <div class="topbar">
    <div style="font-size:18px; font-weight:700;">{{ title }}</div>
    <div class="sm">Serving from <code>{{ root }}</code></div>
    {% if files %}
      <a class="btn" href="{{ url_for('slideshow') }}">Start slideshow</a>
    {% endif %}
  </div>

  {% if not files %}
    <div class="sm">No HTML figures found in <code>{{ root }}</code>.</div>
  {% else %}
    <div class="grid">
      {% for f in files %}
        <div class="card">
          <div class="name">{{ f }}</div>
          <div class="sm">
            <a class="btn" href="{{ url_for('view', name=f) }}">Preview</a>
            <a class="btn" href="{{ url_for('files', filename=f) }}" target="_blank">Open raw</a>
          </div>
        </div>
      {% endfor %}
    </div>
  {% endif %}
</body>
</html>
"""

VIEW_TMPL = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Preview – {{ name }}</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <style>
    body { font-family: Inter, system-ui, Arial, sans-serif; margin: 0; }
    .bar { display:flex; align-items:center; gap:8px; padding:10px 12px; border-bottom:1px solid #eee; position:sticky; top:0; background:#fff; z-index:10; }
    .btn { display:inline-block; padding:6px 10px; border-radius:7px; border:1px solid #ccc; background:#fafafa; text-decoration:none; color:#222; font-size:13px; }
    .btn:hover { background:#f2f2f2; }
    iframe { width: 100vw; height: calc(100vh - 58px); border: 0; }
  </style>
</head>
<body>
  <div class="bar">
    <a class="btn" href="{{ url_for('index') }}">← Back</a>
    <a class="btn" href="{{ url_for('slideshow', i=idx) }}">Start slideshow here</a>
    <a class="btn" href="{{ url_for('files', filename=name) }}" target="_blank">Open raw</a>
    <div style="font-weight:700; font-size:14px; margin-left:8px;">{{ name }}</div>
  </div>
  <iframe src="{{ url_for('files', filename=name) }}"></iframe>
</body>
</html>
"""

SLIDESHOW_TMPL = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Slideshow</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <style>
    html, body { margin:0; padding:0; height:100%; font-family: Inter, system-ui, Arial, sans-serif; }
    .topbar { position:fixed; top:0; left:0; right:0; height:46px; border-bottom:1px solid #eee; background:#fff; display:flex; align-items:center; gap:8px; padding:6px 10px; z-index:10; }
    .btn { display:inline-block; padding:6px 10px; border-radius:7px; border:1px solid #ccc; background:#fafafa; text-decoration:none; color:#222; font-size:13px; }
    .btn:hover { background:#f2f2f2; }
    .title { font-weight:700; margin-left:8px; }
    .stage { position:absolute; top:46px; left:0; right:0; bottom:0; background:#fff; }
    iframe { width: 100%; height: 100%; border: 0; }
    .hint { font-size:12px; color:#666; margin-left:auto; }
  </style>
</head>
<body>
  <div class="topbar">
    <a class="btn" href="{{ url_for('index') }}">Files</a>
    <a class="btn" id="prev" href="#">← Prev</a>
    <a class="btn" id="next" href="#">Next →</a>
    <div class="title">{{ names[i] if names else 'No slides' }}</div>
    <div class="hint">Use ← / → keys</div>
  </div>
  <div class="stage">
    {% if names %}
      <iframe id="slideframe" src="{{ url_for('files', filename=names[i]) }}"></iframe>
    {% else %}
      <div style="padding:14px;">No slides found.</div>
    {% endif %}
  </div>
  <script>
    const names = {{ names|tojson }};
    let i = {{ i }};
    const prevBtn = document.getElementById('prev');
    const nextBtn = document.getElementById('next');

    function go(idx) {
      if (!names.length) return;
      i = Math.max(0, Math.min(names.length - 1, idx));
      document.getElementById('slideframe').src = "{{ url_for('files', filename='__PLACEHOLDER__') }}".replace('__PLACEHOLDER__', names[i]);
      history.replaceState(null, '', '{{ url_for("slideshow") }}?i=' + i);
      document.querySelector('.title').textContent = names[i];
    }

    prevBtn.addEventListener('click', function(e){ e.preventDefault(); go(i - 1); });
    nextBtn.addEventListener('click', function(e){ e.preventDefault(); go(i + 1); });

    window.addEventListener('keydown', function(e){
      if (e.key === 'ArrowLeft') go(i - 1);
      if (e.key === 'ArrowRight') go(i + 1);
      if (e.key.toLowerCase() === 's') window.location = "{{ url_for('index') }}";
    });
  </script>
</body>
</html>
"""

@app.route("/")
def index():
    files = _list_figs()
    return render_template_string(
        INDEX_TMPL,
        title=APP_TITLE,
        intro=INTRO_BLOCK,
        root=str(_fig_dir()),
        files=files
    )

@app.route("/files/<path:filename>")
def files(filename):
    # Strictly serve from figures dir
    directory = str(_fig_dir())
    fpath = _fig_dir() / filename
    if not fpath.exists() or fpath.suffix.lower() != ".html":
        abort(404)
    return send_from_directory(directory, filename)

@app.route("/view/<path:name>")
def view(name):
    files = _list_figs()
    if name not in files:
        abort(404)
    idx = files.index(name)
    return render_template_string(VIEW_TMPL, name=name, idx=idx)

@app.route("/slideshow")
def slideshow():
    files = _list_figs()
    if not files:
        return render_template_string(SLIDESHOW_TMPL, names=[], i=0)
    try:
        i = int(request.args.get("i", 0))
    except Exception:
        i = 0
    i = max(0, min(len(files) - 1, i))
    return render_template_string(SLIDESHOW_TMPL, names=files, i=i)

@app.route("/api/list")
def api_list():
    return jsonify({"root": str(_fig_dir()), "files": _list_figs()})

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", type=str, default="127.0.0.1")
    ap.add_argument("--port", type=int, default=5000)
    args = ap.parse_args()

    figdir = _fig_dir()
    figdir.mkdir(parents=True, exist_ok=True)
    print(f"{APP_TITLE}\nServing from {figdir}\n")
    print("Open the landing page:")
    print(f"  http://{args.host}:{args.port}/\n")
    app.run(host=args.host, port=args.port, debug=False)

if __name__ == "__main__":
    main()