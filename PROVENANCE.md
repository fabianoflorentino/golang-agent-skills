# Provenance

This repository is a **clean-room, house-developed skill catalog** for Golang agent workflows, published under MIT. It was informed by — but is not a copy of — the open skill catalog at [samber/cc-skills-golang](https://github.com/samber/cc-skills-golang).

## Origin and method

- **Reference only.** The upstream catalog was used during development solely as a capability checklist — which Go domains deserve agent skills — never as source text.
- **Every skill body was written in house** following a shared template (`**Persona:**`, `**Modes:**`, `**When to use:**`, original Go examples, decision tables, `## Cross-references`).
- **Skill count:** this repo ships 58 skills; 46 of them have a name counterpart in the upstream catalog, and all 46 were rewritten from scratch in house style.

## Divergence measurement

Each rewritten skill's body (text after the YAML front matter) was compared to its upstream counterpart using **Jaccard similarity** over lowercased `[a-z0-9_]+` tokens:

| Metric | Value |
| --- | --- |
| Skills measured | 46 |
| Similarity range | 0.233 – 0.747 |
| Mean similarity | 0.576 |
| Skills above 0.75 | 0 |

As a baseline, the un-rewritten counterparts measured **≈0.99** similarity to upstream.

## Deliberate differences

- `skill-library-version` keys present upstream were **dropped**; they pinned the upstream catalog's own dependency versions.
- Cross-references use short house names (`golang-grpc`) instead of long-form upstream paths, and point only at skills that exist in this catalog.
- Front matter (name, description, compatibility, `allowed-tools`) was authored here; `metadata.author` and license (`MIT`) reflect this repository.
- `references/` and `assets/` subdirectories are capability references for each skill. Most are upstream-derived reference material kept for completeness; assets such as `skills/golang-lint/assets/.golangci.yml` and the CI workflow templates under `skills/golang-continuous-integration/assets/` were authored in this repository.

## Distribution

- Docs are regenerated from the skill catalog into `docs/index.html` by `scripts/generate_docs.py` and published via GitHub Actions → GitHub Pages.
- CI runs a markdown lint (0 issues), a skills security scan, and the Pages build/deploy on every push.

Copyright (c) Fabiano Florentino. Licensed under the MIT License — see the [LICENSE](LICENSE) file.
