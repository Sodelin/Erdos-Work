#!/usr/bin/env python3
# SPDX-License-Identifier: MIT; see scripts/LICENSE
"""Validate an idea record and optionally check permission to begin research.

This checks recorded evidence and budget declarations, not novelty or correctness.
"""
import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlsplit

NOTICE = "No match is not proof of novelty. This gate does not assess proof correctness."
STATUSES = {"proposed", "blocked", "attempting", "complete", "stopped"}
VERDICTS = {"known", "overlap", "unresolved", "no_match"}


def claim_hash(claim):
    return hashlib.sha256(claim.encode("utf-8")).hexdigest()


def load_record(path):
    def unique_pairs(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"Duplicate JSON key: {key}")
            result[key] = value
        return result

    def reject_constant(value):
        raise ValueError(f"Invalid JSON constant: {value}")

    return json.loads(Path(path).read_text(encoding="utf-8"),
                      object_pairs_hook=unique_pairs, parse_constant=reject_constant)


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def url(value):
    if not nonempty(value) or any(c.isspace() for c in value):
        return False
    try:
        parsed = urlsplit(value)
        return parsed.scheme in {"http", "https"} and bool(parsed.hostname)
    except ValueError:
        return False


def timestamp(value):
    if not isinstance(value, str) or not re.fullmatch(
            r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z", value):
        raise ValueError("Expected an ISO UTC timestamp ending in Z")
    return datetime.fromisoformat(value[:-1] + "+00:00")


def validate(record, *, can_start=False, now=None):
    errors = []
    if not isinstance(record, dict):
        return ["Record must be a JSON object"]
    now = now or datetime.now(timezone.utc)
    starting = can_start or record.get("status") == "attempting"

    def require(condition, message):
        if not condition:
            errors.append(message)

    require(isinstance(record.get("id"), str) and bool(re.fullmatch(
        r"[a-z0-9]+(?:-[a-z0-9]+)*", record["id"])), "id must be a lowercase slug")
    require(type(record.get("revision")) is int and record["revision"] > 0,
            "revision must be a positive integer")
    require(nonempty(record.get("claim")), "claim must be a nonempty string")
    require(record.get("status") in STATUSES if isinstance(record.get("status"), str) else False,
            "status is invalid")
    if starting:
        require(isinstance(record.get("status"), str) and record["status"] in {"proposed", "attempting"},
                "Starting requires status proposed or attempting")
    require(record.get("lane") in {"income", "research"} if isinstance(record.get("lane"), str) else False,
            "lane must be income or research")
    queries = record.get("search_queries")
    require(isinstance(queries, list) and 1 <= len(queries) <= 3 and all(map(nonempty, queries)),
            "search_queries must contain 1 to 3 nonempty strings")
    require(isinstance(record.get("correctness"), dict), "correctness must be an object")
    require(isinstance(record.get("history"), list), "history must be a list")

    budget = record.get("budget")
    if not isinstance(budget, dict):
        errors.append("budget must be an object")
    else:
        minutes, spend = budget.get("max_minutes"), budget.get("max_new_spend_usd")
        require(type(minutes) is int and 1 <= minutes <= 120,
                "budget.max_minutes must be an integer from 1 to 120")
        require(type(spend) in (int, float) and spend == 0,
                "budget.max_new_spend_usd must be numeric zero")

    reviews = record.get("reviews")
    if not isinstance(reviews, dict):
        errors.append("reviews must be an object")
        reviews = {}
    for name in ("alphaxiv", "primary"):
        review = reviews.get(name)
        prefix = f"reviews.{name}"
        if not isinstance(review, dict):
            errors.append(f"{prefix} must be an object")
            continue
        status = review.get("status")
        require(isinstance(status, str) and status in {"complete", "unavailable", "pending"},
                f"{prefix}.status is invalid")
        complete = status == "complete"
        checked = None
        revision = review.get("revision")
        if complete or "revision" in review:
            require(type(revision) is int and revision > 0,
                    f"{prefix}.revision must be a positive integer")
        for field in ("claim_sha256", "checked_at", "verdict", "gap"):
            if complete or field in review:
                require(isinstance(review.get(field), str), f"{prefix}.{field} must be a string")
        digest = review.get("claim_sha256")
        if complete or digest:
            require(isinstance(digest, str) and bool(re.fullmatch(r"[0-9a-f]{64}", digest)),
                    f"{prefix}.claim_sha256 must be a SHA256 hex digest")
        if complete or review.get("checked_at"):
            try:
                checked = timestamp(review.get("checked_at"))
            except ValueError:
                errors.append(f"{prefix}.checked_at must be a valid ISO UTC timestamp ending in Z")
        verdict = review.get("verdict")
        if complete or verdict:
            require(isinstance(verdict, str) and verdict in VERDICTS, f"{prefix}.verdict is invalid")
        sources = review.get("sources")
        if complete or "sources" in review:
            require(isinstance(sources, list) and all(map(url, sources)),
                    f"{prefix}.sources must be a list of HTTP(S) URLs")
        if starting:
            require(complete, f"{prefix} must be complete before starting")
            require(nonempty(record.get("claim")) and digest == claim_hash(record["claim"]),
                    f"{prefix} must be bound to the current claim")
            require(type(revision) is int and revision == record.get("revision"),
                    f"{prefix} must be bound to the current revision")
            require(checked is not None and timedelta(0) <= now - checked <= timedelta(days=7),
                    f"{prefix} must be checked within 7 days and not in the future")
            require(verdict == "no_match", f"{prefix} verdict must be no_match before starting")
            require(isinstance(sources, list) and bool(sources), f"{prefix} requires sources before starting")
            require(nonempty(review.get("gap")), f"{prefix} requires a gap before starting")

    reward = record.get("reward")
    if not isinstance(reward, dict):
        errors.append("reward must be an object")
    else:
        status = reward.get("status")
        require(isinstance(status, str) and status in {"verified", "unverified", "none"},
                "reward.status is invalid")
        if starting and record.get("lane") == "income":
            require(status == "verified", "income lane requires a verified reward before starting")
        for field in ("source_url", "acceptance_criteria", "payment_trigger"):
            if status == "verified":
                require(nonempty(reward.get(field)), f"verified reward requires {field}")
            elif field in reward:
                require(isinstance(reward[field], str), f"reward.{field} must be a string")
        if reward.get("source_url"):
            require(url(reward["source_url"]), "reward.source_url must be an HTTP(S) URL")
    return errors


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path, help="JSON idea record")
    parser.add_argument("--can-start", action="store_true", help="Check the research start requirements")
    args = parser.parse_args(argv)
    try:
        record = load_record(args.path)
        errors = validate(record, can_start=args.can_start)
    except (OSError, ValueError) as exc:
        record, errors = {}, [str(exc)]
    starting = args.can_start or (isinstance(record, dict) and record.get("status") == "attempting")
    print(json.dumps({"valid": not errors, "can_start": not errors if starting else None,
                      "income_gate_passed": not errors and starting and record.get("lane") == "income",
                      "errors": errors, "notice": NOTICE}, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
