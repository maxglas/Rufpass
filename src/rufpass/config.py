"""Configuration for foreground execution and services; no credentials in logs."""

import getpass
import json
import os
import re
import tomllib
import warnings
from dataclasses import dataclass, field
from pathlib import Path


if os.name == "nt":
    data_dir = Path(os.environ.get("LOCALAPPDATA", Path.home())) / "Rufpass"
    DEFAULT_CONFIG = str(data_dir / "config.toml")
    DEFAULT_DATABASE = str(data_dir / "state.sqlite3")
else:
    DEFAULT_CONFIG = "/etc/rufpass/config.toml"
    DEFAULT_DATABASE = "/var/lib/rufpass/state.sqlite3"


@dataclass(frozen=True)
class Config:
    host: str
    user: str
    password: str = field(repr=False)
    phonebook_id: int
    phonebook_name: str
    country_code: str
    area_code: str
    ttl_days: int = 365
    database: str = DEFAULT_DATABASE
    reverse_lookup: bool = True

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
        if type(self.reverse_lookup) is not bool:
            raise ValueError("reverse_lookup muss true oder false sein.")
        if not self.database or self.database == ":memory:":
            raise ValueError("Für den Dauerbetrieb ist eine persistente Datenbank erforderlich.")


def load_config(path: str) -> Config:
    """Load local TOML and validate it before credentials reach the router client."""
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
    host = ask("FRITZ!Box-Hostname oder IPv4", "fritz.box")
    user = ask("FRITZ!Box-Benutzer", "rufpass")
    with warnings.catch_warnings():
        warnings.simplefilter("error", getpass.GetPassWarning)
        password = getpass.getpass(f"FRITZ!Box-Kennwort für den Benutzer '{user}': ")
    values = dict(
        host=host,
        user=user,
        password=password,
        phonebook_name=ask("Name des zusätzlichen Telefonbuchs", "Rufpass"),
        phonebook_id=int(ask("ID dieses Telefonbuchs", "1")),
        country_code=ask("Landesvorwahl ohne +", "49"),
        area_code=ask("Ortsvorwahl, z. B. 030").removeprefix("0"),
        ttl_days=int(ask("Gültigkeit in Tagen", "365")),
    )
    config = Config(**values)
    destination.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive creation prevents accidental replacement during concurrent setup.
    descriptor = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "w", encoding="utf-8") as file:
        for key, value in vars(config).items():
            file.write(f"{key} = {json.dumps(value, ensure_ascii=False)}\n")
    print("Namenssuche ist aktiviert: Unbekannte Wählziele werden an Wikidata übertragen. Abschaltbar mit reverse_lookup = false.")
    print("Konfiguration gespeichert. Schnittstellen mit rufpass validate prüfen.")
