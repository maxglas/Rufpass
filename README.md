# Rufpass

Selbst gewählte Telefonnummern automatisch für Rückrufe an der FRITZ!Box freigeben.

Lokales Projektverzeichnis: `C:\Projekte\Rufpass`.

## Status

Projektvorbereitung. Noch kein lauffähiger Dienst und keine Änderungen an der FRITZ!Box.
Vor der Implementierung muss ein manueller Test bestätigen, dass die bestehende
Regel „Nicht im Telefonbuch“ auch ein zusätzliches lokales Telefonbuch berücksichtigt.

## Ausgangslage

- FRITZ!Box 7690 mit FRITZ!OS 8.25.
- Eingehende Anrufe ohne Telefonbucheintrag werden bereits blockiert.
- Ein Lenovo ThinkCentre M910q läuft im Heimnetz; Caddy und MQTT sind vorhanden.
- Betriebssystem, Containerverwaltung und Installationspfad auf dem Lenovo sind noch offen.

## Geplantes Verhalten

1. Den Wählbeginn externer Anrufe über den Callmonitor erkennen, auch ohne Gesprächsannahme.
2. Die Zielnummer normalisieren und mit vorhandenen Kontakten abgleichen.
3. Neue Nummern über TR-064 in ein eigenes lokales Telefonbuch schreiben.
4. Den letzten eigenen Wählversuch lokal speichern; vorgeschlagene Gültigkeit: 30 Tage.
5. Nur automatisch angelegte Einträge nach Ablauf entfernen. Persönliche Kontakte bleiben erhalten.

Der Dienst verarbeitet ausschließlich Telefonate über diese FRITZ!Box. Ein Rückruf
von einer anderen oder unterdrückten Nummer wird dadurch nicht freigegeben.

## Aufbau

Ein kleiner Python-Hintergrunddienst auf dem Lenovo verbindet sich mit dem
Callmonitor der FRITZ!Box (TCP 1012). Änderungen am Telefonbuch erfolgen getrennt
davon über die authentifizierte TR-064-Schnittstelle. SQLite speichert Freigaben,
deren Ablaufzeit und die IDs der vom Dienst angelegten Einträge.

Falls Docker Compose vorhanden ist, wird der Dienst als eigener Container mit
persistentem Datenverzeichnis betrieben; andernfalls ist unter Linux systemd möglich.
Caddy und MQTT sind für die Kernfunktion nicht erforderlich.

## Rechte und Grenzen

Ein eigener FRITZ!Box-Benutzer benötigt Telefonie-Rechte (Phone). Diese sind nicht
auf ein einzelnes Telefonbuch begrenzbar. Die Einschränkung auf die Ziel-Telefonbuch-ID
wird im Programm umgesetzt, nicht durch eine entsprechende Berechtigung der Box.
Keine Zugangsdaten oder echten Telefonnummern in Git speichern.

Der Callmonitor liefert Live-Ereignisse. Während eines Ausfalls verpasste erfolglose
Wählversuche lassen sich nicht zuverlässig aus der normalen Anrufliste nachholen.
Bereits angelegte Telefonbucheinträge bleiben bei einem Dienstausfall bestehen.

## Weiterführend

- [Architektur und Implementierungsgrenzen](docs/architecture.md)
- [Manueller Vorabtest und nächste Schritte](docs/setup.md)
- [Quellen](docs/research.md)
