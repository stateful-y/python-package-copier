---
name: fan-out-to-packages
description: Roll a template change out to every stateful-y package generated from python-package-copier, one agent per repo in parallel. Use when a template release must reach the fleet, when auditing all generated projects for a shared defect, or when applying a docs/config convention everywhere. Covers the seven repos and what differs between them, the copier update hazards that destroy local content silently, the per-repo invariants, and the verification discipline that stops a green result from being meaningless.
---

# Fan Out To Packages

Roll a change out to every package generated from this template. One agent per repo,
in parallel, each owning exactly one clone.

**The governing fact: this fleet fails silently.** Copier overwrites local files with
no conflict and no `.rej`. Docs markers that resolve to nothing render nothing.
Hook-emitted links are invisible to `--strict`. Almost every real defect found in this
fleet was invisible in a green build, and almost every *first* measurement of it was
wrong. Plan for that or the fan-out reports success and ships damage.

## 1. The fleet

Seven repos in `stateful-y`, all generated from this template (verify with
`.copier-answers.yml` `_src_path`). `internal`, `kedro-dagster-example`,
`staged-recipes` and `website` are **not** generated and must never be included.

| repo | `include_examples` | what makes it different |
|---|---|---|
| **yohou** | True | The reference implementation and the biggest: ~79 notebooks in 6 `examples/` subdirs, 46 companion pages, 6 curated section pages, hand-written See Also bullets, a 35-link how-to index grouped under 8 headings. Its docs are the quality bar — do not "normalise" them without a reason. |
| yohou-nixtla | True | 2 notebooks. Its logos were destroyed by a past update and restored from `f166f46`; **never touch `docs/assets/`**. `_base.py` is `_`-prefixed so `BaseNixtlaForecaster` gets no API page. Known-flagged: inert `environments` key under `[tool.coverage.report]`, `lightning_logs` xdist race. |
| yohou-optuna | True | 5 notebooks. Carries **8 custom skills / 24 files** under `.claude/skills/` that must stay tracked. `plot_model_comparison_bar` was hand-rewritten as a plotly grouped bar — flagged for human review, do not revert. |
| sklearn-wrap | True | 9 notebooks. Flat `src/` layout. Docs build needs `--extra config` (pydantic is an optional extra; `uv sync --all-groups` alone leaves `ty` failing). |
| sklearn-optuna | True | 9 notebooks. Flat layout. Some See Also entries resolve into the `sklearn_optuna` dependency's own inventory — that is correct, not a defect. |
| **kedro-dagster** | **False** | No notebooks. Largest docstring surface (~126 See Also links). `docstring_options: {warn_unknown_params: false}` is **CI-critical** — flipping it emits 77 griffe warnings and now *fails* the build. Snippets `base_path` must stay `[docs, .]`: it includes repo-root-relative `src/kedro_dagster/templates/*`. `datasets/` re-export layout. |
| **kedro-azureml-pipeline** | **False** | No notebooks. `warn_unknown_params: false` is CI-critical (46 warnings). Keeps a local `inventories` list. `distributed/` re-export layout. Best index coverage in the fleet. |

**`include_examples: False` is real and load-bearing.** For those two repos the gallery,
companion-notebook and `GALLERY:section` machinery is Jinja-gated *out of their
`hooks.py` entirely*. Any release that only touches example machinery is genuinely inert
for them — verify by diffing the two pristine renders rather than assuming either way.
If an update tries to introduce example content or an `Examples` nav entry there, that is
a template bug: report it, do not accommodate it.

## 2. Before dispatching

1. **The release must be TAGGED, not merged.** "Latest" means the newest *tag*. A repo
   whose `_commit` is ahead of the newest tag cannot update at all — it fails as
   `Downgrades are not supported`, not as a no-op. Verify the tag resolves and actually
   contains the change:
   `git rev-list -n1 vX.Y.Z` and grep the changed file out of `git show vX.Y.Z:<path>`.
2. **Diff the two pristine renders across the version pair, per `include_examples` value.**
   This tells you what each repo will actually receive, and it is the only thing that makes
   a later "untouched!" result meaningful. Do it before writing the briefs.
