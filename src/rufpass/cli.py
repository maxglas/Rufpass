"""Command-line entry points for the service, diagnostics and controlled write probes."""

import argparse
import getpass
import logging
import os
import queue
import re
import sys
import warnings
import uuid
from datetime import date
from importlib.metadata import version
from xml.etree import ElementTree as ET

from fritzconnection import FritzConnection, FritzMonitor
from fritzconnection.lib.fritzphonebook import FritzPhonebook
from fritzconnection.core.exceptions import FritzArrayIndexError


class DiagnosticError(Exception):
    """A user-facing error composed locally, without router response data."""


def outgoing_number(event: str) -> str | None:
    """CALL fields: timestamp;CALL;id;extension;own number;target;line;."""
    fields = event.rstrip("\r\n").split(";")
    if len(fields) < 7 or fields[1] != "CALL":
        return None
    number = fields[5]
    # Diagnostic scope: internal numbers and dial control sequences are skipped.
    if re.fullmatch(r"\+?[0-9]{1,32}", number) is None:
        return None
    return number


def event_message(event: str, show_numbers: bool = False) -> str | None:
    number = outgoing_number(event)
    if number is not None:
        displayed = number if show_numbers else "[maskiert]"
        return f"Wählversuch erkannt: {displayed} — nur Diagnose, keine Freigabe angelegt."
    fields = event.split(";")
    if len(fields) > 1 and fields[1] == "CALL":
        return "Wählereignis erkannt, Zielformat nicht ausgewertet (z. B. interne Nummer oder Steuercode)."
    return None


def phonebook_counts(root: ET.Element, name: str) -> tuple[int, int]:
    """Count the requested book, separating router-supplied internal contacts."""
    if root.tag == "phonebook":
        books = [root]
    elif root.tag == "phonebooks":
        books = root.findall("phonebook")
    else:
        raise DiagnosticError("Unerwartetes Telefonbuch-XML; keine verlässliche Zählung möglich.")
    matches = [book for book in books if book.get("name") == name and book.get("owner") != "255"]
    if len(matches) != 1:
        raise DiagnosticError("Das heruntergeladene XML enthält das Zielbuch nicht eindeutig unter seinem Namen.")
    regular = internal = 0
    for contact in matches[0].findall("contact"):
        numbers = contact.findall("telephony/number")
        if numbers and all(node.get("type") == "intern" or (node.text or "").strip().startswith("**")
                           for node in numbers):
            internal += 1
        else:
            regular += 1
    # Some exports put generated system contacts in a separate internal book.
    internal += sum(len(book.findall("contact")) for book in books if book.get("owner") == "255")
    return regular, internal


def check_phonebook(connection, name: str) -> tuple[int, int, int]:
    """Find the book unambiguously and read it without displaying contacts."""
    phonebooks = FritzPhonebook(fc=connection)
    matches = []
    for book_id in phonebooks.phonebook_ids:
        info = phonebooks.phonebook_info(book_id)
        print(f"Telefonbuch-ID {book_id}: {info['name']!r}")
        if info["name"] == name:
            matches.append((book_id, info))
    if not matches:
        raise DiagnosticError("Ziel-Telefonbuch nicht gefunden; Namen mit --phonebook exakt angeben.")
    if len(matches) != 1:
        raise DiagnosticError("Telefonbuchname ist nicht eindeutig; vor dem Einsatz eindeutig benennen.")
    book_id, info = matches[0]
    with connection.session.get(info["url"], timeout=10) as response:
        response.raise_for_status()
        regular, internal = phonebook_counts(ET.fromstring(response.content), name)
    return book_id, regular, internal


def connect(args):
    password = os.environ.get("RUFPASS_PASSWORD")
    if not password:
        # Do not let getpass fall back to an echoed password on a non-interactive terminal.
        with warnings.catch_warnings():
            warnings.simplefilter("error", getpass.GetPassWarning)
            password = getpass.getpass("FRITZ!Box-Kennwort für den Benutzer rufpass (bzw. --user): ")
    if not password:
        raise DiagnosticError("Kein Kennwort angegeben.")
    return FritzConnection(
        address=args.host,
        user=args.user,
        password=password,
        timeout=10,
        redact_debug_log=True,
    )


def run_check(args) -> int:
    book_id, count, internal = check_phonebook(connect(args), args.phonebook)
    print(f"OK: Ziel-Telefonbuch lesbar, ID {book_id}, {count} Kontakte.")
    print(f"Zusätzlich {internal} interne Einträge im XML (keine externen Kontakte).")
    print("Keine Änderungen vorgenommen. Schreibrechte wurden damit noch nicht geprüft.")
    return 0


