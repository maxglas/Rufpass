"""Persistent call grants and foreground service managed by systemd."""

import contextlib
import logging
import os
import queue
import re
import signal
import sqlite3
import threading
import time
import uuid
from datetime import datetime
from pathlib import Path

from fritzconnection import FritzMonitor

from rufpass.config import load_config
from rufpass.router import Router
from rufpass.lookup import NameLookup


LOG = logging.getLogger("rufpass")


def normalize_number(value, country_code, area_code):
    """Normalize dialled external numbers; reject internal/control/short service calls."""
    value = re.sub(r"[ ()/\-]", "", value.strip())
    if re.fullmatch(r"\+?[0-9]+", value) is None:
        return None
    if value.startswith("00"):
        value = "+" + value[2:]
    elif value.startswith("0"):
        value = "+" + country_code + value[1:]
    elif not value.startswith("+"):
        if len(value) < 4 or value.startswith(("110", "112", "115", "116", "118")):
            return None
        value = "+" + country_code + area_code + value
    if re.fullmatch(r"\+[1-9][0-9]{6,14}", value) is None:
        return None
    if value.startswith("+" + country_code + "0"):
        return None
    # German premium-rate/shared-cost numbers are not ordinary callback destinations.
    if country_code == "49" and value.startswith(("+49137", "+49180", "+49900", "+49118", "+49116")):
        return None
    return value


