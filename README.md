# golang-agent-skills

**Go skills for AI coding agents** — a single pack of 58 versioned, cross-referenced skills that make an agent reliably write, review and debug idiomatic Go.

The pack is our own curated set, built on top of two foundations that we attribute explicitly:

- the general-purpose and library catalog from [samber/cc-skills-golang](https://github.com/samber/cc-skills-golang) (MIT, © Samuel Berthe), which we fork, curate, test and extend — keeping a single voice across the whole set;
- a new **Pitfalls** category we authored, distilled from [*100 Go Mistakes and How to Avoid Them*](https://100go.co/) by Teiva Harsanyi — 100 numbered mistakes turned into 11 ordered audit checklists.

Everything is English, MIT-licensed, and verified by the repo's own linters so the pack stays coherent at scale.

## Why this pack

- **One entry point.** Set `golang-how-to` as a gateway and the always-on routing rules handle the rest: each task loads the right skill and any cross-references it needs.
- **Two layers, complementary.** The `golang-*` skills carry the full best-practice depth; the `golang-pitfalls-*` checklists answer "did we already hit mistake N?" — load a Pitfalls skill alongside its general-purpose owner.
- **Predicted weight, on purpose.** Skills trigger only when their topic is relevant, and deep material lives in `references/` files that load lazily, so they stay out of the context budget until actually needed.
- **Verified, not AI-slop.** The repository is linted in CI (`markdownlint`), skills are validated for frontmatter consistency, and the upstream adversarial-evaluation methodology is kept — see [EVALUATIONS.md](./EVALUATIONS.md).

## Install

**skills CLI** — works with any Agent Skills–compatible tool:

```sh
npx skills add https://github.com/fabianoflorentino/golang-agent-skills --all
# or one skill at a time:
npx skills add https://github.com/fabianoflorentino/golang-agent-skills --skill golang-pitfalls-error-handling
```

**Per tool:**

| Tool | Command / how |
| --- | --- |
| Claude Code | `/plugin install github.com/fabianoflorentino/golang-agent-skills` |
| OpenAI Codex | `codex plugin add github:fabianoflorentino/golang-agent-skills` |
| Gemini CLI | `gemini extensions install https://github.com/fabianoflorentino/golang-agent-skills` (update: `gemini extensions update golang-agent-skills`) |
| Openclaw | `git clone https://github.com/fabianoflorentino/golang-agent-skills.git ~/.openclaw/skills/golang-agent-skills` |
| Cursor | `git clone https://github.com/fabianoflorentino/golang-agent-skills.git ~/.cursor/skills/golang-agent-skills` |
| Copilot | `git clone https://github.com/fabianoflorentino/golang-agent-skills.git ~/.copilot/skills/golang-agent-skills` |
| OpenCode | `git clone https://github.com/fabianoflorentino/golang-agent-skills.git ~/.agents/skills/golang-agent-skills` |
| Antigravity | `git clone https://github.com/fabianoflorentino/golang-agent-skills.git ~/.antigravity/skills/golang-agent-skills` (update: `git pull`) |

Browse the full catalog with descriptions, versions and weights at <https://fabianoflorentino.github.io/golang-agent-skills/>.

## What's inside

Three groups of skills. `Size` is the estimated weight of a whole skill directory (`SKILL.md` + `references/`, chars/4), computed from this repo.

### General purpose — 31 skills

| Skill | Area | Focus | Size (tok) |
| --- | --- | --- | --- |
| `golang-rest` | APIs | REST design: resources, JSON contract, problem+json errors, pagination, idempotency, timeouts | 2078 |
| `golang-code-style` | Code Quality | Formatting and conventions: gofmt/goimports, comments, style consistency | 3206 |
| `golang-documentation` | Code Quality | Package docs, godoc conventions, examples, README structure | 11004 |
| `golang-error-handling` | Code Quality | Error creation, wrapping, sentinels, `errors.Is`/`As`, panic recovery | 5393 |
| `golang-lint` | Code Quality | `golangci-lint` presets, custom rules, CI integration, suppression | 4568 |
| `golang-naming` | Code Quality | Identifiers: packages, constructors, structs, interfaces, errors, acronyms | 7823 |
| `golang-safety` | Code Quality | Defensive coding: nil safety, append aliasing, overflow, zero values | 5646 |
| `golang-security` | Code Quality | Injection, crypto, secrets, cookies; audit and review modes | 23299 |
| `golang-structs-interfaces` | Code Quality | Struct/interface design, embedding, tags, pointer vs value receivers | 4550 |
| `golang-concurrency` | Architecture | Goroutines, channels, sync primitives, pipelines, worker pools | 7565 |
| `golang-context` | Architecture | `context.Context` creation, cancellation, timeouts, propagation | 4846 |
| `golang-data-structures` | Architecture | Slice/map/channel internals, capacity handling, aliasing pitfalls | 6548 |
| `golang-database` | Architecture | Bind params, pooling, transactions, migrations, sqlc/sqlboiler | 7804 |
| `golang-dependency-injection` | Architecture | DI patterns and how to choose between wire, dig and fx | 5812 |
| `golang-design-patterns` | Architecture | Idiomatic patterns: functional options, builder, middleware, circuit breaker | 10705 |
| `golang-modernize` | Architecture | Adopting recent language features and stdlib packages | 13380 |
| `golang-refactoring` | Architecture | Safe, staged refactoring with gopls-driven, behavior-preserving transforms | 23591 |
| `golang-benchmark` | QA & Perf | Benchmarks, pprof profiles, benchstat, continuous profiling | 33936 |
| `golang-observability` | QA & Perf | slog, Prometheus, OpenTelemetry, pprof, alerting | 19913 |
| `golang-performance` | QA & Perf | Allocations, GC tuning, caching, pooling, hot-path reviews | 19880 |
| `golang-testing` | QA & Perf | Table-driven tests, fuzzing, goleak, snapshots, coverage | 9088 |
| `golang-troubleshooting` | QA & Perf | Debugging methodology: Delve, race detector, GODEBUG, pprof | 18153 |
| `golang-cli` | Project Setup | CLI architecture: layout, exit codes, signals, terminal UX | 2563 |
| `golang-continuous-integration` | Project Setup | CI/CD pipelines for Go on GitHub Actions | 4694 |
| `golang-dependency-management` | Project Setup | go.mod hygiene, versioning, `replace`, workspaces | 5890 |
| `golang-gopls` | Project Setup | Semantic navigation and safe refactoring through the Go language server | 12808 |
| `golang-pkg-go-dev` | Project Setup | Exploring pkg.go.dev (godig): docs, versions, importers, CVEs | 4939 |
| `golang-popular-libraries` | Project Setup | When the stdlib is enough vs. which library to adopt | 5488 |
| `golang-project-layout` | Project Setup | Repo structure: `cmd`/`internal`/`pkg`, monorepos, keeping it flat | 5362 |
| `golang-stay-updated` | Project Setup | Where to follow Go's evolution and learning resources | 1754 |
| `golang-how-to` | Gateway | The routing table: picks the right skill for every Go task | 18025 |

### Libraries & frameworks — 16 skills

| Skill | Focus | Size (tok) |
| --- | --- | --- |
| `golang-google-wire` | Compile-time dependency injection with google/wire | 7808 |
| `golang-uber-dig` | Reflection-based DI: Provide/Invoke, value groups, Decorate | 6801 |
| `golang-uber-fx` | Application framework: modules, lifecycle, signal-aware run | 7644 |
| `golang-grpc` | Protobuf layout, services, streaming, interceptors, error codes | 5651 |
| `golang-graphql` | gqlgen/graphql-go: schema, resolvers, subscriptions, federation | 8582 |
| `golang-swagger` | OpenAPI/Swagger via swaggo: annotations, codegen, security | 3629 |
| `golang-spf13-cobra` | Command trees, hooks, flags, shell completion, testing | 7977 |
| `golang-spf13-viper` | Layered config: flag > env > file > KV > default | 7633 |
| `golang-stretchr-testify` | assert/require/mock/suite and custom matchers | 2662 |
| `golang-samber-do` | Type-safe DI container with lifecycle and health checks | 4148 |
| `golang-samber-lo` | 500+ generic helpers for slices, maps, channels, strings | 10158 |
| `golang-samber-mo` | Monadic types: Option, Result, Either, Future, IO | 12340 |
| `golang-samber-oops` | Structured errors: builders, stack traces, error codes | 2960 |
| `golang-samber-ro` | Reactive streams: 150+ operators, backpressure, context | 12046 |
| `golang-samber-slog` | Multi-handler logging pipeline, sampling, 20+ sinks | 10590 |
| `golang-samber-hot` | In-memory cache with 9 eviction algorithms and TTL | 7913 |

### Pitfalls — 11 skills (100 Go Mistakes, in book order)

| Skill | Mistakes | Focus | Size (tok) |
| --- | --- | --- | --- |
| `golang-pitfalls-code-organization` | #1–16 | Shadowing, init, interface pollution, generics, layout | 2236 |
| `golang-pitfalls-data-types` | #17–29 | Overflow, floats, slices (cap/nil), maps, leaks | 1697 |
| `golang-pitfalls-control-structures` | #30–35 | Range copies, range args, labels, `defer` in loops | 989 |
| `golang-pitfalls-strings` | #36–41 | Runes vs bytes, iteration, trimming, `Builder` | 966 |
| `golang-pitfalls-functions-methods` | #42–47 | Receivers, named results, nil receivers, `defer` eval | 1135 |
| `golang-pitfalls-error-handling` | #48–54 | Panic vs error, `%w`, `As`/`Is`, sentinels, swallowing | 974 |
| `golang-pitfalls-concurrency-foundations` | #55–60 | Parallelism, channels vs mutexes, races, context | 1020 |
| `golang-pitfalls-concurrency-practice` | #61–74 | Cancellation, `select`, nil channels, `WaitGroup`, `errgroup` | 1698 |
| `golang-pitfalls-standard-library` | #75–81 | `time`, JSON, `database/sql`, HTTP timeouts, closing | 1200 |
| `golang-pitfalls-testing` | #82–90 + fuzz | Categorization, race flag, parallelism, sleeps, benchmarks | 1522 |
| `golang-pitfalls-optimizations` | #91–100 | Caches, false sharing, alignment, allocations, GC | 1744 |

## How the pack is wired

- **Routing.** The gateway skill `golang-how-to` maps every Go task to its primary skill and its cross-references. The same routing table ships as always-on rules in `rules/golang-always.mdc`, so agents that read `.mdc` rules get the mapping without loading any skill.
- **Atomic units that reference each other.** Rules live in one place and are imported elsewhere (e.g. error-handling conventions that affect logging live in `golang-error-handling`, not `golang-observability`). Installing only a subset gives a partial, possibly inconsistent view — install general-purpose skills together.
- **Lazy depth.** `SKILL.md` stays an entrypoint; deep material sits in `references/` and is read on demand.
- **Override.** Skills marked ⚙️ in their frontmatter can be superseded by a company skill. Declare it explicitly, e.g.: `This skill supersedes fabianoflorentino/golang-agent-skills@golang-naming skill for [company] projects.`

## Use in CI for AI-driven reviews

Add an AI agent as a PR reviewer alongside static analysis: it routes each review area to the matching skill and catches architectural drift, logic bugs and concurrency hazards that linters miss. Setup for Claude Code Action and GitHub Copilot is in [GOLANG-AI-DRIVEN-REVIEW.md](./GOLANG-AI-DRIVEN-REVIEW.md).

## Evaluations

The upstream `golang-*` skills ship with adversarial evaluation reports; we keep the methodology but the published numbers are the upstream's measurement runs and were **not** reproduced here. The `golang-pitfalls-*` skills are not adversarially evaluated yet. See [EVALUATIONS.md](./EVALUATIONS.md) for the format and the plan.

## Tuning triggers

If a skill fires too often or too rarely, open an issue proposing a `description` change — that field is the primary trigger. Some skills also carry a `When to use` section as an exclusion layer. `SKILL.md` is meant to stay lean; move detail into `references/`.

## Overlap

- The Pitfalls checklists overlap deliberately with their general-purpose owners. Load them together for audits; load the general skill alone for greenfield code. `golang-how-to` documents each pair.
- Expect some overlap between `golang-naming` / `golang-code-style` and golangci-lint — the skills add rationale, not just rules.
- `golang-security` distills a large part of the Bearer (SAST) checklist; the skill is still worth it for methodology and workflow.

## Contributing

- ~100 tokens for a skill `description` (what/when to use).
- 1,000–2,500 tokens per `SKILL.md` — keep the main file focused on essentials.
- Use `references/` for depth; link from `SKILL.md` so it loads lazily.
- Design skills to coexist: 2–4 skills load per session, keep total loaded below ~10k tokens.

Full guidelines live in `CLAUDE.md`.

## Acknowledgements

- **Samuel Berthe** — author of the upstream [samber/cc-skills-golang](https://github.com/samber/cc-skills-golang) catalog this pack forks and extends (MIT).
- **Teiva Harsanyi** — author of [*100 Go Mistakes and How to Avoid Them*](https://100go.co/), the source of the Pitfalls category.

## License

MIT — see [LICENSE](./LICENSE). Copyright © 2026 Samuel Berthe (upstream catalog) and Fabiano Santos Florentino (fork, curation and the `golang-pitfalls-*` skills).