def probe_phonebook(connection, book_id: int, expected_name: str, *, keep: bool = False,
                    number: str | None = None) -> None:
    """Create and verify our test contact; remove it unless explicitly retained."""
    if book_id <= 0:
        raise DiagnosticError("Der Schreibtest ist im Standard-Telefonbuch (ID 0) nicht erlaubt.")
    if keep:
        number = re.sub(r"[ ()/\-]", "", number or "")
        if re.fullmatch(r"(?:\+[1-9][0-9]{6,14}|0[0-9]{6,14})", number) is None:
            raise DiagnosticError("Für den sichtbaren Test eine eigene externe Nummer mit Orts-/Mobilfunk- "
                                  "oder Landesvorwahl eingeben; keine internen Nummern oder Steuercodes.")
    else:
        number = "**9"
    service = "X_AVM-DE_OnTel1"
    info = connection.call_action(service, "GetPhonebook", NewPhonebookID=book_id)
    if info.get("NewPhonebookName") != expected_name:
        raise DiagnosticError("Telefonbuch-ID und Name passen nicht zusammen; keine Änderung vorgenommen.")
    name = f"Rufpass Schreibtest {date.today().isoformat()} {uuid.uuid4().hex}"
    contact = ET.Element("contact")
    ET.SubElement(contact, "category").text = "0"
    ET.SubElement(ET.SubElement(contact, "person"), "realName").text = name
    ET.SubElement(ET.SubElement(contact, "telephony"), "number",
                  type="work" if keep else "intern", prio="0").text = number
    print(f"Testkontakt: {name!r}, Telefonbuch-ID {book_id}.", flush=True)
    if keep:
        print("Der sichtbare Testkontakt bleibt gespeichert, bis du ihn im Telefonbuch löschst. "
              "Es wird kein Anruf ausgelöst.", flush=True)
    else:
        print("Verwendet nur die interne Rundrufnummer **9; es wird kein Anruf ausgelöst.", flush=True)
    uid = None
    try:
        result = connection.call_action(
            service, "SetPhonebookEntryUID", NewPhonebookID=book_id,
            NewPhonebookEntryData=ET.tostring(contact, encoding="unicode"),
        )
        raw_uid = result.get("NewPhonebookEntryUniqueID")
        if isinstance(raw_uid, bool) or not re.fullmatch(r"[0-9]+", str(raw_uid)):
            raise DiagnosticError("Die Box hat keine gültige Eintrags-UID geliefert; keine automatische Löschung.")
        uid = int(raw_uid)
        entry = connection.call_action(
            service, "GetPhonebookEntryUID", NewPhonebookID=book_id,
            NewPhonebookEntryUniqueID=uid,
        )
        saved = ET.fromstring(entry["NewPhonebookEntryData"])
        if (saved.tag != "contact" or saved.findtext("person/realName") != name
                or saved.findtext("uniqueid") != str(uid)
                or [node.text for node in saved.findall("telephony/number")] != [number]):
            raise DiagnosticError("Rückgelesener Kontakt ist nicht eindeutig unser Testkontakt; keine Löschung.")
        print(f"Anlegen und Rücklesen erfolgreich (Eintrags-UID {uid}).", flush=True)
        if keep:
            print("OK: Testkontakt bleibt gespeichert. Telefonbuchansicht in der FRITZ!Box neu laden.",
                  flush=True)
            return
        connection.call_action(
            service, "DeletePhonebookEntryUID", NewPhonebookID=book_id,
            NewPhonebookEntryUniqueID=uid,
        )
        try:
            connection.call_action(
                service, "GetPhonebookEntryUID", NewPhonebookID=book_id,
                NewPhonebookEntryUniqueID=uid,
            )
        except FritzArrayIndexError:
            print("OK: Testkontakt angelegt, zurückgelesen und wieder entfernt.", flush=True)
        else:
            raise DiagnosticError("Die Entfernung des Testkontakts konnte nicht bestätigt werden.")
    except (Exception, KeyboardInterrupt):
        # Never retry creation after an uncertain response or delete an unverified UID.
        print(f"Test nicht vollständig abgeschlossen. In Telefonbuch-ID {book_id} nach {name!r} suchen "
              "und, falls vorhanden, ausschließlich diesen Testkontakt manuell entfernen.",
              file=sys.stderr, flush=True)
        raise


