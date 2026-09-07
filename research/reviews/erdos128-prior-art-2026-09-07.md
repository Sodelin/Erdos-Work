# Erdős #128: prior work, method barriers and the next research step

Checked 7 September 2026. Scope: the complete sparse-half conjecture, including the exact finite cardinality condition.

**The conjecture remains unproved in our work. The review located no full solution.** The latest relevant 2026 primary paper explicitly calls it open and identifies the best general bound as 27/1024, compared with the conjectured 1/50. This is a literature finding, not a guarantee that no unpublished or unindexed solution exists. [Balogh–Buczek–Grzesik–Kuc, introduction](https://arxiv.org/html/2605.05346v1)

## Exact target and provenance

Every finite triangle-free simple graph G on n vertices should contain a set S of floor(n/2) vertices such that 50 e(G[S]) ≤ n². Removing vertices from a larger selected set cannot increase its edge count.

Erdős's 1976 Problem 25 states the question, printed p.189. His 1984 first problem discusses balanced five-cycle and Petersen blowups as extremal examples; it does not prove those are the only extremals. [1976 original scan](https://www.renyi.hu/~p_erdos/1976-36.pdf), [1984 original scan](https://www.renyi.hu/~p_erdos/1984-11.pdf)

The existing Lean statement uses the guard 2|S|+1 ≥ n, which matches floor(n/2). It is marked research open and contains `sorry`; the existence of a formal statement is not a proof. Source blob inspected: `8fdaf7eaa6629dfd5aaad6521f7c84a6a9e96dca`. Never substitute ceil(n/2) for odd n without a separate argument. [Formal Conjectures source](https://github.com/google-deepmind/formal-conjectures/blob/main/FormalConjectures/ErdosProblems/128.lean)

## What the classical attacks establish

Use θ=e(G)/n², β=min e(G[S])/n², and α=α(G)/n. Some papers instead use ρ=2θ. Confusing these density conventions doubles a threshold.

| Source | Verified result and mechanism | Boundary of its use |
|---|---|---|
| Uniform random half | β≤θ/4, so θ≤2/25 suffices. | The estimate exceeds 1/50 at larger density. |
| Krivelevich 1995 | Universal β≤1/36; an asymptotic positive improvement; dense regular case D≥2n/5. Finds an edge with d(u)+d(v)≥4e/n, then exploits its disjoint independent neighborhoods. | Regularity cannot be dropped from that theorem. Theorem 6 prevents a density-independent multiplicative improvement below e/4 for every triangle-free graph. |
| Keevash–Sudakov 2006 | Proposition 1.2 handles θ≤1/12. Theorem 1.1 handles θ≥1/5 without regularity and characterizes its equality case as the balanced C5 blowup. | The proof uses these density assumptions; it supplies no universal middle-density reduction. |
| Norin–Yepremyan 2015 | Minimum degree ≥5n/14; edge density ≥1/5−γ for some fixed γ>0; stability near balanced C5/Petersen models. | Proximity to those models must be established. Local stability does not classify all difficult graphs. |

Sources: [Krivelevich author manuscript, Theorems 1–3,5–6](https://www.math.tau.ac.il/~krivelev/3.pdf); [Keevash–Sudakov, pp.614–620](https://people.math.ethz.ch/~sudakovb/sparse-halves.pdf); [Norin–Yepremyan, Theorems 1.1–1.2,4.8,6.3](https://arxiv.org/abs/1311.5818).

The weighted formulation, endpoint rounding and homomorphism lifting already appear in Norin–Yepremyan, Lemmas 2.1–2.2. Their distributions of sparse halves permit controlled perturbations of a solved template. Optimizing the half selected from fixed weights does not justify averaging the graph weights themselves.

## Modern coverage and related results

| Source | Exact coverage relevant to #128 | What it does not prove |
|---|---|---|
| Bedenknecht–Mota–Reiher–Schacht | Every graph homomorphic to any Andrásfai graph. Consequences: triangle-free minimum degree >10n/29; or >n/3 with chromatic number ≤3. | Does not encompass every four-chromatic Vega graph or the Grötzsch graph. |
| Razborov 2021/2022 | Universal β≤27/1024. The conjecture holds if ρ≤(33−√161)/116, or α≥2/5, or the graph has no induced 2K2, is strongly regular, or has girth ≥5. For 3/8≤α≤1/2, β≤α(1/2−α)/2. | Strong regularity and girth do not survive arbitrary blowups. The three-part edge-neighborhood construction has a sharp 27/1024 barrier. |
| Balogh–Clemen–Lidický–Norin–Volec, latest v3 | Smallest signless-Laplacian eigenvalue ≤15n/94. Neighborhood Rayleigh vectors and exact flag certificates prove a spectral inequality. | This is not a rounding theorem producing the required half. Reversing a necessary spectral implication is invalid. |
| Balogh–Clemen–Lidický | Related balanced bipartite deletion and local-density results. | Their Grötzsch example concerns deletion to three-partiteness, a different objective. |
| Balogh–Buczek–Grzesik–Kuc 2026 | K4-free balanced bipartite deletion ≤n²/9, using local stability plus colored graphon/flag constraints. | Different forbidden graph and objective. Its transferable method has not solved #128. |

Sources: [Andrásfai theorem and strict-degree corollaries](https://arxiv.org/html/1609.05712v2); [Razborov, Theorems 3.1–3.8](https://arxiv.org/html/2104.09406v2); [Spectrum paper v3, Theorem 1.6](https://arxiv.org/html/2204.00093v3); [Related partition paper](https://lidicky.name/pub/10problems.pdf); [2026 K4-free theorem](https://arxiv.org/html/2605.05346v1).

Further current checks did not produce a full solution: the 2026 Ramsey–Turán bipartite-cut paper uses different clique assumptions and edge weights; Local flag algebras supplies methodology rather than a sparse-half improvement; the local clique-density theorem solves an inverse problem whose direct triangle-free half specialization is trivial. [Ramsey–Turán paper](https://arxiv.org/html/2606.20397v1), [Local flag algebras](https://arxiv.org/html/2607.12461v1), [Local clique-density theorem](https://arxiv.org/html/2608.18663)

## What happened to the Grötzsch direction

Our exact symmetric certificate establishes a restricted family of weights. Two independent rational checkers passed. This is not a full #128 solution, and its novelty is still unresolved.

Bispo's thesis identifies Grötzsch as Upsilon_2^11. Its specified apex-deleted theorem is not a theorem for every Vega blowup. Its d≥29 theorem has statement/proof parameter issues requiring clarification; the conclusion leaves small d and other regimes for future work. The 2025 talk announces a small-independence result without a numeric threshold, so exact overlap remains unresolved. The thesis's historical “best bound” prose is stale; use individual checked results instead. [Thesis, pp.27–28,35–37](https://www.teses.usp.br/teses/disponiveis/45/45134/tde-21082025-115625/publico/Dissertacao_CesarAugustoDosSantosBispo_.pdf), [2025 official abstract-book page](https://sbm.org.br/jointmeeting-mexico/book-of-abstracts/)

Even a proof for all Grötzsch weights would still need a reduction covering arbitrary triangle-free graphs. Brandt–Thomassé's Andrásfai/Vega classification assumes minimum degree strictly greater than n/3; it does not supply that global reduction. [Classification, Corollary 4.1](https://perso.ens-lyon.fr/stephan.thomasse/liste/vega11.pdf)

## First mathematical check: reproduce a real barrier

The registered review replay used the 16-vertex Clebsch graph. For every one of its 40 edges, the two endpoint neighborhoods and the remaining vertices have sizes 5,5,6, with inter-part edge counts 13,12,12 and three edges inside the remainder.

A half constant on these three parts uses inclusion weights p,q,r satisfying 5p+5q+6r=8. Its cost is 13pq+12(p+q)r+3r². Exact one-variable minimization gives 27/4, hence normalized cost 27/1024. An actual eight-vertex half has only four edges, giving 1/64; enumeration of all 12,870 halves confirms that minimum.

This reproduces a published method limitation. It is neither a new theorem nor a counterexample. The practical stop rule is concrete: optimizing only that three-part family cannot settle #128. The computation checks the obstruction, not the universal conjecture.

## Research decision

**The next full-problem direction is a structural reduction paired with a richer half-selection certificate.** This is a proposed direction derived from existing methods, not an established novel strategy.

1. Express the exact half-size constraint explicitly in any local or colored certificate. A bound on total partition edges or an asymptotic o(n²) statement is insufficient by itself.
2. Audit whether failures of richer local half selections force proximity to a solved model. Do not assume the two classical extremal examples exhaust all possibilities.
3. Require the selection family to get past the Clebsch obstruction before allocating a larger search. Keep C5 and Petersen equality examples as controls.
4. State the missing lemma with all quantifiers before a new attempt. Compare it with existing stability, flag and spectral theorems; invalidate the review if the proposed method changes.
5. Use rationally checked certificates or a genuine Lean proof for successful steps, and record the exact connection to arbitrary finite graphs. A finite computation or a solved family is not the missing reduction.

A shorter intermediate question explicitly posed by Razborov is whether α≥2/5−ε suffices for some fixed ε>0. It is known as an open direction, so merely proposing it is not novel. Any proof would need a further argument to settle the entire conjecture.

## Reward and AI eligibility

The historical $250 source is cited as Erdős (1997), “Some old and new problems in various branches of combinatorics,” Discrete Mathematics 165/166:227–231, DOI 10.1016/S0012-365X(96)00173-2. The original reward passage was not obtained in this review; the current evidence is the explicit citation in Norin–Yepremyan.

The Combinatorics Foundation requires the reward to be documented in Erdős's own publication and the first accepted solution to appear in a reputable peer-reviewed mathematics journal. Awards remain discretionary. Its published rules do not explicitly confirm AI-assisted eligibility or promise payment upon a Lean check. **Reward eligibility remains unverified.** [Official award rules](https://www.combinatoricsfoundation.org/erd%C5%91s-problems)

Elsevier's June 2026 policy allows disclosed AI support with human oversight, verification and responsibility, and requires research uses to be described. AI tools cannot be listed as authors. This demonstrates a conditional publication route; it does not establish this sponsor's award decision. [Official publisher policy](https://www.elsevier.com/about/policies-and-standards/generative-ai-policies-for-journals)

No prize claim, submission, acceptance or payment is recorded.

## Review coverage and limits

The review combined alphaXiv discovery, original papers and author manuscripts, recent full texts, the formal statement, and separate classical/modern scope audits. Previously retrieved sources were reused. An alphaXiv author lookup that confused César Bispo with an unrelated researcher was rejected.

The PR's reference-check CI passed for head fb096e212203365accba56cf1ee5abe1160c3aa9. The artifact was listed and a download reference obtained, but reading its ZIP returned HTTP 403; its contents were not inspected. A separate live lookup of the public Norin–Yepremyan DOI succeeded. Neither metadata lookup nor CI certifies novelty. [CI run](https://github.com/Sodelin/Erdos-Work/actions/runs/34142143106)

The missing original reward passage, unspecified Bispo follow-up scope, possible unpublished work and unproved global reduction remain explicit gaps. This review supports a bounded next research decision; it establishes neither a percentage toward a solution nor an expected payout.
