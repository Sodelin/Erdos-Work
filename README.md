# Erdős Work

Research index for the Sodelin project's mathematical probes. Updated 7 September 2026.

**Before a new attempt:** register an `[idea]` PR and follow the [novelty and reward gate](docs/novelty-workflow.md). [Current idea records](research/ideas) distinguish known overlap, unresolved novelty, correctness and applicable rewards. The [restricted Grötzsch certificate](research/results/erdos128) is checked but remains blocked for income work; it does not solve Erdős #128.

| Project | Result | Verification and publication |
|---|---|---|
| [Erdős #302 finite plateau](https://github.com/Sodelin/oldest-conjecture-) | Proved f(732)=f(731), f(733)=f(732)+1, and f(734)=f(732)+2. With the external published731=606 baseline, the candidate new terms are 732606, 733607, 734608. Novelty is provisional; the historical asymptotic problem is not solved. | The current Lean 4.33.1 proofs pass build, leanchecker, and a strict audit allowing only the three ordinary logical axioms; the earlier native-checker dependence was removed. [Passing CI](https://github.com/Sodelin/oldest-conjecture-/actions/runs/34129895492). [VibeMathed review queue](https://vibemathed.com/queue); [Frontier Atlas review request #138](https://github.com/techno-optimist/erdos-frontier-atlas/issues/138). Both venues received the expanded-result addendum; neither review is claimed as acceptance. |
| [Egyptian fractions / Erdős #295](https://github.com/Sodelin/Egyptian-Fractions-Erdos-295) | Reproduced the known 35-term construction at cutoff 18; bounded searches found no improvement. No new result claimed. | Lean proof and strict axiom audit passed in [public CI](https://github.com/Sodelin/Egyptian-Fractions-Erdos-295/actions/runs/34126995036). Not submitted as a new discovery. |

The [OEIS proposal](https://github.com/Sodelin/oldest-conjecture-/blob/main/docs/oeis-proposal.md) is ready; sign-in succeeded and the contributor-account request was submitted. OEIS editor approval is pending; the sequence update itself has not yet been submitted. See the [publication record](https://github.com/Sodelin/oldest-conjecture-/blob/main/docs/submission-status.md) for exact receipts and limitations.

[Potential follow-on targets](https://github.com/Sodelin/oldest-conjecture-/blob/main/docs/target-shortlist.md): Erdős #686 consecutive-product ratios and Erdős–Graham #287 Egyptian-fraction gaps. These are checked research candidates, not predictions of an easy solution. Refresh prior work before a new claim.

Research initiated by the Sodelin project owner; arguments and artifacts developed with an OpenAI ChatGPT/Codex assistant. AI reviews are not human expert endorsements. Formal checking establishes the stated theorem under its disclosed trust assumptions; it does not establish first discovery. No prize eligibility has been established.

[Submission workflow and report format](docs/submission-workflow.md): each completed item records what was proved, where and when it was submitted, why it qualifies, how it was checked, and what remains unresolved. Status checks are scheduled through this evening; they report recorded progress rather than continuously search for proofs.

[Screened public task leads](research/intake/2026-09-07.json) record duplicate-work and funding blockers so future runs can avoid repeating the same investigations.
