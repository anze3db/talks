#!/usr/bin/env python3
"""Generate _site/index.html from README.md and built slides."""

import re
from pathlib import Path

MONTHS = {
    "Jan": "01",
    "Feb": "02",
    "Mar": "03",
    "Apr": "04",
    "May": "05",
    "Jun": "06",
    "Jul": "07",
    "Aug": "08",
    "Sep": "09",
    "Oct": "10",
    "Nov": "11",
    "Dec": "12",
    "June": "06",
    "July": "07",
}

TEMPLATE_START = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Talks — Anže Pečar</title>
  <style>
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      max-width: 700px;
      margin: 2rem auto;
      padding: 0 1rem;
      color: #1a1a1a;
      line-height: 1.6;
    }
    h1 { margin-bottom: 0.25rem; }
    p.subtitle { color: #666; margin-top: 0; }
    .talk { padding: 1rem 0; border-bottom: 1px solid #eee; }
    .talk:last-child { border-bottom: none; }
    .talk h3 { margin: 0 0 0.15rem; }
    .talk .event { color: #666; font-size: 0.9rem; }
    .talk .links { font-size: 0.9rem; margin-top: 0.35rem; }
    .talk .links a { margin-right: 1rem; }
    a { color: #0366d6; text-decoration: none; }
    a:hover { text-decoration: underline; }
  </style>
</head>
<body>
  <h1>Talks</h1>
  <p class="subtitle">Anže Pečar</p>
"""

TEMPLATE_END = """\
</body>
</html>
"""


def date_to_iso(date_str):
    """'02 Apr 2026' or '7 June 2024' -> '2026-04-02'."""
    parts = date_str.split()
    if len(parts) != 3:
        return None
    day, mon, year = parts
    m = MONTHS.get(mon)
    if not m:
        return None
    return f"{year}-{m}-{day.zfill(2)}"


def main():
    site = Path("_site")
    readme = Path("README.md").read_text(encoding="utf-8")

    html_files = {f.stem: f.name for f in site.glob("*.html") if f.stem != "index"}
    pdf_files = {f.stem: f.name for f in site.glob("*.pdf")}
    used_html = set()

    parts = []
    sections = re.split(r"^## ", readme, flags=re.MULTILINE)[1:]

    for section in sections:
        lines = [l for l in section.strip().splitlines() if l.strip()]
        if not lines:
            continue

        date = lines[0].strip()
        desc = lines[1].strip() if len(lines) > 1 else ""
        links_md = " ".join(lines[2:]) if len(lines) > 2 else ""

        if " @ " in desc:
            title, event = desc.rsplit(" @ ", 1)
        else:
            title, event = desc, ""

        links = []

        for m in re.finditer(r"\[([^\]]+)\]\(([^)]+)\)", links_md):
            label_raw, url = m.group(1), m.group(2)

            if "/blob/main/" in url and url.endswith(".pdf"):
                stem = Path(url.split("/blob/main/")[-1]).stem
                if stem in html_files:
                    links.append(("Slides", html_files[stem]))
                    used_html.add(stem)
                if stem in pdf_files:
                    links.append(("PDF", pdf_files[stem]))
                else:
                    links.append(("PDF", url))
            elif "youtube.com" in url or "youtu.be" in url:
                links.append(("Video", url))
            elif "github.com" in url:
                links.append(("Code", url))

        event_str = f"{date} — {event.strip()}" if event.strip() else date
        links_html = "".join(f'<a href="{url}">{label}</a>' for label, url in links)
        parts.append(
            f'  <div class="talk">\n'
            f"    <h3>{title.strip()}</h3>\n"
            f'    <div class="event">{event_str}</div>\n'
            f'    <div class="links">{links_html}</div>\n'
            f"  </div>\n"
        )

    # Add Marp slides not referenced in README
    for stem in sorted(html_files.keys() - used_html, reverse=True):
        m = re.match(r"(\d{4}-\d{2}-\d{2})-(.*)", stem)
        if m:
            date, slug = m.group(1), m.group(2)
            title = slug.replace("-", " ").title()
        else:
            date, title = "", stem

        link_els = [f'<a href="{html_files[stem]}">Slides</a>']
        if stem in pdf_files:
            link_els.append(f'<a href="{pdf_files[stem]}">PDF</a>')

        parts.insert(
            0,
            f'  <div class="talk">\n'
            f"    <h3>{title}</h3>\n"
            f'    <div class="event">🚧</div>\n'
            f'    <div class="links">{"".join(link_els)}</div>\n'
            f"  </div>\n",
        )

    (site / "index.html").write_text(TEMPLATE_START + "\n".join(parts) + TEMPLATE_END)
    print(f"Generated _site/index.html with {len(parts)} talks")


if __name__ == "__main__":
    main()
