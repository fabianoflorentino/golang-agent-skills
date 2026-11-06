#!/usr/bin/env python3
"""Generate docs/index.html from the skills/*/SKILL.md catalog.

Reads the YAML frontmatter of every skill, groups skills by category, and
writes a static site that can be served from GitHub Pages. Typography is
loaded from Google Fonts; everything else is self-contained.
"""
from __future__ import annotations

import glob
import html
import os
import re
import sys

REPO = "https://github.com/fabianoflorentino/golang-agent-skills"
NAME = "golang-agent-skills"
INSTALL_ALL = f"npx skills add {REPO} --all"
INSTALL_ONE = f"npx skills add {REPO} --skill golang-pitfalls-error-handling"

MIND_NODES = [
    ("golang-security", "security"),
    ("golang-concurrency", "concurrency"),
    ("golang-rest", "rest"),
    ("golang-testing", "testing"),
    ("golang-project-layout", "layout"),
    ("golang-pitfalls-error-handling", "pitfalls"),
]

CATEGORIES = [
    ("Getting Started", [
        "golang-how-to",
    ]),
    ("Code Quality", [
        "golang-code-style", "golang-documentation", "golang-error-handling",
        "golang-lint", "golang-naming", "golang-safety", "golang-security",
        "golang-structs-interfaces",
    ]),
    ("Architecture & Design", [
        "golang-concurrency", "golang-context", "golang-data-structures",
        "golang-database", "golang-dependency-injection",
        "golang-design-patterns", "golang-modernize", "golang-refactoring",
    ]),
    ("QA & Performance", [
        "golang-benchmark", "golang-observability", "golang-performance",
        "golang-testing", "golang-troubleshooting",
    ]),
    ("Project Setup", [
        "golang-cli", "golang-continuous-integration",
        "golang-dependency-management", "golang-gopls", "golang-pkg-go-dev",
        "golang-popular-libraries", "golang-project-layout",
        "golang-stay-updated",
    ]),
    ("APIs", [
        "golang-rest", "golang-graphql", "golang-grpc", "golang-swagger",
    ]),
    ("Dependency Injection", [
        "golang-google-wire", "golang-uber-dig", "golang-uber-fx",
    ]),
    ("Frameworks", [
        "golang-spf13-cobra", "golang-spf13-viper",
    ]),
    ("samber/*", [
        "golang-samber-do", "golang-samber-hot", "golang-samber-lo",
        "golang-samber-mo", "golang-samber-oops", "golang-samber-ro",
        "golang-samber-slog",
    ]),
    ("Testing", [
        "golang-stretchr-testify",
    ]),
    ("Pitfalls (100 Go Mistakes)", [
        "golang-pitfalls-code-organization", "golang-pitfalls-data-types",
        "golang-pitfalls-control-structures", "golang-pitfalls-strings",
        "golang-pitfalls-functions-methods", "golang-pitfalls-error-handling",
        "golang-pitfalls-concurrency-foundations",
        "golang-pitfalls-concurrency-practice",
        "golang-pitfalls-standard-library", "golang-pitfalls-testing",
        "golang-pitfalls-optimizations",
    ]),
]

CATEGORY_FOR = {}
for cat, skills in CATEGORIES:
    for name in skills:
        CATEGORY_FOR[name] = cat

DEFAULT_EMOJI = "🃏"

BRAND_MARK = """<svg class="brand-mark" viewBox="0 0 64 64" fill="none" aria-hidden="true" focusable="false">
        <defs>
          <linearGradient id="brand-grad" x1="6" y1="4" x2="58" y2="60" gradientUnits="userSpaceOnUse">
            <stop stop-color="#00e5a8"/>
            <stop offset=".5" stop-color="#38bdf8"/>
            <stop offset="1" stop-color="#a78bfa"/>
          </linearGradient>
        </defs>
        <rect x="4" y="4" width="56" height="56" rx="16" fill="url(#brand-grad)" fill-opacity=".1" stroke="url(#brand-grad)" stroke-width="2"/>
        <path d="M23 24l-8 8 8 8M41 24l8 8-8 8" stroke="url(#brand-grad)" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"/>
        <path d="M37 18l-10 28" stroke="url(#brand-grad)" stroke-width="3.2" stroke-linecap="round"/>
      </svg>"""

FAVICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64" role="img" aria-label="golang-agent-skills">
  <defs>
    <linearGradient id="favicon-grad" x1="6" y1="4" x2="58" y2="60" gradientUnits="userSpaceOnUse">
      <stop stop-color="#00e5a8"/>
      <stop offset=".5" stop-color="#38bdf8"/>
      <stop offset="1" stop-color="#a78bfa"/>
    </linearGradient>
  </defs>
  <rect x="2" y="2" width="60" height="60" rx="16" fill="#080b14"/>
  <rect x="4" y="4" width="56" height="56" rx="15" fill="url(#favicon-grad)" fill-opacity=".12" stroke="url(#favicon-grad)" stroke-width="2.5"/>
  <path d="M23 24l-8 8 8 8M41 24l8 8-8 8" fill="none" stroke="url(#favicon-grad)" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M37 18l-10 28" fill="none" stroke="url(#favicon-grad)" stroke-width="3.4" stroke-linecap="round"/>
</svg>
"""

GITHUB_ICON = """<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true" focusable="false">
          <path d="M12 .5C5.37.5 0 5.87 0 12.5c0 5.3 3.44 9.8 8.21 11.39.6.11.82-.26.82-.58 0-.29-.01-1.05-.02-2.06-3.34.73-4.04-1.61-4.04-1.61-.55-1.39-1.34-1.76-1.34-1.76-1.09-.75.08-.73.08-.73 1.2.08 1.84 1.24 1.84 1.24 1.07 1.84 2.81 1.31 3.5 1 .11-.78.42-1.31.76-1.61-2.67-.3-5.47-1.33-5.47-5.93 0-1.31.47-2.38 1.24-3.22-.12-.3-.54-1.52.12-3.18 0 0 1.01-.32 3.3 1.23a11.5 11.5 0 0 1 6 0c2.29-1.55 3.3-1.23 3.3-1.23.66 1.66.24 2.88.12 3.18.77.84 1.24 1.91 1.24 3.22 0 4.61-2.8 5.63-5.48 5.92.43.37.81 1.1.81 2.22 0 1.6-.01 2.9-.01 3.29 0 .32.21.7.82.58A12.01 12.01 0 0 0 24 12.5C24 5.87 18.63.5 12 .5Z"/>
        </svg>"""


def parse_frontmatter(text: str) -> dict:
    m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    fm = m.group(1) if m else ""
    data: dict = {}
    data["body"] = text[m.end():] if m else text
    lines = fm.splitlines()
    parents: dict[int, str] = {}
    i = 0
    while i < len(lines):
        line = lines[i]
        indent = len(line) - len(line.lstrip())
        km = re.match(r"^(\s*)([A-Za-z0-9_-]+):\s*(.*)$", line)
        if not km:
            i += 1
            continue
        key, val = km.group(2), km.group(3).strip()
        path = key
        if indent > 0:
            falls = sorted((p for p in parents if p < indent), reverse=True)
            parent = parents[falls[0]] if falls else ""
            path = f"{parent}.{key}"
        parents[indent] = path
        if val in ("|", ">-", ">") and i + 1 < len(lines) and lines[i + 1][:1] in (" ", "\t"):
            collected = []
            i += 1
            while i < len(lines) and lines[i][:2] in ("  ", "\t"):
                collected.append(lines[i].strip())
                i += 1
            data[path] = " ".join(collected)
            continue
        if val[:1] in ("'", '"') and not (len(val) > 1 and val[-1] == val[0]):
            quote = val[0]
            collected = [val[1:]]
            i += 1
            while i < len(lines):
                chunk = lines[i].strip()
                if chunk.endswith(quote):
                    collected.append(chunk[:-1])
                    i += 1
                    break
                collected.append(chunk)
                i += 1
            data[path] = " ".join(c for c in collected if c).strip()
            continue
        if val and val[:1] not in ("'", '"', "[", "{"):
            collected = [val]
            j = i + 1
            while j < len(lines):
                nxt = lines[j]
                if not nxt.strip():
                    break
                nindent = len(nxt) - len(nxt.lstrip())
                if nindent <= indent:
                    break
                if indent > 0 and re.match(r"^\s*[A-Za-z0-9_-]+:\s", nxt):
                    break
                collected.append(nxt.strip())
                j += 1
            if len(collected) > 1:
                data[path] = " ".join(collected)
                i = j
                continue
        data[path] = val.strip('"').strip()
        i += 1
    return data


def nested(data: dict, path: str, default=""):
    return data.get(path, default)


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def skill_blurb(skill: str) -> str:
    return f"{REPO}/blob/main/skills/{skill}/SKILL.md"


def render_skill_html(skill: str, data: dict, index: int) -> str:
    name = nested(data, "name", skill)
    desc = nested(data, "description", "")
    emoji = nested(data, "metadata.openclaw.emoji", DEFAULT_EMOJI)
    version = nested(data, "metadata.version", "?")
    author = nested(data, "metadata.author", "")
    invoc = nested(data, "user-invocable", "false")
    compat = nested(data, "compatibility", "")
    flags = []
    if invoc == "true":
        flags.append("⚡ command")
    badge = " ".join(f"<span class='badge'>{html.escape(f)}</span>" for f in flags)
    meta = [f"v{version}" if version and version != "?" else "", author]
    meta_html = " &middot; ".join(html.escape(v) for v in meta if v)
    return f"""<details class="entry" data-category="{html.escape(CATEGORY_FOR.get(skill, 'Other'))}" data-name="{html.escape(skill)}" data-search="{html.escape(desc).lower()}">
  <summary class="entry-row">
    <span class="entry-no">{index:02d}</span>
    <span class="emoji">{html.escape(emoji)}</span>
    <span class="entry-copy">
      <span class="entry-title"><code>{html.escape(name)}</code><span class="skill-meta">{meta_html}</span>{badge}</span>
      <span class="desc">{html.escape(desc)}</span>
    </span>
    <span class="chev" aria-hidden="true">+</span>
  </summary>
  <div class="entry-body">
    <div class="compat">{html.escape(compat)}</div>
    <pre class="body">{html.escape(data["body"].strip())}</pre>
    <p class="src"><a href="{skill_blurb(skill)}" target="_blank" rel="noopener">View source on GitHub &rarr;</a></p>
  </div>
</details>"""


def main() -> int:
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    skills_dir = os.path.join(root, "skills")
    out_dir = os.path.join(root, "docs")
    os.makedirs(out_dir, exist_ok=True)

    skill_paths = sorted(glob.glob(os.path.join(skills_dir, "*", "SKILL.md")))
    if not skill_paths:
        alt_dir = os.path.join(root, "agent", "skills")
        skill_paths = sorted(glob.glob(os.path.join(alt_dir, "*", "SKILL.md")))
        if skill_paths:
            print(f"note: skills/ is empty, reading {os.path.relpath(alt_dir, root)}",
                  file=sys.stderr)

    parsed: dict[str, dict] = {}
    for path in skill_paths:
        skill = os.path.basename(os.path.dirname(path))
        with open(path, encoding="utf-8") as f:
            parsed[skill] = parse_frontmatter(f.read())

    missing = [s for s in CATEGORY_FOR if s not in parsed]
    if missing:
        print(f"warning: skills not found on disk: {missing}", file=sys.stderr)
    unlisted = [s for s in sorted(parsed) if s not in CATEGORY_FOR]
    if unlisted:
        print(f"warning: skills on disk not in any category: {unlisted}",
              file=sys.stderr)

    present_categories = []
    for cat, skills in CATEGORIES:
        present = [s for s in skills if s in parsed]
        if present:
            present_categories.append((cat, present))

    category_counts = {cat: len(present) for cat, present in present_categories}
    mind_nodes = []
    for i, (skill, short) in enumerate(MIND_NODES):
        if skill not in parsed:
            continue
        cat = CATEGORY_FOR.get(skill, "Other")
        emoji = nested(parsed[skill], "metadata.openclaw.emoji", DEFAULT_EMOJI)
        count = category_counts.get(cat, 0)
        label = f"{html.escape(cat)} &middot; {count} skill" + ("" if count == 1 else "s")
        mind_nodes.append(
            f'<button class="mind-node n{i + 1}" type="button" data-filter="{html.escape(cat)}" aria-pressed="false" title="Filter {html.escape(cat)} skills" style="--i:{i}">'
            f'<span class="mind-emoji">{html.escape(emoji)}</span>'
            f'<span class="mind-name"><span class="full">{html.escape(skill)}</span><span class="short">{html.escape(short)}</span></span>'
            f'<span class="mind-cat">{label}</span></button>'
        )
    mind_html = "".join(mind_nodes)

    sections = []
    for idx, (cat, present) in enumerate(present_categories, start=1):
        entries = "\n".join(
            render_skill_html(s, parsed[s], i)
            for i, s in enumerate(present, start=1)
        )
        sections.append(
            f'<section class="category" id="cat-{slugify(cat)}" '
            f'data-category="{html.escape(cat)}">'
            f'<header class="category-head"><span class="cat-index">{idx:02d}</span>'
            f'<h2>{html.escape(cat)}</h2>'
            f'<span class="count">{len(present)} skill{"s" if len(present) != 1 else ""}</span></header>'
            f'<div class="entries">{entries}</div></section>'
        )

    total = len(parsed)
    pitfalls = sum(1 for s in parsed if s.startswith("golang-pitfalls-"))
    routes = len(present_categories)

    rail_items = [("All", total)] + [(cat, len(present)) for cat, present in present_categories]
    chips = "".join(
        f'<button class="route-chip{" active" if c == "All" else ""}" data-filter="{html.escape(c)}">'
        f'<span>{html.escape(c)}</span><span class="rail-count">{n}</span></button>'
        for c, n in rail_items
    )

    page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#080b14">
<title>{NAME} — a field guide for Go agents</title>
<meta name="description" content="AI Agent Skills for production-ready Go projects, plus the pitfalls from 100 Go Mistakes and How to Avoid Them.">
<link rel="icon" type="image/svg+xml" href="favicon.svg">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>
  :root {{
    --bg: #080b14; --bg-2: #0a0f1a; --surface: #0d1220; --surface-2: #111827; --surface-3: #182235;
    --border: #1e2b3d; --border-2: #2a3b52;
    --primary: #00e5a8; --primary-2: #00b894; --primary-dim: rgba(0, 229, 168, 0.12);
    --secondary: #38bdf8; --accent: #a78bfa; --pink: #ff4d9d;
    --text: #e9f1f7; --text-2: #c3d0dc; --muted: #8a9bb0; --muted-2: #62748a;
    --green: #34d399; --warning: #fbbf24; --error: #fb7185;
    --sans: 'Inter', system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
    --mono: 'JetBrains Mono', 'Fira Code', ui-monospace, monospace;
    --grad: linear-gradient(120deg, #00e5a8 0%, #38bdf8 48%, #a78bfa 100%);
    --grad-text: linear-gradient(120deg, #6bffd6 0%, #38bdf8 52%, #a78bfa 100%);
    --radius: 10px; --radius-lg: 18px; --max-w: 1200px; --nav-h: 68px;
  }}
  *, *::before, *::after {{ box-sizing: border-box; }}
  html {{ scroll-behavior: smooth; scroll-padding-top: 6rem; -webkit-text-size-adjust: 100%; }}
  body {{
    margin: 0; min-height: 100vh; overflow-x: hidden; color: var(--text);
    background-color: var(--bg);
    background-image:
      radial-gradient(1100px 620px at 78% -8%, rgba(0, 229, 168, 0.1), transparent 62%),
      radial-gradient(900px 560px at 4% 14%, rgba(56, 189, 248, 0.08), transparent 60%),
      radial-gradient(760px 520px at 58% 108%, rgba(167, 139, 250, 0.07), transparent 60%);
    background-repeat: no-repeat;
    font-family: var(--sans); font-size: 16px; line-height: 1.65;
    -webkit-font-smoothing: antialiased;
  }}
  ::selection {{ background: var(--primary); color: #04120e; }}
  a {{ color: inherit; text-decoration: none; }}
  img, svg {{ display: block; max-width: 100%; }}
  button {{ cursor: pointer; font: inherit; }}
  code, pre, kbd {{ font-family: var(--mono); }}
  :focus-visible {{ outline: 2px solid var(--primary); outline-offset: 3px; }}
  .container {{ width: 100%; max-width: var(--max-w); margin: 0 auto; padding: 0 clamp(1.25rem, 4vw, 2rem); }}
  #bg-canvas {{ position: fixed; inset: 0; z-index: 0; width: 100%; height: 100%; pointer-events: none; opacity: .7; }}
  main, .site-footer {{ position: relative; z-index: 1; }}
  .aurora {{ position: fixed; inset: 0; z-index: 0; overflow: hidden; pointer-events: none; }}
  .aurora::before, .aurora::after {{ content: ""; position: absolute; width: min(62vw, 720px); aspect-ratio: 1; border-radius: 50%; filter: blur(85px); opacity: .16; animation: aurora-drift 26s ease-in-out infinite alternate; }}
  .aurora::before {{ top: -12%; left: -8%; background: radial-gradient(circle, #00e5a8, transparent 65%); }}
  .aurora::after {{ right: -8%; bottom: -18%; background: radial-gradient(circle, #a78bfa, transparent 65%); animation-delay: -11s; animation-duration: 32s; }}
  .skip-link {{ position: fixed; top: .75rem; left: .75rem; z-index: 1000; padding: .6rem .9rem; border: 1px solid var(--primary); border-radius: var(--radius); background: var(--bg); color: var(--primary); font-family: var(--mono); font-size: .75rem; transform: translateY(-160%); transition: transform .2s ease; }}
  .skip-link:focus {{ transform: translateY(0); }}
  .eyebrow {{ margin: 0 0 .5rem; color: var(--primary); font-family: var(--mono); font-size: .62rem; letter-spacing: .18em; text-transform: uppercase; }}

  /* Header */
  .site-header {{ position: sticky; top: 0; z-index: 100; border-bottom: 1px solid transparent; background: transparent; transition: background .3s ease, border-color .3s ease, box-shadow .3s ease; }}
  .site-header.scrolled {{ border-bottom-color: var(--border); background: rgba(8, 11, 20, .82); box-shadow: 0 12px 40px rgba(0, 0, 0, .45); backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px); }}
  .site-header nav {{ display: flex; align-items: center; gap: 1.5rem; min-height: var(--nav-h); }}
  .nav-logo {{ display: inline-flex; flex-shrink: 0; align-items: center; gap: .6rem; font-family: var(--mono); font-size: .95rem; font-weight: 500; letter-spacing: -.01em; }}
  .brand-mark {{ width: 34px; height: 34px; filter: drop-shadow(0 0 8px rgba(0, 229, 168, .55)); transition: filter .2s ease; }}
  .nav-logo:hover .brand-mark {{ filter: drop-shadow(0 0 12px rgba(0, 229, 168, .85)); }}
  .nav-links {{ display: flex; gap: .2rem; margin-left: auto; padding: 0; list-style: none; }}
  .nav-links a {{ display: block; padding: .42rem .75rem; border-radius: var(--radius); color: var(--muted); font-size: .88rem; font-weight: 500; white-space: nowrap; transition: color .2s ease, background .2s ease; }}
  .nav-links a:hover {{ background: var(--surface-2); color: var(--text); }}
  .nav-actions {{ display: flex; flex-shrink: 0; align-items: center; gap: .65rem; }}
  .nav-github {{ display: flex; align-items: center; justify-content: center; width: 36px; height: 36px; border: 1px solid var(--border); border-radius: var(--radius); background: var(--surface-2); color: var(--muted); transition: color .2s ease, border-color .2s ease, background .2s ease; }}
  .nav-github svg {{ width: 18px; height: 18px; }}
  .nav-github:hover {{ border-color: var(--primary); background: var(--primary-dim); color: var(--text); }}
  .nav-cta {{ padding: .55rem 1.05rem; border: 1px solid var(--border-2); border-radius: var(--radius); background: var(--surface-2); color: var(--text); font-size: .85rem; font-weight: 600; transition: border-color .2s ease, background .2s ease, color .2s ease; }}
  .nav-cta:hover {{ border-color: var(--primary); background: var(--primary-dim); color: var(--primary); }}

  /* Buttons */
  .btn {{ display: inline-flex; align-items: center; justify-content: center; gap: .5rem; padding: .72rem 1.35rem; border: 1px solid transparent; border-radius: var(--radius); font-size: .9rem; font-weight: 600; white-space: nowrap; transition: transform .2s ease, box-shadow .2s ease, border-color .2s ease, background .2s ease, color .2s ease; }}
  .btn svg {{ width: 17px; height: 17px; }}
  .btn-primary {{ background: linear-gradient(135deg, var(--primary) 0%, var(--primary-2) 100%); color: #04120e; box-shadow: 0 0 22px rgba(0, 229, 168, .22); }}
  .btn-primary:hover {{ transform: translateY(-1px); box-shadow: 0 0 34px rgba(0, 229, 168, .42); }}
  .btn-outline {{ border-color: var(--border-2); background: transparent; color: var(--text); }}
  .btn-outline:hover {{ border-color: var(--primary); background: var(--primary-dim); color: var(--primary); }}

  /* Hero */
  .hero {{ position: relative; overflow: hidden; }}
  .hero::before {{ content: ""; position: absolute; inset: 0; z-index: 0; pointer-events: none; background-image: linear-gradient(rgba(56, 189, 248, .055) 1px, transparent 1px), linear-gradient(90deg, rgba(56, 189, 248, .055) 1px, transparent 1px); background-size: 64px 64px; -webkit-mask-image: radial-gradient(ellipse 72% 70% at 50% 42%, #000 20%, transparent 76%); mask-image: radial-gradient(ellipse 72% 70% at 50% 42%, #000 20%, transparent 76%); }}
  .hero-inner {{ position: relative; z-index: 1; display: grid; grid-template-columns: minmax(0, 1.02fr) minmax(0, .98fr); gap: clamp(2rem, 5vw, 4.25rem); align-items: center; padding: clamp(2rem, 5vw, 3.75rem) clamp(1.25rem, 4vw, 2rem) clamp(2.25rem, 5vw, 3.5rem); }}
  .hero-copy > * {{ animation: fade-in-up .75s cubic-bezier(.2, .7, .2, 1) both; }}
  .hero-copy > *:nth-child(1) {{ animation-delay: .04s; }}
  .hero-copy > *:nth-child(2) {{ animation-delay: .1s; }}
  .hero-copy > *:nth-child(3) {{ animation-delay: .16s; }}
  .hero-copy > *:nth-child(4) {{ animation-delay: .22s; }}
  .hero-copy > *:nth-child(5) {{ animation-delay: .28s; }}
  .hero-copy > *:nth-child(6) {{ animation-delay: .34s; }}
  .hero-kicker {{ display: flex; flex-wrap: wrap; align-items: center; gap: .55rem; margin: 0 0 1.15rem; color: var(--muted-2); font-family: var(--mono); font-size: .66rem; letter-spacing: .14em; text-transform: uppercase; }}
  .hero-kicker b {{ color: var(--primary); font-weight: 500; }}
  .hero-kicker i {{ width: 3px; height: 3px; border-radius: 50%; background: var(--border-2); }}
  .hero-headline {{ margin: 0 0 1.2rem; font-size: clamp(2.5rem, 4.6vw, 3.65rem); font-weight: 800; letter-spacing: -.035em; line-height: 1.02; text-wrap: balance; }}
  .gradient-text {{ background: var(--grad-text); -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; color: transparent; }}
  .hero-sub {{ max-width: 52ch; margin: 0 0 1.6rem; color: var(--text-2); font-size: clamp(1rem, 1.3vw, 1.08rem); line-height: 1.7; }}
  .hero-actions {{ display: flex; flex-wrap: wrap; gap: .7rem; margin-bottom: 1.5rem; }}
  .hero-facts {{ display: flex; flex-wrap: wrap; align-items: center; gap: 0; margin: 0; padding: 0; list-style: none; border-top: 1px solid var(--border); }}
  .hero-facts li {{ padding: .7rem 1.1rem .7rem 0; margin-right: 1.1rem; border-right: 1px solid var(--border); font-family: var(--mono); font-size: .64rem; color: var(--muted-2); letter-spacing: .06em; text-transform: uppercase; }}
  .hero-facts li:last-child {{ border-right: 0; margin-right: 0; padding-right: 0; }}
  .hero-facts b {{ display: block; margin-bottom: .1rem; color: var(--text); font-family: var(--sans); font-size: 1.05rem; font-weight: 700; letter-spacing: -.02em; text-transform: none; }}
  .hero-hint {{ margin: .85rem 0 0; color: var(--muted-2); font-size: .76rem; }}
  .hero-hint code {{ padding: .1em .35em; border-radius: 5px; background: var(--primary-dim); color: var(--primary); font-size: .9em; }}

  /* Mind map */
  .mind-map {{ position: relative; justify-self: end; width: 100%; max-width: 520px; aspect-ratio: 1 / 1; animation: fade-in-right .9s cubic-bezier(.2, .7, .2, 1) both .15s; }}
  .mind-map::before {{ content: ""; position: absolute; inset: 10%; border-radius: 50%; background: radial-gradient(circle, rgba(56, 189, 248, .1), transparent 62%); filter: blur(18px); }}
  .mind-lines {{ position: absolute; inset: 0; width: 100%; height: 100%; overflow: visible; }}
  .mind-lines path {{ fill: none; stroke: url(#mind-grad); stroke-width: .45; stroke-linecap: round; opacity: .52; stroke-dasharray: 100; stroke-dashoffset: 0; animation: mind-draw .9s cubic-bezier(.2, .7, .2, 1) backwards; }}
  .mind-lines path:nth-of-type(1) {{ animation-delay: .15s; }}
  .mind-lines path:nth-of-type(2) {{ animation-delay: .27s; }}
  .mind-lines path:nth-of-type(3) {{ animation-delay: .39s; }}
  .mind-lines path:nth-of-type(4) {{ animation-delay: .51s; }}
  .mind-lines path:nth-of-type(5) {{ animation-delay: .63s; }}
  .mind-lines path:nth-of-type(6) {{ animation-delay: .75s; }}
  .mind-pulses {{ opacity: 0; transition: opacity .5s ease; }}
  .pulses-ready .mind-pulses {{ opacity: 1; }}
  .mind-pulse {{ fill: #6bffd6; filter: drop-shadow(0 0 2px rgba(107, 255, 214, .9)); }}
  .mind-agent {{ position: absolute; top: 50%; left: 50%; z-index: 2; display: flex; flex-direction: column; align-items: center; gap: .08rem; text-align: center; transform: translate(-50%, -50%); }}
  .mind-agent .robot {{ width: 74px; height: 74px; filter: drop-shadow(0 0 12px rgba(0, 229, 168, .35)); }}
  .mind-agent .eye {{ transform-box: fill-box; transform-origin: center; animation: robot-blink 4.6s ease-in-out infinite; }}
  .mind-agent .antenna-dot {{ transform-box: fill-box; transform-origin: center; animation: antenna-pulse 2.4s ease-out infinite; }}
  .agent-ring {{ position: absolute; top: 37px; left: 50%; width: 92px; height: 92px; border: 1px solid rgba(0, 229, 168, .3); border-radius: 50%; transform: translate(-50%, -50%); animation: agent-ping 3.4s ease-out infinite; }}
  .agent-label {{ margin-top: .1rem; color: var(--primary); font-family: var(--mono); font-size: .55rem; letter-spacing: .18em; text-transform: uppercase; }}
  .agent-skill {{ color: var(--muted-2); font-family: var(--mono); font-size: .6rem; }}
  .mind-node {{ position: absolute; z-index: 2; display: grid; grid-template-columns: 26px minmax(0, 1fr); grid-template-rows: auto auto; gap: .12rem .45rem; align-items: center; min-width: 118px; max-width: 150px; padding: .52rem .6rem; border: 1px solid var(--border); border-radius: 11px; background: linear-gradient(180deg, rgba(17, 24, 39, .94), rgba(13, 18, 32, .97)); color: var(--text); text-align: left; transform: translate(-50%, -50%); animation: mind-node .5s cubic-bezier(.2, .7, .2, 1) backwards; animation-delay: calc(var(--i) * .11s + .55s); transition: border-color .2s ease, box-shadow .2s ease, background .2s ease, transform .2s ease; }}
  .mind-node:hover, .mind-node:focus-visible {{ z-index: 3; border-color: rgba(0, 229, 168, .5); background: linear-gradient(180deg, rgba(17, 24, 39, .98), rgba(13, 18, 32, 1)); box-shadow: 0 14px 34px rgba(0, 0, 0, .4), 0 0 22px rgba(0, 229, 168, .1); transform: translate(-50%, -50%) scale(1.045); }}
  .mind-node.active {{ border-color: rgba(0, 229, 168, .65); box-shadow: 0 0 0 1px rgba(0, 229, 168, .08), 0 0 22px rgba(0, 229, 168, .12); }}
  .mind-node.hit {{ border-color: rgba(0, 229, 168, .75); box-shadow: 0 0 0 4px rgba(0, 229, 168, .08), 0 0 26px rgba(0, 229, 168, .4); }}
  .mind-node.n1 {{ left: 50%; top: 7%; }}
  .mind-node.n2 {{ left: 87%; top: 27%; }}
  .mind-node.n3 {{ left: 87%; top: 73%; }}
  .mind-node.n4 {{ left: 50%; top: 93%; }}
  .mind-node.n5 {{ left: 13%; top: 73%; }}
  .mind-node.n6 {{ left: 13%; top: 27%; }}
  .mind-emoji {{ grid-row: 1 / span 2; display: inline-flex; align-items: center; justify-content: center; width: 26px; height: 26px; border: 1px solid var(--border); border-radius: 8px; background: var(--surface-3); font-size: 13px; }}
  .mind-name {{ color: var(--primary); font-family: var(--mono); font-size: .6rem; font-weight: 600; line-height: 1.25; overflow-wrap: anywhere; }}
  .mind-name .short {{ display: none; }}
  .mind-cat {{ color: var(--muted-2); font-size: .52rem; line-height: 1.2; }}

  /* Guide / index */
  .guide {{ padding: clamp(2.75rem, 5vw, 4.5rem) clamp(1.25rem, 4vw, 2rem) 4.5rem; }}
  .guide-head {{ max-width: 72ch; margin-bottom: 2rem; }}
  .guide-head h2, .quickstart-copy h2 {{ margin: 0 0 .45rem; font-size: clamp(1.7rem, 3vw, 2.25rem); font-weight: 700; letter-spacing: -.03em; line-height: 1.1; }}
  .guide-head p, .quickstart-copy p {{ margin: 0; color: var(--muted); font-size: .95rem; }}
  .filter-card {{ position: sticky; top: calc(var(--nav-h) + .85rem); z-index: 8; display: grid; grid-template-columns: minmax(190px, 240px) minmax(0, 1fr) auto; gap: .9rem 1.25rem; align-items: end; margin-bottom: 2rem; padding: 1rem 1.1rem; border: 1px solid var(--border); border-radius: var(--radius-lg); background: rgba(13, 18, 32, .92); box-shadow: 0 18px 44px rgba(0, 0, 0, .35); backdrop-filter: blur(14px); -webkit-backdrop-filter: blur(14px); }}
  .filter-label {{ display: block; margin: 0 0 .5rem; color: var(--muted-2); font-family: var(--mono); font-size: .58rem; letter-spacing: .16em; text-transform: uppercase; }}
  input[type=search] {{ width: 100%; padding: .68rem .85rem; border: 1px solid var(--border); border-radius: 9px; background: var(--surface-2); color: var(--text); font: .82rem var(--sans); outline: none; transition: border-color .2s ease, box-shadow .2s ease; }}
  input[type=search]::placeholder {{ color: var(--muted-2); }}
  input[type=search]:focus {{ border-color: var(--primary); box-shadow: 0 0 0 3px rgba(0, 229, 168, .12); }}
  .route-chips {{ display: flex; flex-wrap: wrap; gap: .35rem; }}
  .route-chip {{ display: inline-flex; align-items: center; gap: .4rem; padding: .36rem .62rem; border: 1px solid var(--border); border-radius: 999px; background: var(--surface-2); color: var(--muted); font-size: .72rem; white-space: nowrap; transition: border-color .2s ease, background .2s ease, color .2s ease; }}
  .route-chip:hover {{ border-color: var(--border-2); color: var(--text); }}
  .route-chip.active {{ border-color: rgba(0, 229, 168, .45); background: var(--primary-dim); color: var(--primary); }}
  .rail-count {{ color: var(--muted-2); font-family: var(--mono); font-size: .55rem; }}
  .route-chip.active .rail-count {{ color: var(--primary); }}
  .filter-note {{ margin: 0; color: var(--muted-2); font-family: var(--mono); font-size: .62rem; white-space: nowrap; }}
  .filter-note strong {{ color: var(--text); font-weight: 500; }}
  .guide-body {{ min-width: 0; }}
  .guide-body.filtered {{ min-height: max(420px, calc(100vh - 340px)); }}
  .category {{ margin: 0 0 2.5rem; scroll-margin-top: 11rem; }}
  .category.fade-in {{ animation: fade-in-up .3s ease both; }}
  .category:last-child {{ margin-bottom: 0; }}
  .category-head {{ display: flex; align-items: baseline; gap: .7rem; padding-bottom: .55rem; border-bottom: 1px solid var(--border); }}
  .cat-index {{ color: var(--primary); font-family: var(--mono); font-size: .6rem; letter-spacing: .1em; }}
  .category-head h2 {{ margin: 0; font-size: 1.02rem; font-weight: 700; letter-spacing: -.01em; }}
  .category-head .count {{ margin-left: auto; color: var(--muted-2); font-family: var(--mono); font-size: .6rem; }}
  .entries {{ display: flex; flex-direction: column; }}
  .entry {{ border-bottom: 1px solid var(--border); border-radius: 12px; transition: background .2s ease, border-color .25s ease, box-shadow .25s ease, margin .25s ease; }}
  .entry:last-child {{ border-bottom: 0; }}
  .entry[open] {{ margin: .45rem 0; border: 1px solid var(--border); background: linear-gradient(180deg, rgba(17, 24, 39, .82), rgba(13, 18, 32, .94)); box-shadow: 0 18px 46px rgba(0, 0, 0, .32), 0 0 0 1px rgba(0, 229, 168, .05); }}
  .entry-row {{ display: grid; grid-template-columns: 30px 36px minmax(0, 1fr) 22px; gap: .75rem; align-items: start; padding: .95rem .55rem; cursor: pointer; list-style: none; border-radius: 12px; transition: background .2s ease; }}
  .entry-row::-webkit-details-marker {{ display: none; }}
  .entry-row:hover {{ background: rgba(56, 189, 248, .045); }}
  .entry[open] > .entry-row {{ border-bottom: 1px solid var(--border); border-radius: 12px 12px 0 0; }}
  .entry-no {{ padding-top: .42rem; color: var(--muted-2); font-family: var(--mono); font-size: .58rem; }}
  .emoji {{ display: inline-flex; align-items: center; justify-content: center; width: 32px; height: 32px; border: 1px solid var(--border); border-radius: 9px; background: var(--surface-3); font-size: 16px; }}
  .entry-copy {{ display: flex; flex-direction: column; gap: .2rem; min-width: 0; }}
  .entry-title {{ display: flex; flex-wrap: wrap; align-items: center; gap: .5rem; }}
  .entry-title code {{ color: var(--primary); font-size: .84rem; font-weight: 600; overflow-wrap: anywhere; }}
  .skill-meta {{ color: var(--muted-2); font-family: var(--mono); font-size: .58rem; }}
  .badge {{ padding: .15rem .4rem; border: 1px solid rgba(167, 139, 250, .32); border-radius: 5px; background: rgba(167, 139, 250, .12); color: var(--accent); font-family: var(--mono); font-size: .55rem; }}
  .desc {{ display: -webkit-box; overflow: hidden; margin: 0; color: var(--muted); font-size: .8rem; line-height: 1.55; -webkit-box-orient: vertical; -webkit-line-clamp: 2; }}
  .chev {{ padding-top: .18rem; color: var(--muted-2); font-family: var(--mono); font-size: 1rem; line-height: 1; transition: transform .25s ease, color .2s ease; }}
  .entry-row:hover .chev {{ color: var(--secondary); }}
  .entry[open] > .entry-row .chev {{ color: var(--primary); transform: rotate(45deg); }}
  .entry[open] .desc {{ display: block; overflow: visible; -webkit-line-clamp: unset; }}
  .entry-body {{ height: auto; overflow: hidden; padding: 0 .55rem 1.1rem 4.25rem; transition: height .28s cubic-bezier(.2, .7, .2, 1); }}
  .compat {{ color: var(--muted); font-size: .73rem; }}
  pre.body {{ margin-top: .8rem; padding: 1rem; max-height: 420px; overflow: auto; border: 1px solid var(--border); border-radius: var(--radius); background: #070b13; color: var(--text-2); font-size: .72rem; line-height: 1.65; white-space: pre-wrap; }}
  .src {{ margin: .8rem 0 0; }}
  .src a {{ color: var(--secondary); font-size: .72rem; }}
  .src a:hover {{ color: var(--primary); }}

  /* Quickstart */
  .quickstart {{ padding: clamp(1.75rem, 3.5vw, 3rem) clamp(1.25rem, 4vw, 2rem) 0; }}
  .quickstart-band {{ display: grid; grid-template-columns: minmax(0, .85fr) minmax(0, 1.15fr); gap: clamp(1.5rem, 4vw, 3rem); align-items: center; padding: clamp(1.5rem, 4vw, 2.5rem); border: 1px solid var(--border); border-left: 3px solid var(--primary); border-radius: var(--radius-lg); background: linear-gradient(120deg, rgba(0, 229, 168, .055), rgba(56, 189, 248, .035) 55%, rgba(167, 139, 250, .05)); }}
  .quickstart-commands {{ display: flex; flex-direction: column; gap: .75rem; }}
  .command {{ padding: .7rem .85rem; border: 1px solid var(--border); border-radius: var(--radius); background: #070b13; }}
  .cmd-label {{ display: block; margin-bottom: .3rem; color: var(--muted-2); font-family: var(--mono); font-size: .55rem; letter-spacing: .14em; text-transform: uppercase; }}
  .cmd-line {{ display: flex; align-items: baseline; gap: .55rem; }}
  .cmd-line span {{ color: var(--primary); font-family: var(--mono); font-size: .7rem; }}
  .cmd-line code {{ flex: 1; min-width: 0; color: var(--text-2); font-size: .7rem; overflow-wrap: anywhere; }}
  .install-copy {{ flex-shrink: 0; padding: .18rem .38rem; border: 1px solid transparent; border-radius: 5px; background: transparent; color: var(--muted-2); font-family: var(--mono); font-size: .55rem; letter-spacing: .08em; text-transform: uppercase; transition: color .2s ease, border-color .2s ease; }}
  .install-copy:hover, .install-copy.is-copied {{ border-color: var(--border-2); color: var(--primary); }}
  .harness-row {{ display: flex; flex-wrap: wrap; gap: .4rem; margin-top: 1rem; }}
  .harness-row span {{ padding: .28rem .55rem; border: 1px solid var(--border); border-radius: 6px; background: var(--surface-2); color: var(--muted); font-family: var(--mono); font-size: .6rem; }}

  /* Footer */
  .site-footer {{ border-top: 1px solid var(--border); padding: 2rem 0; color: var(--muted-2); font-size: .76rem; }}
  .footer-inner {{ display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 1rem; }}
  .footer-brand {{ display: flex; align-items: center; gap: .55rem; color: var(--text); font-family: var(--mono); font-size: .78rem; }}
  .footer-brand .brand-mark {{ width: 24px; height: 24px; filter: none; }}
  .footer-brand p {{ margin: 0; color: var(--muted-2); font-family: var(--sans); font-size: .74rem; }}
  .footer-links {{ display: flex; flex-wrap: wrap; gap: 1rem; }}
  .footer-links a {{ color: var(--muted); transition: color .2s ease; }}
  .footer-links a:hover {{ color: var(--primary); }}
  .footer-license {{ margin: 0; }}

  #toTop {{ position: fixed; right: 1.5rem; bottom: 1.5rem; z-index: 60; display: flex; align-items: center; justify-content: center; width: 44px; height: 44px; border: 1px solid var(--border); border-radius: 50%; background: var(--surface-2); color: var(--primary); opacity: 0; pointer-events: none; transform: translateY(8px); transition: opacity .2s ease, transform .2s ease, border-color .2s ease; box-shadow: 0 8px 24px rgba(0, 0, 0, .4); }}
  #toTop.show {{ opacity: 1; pointer-events: auto; transform: translateY(0); }}
  #toTop:hover {{ border-color: var(--primary); }}
  #toTop svg {{ width: 18px; height: 18px; }}

  @keyframes fade-in-up {{ from {{ opacity: 0; transform: translateY(24px); }} to {{ opacity: 1; transform: translateY(0); }} }}
  @keyframes fade-in-right {{ from {{ opacity: 0; transform: translateX(34px); }} to {{ opacity: 1; transform: translateX(0); }} }}
  @keyframes aurora-drift {{ from {{ transform: translate3d(-3%, -2%, 0) scale(1); }} to {{ transform: translate3d(4%, 3%, 0) scale(1.08); }} }}
  @keyframes mind-draw {{ from {{ stroke-dashoffset: 100; }} }}
  @keyframes mind-node {{ from {{ opacity: 0; transform: translate(-50%, -50%) scale(.82); }} }}
  @keyframes robot-blink {{ 0%, 92%, 100% {{ transform: scaleY(1); }} 95% {{ transform: scaleY(.1); }} }}
  @keyframes antenna-pulse {{ 0%, 100% {{ opacity: 1; transform: scale(1); }} 50% {{ opacity: .45; transform: scale(.7); }} }}
  @keyframes agent-ping {{ 0% {{ opacity: .55; transform: translate(-50%, -50%) scale(.75); }} 100% {{ opacity: 0; transform: translate(-50%, -50%) scale(1.5); }} }}
  @media (prefers-reduced-motion: reduce) {{
    *, *::before, *::after {{ animation: none !important; transition: none !important; }}
  }}

  @media (max-width: 980px) {{
    .hero-inner {{ grid-template-columns: 1fr; }}
    .mind-map {{ justify-self: center; max-width: 470px; margin-top: .5rem; }}
    .filter-card {{ position: static; grid-template-columns: 1fr 1fr; }}
    .filter-note {{ grid-column: 1 / -1; }}
    .nav-links {{ display: none; }}
    .quickstart-band {{ grid-template-columns: 1fr; }}
  }}
  @media (max-width: 640px) {{
    .nav-cta {{ display: none; }}
    .nav-logo {{ font-size: .85rem; }}
    .filter-card {{ grid-template-columns: 1fr; }}
    .mind-map {{ max-width: 380px; }}
    .mind-agent .robot {{ width: 58px; height: 58px; }}
    .agent-ring {{ top: 29px; width: 74px; height: 74px; }}
    .mind-node {{ min-width: 98px; max-width: 106px; padding: .45rem .5rem; grid-template-columns: 20px minmax(0, 1fr); gap: .1rem .3rem; }}
    .mind-node.n2, .mind-node.n3 {{ left: 86%; }}
    .mind-node.n5, .mind-node.n6 {{ left: 14%; }}
    .mind-emoji {{ width: 20px; height: 20px; font-size: 11px; }}
    .mind-name {{ font-size: .5rem; }}
    .mind-name .full {{ display: none; }}
    .mind-name .short {{ display: inline; }}
    .mind-cat {{ display: none; }}
    .entry-row {{ grid-template-columns: 24px 32px minmax(0, 1fr) 18px; gap: .55rem; padding: .9rem .3rem; }}
    .entry-body {{ padding-left: .55rem; }}
    .hero-facts li {{ padding-right: .8rem; margin-right: .8rem; }}
    .footer-inner {{ flex-direction: column; align-items: flex-start; }}
  }}
</style>
</head>
<body>
<canvas id="bg-canvas" aria-hidden="true"></canvas>
<div class="aurora" aria-hidden="true"></div>
<a class="skip-link" href="#catalog">Skip to content</a>
<header class="site-header" id="site-header">
  <nav class="container">
    <a class="nav-logo" href="#top" aria-label="{NAME} home">
      {BRAND_MARK}
      <span>{NAME}</span>
    </a>
    <ul class="nav-links">
      <li><a href="#catalog">Index</a></li>
      <li><a href="#cat-pitfalls-100-go-mistakes">Pitfalls</a></li>
      <li><a href="#install">Quickstart</a></li>
      <li><a href="{REPO}/blob/main/README.md" target="_blank" rel="noopener">README</a></li>
    </ul>
    <div class="nav-actions">
      <a class="nav-github" href="{REPO}" target="_blank" rel="noopener" aria-label="GitHub repository">{GITHUB_ICON}</a>
      <a class="nav-cta" href="#install">Install</a>
    </div>
  </nav>
</header>
<main id="top">
  <section class="hero">
    <div class="hero-inner container">
      <div class="hero-copy">
        <p class="hero-kicker"><b>field guide</b><i></i>{total} skills<i></i>MIT</p>
        <h1 class="hero-headline">A field guide<br>for <span class="gradient-text">Go agents.</span></h1>
        <p class="hero-sub">A versioned, cross-referenced pack that makes an agent reliably write, review and debug idiomatic Go &mdash; from architecture and concurrency to security and performance.</p>
        <div class="hero-actions">
          <a class="btn btn-primary" href="#catalog">Open the index <span aria-hidden="true">&rarr;</span></a>
          <a class="btn btn-outline" href="{REPO}" target="_blank" rel="noopener">{GITHUB_ICON} GitHub</a>
        </div>
        <ul class="hero-facts">
          <li><b>{total}</b>skills</li>
          <li><b>{pitfalls}</b>pitfall audits</li>
          <li><b>{routes}</b>routes</li>
          <li><b>MIT</b>license</li>
        </ul>
        <p class="hero-hint">Start with <code>golang-how-to</code> &mdash; the gateway that routes every task to the right skills.</p>
      </div>
      <div class="mind-map" aria-label="Agent skill map">
        <svg class="mind-lines" viewBox="0 0 100 100" preserveAspectRatio="none">
          <defs>
            <linearGradient id="mind-grad" x1="0" y1="0" x2="100" y2="100" gradientUnits="userSpaceOnUse">
              <stop stop-color="#00e5a8"/>
              <stop offset=".5" stop-color="#38bdf8"/>
              <stop offset="1" stop-color="#a78bfa"/>
            </linearGradient>
          </defs>
          <path id="mind-p1" pathLength="100" d="M50 50 C 50 34 50 22 50 10"/>
          <path id="mind-p2" pathLength="100" d="M50 50 C 64 42 78 34 88 27"/>
          <path id="mind-p3" pathLength="100" d="M50 50 C 64 58 78 66 88 73"/>
          <path id="mind-p4" pathLength="100" d="M50 50 C 66 64 62 80 50 90"/>
          <path id="mind-p5" pathLength="100" d="M50 50 C 36 58 22 66 12 73"/>
          <path id="mind-p6" pathLength="100" d="M50 50 C 36 42 22 34 12 27"/>
          <g class="mind-pulses">
            <circle class="mind-pulse" r="1.4" data-path="mind-p1" data-target="n1" data-dur="3400" data-offset="0"/>
            <circle class="mind-pulse" r="1.4" data-path="mind-p2" data-target="n2" data-dur="3800" data-offset="0.16"/>
            <circle class="mind-pulse" r="1.4" data-path="mind-p3" data-target="n3" data-dur="4200" data-offset="0.32"/>
            <circle class="mind-pulse" r="1.4" data-path="mind-p4" data-target="n4" data-dur="3600" data-offset="0.48"/>
            <circle class="mind-pulse" r="1.4" data-path="mind-p5" data-target="n5" data-dur="4000" data-offset="0.64"/>
            <circle class="mind-pulse" r="1.4" data-path="mind-p6" data-target="n6" data-dur="3200" data-offset="0.8"/>
          </g>
        </svg>
        <div class="mind-agent">
          <span class="agent-ring" aria-hidden="true"></span>
          <svg class="robot" viewBox="0 0 64 64" aria-hidden="true">
            <defs>
              <linearGradient id="robot-grad" x1="8" y1="6" x2="56" y2="58" gradientUnits="userSpaceOnUse">
                <stop stop-color="#00e5a8"/>
                <stop offset=".5" stop-color="#38bdf8"/>
                <stop offset="1" stop-color="#a78bfa"/>
              </linearGradient>
            </defs>
            <circle class="antenna-dot" cx="32" cy="5" r="2.6" fill="url(#robot-grad)"/>
            <path d="M32 8v7" stroke="url(#robot-grad)" stroke-width="2" stroke-linecap="round"/>
            <rect x="10" y="15" width="44" height="36" rx="12" fill="rgba(13, 18, 32, .92)" stroke="url(#robot-grad)" stroke-width="2.2"/>
            <rect x="4" y="25" width="5" height="14" rx="2.5" fill="rgba(13, 18, 32, .92)" stroke="url(#robot-grad)" stroke-width="1.6"/>
            <rect x="55" y="25" width="5" height="14" rx="2.5" fill="rgba(13, 18, 32, .92)" stroke="url(#robot-grad)" stroke-width="1.6"/>
            <circle class="eye" cx="24" cy="31" r="3.4" fill="#6bffd6"/>
            <circle class="eye" cx="40" cy="31" r="3.4" fill="#6bffd6"/>
            <path d="M24 41h16" stroke="url(#robot-grad)" stroke-width="2" stroke-linecap="round"/>
            <path d="M28 46h8" stroke="url(#robot-grad)" stroke-width="1.4" stroke-linecap="round" opacity=".6"/>
          </svg>
          <span class="agent-label">agent</span>
          <span class="agent-skill">golang-how-to</span>
        </div>
        {mind_html}
      </div>
    </div>
  </section>
  <section class="quickstart" id="install">
    <div class="container quickstart-band">
      <div class="quickstart-copy">
        <p class="eyebrow">quickstart</p>
        <h2>Install the whole field guide</h2>
        <p>One command installs every skill for any Agent Skills&ndash;compatible harness. Or pick a single skill to start with.</p>
        <div class="harness-row">
          <span>Claude Code</span><span>Codex</span><span>Gemini CLI</span><span>Cursor</span><span>Copilot</span><span>OpenCode</span><span>Antigravity</span>
        </div>
      </div>
      <div class="quickstart-commands">
        <div class="command">
          <span class="cmd-label">all skills</span>
          <div class="cmd-line"><span aria-hidden="true">$</span><code>{INSTALL_ALL}</code><button class="install-copy" type="button" data-copy="{INSTALL_ALL}">copy</button></div>
        </div>
        <div class="command">
          <span class="cmd-label">one skill</span>
          <div class="cmd-line"><span aria-hidden="true">$</span><code>{INSTALL_ONE}</code><button class="install-copy" type="button" data-copy="{INSTALL_ONE}">copy</button></div>
        </div>
      </div>
    </div>
  </section>
  <section class="guide container" id="catalog">
    <div class="guide-head">
      <p class="eyebrow">the index</p>
      <h2>Every skill, one shelf.</h2>
      <p>A dense, searchable index of the whole pack. Filter by route, then open any entry to read the full skill.</p>
    </div>
    <div class="filter-card" id="filters">
      <div class="filter-search">
        <label class="filter-label" for="search">Search</label>
        <input type="search" id="search" placeholder="name or description..." autocomplete="off">
      </div>
      <div class="filter-routes">
        <p class="filter-label">Routes</p>
        <div class="route-chips" id="chips">{chips}</div>
      </div>
      <p class="filter-note"><strong id="result-count">{total}</strong> <span id="result-label">skills</span> in view</p>
    </div>
    <div class="guide-body" id="catalog-body">{"\n".join(sections)}</div>
  </section>
</main>
<footer class="site-footer">
  <div class="container footer-inner">
    <div class="footer-brand">{BRAND_MARK}<p>{NAME} &mdash; a field guide for Go agents.</p></div>
    <div class="footer-links">
      <a href="{REPO}" target="_blank" rel="noopener">GitHub</a>
      <a href="{REPO}/blob/main/README.md" target="_blank" rel="noopener">README</a>
      <a href="{REPO}/blob/main/EVALUATIONS.md" target="_blank" rel="noopener">Evaluations</a>
      <a href="{REPO}/issues" target="_blank" rel="noopener">Issues</a>
    </div>
    <p class="footer-license">&copy; 2026 Fabiano Florentino &middot; MIT License</p>
  </div>
</footer>
<button id="toTop" type="button" aria-label="Back to top">
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 19V6M6 12l6-6 6 6"/></svg>
</button>
<script>
  (function backgroundParticles() {{
    const canvas = document.getElementById('bg-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    const COLORS = ['0,229,168', '56,189,248', '167,139,250'];
    let width = 0;
    let height = 0;
    let particles = [];
    let tick = 0;

    function resize() {{
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      width = window.innerWidth;
      height = window.innerHeight;
      canvas.width = Math.round(width * dpr);
      canvas.height = Math.round(height * dpr);
      canvas.style.width = width + 'px';
      canvas.style.height = height + 'px';
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      const count = Math.max(32, Math.min(88, Math.round((width * height) / 24000)));
      particles = Array.from({{ length: count }}, () => ({{
        x: Math.random() * width,
        y: Math.random() * height,
        vx: (Math.random() - 0.5) * 0.16,
        vy: (Math.random() - 0.5) * 0.16,
        r: Math.random() * 1.2 + 0.35,
        c: COLORS[Math.floor(Math.random() * COLORS.length)],
        a: Math.random() * 0.34 + 0.12
      }}));
    }}

    function frame() {{
      ctx.clearRect(0, 0, width, height);
      for (const p of particles) {{
        p.x += p.vx;
        p.y += p.vy;
        if (p.x < -24) p.x = width + 24;
        if (p.x > width + 24) p.x = -24;
        if (p.y < -24) p.y = height + 24;
        if (p.y > height + 24) p.y = -24;
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(' + p.c + ',' + p.a + ')';
        ctx.fill();
      }}
      tick++;
      if (tick % 2 === 0) {{
        const reach = 135;
        for (let i = 0; i < particles.length; i++) {{
          for (let j = i + 1; j < particles.length; j++) {{
            const a = particles[i];
            const b = particles[j];
            const dx = a.x - b.x;
            const dy = a.y - b.y;
            const d2 = dx * dx + dy * dy;
            if (d2 > reach * reach) continue;
            const alpha = (1 - Math.sqrt(d2) / reach) * 0.16;
            ctx.strokeStyle = 'rgba(56,189,248,' + alpha + ')';
            ctx.lineWidth = 0.6;
            ctx.beginPath();
            ctx.moveTo(a.x, a.y);
            ctx.lineTo(b.x, b.y);
            ctx.stroke();
          }}
        }}
      }}
      requestAnimationFrame(frame);
    }}

    resize();
    window.addEventListener('resize', resize);
    requestAnimationFrame(frame);
  }})();


  const search = document.getElementById('search');
  const chips = document.querySelectorAll('.route-chip');
  const categories = document.querySelectorAll('.category');
  const toTop = document.getElementById('toTop');
  const header = document.getElementById('site-header');
  const resultCount = document.getElementById('result-count');
  const resultLabel = document.getElementById('result-label');
  const filters = document.getElementById('filters');
  const guideBody = document.getElementById('catalog-body');
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  let activeFilter = 'All';

  function currentY() {{
    return window.scrollY || window.pageYOffset || document.documentElement.scrollTop || 0;
  }}

  function smoothScrollTo(y) {{
    window.scrollTo({{ top: Math.max(y, 0), behavior: 'smooth' }});
  }}

  function updateChrome() {{
    const y = currentY();
    header.classList.toggle('scrolled', y > 8);
    toTop.classList.toggle('show', y > 400);
  }}

  function apply() {{
    const q = search.value.trim().toLowerCase();
    let visible = 0;
    categories.forEach(cat => {{
      let anyVisible = false;
      cat.querySelectorAll('.entry').forEach(s => {{
        const hay = s.dataset.search || s.dataset.name;
        const okCat = activeFilter === 'All' || s.dataset.category === activeFilter;
        const okQ = !q || s.dataset.name.toLowerCase().includes(q) || hay.includes(q);
        const show = okCat && okQ;
        s.style.display = show ? '' : 'none';
        if (show) {{ anyVisible = true; visible++; }}
      }});
      cat.style.display = anyVisible ? '' : 'none';
      if (anyVisible && !reduceMotion) {{
        cat.classList.remove('fade-in');
        void cat.offsetWidth;
        cat.classList.add('fade-in');
      }}
    }});
    guideBody.classList.toggle('filtered', activeFilter !== 'All' || q !== '');
    resultCount.textContent = visible;
    resultLabel.textContent = visible === 1 ? 'skill' : 'skills';
    updateChrome();
  }}

  function revealResults() {{
    if (reduceMotion) return;
    const visibleTop = header.offsetHeight + filters.offsetHeight + 16;
    const top = guideBody.getBoundingClientRect().top;
    if (top >= visibleTop && top <= window.innerHeight - 80) return;
    const y = top + currentY() - visibleTop;
    smoothScrollTo(y);
  }}

  function syncMap(filter) {{
    document.querySelectorAll('.mind-node').forEach(node => {{
      node.classList.toggle('active', node.dataset.filter === filter);
      node.setAttribute('aria-pressed', String(node.classList.contains('active')));
    }});
  }}

  chips.forEach(chip => chip.addEventListener('click', () => {{
    chips.forEach(c => c.classList.remove('active'));
    chip.classList.add('active');
    activeFilter = chip.dataset.filter;
    syncMap(activeFilter);
    apply();
    revealResults();
  }}));

  document.querySelectorAll('.mind-node').forEach(node => {{
    node.addEventListener('click', () => {{
      const chip = [...chips].find(c => c.dataset.filter === node.dataset.filter);
      if (chip) chip.click();
    }});
  }});

  (function mindPulses() {{
    const circles = document.querySelectorAll('.mind-pulse');
    if (!circles.length || reduceMotion) return;
    const items = [];
    circles.forEach(circle => {{
      const path = document.getElementById(circle.dataset.path);
      if (!path) return;
      items.push({{
        circle,
        path,
        target: circle.dataset.target ? document.querySelector('.mind-node.' + circle.dataset.target) : null,
        length: path.getTotalLength(),
        dur: Number(circle.dataset.dur) || 3600,
        offset: Number(circle.dataset.offset) || 0,
        prev: null
      }});
    }});
    if (!items.length) return;
    for (const item of items) {{
      const t = item.offset % 1;
      const point = item.path.getPointAtLength(t * item.length);
      item.circle.setAttribute('cx', point.x);
      item.circle.setAttribute('cy', point.y);
      item.prev = t;
    }}
    setTimeout(() => {{
      document.documentElement.classList.add('pulses-ready');
      let start = null;
      function tick(now) {{
        if (start === null) start = now;
        for (const item of items) {{
          const t = (((now - start) / item.dur) + item.offset) % 1;
          const point = item.path.getPointAtLength(t * item.length);
          item.circle.setAttribute('cx', point.x);
          item.circle.setAttribute('cy', point.y);
          item.circle.style.opacity = (0.4 + 0.6 * Math.sin(t * Math.PI)).toFixed(2);
          if (item.target && t < item.prev) {{
            item.target.classList.add('hit');
            setTimeout(() => item.target.classList.remove('hit'), 420);
          }}
          item.prev = t;
        }}
        requestAnimationFrame(tick);
      }}
      requestAnimationFrame(tick);
    }}, 1800);
  }})();

  search.addEventListener('input', apply);

  document.querySelectorAll('details.entry').forEach(entry => {{
      const summary = entry.querySelector('summary.entry-row');
      const body = entry.querySelector('.entry-body');
      if (!summary || !body) return;
      let animating = false;
      summary.addEventListener('click', event => {{
        if (reduceMotion) return;
        event.preventDefault();
        if (animating) return;
        animating = true;
        if (entry.open) {{
          const finish = () => {{
            entry.open = false;
            body.style.height = '';
            animating = false;
          }};
          const timer = setTimeout(finish, 380);
          body.style.height = body.scrollHeight + 'px';
          requestAnimationFrame(() => {{ body.style.height = '0px'; }});
          body.addEventListener('transitionend', () => {{
            clearTimeout(timer);
            finish();
          }}, {{ once: true }});
        }} else {{
          const finish = () => {{
            body.style.height = '';
            animating = false;
          }};
          const timer = setTimeout(finish, 380);
          entry.open = true;
          body.style.height = '0px';
          requestAnimationFrame(() => {{ body.style.height = body.scrollHeight + 'px'; }});
          body.addEventListener('transitionend', () => {{
            clearTimeout(timer);
            finish();
          }}, {{ once: true }});
        }}
      }});
  }});

  document.querySelectorAll('[data-copy]').forEach(btn => {{
    btn.addEventListener('click', async () => {{
      const text = btn.dataset.copy;
      try {{ await navigator.clipboard.writeText(text); }} catch (e) {{ /* clipboard unavailable */ }}
      const label = btn.textContent;
      btn.textContent = 'copied';
      btn.classList.add('is-copied');
      setTimeout(() => {{ btn.textContent = label; btn.classList.remove('is-copied'); }}, 1600);
    }});
  }});

  window.addEventListener('scroll', updateChrome, {{ passive: true }});
  window.addEventListener('resize', updateChrome);
  window.addEventListener('load', updateChrome);
  updateChrome();

  toTop.addEventListener('click', e => {{
    e.preventDefault();
    smoothScrollTo(0);
  }});
</script>
</body>
</html>
"""
    with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(page)
    with open(os.path.join(out_dir, "favicon.svg"), "w", encoding="utf-8") as f:
        f.write(FAVICON_SVG)

    print(f"generated docs/index.html with {total} skills across "
          f"{len(CATEGORIES)} categories")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
