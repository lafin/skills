# Output Templates

Three artifacts, every run: the compressed document, the removal log, the scorecard.
Per-run outputs are saved to the working directory and are never committed to a repo.
Name the saved paths at the end of the run.

## Artifact 1: Compressed Document

The full tightened document with all structure intact. FLAG items stay in place, each
marked with a lightweight inline marker that renders invisibly but greps easily:

```markdown
<!-- FLAG: §4.2 metric list appears to duplicate §2.1 — confirm they are the same, then merge. -->
```

Save to `<slug>-compressed.md`, where `<slug>` is a short kebab-case name derived from the
document title.

## Artifact 2: Removal Log

The account of what was cut. Group by the five categories from `removal-taxonomy.md`, give
a span count, the words removed, and one representative before → after per category, then
list every flag. The words-removed counts must sum to approximately `before − after`.

```markdown
# Removal Log: <document title>

**Words:** <before> → <after> (−<percent>%)

## Removed

- **filler** (<n> spans, −<w> words): "It is important to note that the API is rate-limited." → "The API is rate-limited."
- **hedging** (<n> spans, −<w> words): "This is basically a ranking problem." → "This is a ranking problem."
- **slop** (<n> spans, −<w> words): removed ceremonial intro "In today's fast-paced world…"
- **restatement** (<n> spans, −<w> words): removed second definition of <metric>, identical to the first.
- **verbose-phrasing** (<n> spans, −<w> words): "at this point in time" → "now"

**Words removed, total:** <sum of w> (compare with <before> − <after>)

## Flags (author decides — left in the document)

- **<location>** — <what> — recommend: <merge | cut | keep>. <one-line reason>.
```

Save to `<slug>-removal-log.md`.

## Artifact 3: Scorecard

A screenshot-friendly, shareable markdown block. Keep the attribution line at the top
intact and unmodified — small text, never a header.

```markdown
*Compressed with [lossless-doc-compress](https://github.com/ML-SystemDesign/MLSystemDesign/tree/main/skills) · [ML System Design](https://arseny.info/ml_design_book) by Kravchenko and Babushkin*

## Compression Scorecard: <document title>

**Result:** Tightened −<percent>% · <lossless ✓ | see flags> · <n> flags
**Words:** <before> → <after>
**Fidelity:** lossless — no facts, numbers, decisions, or caveats removed; numbers, identifiers, code blocks, and table cells byte-exact
**Flags:** <n> judgment calls left for the author (see removal log)

**Top flag:** <the single highest-value structural suggestion, or "none">
**Takeaway:** <one reusable, non-marketing lesson from this compression>
```

Save to `<slug>-compression-scorecard.md`.

Use `lossless ✓` only after the self-check in `compression-workflow.md` passes, including the
byte-exact check. Otherwise write `see flags` and name the failed check.

## Save Rule

Default to the three filenames above in the working directory. Do not commit them. Skip a
file only when no writable filesystem is available or the user asks not to. Name every
saved path at the end of the run.

## Note On The Verdict Line

The reduction percentage is whatever honest lossless compression produced — never inflate
it by demoting content to flags or by paraphrasing. If the document was already tight, a
small percentage with "lossless ✓" is the correct, honest result.
