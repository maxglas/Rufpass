# Vorabtest und nächste Schritte

## 1. Sperrregel manuell prüfen

1. Aktuelle Telefonbücher sichern und die vorhandene Sperrregel dokumentieren.
2. Unter Telefonie → Telefonbuch ein zusätzliches lokales Telefonbuch anlegen.
3. Eine kontrollierte Testnummer verwenden, die in keinem anderen Telefonbuch steht.
4. Mit aktivierter bestehender Sperrregel von dieser Nummer anrufen: zunächst muss sie blockiert sein.
5. Nummer ausschließlich im neuen Telefonbuch speichern und erneut anrufen.
6. Erwartung: Der zweite Anruf klingelt. Falls nicht, erst die Rufbehandlung klären.
7. Testeintrag wieder entfernen und erneut prüfen.

Keine Produktivautomatisierung aktivieren, bevor dieser Test erfolgreich war.

## 2. Lenovo-Umgebung klären

- Betriebssystem und vorhandene Docker-/Compose-Nutzung.
- Gewünschter Installationspfad und übliche Ablage von Konfiguration und Daten.
- Erreichbarkeit der Box aus dem späteren Dienst bzw. Container.

## 3. FRITZ!Box vorbereiten

- Eigener Benutzer mit Telefonie-Rechten; keine allgemeinen Einstellungsrechte und kein Internetzugriff.
- Zugriff für Anwendungen (TR-064) aktivieren, soweit noch nicht aktiv.
- Callmonitor mit einem angeschlossenen Telefon über `#96*5*` aktivieren.
  Mit `#96*4*` kann er wieder deaktiviert werden. Bestehende Nutzer des Monitors beachten.
- Ziel-Telefonbuch-ID und erforderliche Schnittstellen am Gerät ermitteln.
- Zugangsdaten nur lokal hinterlegen, nicht in Chat, Repository oder Beispielkonfiguration.

## 4. Implementierung

- Live-Ereignisse zunächst nur lokal prüfen.
- Nummernnormalisierung, Freigabelogik und gezieltes Schreiben implementieren.
- Kleine Tests mit synthetischen Telefonnummern und simulierten Schnittstellen.
- Probelauf, anschließend kontrollierter Test am Gerät und erst dann Dauerbetrieb.

Projektname: Rufpass. Lokales Projektverzeichnis: `C:\Projekte\Rufpass`.

Offen: GitHub-Repository, lokale Projektregistrierung, Lenovo-Umgebung und
gewünschte Gültigkeit der Freigaben.
