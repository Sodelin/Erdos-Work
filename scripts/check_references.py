#!/usr/bin/env python3
# SPDX-License-Identifier: MIT; see scripts/LICENSE
"""Bounded public-DOI metadata checks; never an automated novelty verdict."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import http.client
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import unicodedata
import urllib.error
import urllib.parse
import urllib.request


API_URL = "https://api.crossref.org/works"
USER_AGENT = "Bibliographic-Metadata-Checker/1.0"
HTTP_TIMEOUT = 15
MAX_INPUT_BYTES = 128 * 1024
MAX_RESPONSE_BYTES = 1024 * 1024
MAX_DOIS = 3
NOTICE = (
    "Bibliographic verification only: DOI metadata does not establish semantic "
    "equivalence, correctness, novelty, priority, or prize eligibility. Missing "
    "records do not establish novelty."
)


class InputError(ValueError):
    pass


class ProviderError(ValueError):
    pass


class CrossrefRedirectGuard(urllib.request.HTTPRedirectHandler):
    """A provider redirect may not change the host or the exact DOI endpoint."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        target = urllib.parse.urlsplit(newurl)
        original = urllib.parse.urlsplit(req.full_url)
        if (target.scheme != "https" or target.netloc != "api.crossref.org"
                or target.path != original.path or target.query or target.fragment):
            raise ProviderError("Crossref attempted a redirect outside the fixed endpoint")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def unique_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise InputError("Input JSON contains duplicate object keys")
        result[key] = value
    return result


def validate_idea(idea):
    if not isinstance(idea, dict):
        raise InputError("Idea must be a JSON object")
    for field, maximum in (("id", 200), ("claim", 64000)):
        value = idea.get(field)
        if not isinstance(value, str) or not value.strip() or len(value) > maximum:
            raise InputError(f"{field} must be a nonempty string of at most {maximum} characters")
        try:
            value.encode("utf-8")
        except UnicodeError as exc:
            raise InputError(f"{field} must contain valid Unicode") from exc
    if type(idea.get("revision")) is not int:
        raise InputError("revision must be an integer, not a boolean")
    dois = idea.get("prior_work_dois")
    if not isinstance(dois, list) or not 1 <= len(dois) <= MAX_DOIS:
        raise InputError("prior_work_dois must contain between one and three public DOI strings")
    for doi in dois:
        if (not isinstance(doi, str) or len(doi) > 200
                or re.fullmatch(r"10\.\d{4,9}/\S+", doi) is None):
            raise InputError("Each public DOI must match 10.<4-9 digits>/<nonspace suffix> and be at most 200 characters")
        try:
            doi.encode("utf-8")
        except UnicodeError as exc:
            raise InputError("DOI strings must contain valid Unicode") from exc
    return idea


def read_idea(path):
    with Path(path).open("rb") as handle:
        raw = handle.read(MAX_INPUT_BYTES + 1)
    if len(raw) > MAX_INPUT_BYTES:
        raise InputError("Idea file exceeds the 128 KiB input limit")
    try:
        idea = json.loads(raw.decode("utf-8"), object_pairs_hook=unique_keys)
    except InputError:
        raise
    except (UnicodeError, ValueError, RecursionError) as exc:
        raise InputError("Idea file must be valid UTF-8 JSON") from exc
    return validate_idea(idea)


def fetch_work(doi):
    # Only a previously published DOI identifier leaves the process.
    url = API_URL + "/" + urllib.parse.quote(doi, safe="")
    request = urllib.request.Request(url, headers={
        "User-Agent": USER_AGENT, "Accept": "application/json"})
    opener = urllib.request.build_opener(CrossrefRedirectGuard())
    with opener.open(request, timeout=HTTP_TIMEOUT) as response:
        body = response.read(MAX_RESPONSE_BYTES + 1)
    if len(body) > MAX_RESPONSE_BYTES:
        raise ProviderError("Crossref response exceeds the 1 MiB limit")
    try:
        payload = json.loads(body.decode("utf-8"))
    except (UnicodeError, ValueError, RecursionError) as exc:
        raise ProviderError("Crossref returned invalid UTF-8 JSON") from exc
    if not isinstance(payload, dict) or payload.get("status") != "ok":
        raise ProviderError("Crossref response has no successful status")
    message = payload.get("message")
    if not isinstance(message, dict) or not isinstance(message.get("DOI"), str):
        raise ProviderError("Crossref response has no single DOI metadata object")
    return message


