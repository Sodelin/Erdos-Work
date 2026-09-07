# SPDX-License-Identifier: MIT; see scripts/LICENSE
import copy
import importlib.util
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1] / "scripts" / "check_idea.py"
SPEC = importlib.util.spec_from_file_location("check_idea", MODULE)
gate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gate)
NOW = datetime(2026, 9, 7, 12, tzinfo=timezone.utc)


def record(ready=False):
    result = {
        "id": "example-claim", "revision": 1, "claim": "A precisely scoped mathematical claim.",
        "status": "proposed", "search_queries": ["precisely scoped claim"],
        "budget": {"max_minutes": 30, "max_new_spend_usd": 0}, "lane": "research",
        "reviews": {"alphaxiv": {"status": "pending"}, "primary": {"status": "pending"}},
        "reward": {"status": "none"}, "correctness": {}, "history": [],
    }
    if ready:
        review = {"status": "complete", "revision": result["revision"],
                  "claim_sha256": gate.claim_hash(result["claim"]),
                  "checked_at": "2026-09-07T11:00:00Z", "verdict": "no_match",
                  "sources": ["https://example.org/primary"], "gap": "The stated extension was not located."}
        result["reviews"] = {key: copy.deepcopy(review) for key in ("alphaxiv", "primary")}
    return result


class CheckIdeaTests(unittest.TestCase):
    def check(self, value, start=False):
        return gate.validate(value, can_start=start, now=NOW)

    def test_normal_proposed_and_blocked_records_validate_without_starting(self):
        value = record()
        self.assertEqual(self.check(value), [])
        self.assertTrue(self.check(value, True))
        value["status"] = "blocked"
        self.assertEqual(self.check(value), [])

    def test_allowed_attempt_and_automatic_start_gate(self):
        value = record(True)
        self.assertEqual(self.check(value, True), [])
        value["status"] = "attempting"
        self.assertEqual(self.check(value), [])
        value["reviews"]["primary"]["status"] = "pending"
        self.assertTrue(self.check(value))

    def test_stale_changed_and_future_reviews_block_start(self):
        for date in ("2026-08-31T11:59:59Z", "2026-09-07T12:00:01Z"):
            value = record(True)
            value["reviews"]["primary"]["checked_at"] = date
            self.assertTrue(self.check(value, True))
        value = record(True)
        value["claim"] += " Changed."
        self.assertTrue(self.check(value, True))
        value = record(True)
        value["reviews"]["primary"]["checked_at"] = "2026-08-31T12:00:00Z"
        self.assertEqual(self.check(value, True), [])

    def test_changed_revision_invalidates_reviews_without_changing_claim(self):
        value = record(True)
        value["revision"] += 1
        self.assertEqual(self.check(value), [])
        self.assertTrue(self.check(value, True))
        for review in value["reviews"].values():
            review["revision"] = value["revision"]
        self.assertEqual(self.check(value, True), [])
        value["reviews"]["primary"]["revision"] = True
        self.assertTrue(self.check(value))

    def test_blocked_and_terminal_states_cannot_start(self):
        for status in ("blocked", "complete", "stopped"):
            value = record(True)
            value["status"] = status
            with self.subTest(status=status):
                self.assertEqual(self.check(value), [])
                self.assertTrue(self.check(value, True))

    def test_known_overlap_and_unresolved_block_start(self):
        for verdict in ("known", "overlap", "unresolved"):
            value = record(True)
            value["reviews"]["primary"]["verdict"] = verdict
            self.assertEqual(self.check(value), [])
            self.assertTrue(self.check(value, True))

    def test_unavailable_review_validates_but_cannot_start(self):
        value = record(True)
        value["reviews"]["alphaxiv"] = {"status": "unavailable"}
        self.assertEqual(self.check(value), [])
        self.assertTrue(self.check(value, True))

    def test_verified_reward_requires_all_fields(self):
        value = record(True)
        value["lane"] = "income"
        self.assertTrue(self.check(value, True))
        reward = {"status": "verified", "source_url": "https://example.org/prize",
                  "acceptance_criteria": "Independent acceptance of the complete proof.",
                  "payment_trigger": "Written confirmation by the named prize administrator."}
        value["reward"] = reward
        self.assertEqual(self.check(value, True), [])
        for key in ("source_url", "acceptance_criteria", "payment_trigger"):
            broken = copy.deepcopy(value)
            del broken["reward"][key]
            self.assertTrue(self.check(broken))
            self.assertTrue(self.check(broken, True))

    def test_evidence_fields_and_zero_spend_budget_are_enforced(self):
        for field, invalid in (("sources", []), ("gap", " ")):
            value = record(True)
            value["reviews"]["primary"][field] = invalid
            self.assertTrue(self.check(value, True))
        for field, invalid in (("max_minutes", True), ("max_minutes", 0),
                               ("max_minutes", 121), ("max_new_spend_usd", False),
                               ("max_new_spend_usd", -1), ("max_new_spend_usd", 1)):
            value = record()
            value["budget"][field] = invalid
            self.assertTrue(self.check(value))
        value = record()
        value["revision"] = True
        self.assertTrue(self.check(value))

    def test_duplicate_keys_and_malformed_json_are_rejected(self):
        for text in ('{"id":"x","id":"y"}', '{"outer":{"a":1,"a":2}}',
                     '{broken', '{"number":NaN}'):
            with tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "record.json"
                path.write_text(text, encoding="utf-8")
                with self.assertRaises(ValueError):
                    gate.load_record(path)

    def test_wrong_types_do_not_crash_validation(self):
        for key in record(True):
            for invalid in (None, [], True):
                if key == "history" and invalid == []:
                    continue
                value = record(True)
                value[key] = invalid
                with self.subTest(key=key, invalid=invalid):
                    self.assertTrue(self.check(value, True))


if __name__ == "__main__":
    unittest.main()
