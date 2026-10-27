# Sicherheitsprobleme melden

Bitte keine Zugangsdaten, echten Telefonnummern, Telefonbuch-Exporte, Datenbanken
oder unbereinigten Protokolle in öffentliche Issues hochladen.

Für eine vertrauliche Meldung auf GitHub **Security → Advisories → Report a
vulnerability** verwenden:
[Private Meldung für Rufpass](https://github.com/maxglas/Rufpass/security/advisories/new).
Dieser Meldeweg setzt voraus, dass private Sicherheitsmeldungen in den
Repository-Einstellungen eingeschaltet sind. Falls der Link nicht verfügbar ist,
ein öffentliches Issue ausschließlich mit der Bitte um einen vertraulichen
Kontaktweg eröffnen; noch keine Schwachstellendetails oder betroffenen Daten nennen.

Hilfreich sind Rufpass-Version, Betriebssystem, FRITZ!Box-Modell/FRITZ!OS-Version,
eine Beschreibung der Auswirkung und reproduzierbare Schritte mit synthetischen Daten.
Eine Reaktionszeit wird für dieses privat betreute Projekt nicht zugesichert.

## Unterstützter Stand

Sicherheitskorrekturen richten sich zunächst an den aktuellen Entwicklungsstand
auf `main`. Für ältere Vorabversionen gibt es keinen zugesagten Rückport.

## Betriebsgrenzen

Rufpass läuft im vertrauenswürdigen Heimnetz. Der Callmonitor liefert Anrufdaten
ohne eigene Benutzeranmeldung. FRITZ!Box-Benutzerrechte sind nicht auf das zusätzliche
Telefonbuch beschränkbar. Rufpass setzt diese Begrenzung in seinem Code um.
Die optionale Wikidata-Suche überträgt neue unbekannte Rufnummern an einen externen
Dienst; sie lässt sich mit `reverse_lookup = false` abschalten.

Konfiguration und SQLite-Zustand gehören nicht in das Repository. Vor Sicherungen
den Dienst stoppen und die Dateien geschützt aufbewahren. Siehe
[Betrieb und Sicherung](docs/operations.md).