def publication_year(item):
    for field in ("published", "published-print", "published-online", "issued"):
        date = item.get(field)
        parts = date.get("date-parts") if isinstance(date, dict) else None
        if (isinstance(parts, list) and parts and isinstance(parts[0], list)
                and parts[0] and type(parts[0][0]) is int
                and 1 <= parts[0][0] <= 9999):
            return parts[0][0]
    return None


def normalize_item(item):
    if not isinstance(item, dict):
        raise ProviderError("Crossref returned a non-object result")
    titles = item.get("title", [])
    if isinstance(titles, str):
        titles = [titles]
    title = next((" ".join(t.split()) for t in titles
                  if isinstance(t, str) and t.strip()), "") if isinstance(titles, list) else ""
    doi = item.get("DOI")
    doi = doi.strip().lower() if isinstance(doi, str) and doi.strip() else None
    if not title and not doi:
        raise ProviderError("Crossref result has neither a title nor a DOI")
    authors = []
    author_records = item.get("author", [])
    for author in author_records if isinstance(author_records, list) else []:
        if isinstance(author, dict):
            name = " ".join(author[field].strip() for field in ("given", "family")
                            if isinstance(author.get(field), str) and author[field].strip())
            if not name and isinstance(author.get("name"), str):
                name = author["name"].strip()
            if name:
                authors.append(name)
    year = publication_year(item)
    url = item.get("URL")
    try:
        parsed = urllib.parse.urlsplit(url) if isinstance(url, str) else None
        if not parsed or parsed.scheme not in ("https", "http") or not parsed.netloc:
            url = None
    except ValueError:
        url = None
    if not url and doi:
        url = "https://doi.org/" + urllib.parse.quote(doi, safe="/")
    normalized_title = " ".join(re.sub(
        r"[^\w]+", " ", unicodedata.normalize("NFKC", title).casefold()).split())
    key = ("doi", doi) if doi else ("title-year", normalized_title, year)
    record = {"title": title, "authors": authors, "year": year,
              "DOI": doi, "URL": url, "requested_dois": []}
    try:
        json.dumps(record, ensure_ascii=False).encode("utf-8")
    except UnicodeError as exc:
        raise ProviderError("Crossref result contains invalid Unicode") from exc
    return key, record


def collect_evidence(idea):
    validate_idea(idea)
    evidence = {
        "id": idea["id"], "revision": idea["revision"],
        "claim_sha256": hashlib.sha256(idea["claim"].encode("utf-8")).hexdigest(),
        "queried_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "requested_dois": list(idea["prior_work_dois"]), "source": "Crossref",
        "status": "unavailable", "results": [], "errors": [], "notice": NOTICE,
        "novelty_established": False,
    }
    successful_lookups = 0
    by_key = {}
    for doi in idea["prior_work_dois"]:
        try:
            item = fetch_work(doi)
            key, record = normalize_item(item)
            if record["DOI"] != doi.lower():
                raise ProviderError("Crossref returned metadata for a different DOI")
        except (OSError, urllib.error.URLError, http.client.HTTPException, ProviderError) as exc:
            if isinstance(exc, urllib.error.HTTPError):
                message = f"Crossref HTTP error {exc.code}"
            elif isinstance(exc, ProviderError):
                message = str(exc)
            else:
                message = "Crossref request failed: " + type(exc).__name__
            evidence["errors"].append({"DOI": doi, "message": message})
            continue
        successful_lookups += 1
        if key not in by_key:
            by_key[key] = record
        if doi not in by_key[key]["requested_dois"]:
            by_key[key]["requested_dois"].append(doi)
    evidence["results"] = list(by_key.values())
    if successful_lookups:
        evidence["status"] = "partial" if evidence["errors"] else "complete"
    return evidence


def write_evidence(path, evidence):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                         prefix=".references-", suffix=".json", delete=False) as handle:
            temporary = Path(handle.name)
            json.dump(evidence, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        os.replace(temporary, path)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--idea", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        if args.idea.resolve() == args.output.resolve():
            raise InputError("Input and output paths must differ")
        idea = read_idea(args.idea)
        evidence = collect_evidence(idea)
        write_evidence(args.output, evidence)
    except (InputError, OSError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(f"Crossref references: {evidence['status']}; {len(evidence['results'])} unique records")
    return 0 if evidence["status"] == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