def run_probe(args) -> int:
    number = None
    if args.keep:
        number = input("Eigene externe Testnummer mit Vorwahl (wird im Telefonbuch gespeichert): ")
    probe_phonebook(connect(args), args.phonebook_id, args.phonebook, keep=args.keep, number=number)
    return 0


def run_monitor(args) -> int:
    print("Verbinde mit dem Callmonitor auf TCP-Port 1012 …", flush=True)
    with FritzMonitor(address=args.host, timeout=10) as monitor:
        events = monitor.start(reconnect_delay=5, reconnect_tries=3)
        print("Verbunden. Jetzt vom Festnetz aus wählen; Abbruch mit Strg+C.", flush=True)
        print("Nur Diagnose: keine Telefonbuchänderungen, keine Speicherung von Anrufen.", flush=True)
        if args.show_numbers:
            print("Vollständige Zielnummern sind für diese Sitzung sichtbar.", flush=True)
        while True:
            try:
                event = events.get(timeout=1)
            except queue.Empty:
                if not monitor.is_alive:
                    raise OSError("Callmonitor-Verbindung beendet.")
                continue
            message = event_message(event, args.show_numbers)
            if message is not None:
                print(message, flush=True)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Rufpass: automatische Rückruf-Freigaben und FRITZ!Box-Diagnose.")
    parser.add_argument("--version", action="version", version=f"Rufpass {version('rufpass')}")
    commands = parser.add_subparsers(dest="command", required=True)
    for name, help_text in (("run", "Automatische Freigaben im Vordergrund betreiben"),
                            ("configure", "Dienstkonfiguration einmalig interaktiv anlegen"),
                            ("validate", "Dienstkonfiguration und Schnittstellen lesend prüfen"),
                            ("status", "Lokalen Zustand ohne Telefonnummern anzeigen")):
        command = commands.add_parser(name, help=help_text)
        command.add_argument("--config", default="/etc/rufpass/config.toml")
    check = commands.add_parser("check", help="Telefonbuchzugriff und Ziel-ID prüfen")
    monitor = commands.add_parser("monitor", help="Ausgehende Wählversuche live erkennen")
    probe = commands.add_parser("probe", help="Testkontakt anlegen und prüfen; standardmäßig wieder entfernen")
    for command in (check, monitor, probe):
        command.add_argument("--host", default=os.environ.get("RUFPASS_HOST", "fritz.box"),
                             help="FRITZ!Box-Hostname oder IP (Standard: fritz.box)")
    for command in (check, probe):
        command.add_argument("--user", default=os.environ.get("RUFPASS_USER", "rufpass"))
        command.add_argument("--phonebook", default=os.environ.get("RUFPASS_PHONEBOOK", "Rufpass"),
                             help="Exakter Name des zusätzlichen Telefonbuchs (Standard: Rufpass)")
    probe.add_argument("--phonebook-id", type=int, required=True,
                       help="ID des zusätzlichen lokalen Telefonbuchs; ID 0 ist gesperrt")
    probe.add_argument("--keep", action="store_true",
                       help="Sichtbaren Testkontakt mit lokal abgefragter externer Nummer gespeichert lassen")
    monitor.add_argument("--show-numbers", action="store_true",
                         help="Zielnummern für den lokalen Test unmaskiert anzeigen")
    args = parser.parse_args(argv)
    # Router/library exceptions and debug messages may contain authenticated URLs or numbers.
    logging.getLogger("fritzconnection").setLevel(logging.CRITICAL)
    try:
        if args.command in ("run", "configure", "validate", "status"):
            from rufpass.config import configure
            from rufpass.service import run, validate, status
            {"run": run, "configure": configure, "validate": validate, "status": status}[args.command](args.config)
            return 0
        return {"check": run_check, "monitor": run_monitor, "probe": run_probe}[args.command](args)
    except KeyboardInterrupt:
        print("\nDiagnose beendet.")
        return 130
    except DiagnosticError as exc:
        print(f"Fehler: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"Diagnose fehlgeschlagen ({type(exc).__name__}).", file=sys.stderr)
        print("Host, Erreichbarkeit und Aktivierung der Schnittstelle prüfen. Bei check/probe auch Benutzer, "
              "Telefonie-Rechte und Kennwort prüfen. Bei monitor den Callmonitor mit #96*5* aktivieren. "
              "Kennwörter und vollständige Rufnummern nicht in Fehlerberichte kopieren.", file=sys.stderr)
        if args.command in ("run", "configure", "validate", "status"):
            print("Dienstkonfiguration unter /etc/rufpass/config.toml und Zugriffsrechte prüfen.",
                  file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
