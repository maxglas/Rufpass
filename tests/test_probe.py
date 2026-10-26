import contextlib
import io
import unittest
from unittest.mock import Mock
from xml.etree import ElementTree as ET

from fritzconnection.core.exceptions import FritzArrayIndexError
from rufpass.cli import DiagnosticError, probe_phonebook


class ProbeTests(unittest.TestCase):
    def setUp(self):
        self.connection = Mock()
        self.created = None
        self.deleted = []
        self.output = io.StringIO()
        self.error = io.StringIO()

        def action(service, operation, **args):
            self.assertEqual(service, "X_AVM-DE_OnTel1")
            self.assertEqual(args["NewPhonebookID"], 1)
            if operation == "GetPhonebook":
                return {"NewPhonebookName": "Rufpass"}
            if operation == "SetPhonebookEntryUID":
                self.created = ET.fromstring(args["NewPhonebookEntryData"])
                self.assertIsNone(self.created.find("uniqueid"))
                self.assertEqual(self.created.findtext("telephony/number"), "**9")
                ET.SubElement(self.created, "uniqueid").text = "42"
                return {"NewPhonebookEntryUniqueID": 42}
            self.assertEqual(args["NewPhonebookEntryUniqueID"], 42)
            if operation == "GetPhonebookEntryUID":
                if self.deleted:
                    raise FritzArrayIndexError("713: not found")
                return {"NewPhonebookEntryData": ET.tostring(self.created, encoding="unicode")}
            if operation == "DeletePhonebookEntryUID":
                self.deleted.append(42)
                return {}
            self.fail(f"Unexpected operation: {operation}")

        self.action = action
        self.connection.call_action.side_effect = action

    def run_probe(self):
        with contextlib.redirect_stdout(self.output), contextlib.redirect_stderr(self.error):
            probe_phonebook(self.connection, 1, "Rufpass")

    def test_creates_without_uid_and_only_deletes_returned_verified_uid(self):
        self.run_probe()
        self.assertEqual(self.deleted, [42])
        self.assertIn("wieder entfernt", self.output.getvalue())
        self.assertEqual(self.error.getvalue(), "")
        self.assertEqual(self.connection.call_action.call_count, 5)

    def test_default_book_is_rejected_without_any_network_calls(self):
        with self.assertRaises(DiagnosticError):
            probe_phonebook(self.connection, 0, "Telefonbuch")
        self.connection.call_action.assert_not_called()

    def test_mismatched_book_name_is_rejected_before_writes(self):
        self.connection.call_action.side_effect = None
        self.connection.call_action.return_value = {"NewPhonebookName": "Persönliche Kontakte"}
        with self.assertRaises(DiagnosticError):
            self.run_probe()
        self.assertEqual(self.connection.call_action.call_count, 1)

    def test_different_contact_is_never_deleted(self):
        def changed(service, operation, **args):
            result = self.action(service, operation, **args)
            if operation == "GetPhonebookEntryUID":
                root = ET.fromstring(result["NewPhonebookEntryData"])
                root.find("person/realName").text = "Persönlicher Kontakt"
                result["NewPhonebookEntryData"] = ET.tostring(root, encoding="unicode")
            return result
        self.connection.call_action.side_effect = changed
        with self.assertRaises(DiagnosticError):
            self.run_probe()
        self.assertEqual(self.deleted, [])
        self.assertIn("manuell entfernen", self.error.getvalue())

    def test_uncertain_creation_is_not_retried_or_deleted_by_guess(self):
        def lost(service, operation, **args):
            if operation == "SetPhonebookEntryUID":
                raise TimeoutError("synthetic authenticated URL must not be printed")
            return self.action(service, operation, **args)
        self.connection.call_action.side_effect = lost
        with self.assertRaises(TimeoutError):
            self.run_probe()
        self.assertEqual(self.deleted, [])
        self.assertEqual(self.connection.call_action.call_count, 2)
        self.assertNotIn("authenticated URL", self.error.getvalue())
        self.assertIn("Rufpass Schreibtest", self.error.getvalue())

    def test_missing_uid_never_triggers_deletion(self):
        def missing(service, operation, **args):
            result = self.action(service, operation, **args)
            return {} if operation == "SetPhonebookEntryUID" else result
        self.connection.call_action.side_effect = missing
        with self.assertRaises(DiagnosticError):
            self.run_probe()
        self.assertEqual(self.deleted, [])

    def test_delete_failure_leaves_actionable_manual_cleanup_hint(self):
        def fail_delete(service, operation, **args):
            if operation == "DeletePhonebookEntryUID":
                raise OSError("synthetic failure")
            return self.action(service, operation, **args)
        self.connection.call_action.side_effect = fail_delete
        with self.assertRaises(OSError):
            self.run_probe()
        self.assertIn("manuell entfernen", self.error.getvalue())


if __name__ == "__main__":
    unittest.main()
