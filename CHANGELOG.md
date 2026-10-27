# Changelog

Hier stehen Änderungen, die für Anwender und Mitwirkende relevant sind.
Neue Einträge werden zunächst unter **Unveröffentlicht** gesammelt. Bei einer
neuen Version werden sie mit Versionsnummer und Datum übernommen.

Die Einträge ab 0.2.0 wurden aus der Git-Historie rekonstruiert. Die Datumsangaben
bezeichnen die Einführung des jeweiligen Versionsstands im Repository und sind
kein Nachweis eines veröffentlichten GitHub-Releases oder eines Gerätetests.

## Unveröffentlicht

### Dokumentation

- Freigegebenes, anonymisiertes Beispielbild des Rufpass-Telefonbuchs in die README aufgenommen.
- Changelog ab Version 0.2.0 ergänzt und seine laufende Pflege in den Projekt- und Beitragsregeln verankert.

## 0.2.5 – 2026-10-27

### Geändert

- Neue Telefonbuchkontakte verwenden den aufgelösten Namen oder die Rufnummer allein
  als Anzeigenamen. Rufpass-/Datumspräfix und „Name unbekannt“ entfallen; das
  Anlegedatum bleibt intern gespeichert. Bestehende Kontakte behalten ihre Namen.
- Schlüsselmethoden knapp dokumentiert und Betriebsdiagnose auf lesende Prüfungen ausgerichtet.
- Anleitung zum Anwendungszugriff (TR-064) präzisiert: Dieser ist normalerweise bereits aktiv.

### Behoben

- Ein leeres `<setup/>` im Router-XML führt nicht mehr dazu, dass Rufpass die Verwaltung
  eines eigenen Kontakts aufgibt. Persönliche Ergänzungen bleiben geschützt.
- Fehlerhafte oder fehlende HTTP-429-Wartezeitangaben der Namenssuche unterbrechen
  den Rückfall auf die Rufnummer nicht mehr.

### Entfernt

- Entwicklungsbefehl `probe`, seine Beispielkontakt-Funktionen und die dazugehörige Anleitung.

### Lizenz

- Apache-2.0 mit Commons Clause v1.0 als Projektlizenz angelegt und in Paket sowie
  Installer aufgenommen. Siehe [LICENSE](LICENSE) und [Erläuterung](docs/licensing.md).

## 0.2.4 – 2026-10-27

### Hinzugefügt

- Manuelle Python-Ausführung unter Windows mit nativer Instanzsperre und
  Konfigurations-/Datenbankpfaden im Benutzerprofil.
- Windows-Kurzanleitung und vorbereitete CI-Testmatrix für Linux und Windows.

### Geändert

- Kennwortabfrage direkt hinter den FRITZ!Box-Benutzernamen verschoben und eindeutig
  diesem Konto zugeordnet.
- README um konkrete Router-Vorbedingungen, Rechte und Sicherheitswirkung des
  Callmonitors ergänzt. Allgemeine Plattformanforderungen und tatsächlich getestete
  Kombination voneinander getrennt; Raspberry Pi als mögliche Plattform beschrieben.

## 0.2.3 – 2026-10-26

### Hinzugefügt

- Kostenlose optionale Namenssuche über Wikidata für neue, noch unbekannte Nummern.
  Nur eindeutige exakte Zuordnungen werden übernommen; Wartezeiten und Fehlerfälle
  führen zu einem Rückfall ohne Namen.

### Hinweise

- Die standardmäßig aktivierte Suche überträgt unbekannte Wählziele an Wikidata.
  Sie lässt sich mit `reverse_lookup = false` abschalten.
- Der Datenbestand ist kein vollständiges Telefonverzeichnis. Ein erfolgreicher
  Live-Namenstreffer war bei Einführung noch nicht bestätigt.

### Nachfolgende Dokumentations- und Installeränderungen

- Voraussetzungen, Installation, Konfiguration und Dienstprüfung klar getrennt;
  Erstinstallation aus einem neuen Checkout dokumentiert.
- Ubuntu-Systempakete in die Voraussetzungen verschoben; der Installer prüft die
  Laufzeit und richtet anschließend Rufpass und den Dienst ein.
- Hinweise zu Sicherheitsmeldungen, Veröffentlichung und Paket-URLs ergänzt.

## 0.2.2 – 2026-10-26

### Geändert

- Neue Kontakte erhielten das lesbare Muster `Rufpass <Datum> Name unbekannt`.
  Anzeigename und interne Kennung getrennt gespeichert; gleiche Namen für
  unterschiedliche Nummern bleiben unterscheidbar.
- Bestehende Kontaktkennungen und Wiederanlauf nach unklaren Schreibantworten berücksichtigt.

### Tests

- Den bereits vorhandenen Abgleich über alle Telefonbücher einschließlich
  unterschiedlicher Rufnummernschreibweisen und unlesbarer Bücher zusätzlich abgesichert.

## 0.2.1 – 2026-10-26

### Geändert

- Datum im Namen neu angelegter Kontakte ergänzt.
- Standardgültigkeit von 30 auf 365 Tage seit dem letzten eigenen Wählversuch erhöht.
  Explizit gespeicherte Konfigurationswerte bleiben erhalten.

## 0.2.0 – 2026-10-26

### Hinzugefügt

- Automatische Rückruf-Freigaben ab dem ausgehenden Wählversuch über den Callmonitor.
- Abgleich aller Telefonbücher vor einer neuen Anlage und Normalisierung externer Nummern.
- SQLite-Verwaltung mit Verlängerung bestehender Freigaben, Ablaufbereinigung eigener
  Kontakte und Erhalt manuell veränderter Kontakte.
- Wiederanlauf mit Abgleich unklarer Schreibantworten und Schutz gegen doppelte Instanzen.
- Befehle `configure`, `validate`, `status` und `run` sowie ein Ubuntu/systemd-Installer.
- Simulierte Tests und vorbereiteter GitHub-Actions-Workflow.

### Hinweise

- Die grundlegenden Telefonbuchaktionen und Callmonitor-Ereignisse waren am Gerät
  bestätigt. Die vollständige Dienstinstallation und der Dauerbetrieb blieben separat zu prüfen.
