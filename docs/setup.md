# Einrichtungsstand

Für die vollständige Installation ist jetzt die [Betriebsanleitung](operations.md)
maßgeblich. Die früheren Einzeltests bleiben unter [Diagnose](diagnostics.md) dokumentiert.

## Bisher am Gerät bestätigt

- FRITZ!Box 7690, FRITZ!OS 8.25.
- Ubuntu 24.04.4 LTS, Python 3.12.3.
- Ein zweites lokales Telefonbuch wird von der bestehenden Positivliste berücksichtigt.
- Lesender Zugriff mit einem dedizierten Telefonie-Benutzer funktioniert.
- Der Callmonitor meldet den Wählbeginn.
- Ein gezielter Testkontakt lässt sich anlegen, zurücklesen und entfernen.
- Ein externer Testkontakt wurde in der Entwicklungsphase sichtbar gespeichert.
  Die damalige Schreibtest-Funktion ist aus dem aktuellen Produkt entfernt.
- Die zwölf zusätzlichen internen Einträge im XML sind keine normalen Kontakte.

## Automatischer Betrieb

Nummernnormalisierung, SQLite-Verwaltung, Verlängerung, gezieltes Entfernen,
Wiederanlauf und Ubuntu-Installer sind implementiert und lokal simuliert getestet.
Die Installation als systemd-Dienst und der laufende Betrieb auf Ubuntu wurden
vom Betreiber am 27.10.2026 als einwandfrei bestätigt. Daraus werden keine zusätzlich
einzeln bestätigten Neustart-, Langzeit- oder 365-Tage-Ablauftests abgeleitet.

GitHub Actions ist für Commit `7dc92d6` unter Ubuntu und Windows erfolgreich:
Paketinstallation, Unit-Tests und CLI-Start; unter Ubuntu zusätzlich Shell-Syntaxprüfung.
[Geprüfter Testlauf](https://github.com/maxglas/Rufpass/actions/runs/40492124052).

Unter Windows sind die simulierten Tests einschließlich der nativen Instanzsperre
lokal erfolgreich. Ein vollständiger Windows-Lauf mit der FRITZ!Box, andere Router
und Raspberry-Pi-Hardware sind nicht bestätigt.

Die Sprachentscheidung ist in [ADR-001](adr-001-python.md) dokumentiert.
