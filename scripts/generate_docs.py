#!/usr/bin/env python3
"""Generate docs/index.html from the skills/*/SKILL.md catalog.

Reads the YAML frontmatter of every skill, groups skills by category, and
writes a self-contained static site (no external assets) that can be served
from GitHub Pages.
"""
from __future__ import annotations

import glob
import html
import os
import re
import sys

REPO = "https://github.com/fabianoflorentino/golang-agent-skills"
NAME = "golang-agent-skills"

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
        data[path] = val.strip('"').strip()
        i += 1
    return data


def nested(data: dict, path: str, default=""):
    return data.get(path, default)


def skill_blurb(skill: str) -> str:
    return f"{REPO}/blob/main/skills/{skill}/SKILL.md"


def render_skill_html(skill: str, data: dict) -> str:
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
    meta = [
        ("version", version),
        ("author", author),
    ]
    meta_html = " &middot; ".join(
        f'<span class="meta">{html.escape(k)}: <code>{html.escape(v)}</code></span>'
        for k, v in meta if v
    )
    detail_attrs = 'open' if name.startswith("golang-pitfalls") else ""
    return f"""<section class="skill" data-category="{html.escape(CATEGORY_FOR.get(skill, 'Other'))}" data-name="{html.escape(skill)}" data-search="{html.escape(desc).lower()}">
  <h3><span class="emoji">{html.escape(emoji)}</span> <code>{html.escape(name)}</code> {badge}</h3>
  <p class="desc">{html.escape(desc)}</p>
  <p class="metaline">{meta_html}</p>
  <details {detail_attrs}>
    <summary>View skill content</summary>
    <div class="compat">{html.escape(compat)}</div>
    <pre class="body">{html.escape(data["body"].strip())}</pre>
    <p class="src"><a href="{skill_blurb(skill)}" target="_blank" rel="noopener">View source on GitHub</a></p>
  </details>
</section>"""


def main() -> int:
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    skills_dir = os.path.join(root, "skills")
    out_dir = os.path.join(root, "docs")
    os.makedirs(out_dir, exist_ok=True)

    parsed: dict[str, dict] = {}
    for path in sorted(glob.glob(os.path.join(skills_dir, "*", "SKILL.md"))):
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

    sections = []
    for cat, skills in CATEGORIES:
        present = [s for s in skills if s in parsed]
        if not present:
            continue
        cards = "\n".join(render_skill_html(s, parsed[s]) for s in present)
        sections.append(
            f'<section class="category" data-category="{html.escape(cat)}">'
            f'<h2>{html.escape(cat)}</h2>'
            f'<p class="count">{len(present)} skills</p>'
            f'<div class="grid">{cards}</div></section>'
        )

    chip_sections = ["All"] + [c for c, _ in CATEGORIES]
    chips = "".join(
        f'<button class="chip {"" if c == "All" else ""}" data-filter="{html.escape(c)}">{html.escape(c)}</button>'
        for c in chip_sections
    )

    page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{NAME} — Go agent skills catalog</title>
