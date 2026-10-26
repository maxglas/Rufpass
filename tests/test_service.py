import io
import contextlib
import os
import tempfile
import unittest
from dataclasses import replace
from datetime import datetime
from pathlib import Path
from unittest.mock import patch
from xml.etree import ElementTree as ET

from rufpass.config import Config, configure, load_config
from rufpass.router import Router, Snapshot
from rufpass.service import Engine, Store, normalize_number, instance_lock


def config(database):
    return Config(host="example.invalid", user="rufpass", password="synthetic-secret",
                  phonebook_id=1, phonebook_name="Rufpass", country_code="49", area_code="30",
                  database=str(database), ttl_days=30)


def contact(name, number, uid, **attributes):
    root = ET.Element("contact")
    ET.SubElement(root, "category").text = "0"
    ET.SubElement(ET.SubElement(root, "person"), "realName").text = name
    ET.SubElement(ET.SubElement(root, "telephony"), "number", type="work", **attributes).text = number
    ET.SubElement(root, "uniqueid").text = str(uid)
    return root


class FakeRouter:
    def __init__(self, normalize):
        self.contacts = {}
        self.other_numbers = set()
        self.normalize = normalize
        self.created = 0
        self.deleted = []
        self.fail_create_reply = False
        self.fail_delete_reply = False

    def snapshot(self):
        known = set(self.other_numbers)
        known.update(self.normalize(node.text or "") for root in self.contacts.values()
                     for node in root.findall("telephony/number"))
        return Snapshot(dict(self.contacts), known)

    def create(self, marker, number):
        self.created += 1
        uid = 100 + self.created
        self.contacts[uid] = contact(marker, number, uid)
        if self.fail_create_reply:
            raise TimeoutError("synthetic reply lost")
        return uid

    def delete(self, uid):
        self.deleted.append(uid)
        del self.contacts[uid]
        if self.fail_delete_reply:
            raise TimeoutError("synthetic reply lost")

    def get(self, uid):
        return self.contacts.get(uid)


class NormalizationTests(unittest.TestCase):
    def test_national_international_and_local_numbers_match(self):
        for value in ("030 0000-0001", "+49 (30) 00000001", "00493000000001"):
            self.assertEqual(normalize_number(value, "49", "30"), "+493000000001")
        self.assertEqual(normalize_number("23456789", "49", "30"), "+493023456789")

    def test_control_internal_emergency_and_premium_numbers_are_excluded(self):
        for value in ("**610", "*31#03000000001", "110", "112", "116117", "11833", "09001234567",
                      "01371234567", "+491801234567", "abc", "１２３４５６７", "+490301234567", "", "00"):
            with self.subTest(value=value):
                self.assertIsNone(normalize_number(value, "49", "30"))

    def test_foreign_numbers_are_kept_in_international_format(self):
        self.assertEqual(normalize_number("0033123456789", "49", "30"), "+33123456789")


class EngineTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.config = config(Path(self.directory.name) / "state.sqlite3")
        self.store = Store(self.config.database, self.config)
        self.engine = Engine(self.config, self.store)
        self.router = FakeRouter(self.engine.normalize)
        self.number = "+493000000001"
        self.now = 1_000_000

    def tearDown(self):
        self.store.close()
        self.directory.cleanup()

    def create_grant(self):
        self.engine.dial(self.number, self.now)
        self.engine.sync(self.router, self.now)

    def test_outgoing_attempt_persists_before_network_and_creates_normal_contact(self):
        self.engine.dial(self.number, self.now)
        self.assertEqual(len(self.store.rows()), 1)
        self.assertEqual(self.router.created, 0)
        self.engine.sync(self.router, self.now)
        self.assertEqual(self.router.created, 1)
        self.assertEqual(self.store.rows()[0]["uid"], 101)
        name = self.router.contacts[101].findtext("person/realName")
        expected_date = datetime.fromtimestamp(self.now).date().isoformat()
        self.assertRegex(name, rf"^Rufpass automatisch {expected_date} [0-9a-f]{{32}}$")

    def test_repeated_call_extends_expiry_without_duplicate_or_router_write(self):
        self.create_grant()
        original_marker = self.store.rows()[0]["marker"]
        self.engine.dial("03000000001", self.now + 2 * 86400)
        self.engine.sync(self.router, self.now + 2 * 86400)
        row = self.store.rows()[0]
        self.assertEqual(row["marker"], original_marker)
        self.assertEqual(row["expires"], self.now + 2 * 86400 + 30 * 86400)
        self.assertEqual(self.router.created, 1)

    def test_known_personal_contact_is_not_copied_or_modified(self):
        self.router.other_numbers.add(self.number)
        self.create_grant()
        self.assertEqual(self.router.created, 0)
        self.assertEqual(self.store.rows(), [])

    def test_manual_target_contact_is_preserved(self):
        self.router.contacts[7] = contact("Persönlicher Kontakt", self.number, 7)
        self.create_grant()
        self.engine.sync(self.router, self.now + 40 * 86400)
        self.assertIn(7, self.router.contacts)
        self.assertEqual(self.router.created, 0)
        self.assertEqual(self.router.deleted, [])

    def test_expiry_removes_only_owned_contact(self):
        self.router.contacts[7] = contact("Manuell", "+493000000002", 7)
        self.create_grant()
        self.engine.sync(self.router, self.now + 30 * 86400)
        self.assertEqual(self.router.deleted, [101])
        self.assertEqual(list(self.router.contacts), [7])
        self.assertEqual(self.store.rows(), [])

    def test_pending_expired_record_is_not_created_after_long_outage(self):
        self.engine.dial(self.number, self.now)
        self.engine.sync(self.router, self.now + 31 * 86400)
        self.assertEqual(self.router.created, 0)
        self.assertEqual(self.store.rows(), [])

    def test_create_timeout_is_reconciled_after_restart_without_duplicate(self):
        self.engine.dial(self.number, self.now)
        self.router.fail_create_reply = True
        with self.assertRaises(TimeoutError):
            self.engine.sync(self.router, self.now)
        self.assertIsNone(self.store.rows()[0]["uid"])
        self.store.close()
        self.store = Store(self.config.database, self.config)
        self.engine = Engine(self.config, self.store)
        self.router.fail_create_reply = False
        self.engine.sync(self.router, self.now + 1)
        self.assertEqual(self.router.created, 1)
        self.assertEqual(self.store.rows()[0]["uid"], 101)
        name = self.router.contacts[101].findtext("person/realName")
        expected_date = datetime.fromtimestamp(self.now).date().isoformat()
        self.assertRegex(name, rf"^Rufpass automatisch {expected_date} [0-9a-f]{{32}}$")

    def test_delete_timeout_is_reconciled_without_deleting_other_contacts(self):
        self.create_grant()
        self.router.fail_delete_reply = True
        with self.assertRaises(TimeoutError):
            self.engine.sync(self.router, self.now + 31 * 86400)
        self.router.fail_delete_reply = False
        self.engine.sync(self.router, self.now + 31 * 86400 + 1)
        self.assertEqual(self.router.deleted, [101])
        self.assertEqual(self.store.rows(), [])

    def test_manually_edited_contact_is_preserved_after_expiry(self):
        for edit in ("name", "number", "vip", "email", "quickdial", "ringtone"):
            with self.subTest(edit=edit):
                self.store.db.execute("DELETE FROM grants")
                self.store.db.commit()
                self.router = FakeRouter(self.engine.normalize)
                self.create_grant()
                root = self.router.contacts[101]
                if edit == "name":
                    root.find("person/realName").text = "Mein Kontakt"
                elif edit == "number":
                    root.find("telephony/number").text = "+493000000009"
                elif edit == "vip":
                    root.find("category").text = "1"
                elif edit == "email":
                    ET.SubElement(ET.SubElement(root.find("telephony"), "services"), "email").text = "test@example.invalid"
                elif edit == "quickdial":
                    root.find("telephony/number").set("quickdial", "1")
                else:
                    ET.SubElement(root, "ringtone", selected="custom")
                self.engine.sync(self.router, self.now + 31 * 86400)
                self.assertIn(101, self.router.contacts)
                self.assertEqual(self.router.deleted, [])

    def test_contact_edited_since_snapshot_is_not_deleted(self):
        self.create_grant()
        def edited(uid):
            root = self.router.contacts[uid]
            root.find("person/realName").text = "Gerade manuell geändert"
            return root
        self.router.get = edited
        self.engine.sync(self.router, self.now + 31 * 86400)
        self.assertEqual(self.router.deleted, [])
        self.assertIn(101, self.router.contacts)

    def test_manual_removal_does_not_trigger_recreation(self):
        self.create_grant()
        self.router.contacts.clear()
        self.engine.sync(self.router, self.now + 1)
        self.assertEqual(self.router.created, 1)
        self.assertEqual(self.store.rows(), [])

    def test_new_call_can_recreate_a_manually_removed_grant(self):
        self.create_grant()
        self.router.contacts.clear()
        self.engine.dial(self.number, self.now + 1)
        self.engine.sync(self.router, self.now + 1)
        self.assertEqual(self.router.created, 2)
        self.assertEqual(self.store.rows()[0]["uid"], 102)

    def test_changed_uid_is_not_deleted_even_if_marker_was_copied(self):
        self.create_grant()
        root = self.router.contacts.pop(101)
        root.find("uniqueid").text = "202"
        self.router.contacts[202] = root
        self.engine.sync(self.router, self.now + 31 * 86400)
        self.assertIn(202, self.router.contacts)
        self.assertEqual(self.router.deleted, [])

    def test_full_book_keeps_pending_grant_without_deleting_manual_entries(self):
        self.router.contacts = {index: contact("Manuell", f"+493011{index:06d}", index)
                                for index in range(300)}
        with self.assertLogs("rufpass", level="ERROR"):
            self.create_grant()
        self.assertEqual(self.router.created, 0)
        self.assertEqual(self.router.deleted, [])
        self.assertEqual(len(self.store.rows()), 1)

    def test_duplicate_markers_are_not_deleted(self):
        self.create_grant()
        marker = self.store.rows()[0]["marker"]
        self.router.contacts[102] = contact(marker, self.number, 102)
        with self.assertLogs("rufpass", level="ERROR"):
            self.engine.sync(self.router, self.now + 31 * 86400)
        self.assertEqual(self.router.deleted, [])

    def test_changed_target_cannot_reuse_database(self):
        with self.assertRaises(ValueError):
            Store(self.config.database, replace(self.config, phonebook_id=2))

    def test_logs_do_not_include_numbers_or_password(self):
        with self.assertLogs("rufpass", level="INFO") as logs:
            self.create_grant()
            self.engine.sync(self.router, self.now + 31 * 86400)
        text = "\n".join(logs.output)
        self.assertNotIn(self.number, text)
        self.assertNotIn(self.config.password, text)