3. **Give each agent a scratch directory unique to its repo.** Agents have collided at the
   shared scratchpad root and overwritten each other's scripts. One even found a foreign
   script pointed at another repo's clone and correctly refused to run it.
4. **Assume the clones are gone.** The scratchpad is wiped between sessions. Have each
   agent clone fresh from its PR branch; the work lives on GitHub, not on disk.

## 3. What every repo must satisfy (the invariants)

- `docs/hooks.py` is **Tier 1** — take the clean render, never a merge. Verify it is
  byte-identical to a fresh `copier copy` at the same ref. All six historical forks were
  eliminated by v0.20.0 and must not come back.
- **`git diff --stat -- docs/assets` is empty.** The only sanctioned exception in this
  fleet's history is yohou-nixtla's 2-file logo restore.
- `nox -s check_docs` passes with **0 warnings** (it builds `--strict`, notebooks skipped).
- See Also: **0 unlinked**. The absolute count is a measurement artifact — see §5.
- Every index links every one of its sibling pages.
- CI: report **how many checks RAN**, not just how many failed.

### Docs conventions (as of v0.23.0)

| page | convention |
|---|---|
| `docs/index.md` (home) | grid cards, **tailored per package** — leave alone |
| `pages/examples/index.md` | sectioned cards (`<!-- GALLERY -->`, or inline `<!-- GALLERY:section:… -->` per section) |
| `pages/{tutorials,how-to,reference,explanation}/index.md` | a **text list** of subpages, each with a one-line description — *not* cards, *not* tables |
| `pages/reference/api.md` (or `pages/api/index.md`) | frontmatter + H1 + one intro paragraph + `<!-- API_TABLE -->`, nothing else |
| nav order | `Home > Tutorials > How-to Guides > Examples > Explanation > Reference` — **Reference last**; `Examples` present iff the package has notebooks |
| companion card | after the prerequisites (and after any install section), before the first body section |

Group a section index under `##` headings only when it is big enough to need it — yohou's
35 how-tos earn it; 8 do not.

## 4. The hazards, all of which have fired

**Copier destroys local content silently.**
- It **overwrites binaries every run**, regardless of diff — no conflict, no `.rej`, only a
  `Bin NNNN -> NNNN` line. This ate project logos for months. Only `_skip_if_exists`
  stops it; "Tier 3" is a convention for whoever *resolves* an update and is never reached.
- It applies an update as **a diff against the template's version**. Once a local file no
  longer resembles it, one shifted line rejects the whole hunk and the page reverts to the
  stub, content surviving only in a `.rej` nobody reads. A **whitespace-only** template
  change replaced a 244-line curated tutorial with a 74-line placeholder in one release.
- `_skip_if_exists` now covers the 4 logos, `docs/index.md`,
  `docs/pages/tutorials/getting-started.md` and `docs/pages/examples/index.md`.
- **`mkdocs.yml` is NOT protected** and cannot be — it genuinely needs template updates.
  Any release touching the template nav re-imposes the generic one: in a real probe it cut
  tutorials 14→2, how-tos 36→4, api 18→2, with the real nav left in a single `.rej`.
  **Warn every agent whenever the release touches `mkdocs.yml.jinja`.**
- A **`.rej` holds the PROJECT's own changes** that could not be re-applied — not the
  template's. That is why local content goes missing and every conflicted file is
  partially applied.
- The template pins `actions/checkout@v6` while repos run dependabot-bumped `@v7`. A
  release that inserts a job whose checkout step is textually identical to an existing one
  makes the patch **strand v6 on the wrong job**. CI cannot catch it — v6 works. Diff the
  whole workflow against baseline, not the update's own hunks.

**Docs fail by rendering nothing.**
- An unresolved marker renders as blank space; `--strict` never validated it. `check_docs`
  (v0.21.2) makes marker warnings fatal — that job is the only reason any of this is caught.
