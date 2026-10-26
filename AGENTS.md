# Rufpass

Kleiner Hintergrunddienst für automatische Rückruf-Freigaben an einer FRITZ!Box.

## Bekannte Umgebung

- FRITZ!Box 7690, FRITZ!OS 8.25.
- Zielrechner: Lenovo ThinkCentre M910q im Heimnetz mit vorhandenen Caddy- und MQTT-Diensten.
- Lokale Entwicklung: C:\Projekte\Rufpass.
- Betriebssystem und Containerverwaltung des Zielrechners sind noch zu klären.

## Arbeitsregeln

- README.md und docs/ vor Implementierungsarbeiten lesen.
- Zuerst den manuellen Test aus docs/setup.md durchführen lassen: Einträge im zweiten
  Telefonbuch müssen von der vorhandenen Sperrregel berücksichtigt werden.
- Schlanke Umsetzung; Caddy, MQTT und eine Weboberfläche gehören nicht zum ersten Umfang.
- Ausschließlich ein dediziertes lokales Telefonbuch verwalten. Keine persönlichen Kontakte
  löschen, keine kompletten Telefonbücher ersetzen und keine Sperrregeln automatisch ändern.
- Kein FRITZ!Box-Recht pro Telefonbuch verfügbar: Die Programmbegrenzung ist keine Router-ACL.
- Zugangsdaten, echte Telefonnummern und lokale Zustandsdateien nicht committen.
- Schreibzugriffe erst nach Probelauf und mit kontrollierter Testnummer prüfen.
- Nicht angenommene ausgehende Anrufe über Live-Callmonitor erfassen, nicht über Anruflisten-Polling.
- Nicht behaupten, der Dienst sei einsatzbereit, bevor Schnittstellen und Verhalten am Gerät geprüft sind.
