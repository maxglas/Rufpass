import io
import json
import unittest
from unittest.mock import MagicMock, patch
from urllib.error import HTTPError, URLError

from rufpass.lookup import NameLookup


NUMBER = "+493000000001"


def binding(name="Beispielmuseum", phone="+49-30-00000001", item="Q123"):
    return {"item": {"value": "http://www.wikidata.org/entity/" + item},
            "itemLabel": {"value": name}, "phone": {"value": phone}}


class LookupTests(unittest.TestCase):
    def response(self, rows):
        response = MagicMock()
        response.__enter__.return_value.read.return_value = json.dumps(
            {"results": {"bindings": rows}}).encode()
        return response

    @patch("rufpass.lookup.urlopen")
    def test_exact_match_with_formatted_number(self, urlopen):
        urlopen.return_value = self.response([binding()])
        self.assertEqual(NameLookup().find(NUMBER), "Beispielmuseum")
        request = urlopen.call_args.args[0]
        self.assertTrue(request.full_url.startswith("https://query.wikidata.org/sparql?"))
        self.assertIn("Rufpass", request.get_header("User-agent"))
        self.assertEqual(urlopen.call_args.kwargs["timeout"], 3)

    @patch("rufpass.lookup.urlopen")
    def test_missing_ambiguous_mismatched_or_unsafe_names_are_unknown(self, urlopen):
        for rows in ([], [binding(), binding(item="Q456")],
                     [binding(phone="+493000000009")], [binding(name="Q123")],
                     [binding(name="Firma\x1b[31m")], [binding(phone="+49-30-0000000;ext=1")],
                     [binding(name=" ")]):
            with self.subTest(rows=rows):
                urlopen.return_value = self.response(rows)
                self.assertIsNone(NameLookup().find(NUMBER))

    @patch("rufpass.lookup.urlopen")
    def test_long_names_are_bounded(self, urlopen):
        urlopen.return_value = self.response([binding(name="A" * 100)])
        self.assertEqual(NameLookup().find(NUMBER), "A" * 80)

    @patch("rufpass.lookup.urlopen")
    def test_error_and_invalid_responses_are_safe_and_do_not_log_number(self, urlopen):
        for error in (TimeoutError(NUMBER), URLError(NUMBER)):
            urlopen.side_effect = error
            with self.assertLogs("rufpass", level="WARNING") as logs:
                self.assertIsNone(NameLookup().find(NUMBER))
            self.assertNotIn(NUMBER, " ".join(logs.output))
        urlopen.side_effect = None
        for body in (b"invalid", b"{}", b"x" * 65537):
            response = MagicMock()
            response.__enter__.return_value.read.return_value = body
            urlopen.return_value = response
            with self.assertLogs("rufpass", level="WARNING"):
                self.assertIsNone(NameLookup().find(NUMBER))

    @patch("rufpass.lookup.time.monotonic", return_value=100)
    @patch("rufpass.lookup.urlopen")
    def test_429_honors_retry_after_without_retrying(self, urlopen, clock):
        urlopen.side_effect = HTTPError("redacted", 429, "limited", {"Retry-After": "120"}, io.BytesIO())
        lookup = NameLookup()
        with self.assertLogs("rufpass", level="WARNING"):
            self.assertIsNone(lookup.find(NUMBER))
        clock.return_value = 219
        self.assertIsNone(lookup.find(NUMBER))
        self.assertEqual(urlopen.call_count, 1)
        clock.return_value = 220
        urlopen.side_effect = None
        urlopen.return_value = self.response([binding()])
        self.assertEqual(lookup.find(NUMBER), "Beispielmuseum")

    @patch("rufpass.lookup.time.monotonic", return_value=100)
    @patch("rufpass.lookup.urlopen")
    def test_invalid_input_and_rate_limit_do_not_issue_requests(self, urlopen, clock):
        lookup = NameLookup()
        self.assertIsNone(lookup.find('" } UNION { ?a ?b ?c'))
        urlopen.assert_not_called()
        urlopen.return_value = self.response([])
        lookup.find(NUMBER)
        lookup.find("+493000000002")
        self.assertEqual(urlopen.call_count, 1)

    @patch("rufpass.lookup.time.monotonic", return_value=100)
    @patch("rufpass.lookup.urlopen")
    def test_malformed_retry_header_cannot_block_grant_creation(self, urlopen, clock):
        for headers in ({"Retry-After": "9" * 5000}, None):
            with self.subTest(headers_present=headers is not None):
                urlopen.side_effect = HTTPError("redacted", 429, "limited", headers, io.BytesIO())
                lookup = NameLookup()
                with self.assertLogs("rufpass", level="WARNING"):
                    self.assertIsNone(lookup.find(NUMBER))
                self.assertEqual(lookup.next_request, 160)


if __name__ == "__main__":
    unittest.main()