- **Hook-emitted raw HTML is invisible to `--strict`** — mkdocs never validates links inside
  it. The gallery overflow link 404'd into RTD-red this way; API-table `Name`/`Module` links
  have the same exposure. Only RTD's `post_build` linkchecker sees them, and CI does not run it.
  **`check_docs` can pass while RTD goes red.**
- `_get_submodules` skips `_`-prefixed modules **and** never scans the top-level
  `__init__.py`, so a public symbol exported only from there **never reaches the API table**
  (yohou-nixtla: 17 rows vs 18 symbols). Unfixed template bug.
- `__gallery__` assigned inside an `@app.cell` is invisible — `ast.iter_child_nodes` only
  sees module level. Both of yohou-nixtla's notebooks were in no gallery at all, silently.

**Tooling lies.**
- **`gh pr edit` silently fails here** (GraphQL Projects-classic deprecation). Use
  `gh api -X PATCH repos/OWNER/REPO/pulls/N -f title=... -F body=@file` and **read it back**.
- **A CONFLICTING PR runs no Actions.** "0 failures" out of ~1 check is meaningless.
- **RTD 403s urllib's user-agent** — use `curl`.
- A stale `.rumdl_cache` gives a **false clean**. Delete it and re-run.
- Cached notebook exports (`.source_hash`) make a docs build **vacuous**. Clear
  `docs/examples/<stem>/` first — but never `rm -rf docs/examples`, which deletes a tracked
  `.gitkeep`.
- `git check-ignore` is silent for **tracked** files; use `--no-index` to test a rule.
- zsh does not word-split unquoted expansions — several "all clean" sweeps were empty-set
  bugs. Prefer Python over shell for any sweep whose result you intend to trust.

## 5. Verification discipline

**Falsify every check before trusting it.** In this fleet the checker is likelier to be
wrong than the code. Real examples, all of them a confident number over an empty set:
a See Also audit grepping `<h2>` when the markup is `<h3 id="see-also">`; a card counter
matching `gallery-card` when Material emits `grid cards`; a `tee | head` that SIGPIPE'd and
truncated the log *before the build ran*; a `pgrep` matching its own command line; a
readback that diffed an empty file because `gh` errored outside the repo.

**"Untouched" is not evidence.** If the template's render of a file is unchanged across the
version pair, it would have been untouched either way. Diff the pristine renders first
(§2.2); if identical, you have tested nothing.

**`copier update` NEVER recreates a locally-deleted file** — delta or not, skip-listed or
not. Delete→recreate is `copy`/`recopy` semantics. So the delete-half of a two-way control
**cannot** discriminate a firing skip from a blind check. What does:
1. diff the pristine renders across the pair; identical ⇒ vacuous, and
2. **fork the template**, make a deliberate change to the file, update onto the fork, and
   confirm the customised file survives.
Binaries are the exception: copier rewrites them regardless of delta, so "the old version
overwrote it, the new one didn't" *is* a valid A/B on identical inputs.

**Verify by rendering, not by reading.** Count in the built HTML, scoped to `<article>` —
the ToC sidebar inflates counts ~3×. For JS behaviour (the DataTables API filter) drive a
real headless browser; note DataTables **2.x** uses `.dt-search`, not 1.x's
`#api-table_filter`, and two agents nearly reported a missing filter box over that alone.
Do not derive See Also counts by splitting final HTML on newlines: mkdocstrings emits
multi-line `title=` attributes and the split cuts inside the tag, silently dropping entries.

**Prefer a no-op to churn.** If a repo already satisfies the change, say so plainly and
push nothing.

## 6. Reporting

Require from each agent: the `docs/assets` diff **verbatim**; what each `.rej` held and how
it was resolved; per-page before→after with counts measured from rendered output; every
`check_docs` warning and its disposition; **how many CI checks RAN** and whether
"Docs build (strict)" passed; RTD state fetched with curl; and anything they could not
verify, flagged rather than asserted.

Tell them explicitly: **if a warning reveals a template bug rather than a repo bug, report
it and do not work around it locally** — a local patch to a Tier 1 file drifts forever and
undoes the fork elimination. Collect those, and cut a template release instead.
