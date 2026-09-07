# SPDX-License-Identifier: MIT; see scripts/LICENSE
"""Offline tests of exact public DOI lookups. No test uses the network."""
import contextlib
import hashlib
import http.client
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch
import urllib.error
import urllib.parse
import urllib.request

SPEC = importlib.util.spec_from_file_location("check_references", Path(__file__).resolve().parents[1]/"scripts"/"check_references.py")
check = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(check)
DOI = "10.1070/SM9615"
OTHER = "10.1016/j.jctb.2015.04.006"


def idea(dois=None):
    return {"id": "private-local-idea", "revision": 2,
            "claim": "  Unpublished local claim with β and private wording.\n",
            "search_queries": ["private topic text never to transmit"],
            "prior_work_dois": [DOI] if dois is None else dois}


def work(doi=DOI):
    return {"DOI": doi, "title": ["More about sparse halves in triangle-free graphs"],
            "author": [{"given": "Alexander", "family": "Razborov"}],
            "published": {"date-parts": [[2022, 1]]}, "URL": "https://doi.org/" + doi}


def response(item):
    return io.BytesIO(json.dumps({"status": "ok", "message": item}).encode())


class ReferenceTests(unittest.TestCase):
    def setUp(self):
        self.opener = Mock()
        p = patch.object(check.urllib.request, "build_opener", return_value=self.opener)
        p.start()
        self.addCleanup(p.stop)

    def test_request_contains_only_doi_and_hash_preserves_local_claim(self):
        self.opener.open.return_value = response(work())
        data = idea()
        result = check.collect_evidence(data)
        self.assertEqual(result["status"], "complete")
        self.assertEqual(result["claim_sha256"], hashlib.sha256(data["claim"].encode("utf-8")).hexdigest())
        self.assertEqual(result["requested_dois"], [DOI])
        self.assertEqual(result["results"][0]["DOI"], DOI.lower())
        self.assertEqual(result["results"][0]["authors"], ["Alexander Razborov"])
        self.assertEqual(result["results"][0]["year"], 2022)
        request = self.opener.open.call_args.args[0]
        self.assertEqual(request.full_url, "https://api.crossref.org/works/" + urllib.parse.quote(DOI, safe=""))
        self.assertEqual(urllib.parse.urlsplit(request.full_url).query, "")
        self.assertIsNone(request.data)
        outbound = request.full_url + str(dict(request.header_items()))
        for private in (data["claim"], data["id"], data["search_queries"][0]):
            self.assertNotIn(private, outbound)
        self.assertEqual(self.opener.open.call_args.kwargs["timeout"], 15)
        self.assertEqual(request.get_header("User-agent"), "Bibliographic-Metadata-Checker/1.0")
        self.assertNotIn("queries", result)

    def test_deduplicate_lowercase_doi(self):
        self.opener.open.side_effect = [response(work()), response(work(DOI.lower()))]
        result = check.collect_evidence(idea([DOI, DOI.lower()]))
        self.assertEqual(len(result["results"]), 1)
        self.assertEqual(result["results"][0]["requested_dois"], [DOI, DOI.lower()])

    def test_invalid_input_before_http(self):
        for bad in [[], idea([]), idea([DOI]*4), idea([5]), idea(["https://doi.org/"+DOI]),
                    idea(["10.1070/not a DOI"]), idea(["10.1070/"+"a"*201]),
                    dict(idea(), revision=True), dict(idea(), claim="\ud800")]:
            with self.subTest(bad=bad), self.assertRaises(check.InputError):
                check.collect_evidence(bad)
        self.opener.open.assert_not_called()

    def test_outage_retains_evidence_and_nonzero_exit(self):
        self.opener.open.side_effect = urllib.error.URLError("offline")
        with tempfile.TemporaryDirectory() as directory:
            source, target = Path(directory)/"idea.json", Path(directory)/"evidence.json"
            source.write_text(json.dumps(idea()), encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()):
                code = check.main(["--idea", str(source), "--output", str(target)])
            result = json.loads(target.read_text())
        self.assertEqual(code, 1)
        self.assertEqual(result["status"], "unavailable")
        self.assertEqual(result["results"], [])
        self.assertTrue(result["errors"])

    def test_partial_failure_preserves_records(self):
        self.opener.open.side_effect = [response(work()), urllib.error.URLError("offline")]
        result = check.collect_evidence(idea([DOI, OTHER]))
        self.assertEqual(result["status"], "partial")
        self.assertEqual(len(result["results"]), 1)
        self.assertEqual(result["errors"][0]["DOI"], OTHER)

    def test_interrupted_body_preserves_earlier_results(self):
        broken = Mock()
        broken.__enter__ = Mock(return_value=broken)
        broken.__exit__ = Mock(return_value=False)
        broken.read.side_effect = http.client.IncompleteRead(b'{"status":')
        self.opener.open.side_effect = [response(work()), broken]
        result = check.collect_evidence(idea([DOI, OTHER]))
        self.assertEqual(result["status"], "partial")
        self.assertEqual(len(result["results"]), 1)

    def test_missing_record_does_not_establish_novelty(self):
        self.opener.open.side_effect = urllib.error.HTTPError("https://api.crossref.org/works/10.1070%2FSM9615", 404, "Not Found", {}, None)
        result = check.collect_evidence(idea())
        self.assertEqual(result["status"], "unavailable")
        self.assertFalse(result["novelty_established"])
        self.assertIn("Missing records do not establish novelty", result["notice"])

    def test_lookup_count_and_response_size_bounds(self):
        self.opener.open.side_effect = [response(work()) for _ in range(3)]
        check.collect_evidence(idea([DOI]*3))
        self.assertEqual(self.opener.open.call_count, 3)
        oversized = Mock()
        oversized.__enter__ = Mock(return_value=oversized)
        oversized.__exit__ = Mock(return_value=False)
        oversized.read.return_value = b"x" * (check.MAX_RESPONSE_BYTES + 1)
        self.opener.open.side_effect = None
        self.opener.open.return_value = oversized
        self.assertEqual(check.collect_evidence(idea())["status"], "unavailable")
        oversized.read.assert_called_once_with(check.MAX_RESPONSE_BYTES + 1)

    def test_malformed_or_mismatched_metadata_rejected(self):
        for item in ({"items": []}, {"DOI": 5}, work(OTHER)):
            self.opener.open.return_value = response(item)
            result = check.collect_evidence(idea())
            self.assertEqual(result["status"], "unavailable")
            self.assertTrue(result["errors"])

    def test_invalid_json_no_request_or_output(self):
        with tempfile.TemporaryDirectory() as directory:
            source, target = Path(directory)/"idea.json", Path(directory)/"evidence.json"
            source.write_text('{"id":"one","id":"two"}')
            with contextlib.redirect_stderr(io.StringIO()):
                code = check.main(["--idea", str(source), "--output", str(target)])
            self.assertEqual(code, 2)
            self.assertFalse(target.exists())
        self.opener.open.assert_not_called()

    def test_redirect_cannot_search_or_change_doi_or_host(self):
        request = urllib.request.Request("https://api.crossref.org/works/10.1070%2FSM9615")
        for target in ("https://example.invalid/paper", "https://api.crossref.org/works?query=topic", "https://api.crossref.org/works/10.1234%2Fother"):
            with self.subTest(target=target), self.assertRaises(check.ProviderError):
                check.CrossrefRedirectGuard().redirect_request(request, None, 302, "redirect", {}, target)


if __name__ == "__main__":
    unittest.main()
