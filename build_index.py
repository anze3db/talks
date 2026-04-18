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
  <title>Anže's Talks</title>
  <meta name="description" content="Conferences, Meetups, and Workshops">
  <meta name="author" content="Anže Pečar">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@picocss/pico@1.5.3/css/pico.min.css">
  <style>
    @media (min-width: 992px) {
      .container { max-width: 845px; }
    }
    section > h1, h2, h3 { margin-bottom: 10px; }
    .extra-links { margin: 0.3rem 0; }
    .extra-links a mark { font-size: 0.6rem; padding: 0.15rem 0.5rem; margin: 0.3rem 0; display: inline-block; border-radius: 4px; color: #fff; }
    .extra-links .pill-video { background-color: #c62828; }
    .extra-links .pill-code { background-color: #24292f; }
    .extra-links .pill-pdf { background-color: #1565c0; }
    .extra-links .pill-slides { background-color: #6a1b9a; }
  </style>
</head>
<body>
  <header class="container">
    <hgroup>
      <h1><a href="/">Anže's Talks</a></h1>
      <h2>Conferences, Meetups, and Workshops</h2>
    </hgroup>
  </header>
  <main class="container">
"""

TEMPLATE_END = """\
  </main>
  <footer class="container" style="padding-top: 0;">
    <p>
      <a href="https://pecar.me/">Home</a> · <a href="https://blog.pecar.me/">Blog</a>
    </p>
  </footer>
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


MONTH_ABBR = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
AUTO_START = "<!-- AUTO-TALKS-START -->"
AUTO_END = "<!-- AUTO-TALKS-END -->"


def extract_metadata(md_path):
    """Return (title, frontmatter_dict) from a Marp source file."""
    lines = md_path.read_text(encoding="utf-8").splitlines()
    meta = {}
    i = 0
    if lines and lines[0].strip() == "---":
        i = 1
        while i < len(lines) and lines[i].strip() != "---":
            if ":" in lines[i]:
                k, v = lines[i].split(":", 1)
                meta[k.strip()] = v.strip()
            i += 1
        i += 1
    title = md_path.stem
    for line in lines[i:]:
        if line.startswith("# "):
            title = line[2:].strip()
            break
    return title, meta


def sync_readme(readme_path, src_dir, site_dir):
    """Insert Marp talks that aren't yet referenced in README between markers."""
    readme = readme_path.read_text(encoding="utf-8")
    if AUTO_START not in readme or AUTO_END not in readme:
        return readme

    new_sections = []
    for md in sorted(src_dir.glob("*.md"), reverse=True):
        stem = md.stem
        m = re.match(r"(\d{4})-(\d{2})-(\d{2})-", stem)
        if not m:
            continue
        if not (site_dir / f"{stem}.html").exists():
            continue
        year, mo, day = m.groups()
        date_str = f"{day} {MONTH_ABBR[int(mo)]} {year}"
        title, meta = extract_metadata(md)
        event = meta.get("event", "")
        desc = f"{title} @ {event}" if event else title
        if meta.get("lightning", "").lower() in ("true", "yes"):
            desc = f"⚡ {desc}"
        url = f"https://talks.pecar.me/{stem}.html"
        new_sections.append(f"## {date_str}\n\n{desc}\n\n[📖 Slides]({url}) | 📹 Video\n")

    if not new_sections:
        return readme

    before = readme.split(AUTO_START)[0]
    after = readme.split(AUTO_END, 1)[1]
    block = f"{AUTO_START}\n\n" + "\n".join(new_sections) + f"\n{AUTO_END}"
    updated = before + block + after
    readme_path.write_text(updated, encoding="utf-8")
    return updated


def main():
    site = Path("_site")
    readme = sync_readme(Path("README.md"), Path("src"), site)

    src_stems = {f.stem for f in Path("src").glob("*.md")}
    html_files = {f.stem: f.name for f in site.glob("*.html") if f.stem != "index" and f.stem in src_stems}
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
                    links.append(("Slides", "slides", html_files[stem]))
                    used_html.add(stem)
                if stem in pdf_files:
                    links.append(("PDF", "pdf", pdf_files[stem]))
                else:
                    links.append(("PDF", "pdf", url))
            elif url.endswith(".html"):
                stem = Path(url).stem
                if stem in html_files:
                    links.append(("Slides", "slides", html_files[stem]))
                    used_html.add(stem)
                else:
                    links.append(("Slides", "slides", url))
            elif "youtube.com" in url or "youtu.be" in url:
                links.append(("Video", "video", url))
            elif "github.com" in url:
                links.append(("Code", "code", url))

        event_str = f"{date} — {event.strip()}" if event.strip() else date
        href = links[0][2] if links else ""
        title_html = f'<a href="{href}">{title.strip()}</a>' if href else title.strip()
        extra = [f'<a href="{url}"><mark class="pill-{cls}">{label}</mark></a>' for label, cls, url in links[1:]]
        extra_html = f"\n<div class=\"extra-links\">{' '.join(extra)}</div>" if extra else ""
        parts.append(f"<span>{event_str}</span>{extra_html}\n<h1>{title_html}</h1>\n")

    # Add Marp slides not referenced in README
    for stem in sorted(html_files.keys() - used_html, reverse=True):
        m = re.match(r"(\d{4}-\d{2}-\d{2})-(.*)", stem)
        if m:
            date, slug = m.group(1), m.group(2)
            title = slug.replace("-", " ").title()
        else:
            date, title = "", stem

        href = html_files[stem]
        parts.insert(
            0,
            f"<span>🚧</span>\n<h1><a href=\"{href}\">{title}</a></h1>\n",
        )

    (site / "index.html").write_text(TEMPLATE_START + "\n".join(parts) + TEMPLATE_END)
    print(f"Generated _site/index.html with {len(parts)} talks")


if __name__ == "__main__":
    main()
