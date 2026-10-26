# Rufpass

Kleiner Hintergrunddienst für automatische Rückruf-Freigaben an einer FRITZ!Box.

## Entwicklungsstand

- Erste Diagnoseversion: lesender Telefonbuchzugriff und Live-Wählereignisse; noch keine automatische Freigabe.
- Erstes vorgesehenes Testgerät: FRITZ!Box 7690, FRITZ!OS 8.25.
- Umsetzung in Python beschlossen; keine parallele .NET-Implementierung. Siehe docs/adr-001-python.md.
- Erstes Betriebsziel: Ubuntu 24.04.4 LTS mit Python 3.12.3; Dienstinstallation noch offen.
- Öffentliche Dokumentation an Anwender und Mitwirkende richten, nicht als internes Chatprotokoll verfassen.
- Persönliche Installationspfade und Infrastrukturdetails gehören nicht in versionierte Unterlagen.

## Arbeitsregeln

- Nur lokal committen. Nicht pushen, außer der Nutzer beauftragt den konkreten Push ausdrücklich.

- README.md und docs/ vor Implementierungsarbeiten lesen.
- Das Durchstellen einer Nummer aus dem zweiten lokalen Telefonbuch wurde am 26.10.2026
  vom Projektbetreiber bestätigt. Lesender TR-064-Zugriff auf das Zielbuch und die
  Live-Erkennung eines Wählversuchs wurden ebenfalls am Gerät bestätigt.
- check und monitor bleiben ausschließlich lesend. Der temporäre probe-Schreibtest
  wurde am Gerät einschließlich Anlegen, Rücklesen und Entfernen bestätigt.
- probe --keep lässt auf expliziten Aufruf einen sichtbaren Testkontakt mit lokal
  eingegebener externer Nummer bestehen; keine automatische Löschung oder Ablaufverwaltung.
  Der neue Sichttest ist noch am Gerät zu prüfen. Automatische Freigaben gibt es noch nicht.
- Tests: python -m unittest discover -s tests -v (nach Installation des Pakets).
- Schlanke Umsetzung; Caddy, MQTT und eine Weboberfläche gehören nicht zum ersten Umfang.
- Ausschließlich ein dediziertes lokales Telefonbuch verwalten. Keine persönlichen Kontakte
  löschen, keine kompletten Telefonbücher ersetzen und keine Sperrregeln automatisch ändern.
- Kein FRITZ!Box-Recht pro Telefonbuch verfügbar: Die Programmbegrenzung ist keine Router-ACL.
- Zugangsdaten, echte Telefonnummern und lokale Zustandsdateien nicht committen.
- Schreibzugriffe erst nach Probelauf und mit kontrollierter Testnummer prüfen.
- Nicht angenommene ausgehende Anrufe über Live-Callmonitor erfassen, nicht über Anruflisten-Polling.
- Nicht behaupten, der Dienst sei einsatzbereit, bevor Schnittstellen und Verhalten am Gerät geprüft sind.
