# An Rufpass mitwirken

Rufpass wird zunächst für Ubuntu und deutsche Rufnummernkonventionen entwickelt.
Andere Geräte und Plattformen bitte nur als unterstützt dokumentieren, wenn sie
reproduzierbar getestet wurden.

## Entwicklung und Tests

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e .
.venv/bin/python -m unittest discover -s tests -v
bash -n scripts/install.sh
```

Tests verwenden synthetische Daten, temporäre SQLite-Dateien und simulierte
Schnittstellen. Der Linux-Sperrentest wird auf anderen Plattformen übersprungen.
Der Workflow unter `.github/workflows/tests.yml` führt die Suite unter Linux aus;
erst ein tatsächlicher Workflow-Lauf bestätigt dessen Ergebnis.

Änderungen klein halten und die Folgen für Wiederanlauf, eindeutige Zuordnung und
manuelle Kontakte prüfen. Niemals Buch-Import oder Buch-Wiederherstellung als
Abkürzung für Einzeländerungen verwenden.

## Sicherheitsprobleme

Vertrauliche Schwachstellen nach [SECURITY.md](SECURITY.md) melden, nicht mit
Zugangsdaten oder echten Anrufdaten in einem öffentlichen Issue.

## Fehler melden

Modell, FRITZ!OS-Version, Rufpass-Version, Betriebssystem und reproduzierbare Schritte
angeben. Erwartetes und tatsächliches Verhalten unterscheiden. Gerätetests und
simulierte Tests getrennt kennzeichnen.

Keine echten Nummern, Telefonbuch-Exporte, Konfigurationsdateien, Datenbanken,
Zugangsdaten oder unbereinigten Logs veröffentlichen. Für Tests nur eigene oder
ausdrücklich dafür freigegebene Rufnummern verwenden.

Die Lizenz für öffentliche Beiträge muss vor der öffentlichen Freigabe festgelegt werden.
