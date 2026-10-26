# An Rufpass mitwirken

Rufpass befindet sich in der Konzeptphase. Besonders hilfreich sind derzeit
reproduzierbare Erkenntnisse zur Rufbehandlung und zu den Telefonie-Schnittstellen.

## Gerätetest dokumentieren

Bitte Modell, FRITZ!OS-Version, relevante Rufbehandlung und die Schritte des Tests
angeben. Erwartetes und tatsächliches Verhalten getrennt beschreiben. Das Vorgehen
für den Test mit zwei Telefonbüchern steht in [docs/setup.md](docs/setup.md).

Nur eigene oder ausdrücklich für den Test freigegebene Telefonnummern verwenden.
Keine echten Nummern, Telefonbuch-Exporte, Zugangsdaten oder unbereinigten Logs veröffentlichen.

## Änderungen vorschlagen

Den konkreten Anwendungsfall beschreiben. Für Implementierungen den Entwurf in
[docs/architecture.md](docs/architecture.md) beachten. Kleine Änderungen mit klarer
Begründung und passenden Tests sind leichter zu prüfen.

Tests nach Installation: `python -m unittest discover -s tests -v`. Sie verwenden
synthetische Daten und simulierte Schnittstellen. Gerätetests und automatisierte
Tests ausdrücklich unterscheiden. Die aktuelle Diagnose enthält keine Schreibfunktionen.
Die Lizenz für öffentliche Beiträge muss vor der öffentlichen Freigabe festgelegt werden.
