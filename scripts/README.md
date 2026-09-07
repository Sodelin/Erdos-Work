# Public-reference metadata checks

This standard-library tool checks bibliographic metadata for one to three
already-published DOI identifiers. It only requests exact DOI records from
Crossref. It does not discover prior art, compare mathematical claims, or verify
correctness, novelty, priority, or prize eligibility.

Input JSON contains `id`, `claim`, integer `revision`, and `prior_work_dois` (one
to three public DOI strings, each at most 200 characters). Identifiers must match
`^10\.\d{4,9}/\S+$`; supply DOI identifiers, not URLs.

```json
{"id":"local-idea","claim":"Local claim text stays local.","revision":1,"prior_work_dois":["10.1070/SM9615"]}
```

```bash
python scripts/check_references.py --idea idea.json --output evidence.json
python -m unittest discover -s tests -p test_check_references.py -v
```

Only each public DOI leaves the process. The exact UTF-8 claim string is hashed
locally, preserving whitespace. Claim text, topic text, search queries, and other
local research fields never appear in outbound requests or headers. The tool
does not open paper URLs, execute metadata, or write to GitHub.

Each lookup uses the fixed Crossref DOI endpoint, a 15-second network timeout,
no retries, and a 1 MiB response limit. At most three lookups run. No credentials,
cloud dependencies, or paid services are needed. Returned DOI identities must
match requests; metadata is deduplicated by lowercase DOI.

Evidence contains the local claim hash, revision, UTC time, requested DOIs,
metadata, and errors. `complete`, `partial`, and `unavailable` describe retrieval
success only. Missing records do not establish novelty. Exit codes: `0` complete,
`1` partial/unavailable (evidence retained), `2` invalid input or local file error.
Input is capped at 128 KiB. Tests mock HTTP and run entirely offline.

Source discovery and semantic novelty assessment belong in a separate alphaXiv
and primary-source web research workflow. This checker does neither.

Crossref API reference: https://github.com/CrossRef/rest-api-doc

The new checker code and its tests are MIT licensed; see `scripts/LICENSE`. This does not change the license of existing repository content.
