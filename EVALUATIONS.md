# Skill evaluations

This repository merges two skill sets:

- The full `samber/cc-skills-golang` catalog (skills `golang-*`), authored by
  [Samuel Berthe](https://github.com/samber) and released under the MIT license.
- A new **Pitfalls** category (`golang-pitfalls-*`), distilled from
  *100 Go Mistakes and How to Avoid Them* by Teiva Harsanyi.

## Upstream evaluations

The upstream `golang-*` skills ship with adversarial, model-specific evaluation
reports (see the original
[samber/cc-skills-golang EVALUATIONS.md](https://github.com/samber/cc-skills-golang/blob/main/EVALUATIONS.md)).
Those numbers describe upstream's measurement runs and were not reproduced here;
treat them as upstream data. The per-skill `evals/` directories were omitted
from this fork to keep the repository lean — re-run the upstream evaluation
harness if you need to reproduce them.

## Pitfall skills

The `golang-pitfalls-*` skills have not been adversarially evaluated yet. To add
an evaluation for a skill:

1. Create `skills/<name>/evals/evals.json` following the adversarial design
   rules in `CLAUDE.md` (one trap per rule, ~10 assertions per 1,000 tokens,
   50+ assertions per skill).
2. Run the eval with and without the skill on the same model, grade with an
   LLM-as-judge, and append the report here.

## Format

Each report section must contain a summary table (Overall with/without/delta)
and a `<details>` block with the full per-assertion breakdown, following the
format documented in `CLAUDE.md` → Evaluation Reporting.

## CI validation

Automated skill validation with `skills-ref` is suspended: the tool does not yet
support the `user-invocable` frontmatter field used by this catalog (all
validations fail). See
[agentskills/agentskills#105](https://github.com/agentskills/agentskills/issues/105).
Re-enable a `validate` workflow once resolved.
