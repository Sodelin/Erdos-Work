# Start with the gap and the payer

Each mathematical idea has one versioned record in `research/ideas/`. Open a branch and a PR titled `[idea] <id>: <description>` before spending the attempt budget. The initial status is `proposed`; known overlap, missing access or an inapplicable reward makes it `blocked`. Proposing an idea is allowed while blocked. Starting the proof attempt is not.

Two reviews precede an attempt:

- **alphaXiv discovery:** search the claim and equivalent formulations, then inspect relevant full papers. Verify author identity; similar names and generated summaries are insufficient evidence.
- **Independent primary review:** inspect original papers, theses, problem discussions and existing code/formalizations using a separate search. The repository's standard-library reference checker verifies metadata for cited, already-published DOI identifiers. Read the underlying sources to decide scope; metadata cannot establish novelty. The checker sends only public DOI identifiers, never the idea text or research-derived topic queries.

Each review records the exact claim's SHA-256, UTC date, queries, sources, verdict and the precise remaining gap. Verdicts are `known`, `overlap`, `unresolved` or `no_match`. Only a current, completed `no_match` assessment with an explained gap allows a bounded attempt; it still does not certify first discovery. Change the revision and invalidate reviews when the claim or approach changes. Recheck during work when new information appears, and before any public novelty or reward claim.

Run:

```sh
python3 scripts/check_idea.py research/ideas/IDEA.json
python3 scripts/check_references.py --idea research/ideas/IDEA.json --output /tmp/prior-art.json
python3 scripts/check_idea.py research/ideas/IDEA.json --can-start
```

The income lane requires reward evidence that applies to this exact deliverable, including acceptance and payment conditions. Unknown eligibility is a blocker, not projected income. Stop an attempt at its budget. Completed formalizations of known mathematics belong in the reproduction record unless a sponsor explicitly pays for that formalization.

## Automatic checks

GitHub Actions validates records and runs the open-source DOI reference checker on proposed or changed records. Reference-check output is retained as an artifact. Dependency failures are visible failures, never a clean novelty result. The separate ChatGPT automation watches `[idea]` PRs and their commits, uses alphaXiv and primary sources, and writes its review into the existing record. It must skip already-reviewed unchanged claim/revision pairs to avoid responding indefinitely to its own updates.

This is an event-driven review workflow, not a continuously running solver. Direct commits without an idea PR do not trigger the alphaXiv reviewer. If automation access fails, the idea remains blocked and an active agent must finish the missing review. No new paid API or compute budget is authorized by this workflow.

Automatic reviews may update only idea/review records in this repository. Do not merge PRs, submit to a prize body, contact researchers, accept contracts or configure payment through the reviewer. Current owner instructions take precedence over the older submission workflow.

## Current assessment

The symmetric Grötzsch sparse-half certificate passed two independent exact rational checkers. Its novelty is unresolved, and no reward for that restricted result is verified. The arbitrary-weight extension is also blocked pending overlap resolution. Neither solves Erdős #128. The historical reward concerns the full conjecture.
