# tools/inline_plotly.py
import glob, plotly.io as pio
for path in glob.glob("regimes_lab/output/stats/figures/*.html"):
    try:
        fig = pio.read_html(path)[0]  # load the first figure in the HTML
        pio.write_html(fig, file=path, include_plotlyjs="inline", full_html=True)
        print("Rewrote inline:", path)
    except Exception as e:
        print("Skip", path, "->", e)