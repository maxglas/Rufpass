import contextlib
import io
import queue
import unittest
from unittest.mock import MagicMock, patch

from rufpass.cli import DiagnosticError, check_phonebook, event_message, main, outgoing_number, phonebook_counts
from xml.etree import ElementTree as ET


# Synthetic examples only; never use real call records in fixtures.
CALL = "26.10.26 12:00:00;CALL;0;10;03000000000;+493000000001;SIP0;\r\n"


class CallEventTests(unittest.TestCase):
    def test_detects_target_at_dial_start_without_connect(self):
        self.assertEqual(outgoing_number(CALL), "+493000000001")

    def test_ignores_incoming_connected_and_malformed_events(self):
        for event in ("", "CALL", "date;CALL;0;10;own;123",
                      "date;RING;0;123;456;SIP0;", "date;CONNECT;0;10;123;"):
            with self.subTest(event=event):
                self.assertIsNone(outgoing_number(event))

    def test_rejects_internal_control_and_terminal_escape_targets(self):
        for target in ("**610", "*31#03000000001", "\x1b[31m123", "１２３", "", "1" * 33):
            with self.subTest(target=target):
                self.assertIsNone(outgoing_number(CALL.replace("+493000000001", target)))

    def test_masks_numbers_by_default_and_only_opt_in_reveals_target(self):
        message = event_message(CALL)
        self.assertNotIn("+493000000001", message)
        self.assertNotIn("03000000000", message)
        self.assertIn("[maskiert]", message)
        self.assertIn("+493000000001", event_message(CALL, show_numbers=True))
        self.assertIsNone(event_message("date;RING;0;123;456;SIP0;"))


class PhonebookTests(unittest.TestCase):
    @patch("rufpass.cli.FritzPhonebook")
    def test_reads_only_selected_book_and_hides_contacts(self, phonebook_class):
        books = phonebook_class.return_value
        books.phonebook_ids = [0, 7]
        books.phonebook_info.side_effect = [{"name": "Kontakte"},
                                           {"name": "Rufpass", "url": "http://example.invalid/book7"}]
        connection = MagicMock()
        response = connection.session.get.return_value.__enter__.return_value
        response.content = b'<phonebook name="Rufpass"><contact><person><realName>Privater Name</realName></person><telephony><number>03000000001</number></telephony></contact></phonebook>'
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(check_phonebook(connection, "Rufpass"), (7, 1, 0))
        connection.session.get.assert_called_once_with("http://example.invalid/book7", timeout=10)
        response.raise_for_status.assert_called_once()
        self.assertNotIn("Privater Name", output.getvalue())
        self.assertNotIn("03000000001", output.getvalue())

    @patch("rufpass.cli.FritzPhonebook")
    def test_missing_or_duplicate_book_fails_before_reading_contacts(self, phonebook_class):
        books = phonebook_class.return_value
        for names in (("Kontakte",), ("Rufpass", "Rufpass")):
            books.phonebook_ids = list(range(len(names)))
            books.phonebook_info.side_effect = [{"name": name} for name in names]
            with contextlib.redirect_stdout(io.StringIO()), self.assertRaises(DiagnosticError):
                check_phonebook(object(), "Rufpass")
        books.get_all_name_numbers.assert_not_called()

    def test_empty_visible_book_with_twelve_generated_internal_contacts(self):
        root = ET.Element("phonebook", name="Rufpass", owner="0")
        for number in range(12):
            contact = ET.SubElement(root, "contact")
            ET.SubElement(ET.SubElement(contact, "telephony"), "number", type="intern").text = f"**{600 + number}"
        self.assertEqual(phonebook_counts(root, "Rufpass"), (0, 12))

    def test_multiple_books_do_not_mix_personal_contacts_into_target_count(self):
        root = ET.fromstring('''<phonebooks>
          <phonebook name="Telefonbuch"><contact/><contact/><contact/></phonebook>
          <phonebook name="Rufpass"><contact><telephony><number>03000000001</number></telephony></contact></phonebook>
          <phonebook owner="255"><contact/><contact/></phonebook>
        </phonebooks>''')
        self.assertEqual(phonebook_counts(root, "Rufpass"), (1, 2))

    def test_internal_number_without_type_is_excluded_but_mixed_contact_is_counted(self):
        root = ET.fromstring('''<phonebook name="Rufpass">
          <contact><telephony><number>**9</number></telephony></contact>
          <contact><telephony><number>**610</number><number>03000000001</number></telephony></contact>
        </phonebook>''')
        self.assertEqual(phonebook_counts(root, "Rufpass"), (1, 1))

    def test_wrong_ambiguous_and_unexpected_xml_are_not_reported_as_empty_target_book(self):
        for xml in ('<phonebook name="Anderes Buch"/>', '<html/>',
                    '<phonebooks><phonebook name="Rufpass"/><phonebook name="Rufpass"/></phonebooks>'):
            with self.subTest(xml=xml), self.assertRaises(DiagnosticError):
                phonebook_counts(ET.fromstring(xml), "Rufpass")


class CommandTests(unittest.TestCase):
    def test_development_write_probe_is_not_an_available_command(self):
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
            main(["probe"])
        self.assertEqual(error.exception.code, 2)


    @patch("rufpass.cli.FritzConnection")
    @patch("rufpass.cli.getpass.getpass", return_value="synthetic-password")
    def test_router_error_does_not_reveal_password_or_url(self, password_prompt, connection):
        connection.side_effect = OSError("http://box/?sid=private synthetic-password")
        error = io.StringIO()
        with patch.dict("os.environ", {"RUFPASS_PASSWORD": ""}), contextlib.redirect_stderr(error):
            self.assertEqual(main(["check"]), 1)
        self.assertNotIn("private", error.getvalue())
        self.assertNotIn("synthetic-password", error.getvalue())

    @patch("rufpass.cli.FritzMonitor")
    def test_monitor_processes_dial_event_and_detects_dead_connection(self, monitor_class):
        monitor = monitor_class.return_value.__enter__.return_value
        monitor.start.return_value.get.side_effect = [CALL, queue.Empty()]
        monitor.is_alive = False
        output, error = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(error):
            self.assertEqual(main(["monitor", "--host", "example.invalid"]), 1)
        self.assertIn("Wählversuch erkannt", output.getvalue())
        self.assertNotIn("+493000000001", output.getvalue())
        monitor_class.assert_called_once_with(address="example.invalid", timeout=10)
        monitor_class.return_value.__exit__.assert_called_once()


if __name__ == "__main__":
    unittest.main()
