"""Read-only diagnostics. No router writes or persistent call records."""

import argparse
import getpass
import logging
import os
import queue
import re
import sys
import warnings

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


def check_phonebook(connection, name: str) -> tuple[int, int]:
    """Find the book unambiguously and read it without displaying contacts."""
    phonebooks = FritzPhonebook(fc=connection)
    matches = []
    for book_id in phonebooks.phonebook_ids:
        info = phonebooks.phonebook_info(book_id)
        print(f"Telefonbuch-ID {book_id}: {info['name']!r}")
        if info["name"] == name:
            matches.append(book_id)
    if not matches:
        raise DiagnosticError("Ziel-Telefonbuch nicht gefunden; Namen mit --phonebook exakt angeben.")
    if len(matches) != 1:
        raise DiagnosticError("Telefonbuchname ist nicht eindeutig; vor dem Einsatz eindeutig benennen.")
    book_id = matches[0]
    entries = phonebooks.get_all_name_numbers(book_id)
    return book_id, len(entries)


def run_check(args) -> int:
    password = os.environ.get("RUFPASS_PASSWORD")
    if not password:
        # Do not let getpass fall back to an echoed password on a non-interactive terminal.
        with warnings.catch_warnings():
            warnings.simplefilter("error", getpass.GetPassWarning)
            password = getpass.getpass("FRITZ!Box-Kennwort für den Benutzer rufpass (bzw. --user): ")
    if not password:
        raise DiagnosticError("Kein Kennwort angegeben.")
    connection = FritzConnection(
        address=args.host,
        user=args.user,
        password=password,
        timeout=10,
        redact_debug_log=True,
    )
    book_id, count = check_phonebook(connection, args.phonebook)
    print(f"OK: Ziel-Telefonbuch lesbar, ID {book_id}, {count} Einträge.")
    print("Keine Änderungen vorgenommen. Schreibrechte wurden damit noch nicht geprüft.")
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
    parser = argparse.ArgumentParser(description="Rufpass: FRITZ!Box-Diagnose ohne Schreibzugriffe.")
    commands = parser.add_subparsers(dest="command", required=True)
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
        return run_check(args) if args.command == "check" else run_monitor(args)
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
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
