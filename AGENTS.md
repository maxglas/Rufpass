# Rufpass

Python-Dienst für automatische Rückruf-Freigaben an einer FRITZ!Box.

## Arbeitsregeln

- Nur lokal committen. Nicht pushen, außer der Nutzer beauftragt den konkreten Push ausdrücklich.
- README.md und docs/ vor Implementierungsarbeiten lesen.
- Anwenderrelevante Änderungen im CHANGELOG.md unter „Unveröffentlicht“ mitpflegen. Bei einer neuen Paketversion die zugehörigen Einträge unter deren Versionsnummer und Datum übernehmen; keine unbestätigten Releases oder Gerätetests behaupten.
- Kleine Umsetzung ohne Webframework, MQTT oder Cloud-Abhängigkeit.
- check, monitor und validate bleiben lesend. Keine Schreibtest-/Beispielkontakt-Funktion ins Produkt aufnehmen.
- run verwaltet nur eigene, in SQLite nachverfolgte Kontakte im zusätzlichen lokalen Zielbuch.
- Keine persönlichen Kontakte löschen, keine kompletten Telefonbücher ersetzen oder wiederherstellen.
- Beim Löschen Kennung, UID, Nummer und persönliche Ergänzungen prüfen; manuelle Änderungen erhalten.
- Wählversuche vor Router-Schreibzugriffen persistent speichern; unklare Antworten vor Wiederholung abgleichen.
- Zugangsdaten, reale Telefonnummern und lokale Zustandsdateien nicht committen oder in normale Logs schreiben.
- FRITZ!Box-Rechte sind nicht auf ein Telefonbuch begrenzbar; Programmprüfung nicht als Router-ACL darstellen.
- Öffentliche Unterlagen an Anwender richten; private Infrastrukturdetails nicht versionieren.
- Tests: `python -m unittest discover -s tests -v` nach Paketinstallation.
- Installer nur unter Linux ausführen. Für Shell-Syntaxprüfung genügt `bash -n scripts/install.sh`.
- Keine erfolgreichen Geräte-, Linux-Dienst- oder CI-Tests behaupten, wenn nur lokale Simulationen vorliegen.

## Validierung

- FRITZ!Box 7690, FRITZ!OS 8.25; Ubuntu 24.04.4 LTS mit Python 3.12.3.
- Bestätigt: Positivliste berücksichtigt zweites lokales Buch, lesender TR-064-Zugriff,
  Live-Wählversuche, gezieltes Anlegen/Rücklesen/Entfernen und sichtbarer externer Testkontakt.
- Bestätigt: Leeres Zielbuch kann zusätzlich zwölf interne XML-Einträge liefern.
- Der Betreiber bestätigt am 27.10.2026 die systemd-Installation und den einwandfreien
  laufenden Ubuntu-Betrieb. Keine zusätzlichen Neustart- oder Langzeittests daraus ableiten.
- GitHub Actions für Commit 7dc92d6 unter Ubuntu und Windows erfolgreich.