class RouterTests(unittest.TestCase):
    @patch("rufpass.router.FritzPhonebook")
    @patch("rufpass.router.FritzConnection")
    def test_snapshot_reads_selected_book_and_skips_generated_internal_contacts(self, connection_class, books_class):
        cfg = config("synthetic.sqlite3")
        books = books_class.return_value
        books.phonebook_ids = [1]
        books.phonebook_info.return_value = {"name": "Rufpass", "url": "http://example.invalid/book"}
        response = connection_class.return_value.session.get.return_value.__enter__.return_value
        root = ET.Element("phonebook", name="Rufpass")
        internal = ET.SubElement(root, "contact")
        ET.SubElement(ET.SubElement(internal, "telephony"), "number", type="intern").text = "**9"
        internal_without_type = ET.SubElement(root, "contact")
        ET.SubElement(ET.SubElement(internal_without_type, "telephony"), "number").text = " **610 "
        root.append(contact("Manuell", "+493000000001", 9))
        response.content = ET.tostring(root)
        router = Router(cfg, lambda number: normalize_number(number, "49", "30"))
        snapshot = router.snapshot()
        self.assertEqual(set(snapshot.contacts), {9})
        self.assertEqual(snapshot.known, {"+493000000001"})


class ConfigTests(unittest.TestCase):
    def test_config_roundtrip_and_password_is_not_in_repr(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.toml"
            with patch("builtins.input", side_effect=["", "", "", "", "", "030", ""]), \
                    patch("rufpass.config.getpass.getpass", return_value='synthetic-"secret\\#'), \
                    contextlib.redirect_stdout(io.StringIO()):
                configure(str(path))
            cfg = load_config(str(path))
            self.assertEqual(cfg.area_code, "30")
            self.assertEqual(cfg.ttl_days, 365)
            self.assertEqual(cfg.password, 'synthetic-"secret\\#')
            self.assertNotIn(cfg.password, repr(cfg))
            with self.assertRaises(ValueError):
                configure(str(path))

    def test_omitted_ttl_defaults_to_365_and_explicit_value_is_preserved(self):
        values = vars(config("synthetic.sqlite3")).copy()
        values.pop("ttl_days")
        self.assertEqual(Config(**values).ttl_days, 365)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.toml"
            with patch("builtins.input", side_effect=["", "", "", "", "", "030", "30"]), \
                    patch("rufpass.config.getpass.getpass", return_value="synthetic-secret"), \
                    contextlib.redirect_stdout(io.StringIO()):
                configure(str(path))
            self.assertEqual(load_config(str(path)).ttl_days, 30)

    def test_rejects_default_book_and_invalid_expiry_or_area(self):
        for changes in ({"phonebook_id": 0}, {"ttl_days": 0}, {"ttl_days": 366}, {"area_code": "030"}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                replace(config("synthetic.sqlite3"), **changes)

    @unittest.skipUnless(os.name == "posix", "flock is exercised on Linux")
    def test_second_instance_is_rejected_and_lock_is_released(self):
        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory) / "state.sqlite3")
            with instance_lock(path):
                with self.assertRaises(ValueError), instance_lock(path):
                    pass
            with instance_lock(path):
                pass


if __name__ == "__main__":
    unittest.main()
