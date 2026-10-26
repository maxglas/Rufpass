"""Configuration for the Linux background service; no credentials in logs."""

import getpass
import json
import os
import re
import tomllib
import warnings
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class Config:
    host: str
    user: str
    password: str = field(repr=False)
    phonebook_id: int
    phonebook_name: str
    country_code: str
    area_code: str
    ttl_days: int = 30
    database: str = "/var/lib/rufpass/state.sqlite3"

    def __post_init__(self):
        if not re.fullmatch(r"[a-zA-Z0-9_.-]+", self.host):
            raise ValueError("host muss ein Hostname oder eine IPv4-Adresse ohne Protokoll/Port sein.")
        if not self.user or not self.password or not self.phonebook_name:
            raise ValueError("Benutzer, Kennwort und Telefonbuchname müssen gesetzt sein.")
        if type(self.phonebook_id) is not int or self.phonebook_id <= 0:
            raise ValueError("Ein zusätzliches lokales Telefonbuch mit ID größer 0 ist erforderlich.")
        if not re.fullmatch(r"[1-9][0-9]{0,2}", self.country_code):
            raise ValueError("country_code ohne + oder 00 angeben, beispielsweise 49.")
        if not re.fullmatch(r"[1-9][0-9]{1,5}", self.area_code):
            raise ValueError("area_code ohne führende 0 und ohne Landesvorwahl angeben.")
        if type(self.ttl_days) is not int or not 1 <= self.ttl_days <= 365:
            raise ValueError("ttl_days muss zwischen 1 und 365 liegen.")
        if not self.database or self.database == ":memory:":
            raise ValueError("Für den Dauerbetrieb ist eine persistente Datenbank erforderlich.")


def load_config(path: str) -> Config:
    with open(path, "rb") as file:
        values = tomllib.load(file)
    return Config(**values)


def configure(path: str) -> None:
    """Initial interactive setup only; existing credentials are never overwritten."""
    destination = Path(path)
    if destination.exists():
        raise ValueError("Konfiguration existiert bereits; sie wird nicht überschrieben.")

    def ask(prompt, default=""):
        value = input(f"{prompt}" + (f" [{default}]" if default else "") + ": ").strip()
        return value or default

    print("Rufpass-Ersteinrichtung. Zugangsdaten bleiben auf diesem Rechner.")
    values = dict(
        host=ask("FRITZ!Box-Hostname oder IPv4", "fritz.box"),
        user=ask("FRITZ!Box-Benutzer", "rufpass"),
        phonebook_name=ask("Name des zusätzlichen Telefonbuchs", "Rufpass"),
        phonebook_id=int(ask("ID dieses Telefonbuchs", "1")),
        country_code=ask("Landesvorwahl ohne +", "49"),
        area_code=ask("Ortsvorwahl, z. B. 030").removeprefix("0"),
        ttl_days=int(ask("Gültigkeit in Tagen", "30")),
    )
    with warnings.catch_warnings():
        warnings.simplefilter("error", getpass.GetPassWarning)
        values["password"] = getpass.getpass("FRITZ!Box-Kennwort: ")
    config = Config(**values)
    destination.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive creation prevents accidental replacement during concurrent setup.
    descriptor = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "w", encoding="utf-8") as file:
        for key, value in vars(config).items():
            file.write(f"{key} = {json.dumps(value, ensure_ascii=False)}\n")
    print("Konfiguration gespeichert. Die Installation prüft jetzt die Schnittstellen.")
