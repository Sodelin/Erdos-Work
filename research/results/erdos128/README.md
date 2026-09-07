# Restricted sparse-half certificate

For the Grötzsch graph, the certificate establishes the sparse-half bound for weights constant on the five original cycle vertices and on the five shadows, with a separate apex weight: `(a,a,a,a,a,b,b,b,b,b,c)`, where `a,b,c >= 0` and `5a+5b+c=1`.

It combines the known large-independent-set case from [Razborov, Theorem 3.6](https://arxiv.org/html/2104.09406v2) with 32 rational triangles and nine endpoint witnesses for the remaining parameter region. The supremum is `1/50`, achieved by the balanced five-cycle on the boundary. Both included Python checkers use exact rational arithmetic, with different coverage checks.

```sh
python3 research/results/erdos128/verify_grotzsch_symmetric.py
python3 research/results/erdos128/verify_grotzsch_symmetric_independent.py
```

These are executable mathematical certificates, not a Lean formalization. The imported large-independent-set theorem is an external mathematical dependency. Novelty remains unresolved after alphaXiv and primary-source review on 7 September 2026. No independently applicable reward was verified for this special case. This does not prove the arbitrary-weight Grötzsch statement or the full Erdős #128 conjecture. No solution submission or payment is claimed.
