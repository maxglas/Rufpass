# Betriebsdiagnose

Rufpass stellt lesende Diagnosebefehle bereit. Sie legen keine Beispielkontakte an
und ändern keine Telefonbucheinträge. Freigaben erzeugt ausschließlich `run` beim
Verarbeiten tatsächlicher Wählversuche. Zur Einrichtung siehe [Betrieb](operations.md).

## Installierten Dienst prüfen

Unter Ubuntu nach der Dienstinstallation:

```bash
sudo systemctl status rufpass --no-pager
sudo journalctl -u rufpass -n 30 --no-pager
sudo /opt/rufpass/current/bin/rufpass validate
sudo /opt/rufpass/current/bin/rufpass status
```

`validate` liest die konfigurierte Telefonbuchumgebung und prüft die Erreichbarkeit
des Callmonitors. Es bestätigt keine Schreibrechte. `status` zeigt ausschließlich
Zähler aus der lokalen Datenbank; ohne Router-Abgleich sind sie kein Live-Zustand.

## Optionale Diagnoseumgebung

Bei Entwicklung oder Fehlersuche kann im Checkout eine eigene Umgebung verwendet werden:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install .
```

Zuvor die [Voraussetzungen](prerequisites.md) erfüllen. Die Projekt-`.venv` ist
unabhängig von der Dienstumgebung unter `/opt/rufpass`. Für Windows siehe
[manuelle Ausführung](windows.md); dort liegen die Programme unter `.venv\Scripts`.

## 1. Telefonbuchzugriff prüfen

```bash
.venv/bin/rufpass check --host fritz.box --user rufpass --phonebook Rufpass
```

Das Kennwort des angegebenen FRITZ!Box-Benutzers wird verdeckt abgefragt. Der Befehl
zeigt Buchnamen und IDs, zählt normale Kontakte im Zielbuch und weist interne
XML-Einträge getrennt aus. Er zeigt keine Kontaktnamen oder Telefonnummern.

`--phonebook` benötigt den exakten Namen; Namen mit Leerzeichen in Anführungszeichen
setzen. Falls `fritz.box` nicht erreichbar ist, die LAN-IPv4-Adresse mit `--host` angeben.
Ein leeres Buch kann zwölf interne Geräte-/Rundrufeinträge im XML enthalten, obwohl
die Kontaktansicht leer ist. Ein erfolgreicher Lesezugriff bestätigt noch keine Schreibrechte.

## 2. Callmonitor prüfen

```bash
.venv/bin/rufpass monitor --host fritz.box
```

Nach `Verbunden` eine eigene externe Nummer über die FRITZ!Box wählen. Erwartung:
`Wählversuch erkannt: [maskiert]`. Gesprächsannahme ist nicht erforderlich. Abbruch
mit Strg+C. Dieser Befehl speichert keine Anrufe und legt keine Freigaben an.
Der Callmonitor benötigt keine Benutzeranmeldung; für seine Freigabe und die
Sicherheitswirkung siehe [Voraussetzungen](prerequisites.md).

Für einen lokalen Vergleich kann `--show-numbers` ergänzt werden. Solche Ausgaben
enthalten echte Nummern und gehören nicht in öffentliche Fehlerberichte.

## Befehlsübersicht

| Befehl | Wirkung |
| --- | --- |
| `configure` | Legt einmalig die lokale Konfiguration an; keine Router-Änderung |
| `validate` | Prüft Dienstkonfiguration, Telefonbücher und Callmonitor lesend |
| `status` | Zeigt lokale Freigabezähler ohne Router-Zugriff |
| `run` | Verarbeitet Wählversuche und verwaltet eigene Freigaben |
| `check` | Zeigt Telefonbuch-IDs und Kontaktzahlen, ohne zu schreiben |
| `monitor` | Zeigt Live-Wählereignisse, ohne sie zu speichern |

## Fehler eingrenzen

- Telefonbuchzugriff scheitert: Host, Benutzer, dessen Kennwort und Telefonie-Rechte prüfen.
  Der Zugriff für Anwendungen ist normalerweise bereits aktiv; nur bei einer
  deaktivierten Einstellung ist eine Änderung in der Box nötig.
- Zielbuch fehlt: Exakten Namen und ID des zusätzlichen lokalen Buchs prüfen.
- Callmonitor nicht erreichbar: Aktivierung mit `#96*5*` und Netzwerkzugriff auf TCP 1012 prüfen.
- Dienst aktiv, aber keine Freigabe: Wiederkehrende Abgleichfehler im Journal prüfen.
  Bekannte, interne und ausgewählte Sondernummern werden nicht zusätzlich angelegt.

Vor dem Melden eines Fehlers die Version mit `rufpass --version` feststellen und
Modell, FRITZ!OS-Version, Betriebssystem sowie Schritte mit synthetischen Daten angeben.
Keine Kennwörter, Telefonbuch-Exporte oder Datenbanken veröffentlichen.
