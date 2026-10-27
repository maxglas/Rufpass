"""Command-line entry points for normal operation and read-only diagnostics."""

import argparse
import getpass
import logging
import os
import queue
import re
import sys
import warnings
from importlib.metadata import version
from xml.etree import ElementTree as ET

from rufpass.config import DEFAULT_CONFIG

from fritzconnection import FritzConnection, FritzMonitor
from fritzconnection.lib.fritzphonebook import FritzPhonebook


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
    """Authenticate the named router user with protected input or a local environment value."""
    password = os.environ.get("RUFPASS_PASSWORD")
    if not password:
        # Do not let getpass fall back to an echoed password on a non-interactive terminal.
        with warnings.catch_warnings():
            warnings.simplefilter("error", getpass.GetPassWarning)
            password = getpass.getpass(f"FRITZ!Box-Kennwort für den Benutzer '{args.user}': ")
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
    """Report book IDs and counts without writing or displaying contact data."""
    book_id, count, internal = check_phonebook(connect(args), args.phonebook)
    print(f"OK: Ziel-Telefonbuch lesbar, ID {book_id}, {count} Kontakte.")
    print(f"Zusätzlich {internal} interne Einträge im XML (keine externen Kontakte).")
    print("Keine Änderungen vorgenommen. Schreibrechte wurden damit noch nicht geprüft.")
    return 0


def run_monitor(args) -> int:
    """Observe live dial events for troubleshooting; never create grants."""
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
        command.add_argument("--config", default=DEFAULT_CONFIG)
    check = commands.add_parser("check", help="Telefonbuchzugriff und Ziel-ID prüfen")
    monitor = commands.add_parser("monitor", help="Ausgehende Wählversuche live erkennen")
    for command in (check, monitor):
        command.add_argument("--host", default=os.environ.get("RUFPASS_HOST", "fritz.box"),
                             help="FRITZ!Box-Hostname oder IP (Standard: fritz.box)")
    check.add_argument("--user", default=os.environ.get("RUFPASS_USER", "rufpass"))
    check.add_argument("--phonebook", default=os.environ.get("RUFPASS_PHONEBOOK", "Rufpass"),
                       help="Exakter Name des zusätzlichen Telefonbuchs (Standard: Rufpass)")
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
        return {"check": run_check, "monitor": run_monitor}[args.command](args)
    except KeyboardInterrupt:
        print("\nDiagnose beendet.")
        return 130
    except DiagnosticError as exc:
        print(f"Fehler: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"Diagnose fehlgeschlagen ({type(exc).__name__}).", file=sys.stderr)
        print("Host, Erreichbarkeit und Aktivierung der Schnittstelle prüfen. Bei check auch Benutzer, "
              "Telefonie-Rechte und Kennwort prüfen. Bei monitor den Callmonitor mit #96*5* aktivieren. "
              "Kennwörter und vollständige Rufnummern nicht in Fehlerberichte kopieren.", file=sys.stderr)
        if args.command in ("run", "configure", "validate", "status"):
            print("Konfigurationsdatei (--config) und Zugriffsrechte prüfen.",
                  file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