<meta name="description" content="AI Agent Skills for production-ready Go projects, plus the pitfalls from 100 Go Mistakes and How to Avoid Them.">
<style>
  :root {{
    --bg: #0f172a; --panel: #1e293b; --panel2: #263448; --text: #e2e8f0;
    --muted: #9aa7ba; --accent: #38bdf8; --accent-ink: #06202e;
    --border: #334155; --green: #4ade80;
  }}
  * {{ box-sizing: border-box; }}
  html {{ scroll-behavior: smooth; }}
  body {{ margin: 0; background: var(--bg); color: var(--text); font: 17px/1.7 system-ui, -apple-system, "Segoe UI", Roboto, sans-serif; }}
  header.topbar {{ position: sticky; top: 0; z-index: 6; background: rgba(15, 23, 42, 0.95); backdrop-filter: blur(10px); box-shadow: 0 1px 0 var(--border); }}
  header.topbar .bar {{ max-width: 1160px; margin: 0 auto; padding: 12px 28px; }}
  header.topbar .top {{ display: flex; align-items: center; gap: 18px; }}
  header.topbar .brand {{ font-size: 18px; font-weight: 700; color: var(--accent); letter-spacing: -0.3px; white-space: nowrap; }}
  .hero {{ max-width: 1160px; margin: 0 auto; padding: 44px 28px 6px; }}
  .hero h1 {{ margin: 0 0 10px; font-size: 34px; letter-spacing: -0.4px; }}
  .hero p {{ margin: 6px 0; color: var(--muted); font-size: 16.5px; max-width: 860px; }}
  .hero .links {{ margin-top: 16px; }}
  .hero .links a {{ color: var(--accent); margin-right: 18px; text-decoration: none; font-size: 15px; }}
  .hero .links a:hover {{ text-decoration: underline; }}
  main {{ max-width: 1160px; margin: 0 auto; padding: 10px 28px 80px; }}
  input[type=search] {{ flex: 1 1 auto; width: 100%; padding: 12px 18px; font-size: 15px; border-radius: 12px; border: 1px solid var(--border); background: var(--panel); color: var(--text); outline: none; }}
  input[type=search]:focus {{ border-color: var(--accent); }}
  .chips {{ display: flex; flex-wrap: wrap; gap: 10px; margin-top: 14px; }}
  .chip {{ background: var(--panel); color: var(--text); border: 1px solid var(--border); border-radius: 999px; padding: 8px 16px; cursor: pointer; font-size: 14px; }}
  .chip:hover {{ border-color: var(--accent); }}
  .chip.active {{ background: var(--accent); border-color: var(--accent); color: var(--accent-ink); font-weight: 600; }}
  .category {{ margin: 46px 0 0; scroll-margin-top: 130px; }}
  @keyframes rise {{ from {{ transform: translateY(12px); opacity: 0.4; }} to {{ transform: translateY(0); opacity: 1; }} }}
  #catalog.enter {{ animation: rise 0.4s ease-out; }}
  .category h2 {{ font-size: 22px; border-bottom: 1px solid var(--border); padding-bottom: 12px; color: var(--accent); margin: 0 0 4px; }}
  .count {{ color: var(--muted); font-size: 13px; margin: 8px 0 0; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(360px, 1fr)); gap: 26px; margin-top: 22px; }}
  .skill {{ background: var(--panel); border: 1px solid var(--border); border-radius: 16px; padding: 24px 26px; box-shadow: 0 1px 4px rgba(0, 0, 0, 0.25); transition: border-color 0.15s, transform 0.15s; display: flex; flex-direction: column; }}
  .skill:hover {{ border-color: #475569; transform: translateY(-2px); }}
  .skill h3 {{ margin: 0 0 16px; font-size: 19px; display: flex; align-items: center; gap: 14px; }}
  .skill h3 code {{ color: var(--green); font-size: 18px; }}
  .emoji {{ flex: 0 0 auto; width: 46px; height: 46px; display: inline-flex; align-items: center; justify-content: center; background: var(--panel2); border: 1px solid var(--border); border-radius: 13px; font-size: 22px; }}
  .badge {{ display: inline-block; background: var(--panel2); border: 1px solid var(--border); color: var(--muted); border-radius: 7px; font-size: 11px; padding: 3px 7px; margin-left: auto; }}
  .desc {{ margin: 0 0 16px; color: var(--muted); font-size: 15px; line-height: 1.65; flex: 1 1 auto; }}
  .metaline {{ margin: 0 0 16px; font-size: 13px; color: #7d8ba1; }}
  .meta code {{ color: var(--text); }}
  .compat {{ font-size: 13px; color: var(--muted); margin: 14px 0 0; }}
  details {{ border-top: 1px solid var(--border); padding-top: 14px; }}
  summary {{ cursor: pointer; color: var(--accent); font-size: 14px; font-weight: 600; }}
  pre.body {{ background: #0b1220; border: 1px solid var(--border); border-radius: 12px; padding: 18px; overflow: auto; max-height: 440px; font-size: 13px; line-height: 1.6; white-space: pre-wrap; margin-top: 14px; }}
  .src {{ margin: 14px 0 0; }}
  .src a {{ color: var(--accent); text-decoration: none; font-size: 13px; }}
  .src a:hover {{ text-decoration: underline; }}
  #toTop {{ position: fixed; right: 26px; bottom: 26px; width: 48px; height: 48px; border-radius: 50%; border: 1px solid var(--border); background: var(--panel); color: var(--accent); font-size: 20px; cursor: pointer; opacity: 0; pointer-events: none; transition: opacity 0.2s, transform 0.2s; z-index: 60; box-shadow: 0 4px 14px rgba(0, 0, 0, 0.35); }}
  #toTop.show {{ opacity: 1; pointer-events: auto; transform: translateY(0); }}
  #toTop:not(.show) {{ transform: translateY(8px); }}
  footer {{ padding: 32px; text-align: center; color: var(--muted); font-size: 14px; }}
</style>
</head>
<body>
<header class="topbar">
  <div class="bar">
    <div class="top">
      <span class="brand">🛠&nbsp; {NAME}</span>
      <input type="search" id="search" placeholder="Search skills by name or description..." autocomplete="off">
    </div>
    <div class="chips" id="chips">{chips}</div>
  </div>
</header>
<main>
  <section class="hero">
    <h1>🛠&nbsp; {NAME}</h1>
    <p>AI Agent Skills for production-ready Go projects &mdash; the full general-purpose and library catalog, plus the pitfalls distilled from <em>100 Go Mistakes and How to Avoid Them</em>.</p>
    <div class="links">
      <a href="{REPO}" target="_blank" rel="noopener">GitHub</a>
      <a href="{REPO}/blob/main/README.md" target="_blank" rel="noopener">README</a>
      <a href="https://skills.sh/" target="_blank" rel="noopener">skills CLI</a>
    </div>
  </section>
  <div id="catalog">{"\n".join(sections)}</div>
  <button id="toTop" type="button" aria-label="Back to top">↑</button>
</main>
<footer>Generated from <code>skills/*/SKILL.md</code>. Licensed under MIT.</footer>
<script>
  const search = document.getElementById('search');
  const chips = document.querySelectorAll('.chip');
  const categories = document.querySelectorAll('.category');
  const toTop = document.getElementById('toTop');
  let activeFilter = 'All';

  function currentY() {{
    return window.scrollY || window.pageYOffset || document.documentElement.scrollTop || 0;
  }}

  function smoothScrollTo(y) {{
    window.scrollTo({{ top: Math.max(y, 0), behavior: 'smooth' }});
  }}

  function updateToTop() {{
    toTop.classList.toggle('show', currentY() > 300);
  }}

  function apply() {{
    const q = search.value.trim().toLowerCase();
    categories.forEach(cat => {{
      let anyVisible = false;
      cat.querySelectorAll('.skill').forEach(s => {{
        const name = s.dataset.name.toLowerCase();
        const hay = s.dataset.search || s.dataset.name;
        const okCat = activeFilter === 'All' || s.dataset.category === activeFilter;
        const okQ = !q || s.dataset.name.toLowerCase().includes(q) || (s.dataset.search && s.dataset.search.includes(q)) || hay.includes(q);
        const show = okCat && okQ;
        s.style.display = show ? '' : 'none';
        if (show) anyVisible = true;
      }});
      cat.style.display = anyVisible ? '' : 'none';
    }});
    updateToTop();
  }}

  function scrollToFilter() {{
    if (activeFilter === 'All') {{
      smoothScrollTo(0);
    }}
  }}

  chips.forEach(chip => chip.addEventListener('click', () => {{
    chips.forEach(c => c.classList.remove('active'));
    chip.classList.add('active');
    activeFilter = chip.dataset.filter;
    apply();
    const catalog = document.getElementById('catalog');
    catalog.classList.remove('enter');
    void catalog.offsetWidth;
    catalog.classList.add('enter');
    scrollToFilter();
  }}));

  search.addEventListener('input', apply);

  window.addEventListener('scroll', updateToTop, {{ passive: true }});
  window.addEventListener('resize', updateToTop);
  window.addEventListener('load', updateToTop);
  updateToTop();

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

    count = len(parsed)
    print(f"generated docs/index.html with {count} skills across "
          f"{len(CATEGORIES)} categories")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())