class Store:
    def __init__(self, path, config):
        parent = Path(path).parent
        parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(path)
        if os.name == "posix":
            os.chmod(path, 0o600)
        self.db.row_factory = sqlite3.Row
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS contact_names (number TEXT PRIMARY KEY, name TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS grants (
                number TEXT PRIMARY KEY, marker TEXT NOT NULL UNIQUE,
                last_dial REAL NOT NULL, expires REAL NOT NULL, uid INTEGER,
                dirty INTEGER NOT NULL DEFAULT 1
            );
        """)
        binding = f"{config.host}|{config.phonebook_id}|{config.phonebook_name}"
        saved = self.db.execute("SELECT value FROM metadata WHERE key='target'").fetchone()
        if saved is not None and saved[0] != binding:
            self.db.close()
            raise ValueError("Die Datenbank gehört zu einer anderen Zielkonfiguration.")
        with self.db:
            self.db.execute("INSERT OR IGNORE INTO metadata VALUES ('target', ?)", (binding,))

    def close(self):
        self.db.close()

    def record(self, number, now, ttl_days):
        with self.db:
            self.db.execute("""INSERT INTO grants VALUES (?, ?, ?, ?, NULL, 1)
                ON CONFLICT(number) DO UPDATE SET last_dial=excluded.last_dial,
                    expires=excluded.expires, dirty=1""",
                (number, f"Rufpass automatisch {datetime.fromtimestamp(now):%Y-%m-%d} {uuid.uuid4().hex}", now, now + ttl_days * 86400))

    def rows(self):
        return self.db.execute("""SELECT grants.*, COALESCE(contact_names.name, grants.marker) AS contact_name
            FROM grants LEFT JOIN contact_names USING(number) ORDER BY expires, last_dial""").fetchall()

    def set_contact_name(self, number, name):
        with self.db:
            self.db.execute("INSERT OR REPLACE INTO contact_names VALUES (?, ?)", (number, name))

    def set_uid(self, number, uid):
        with self.db:
            self.db.execute("UPDATE grants SET uid=?, dirty=0 WHERE number=?", (uid, number))

    def forget(self, number):
        with self.db:
            self.db.execute("DELETE FROM grants WHERE number=?", (number,))
            self.db.execute("DELETE FROM contact_names WHERE number=?", (number,))


def is_owned(contact, row, normalize):
    """A matching marker alone does not authorize deleting an edited contact."""
    if contact.findtext("person/realName") != row["contact_name"]:
        return False
    if contact.findtext("category") not in (None, "", "0"):
        return False
    numbers = contact.findall("telephony/number")
    if len(numbers) != 1 or normalize(numbers[0].text or "") != row["number"]:
        return False
    if numbers[0].get("type") != "work":
        return False
    for attribute in ("quickdial", "vanity"):
        if numbers[0].get(attribute):
            return False
    # Preserve additions such as email, image, notes, ringtone or a second number.
    allowed_values = {"realName", "number", "category", "uniqueid", "mod_time", "timestamp"}
    allowed_tags = allowed_values | {"contact", "person", "telephony", "services", "imageURL"}
    return all(node.tag in allowed_tags and (not (node.text or "").strip() or node.tag in allowed_values)
               for node in contact.iter())


class Engine:
    def __init__(self, config, store):
        self.config = config
        self.store = store
        self.lookup = NameLookup()

    def normalize(self, value):
        return normalize_number(value, self.config.country_code, self.config.area_code)

    def dial(self, value, now):
        number = self.normalize(value)
        if number is None:
            LOG.info("Wählziel übersprungen: intern, Steuercode, Sonder- oder ungültige Nummer.")
            return False
        self.store.record(number, now, self.config.ttl_days)
        LOG.info("Wählversuch gespeichert; Freigabe zur Synchronisation vorgemerkt.")
        return True

    def sync(self, router, now):
        snapshot = router.snapshot()
        target_size = len(snapshot.contacts)
        for row in self.store.rows():
            matches = [(uid, contact) for uid, contact in snapshot.contacts.items()
                       if contact.findtext("person/realName") == row["contact_name"]
                       and (row["contact_name"] == row["marker"] or any(
                           self.normalize(node.text or "") == row["number"]
                           for node in contact.findall("telephony/number")))]
            if len(matches) > 1:
                LOG.error("Mehrdeutige Rufpass-Kennung im Telefonbuch; keine Änderung an diesem Kontakt.")
                continue
            match = matches[0] if matches else None
            if match and not is_owned(match[1], row, self.normalize):
                self.store.forget(row["number"])
                LOG.warning("Manuell veränderter Kontakt bleibt erhalten; Verwaltung abgegeben.")
                continue
            if match and row["uid"] is not None and row["uid"] != match[0]:
                self.store.forget(row["number"])
                LOG.warning("Kontakt-UID hat sich geändert; Eintrag bleibt unverändert.")
                continue
            if row["expires"] <= now:
                if match:
                    latest = router.get(match[0])
                    if (latest is None or latest.findtext("uniqueid") != str(match[0])
                            or not is_owned(latest, row, self.normalize)):
                        self.store.forget(row["number"])
                        LOG.warning("Kontakt unmittelbar vor Bereinigung verändert oder entfernt; nicht gelöscht.")
                        continue
                    router.delete(match[0])
                    del snapshot.contacts[match[0]]
                    target_size -= 1
                    LOG.info("Abgelaufene eigene Freigabe entfernt.")
                self.store.forget(row["number"])
            elif match:
                self.store.set_uid(row["number"], match[0])
            elif row["uid"] is not None and not row["dirty"]:
                # A user removed or renamed the contact: do not silently recreate it.
                self.store.forget(row["number"])
                LOG.info("Entfernten oder umbenannten Kontakt nicht erneut angelegt.")
            elif row["number"] in snapshot.known:
                self.store.forget(row["number"])
                LOG.info("Nummer ist bereits in einem Telefonbuch bekannt; kein zusätzlicher Kontakt.")
            else:
                if target_size >= 300:
                    LOG.error("Zielbuch enthält bereits mindestens 300 XML-Einträge; "
                              "neue Freigabe bleibt vorgemerkt. Telefonbuchkapazität prüfen.")
                    continue
                if row["uid"] is not None:
                    # A fresh call permits recreating a removed grant, with uncertain replies reconciled by marker.
                    self.store.set_uid(row["number"], None)
                if row["contact_name"] == row["marker"]:
                    name = self.lookup.find(row["number"]) if self.config.reverse_lookup else None
                    date_match = re.search(r"\d{4}-\d{2}-\d{2}", row["marker"])
                    created = date_match[0] if date_match else datetime.fromtimestamp(row["last_dial"]).date().isoformat()
                    row = dict(row)
                    row["contact_name"] = f"Rufpass {created} {name or 'Name unbekannt'}"
                    self.store.set_contact_name(row["number"], row["contact_name"])
                # Persist the exact name before writing, including when the reply gets lost.
                uid = router.create(row["contact_name"], row["number"])
                self.store.set_uid(row["number"], uid)
                snapshot.known.add(row["number"])
                target_size += 1
                LOG.info("Automatische Rückruf-Freigabe angelegt.")


@contextlib.contextmanager
def instance_lock(path):
    if os.name != "posix":
        raise ValueError("Der unterstützte Dienstbetrieb benötigt Linux.")
    import fcntl
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(str(path) + ".lock", "a") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise ValueError("Für diese Datenbank läuft bereits eine Rufpass-Instanz.") from None
        yield


def validate(path):
    import socket
    config = load_config(path)
    normalize = lambda number: normalize_number(number, config.country_code, config.area_code)
    snapshot = Router(config, normalize).snapshot()
    with socket.create_connection((config.host, 1012), timeout=5):
        pass
    print(f"OK: Telefonbuch-ID {config.phonebook_id} lesbar und Callmonitor erreichbar. "
          f"{len(snapshot.contacts)} normale Kontakte im Zielbuch. Keine Änderungen vorgenommen.")


def status(path):
    config = load_config(path)
    database = Path(config.database).resolve()
    if not database.exists():
        print("Noch kein lokaler Zustand vorhanden; Dienst zunächst starten.")
        return
    with sqlite3.connect(database.as_uri() + "?mode=ro", uri=True) as db:
        total, pending, expired = db.execute(
            "SELECT COUNT(*), COALESCE(SUM(uid IS NULL),0), COALESCE(SUM(expires<=?),0) FROM grants",
            (time.time(),)).fetchone()
    print(f"Lokaler Stand: {total} Freigaben, davon {pending} zur Anlage vorgemerkt, {expired} abgelaufen.")
    print("Telefonnummern und Zugangsdaten werden nicht angezeigt. Abgleich erfolgt durch den Dienst.")


def run(path):
    config = load_config(path)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    logging.getLogger("fritzconnection").setLevel(logging.CRITICAL)
    stop = threading.Event()
    for signum in (signal.SIGTERM, signal.SIGINT):
        signal.signal(signum, lambda *_: stop.set())
    with instance_lock(config.database):
        store = Store(config.database, config)
        engine = Engine(config, store)
        try:
            while not stop.is_set():
                try:
                    with FritzMonitor(address=config.host, timeout=5) as monitor:
                        events = monitor.start(queue_size=4096, reconnect_delay=5)
                        LOG.info("Callmonitor verbunden. Automatische Freigaben aktiv; Gültigkeit %s Tage.",
                                 config.ttl_days)
                        router = None
                        next_sync = 0
                        while not stop.is_set():
                            try:
                                event = events.get(timeout=1)
                            except queue.Empty:
                                if not monitor.is_alive:
                                    raise OSError("Callmonitor beendet")
                            else:
                                fields = event.rstrip("\r\n").split(";")
                                if len(fields) >= 7 and fields[1] == "CALL":
                                    if engine.dial(fields[5], time.time()):
                                        next_sync = 0
                            if time.monotonic() >= next_sync:
                                try:
                                    if router is None:
                                        router = Router(config, engine.normalize)
                                    engine.sync(router, time.time())
                                except Exception as exc:
                                    # Do not log exception strings: they can include numbers or session URLs.
                                    LOG.error("Telefonbuchabgleich fehlgeschlagen (%s); erneuter Versuch in 30 Sekunden.",
                                              type(exc).__name__)
                                    router = None
                                next_sync = time.monotonic() + 30
                except Exception as exc:
                    LOG.error("Callmonitor-Verbindung fehlgeschlagen (%s); erneuter Versuch in 5 Sekunden.",
                              type(exc).__name__)
                    stop.wait(5)
        finally:
            store.close()
            LOG.info("Rufpass beendet.")
