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
Schnittstellen. Der Sperrentest prüft die native Implementierung des jeweiligen Systems.
Der Workflow unter `.github/workflows/tests.yml` ist für Linux und Windows vorbereitet;
erst ein tatsächlicher Workflow-Lauf bestätigt dessen Ergebnis.

Änderungen klein halten und die Folgen für Wiederanlauf, eindeutige Zuordnung und
manuelle Kontakte prüfen. Niemals Buch-Import oder Buch-Wiederherstellung als
Abkürzung für Einzeländerungen verwenden.

## Changelog pflegen

Anwenderrelevante Änderungen im [Changelog](CHANGELOG.md) unter **Unveröffentlicht**
eintragen: neue Funktionen, Verhaltensänderungen, Fehlerkorrekturen, entfernte
Funktionen sowie wichtige Installations-, Dokumentations- und Lizenzänderungen.
Kurz die Auswirkung beschreiben; reine interne Aufräumarbeiten brauchen keinen Eintrag.

Bei einer neuen Paketversion die passenden Einträge in einen Abschnitt mit derselben
Versionsnummer wie in `pyproject.toml` und dem Datum `JJJJ-MM-TT` verschieben.
Neue Einträge stehen oben. Nur tatsächlich bestätigte Test- und Veröffentlichungsstände
nennen; ein Versionscommit allein bestätigt kein GitHub-Release.

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

Beiträge werden unter der Projektlizenz Apache-2.0 mit Commons Clause v1.0
eingereicht. Mit einem Beitrag bestätigst du, dafür die nötigen Rechte zu haben.
Die maßgeblichen Bedingungen stehen in [LICENSE](LICENSE); Abhängigkeiten behalten ihre Lizenzen.
