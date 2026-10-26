# Erste Diagnose auf Ubuntu

Diese Version prüft Telefonbuchzugriff und Live-Wählereignisse. Sie kann keine
Telefonbucheinträge schreiben, Freigaben speichern oder abgelaufene Freigaben löschen.
Sie ist noch kein Dienst für den Dauerbetrieb.

## Installation

Die folgenden Befehle auf dem Ubuntu-Rechner im Heimnetz ausführen.
Ein vorhandenes Checkout zuerst mit `git pull --ff-only` aktualisieren;
ansonsten das Repository klonen. Bei einem privaten Repository ist GitHub-Anmeldung erforderlich.

```bash
git clone https://github.com/maxglas/Rufpass.git
cd Rufpass
sudo apt update
sudo apt install python3-venv
python3 -m venv .venv
.venv/bin/python -m pip install .
```

Nach späteren Quellcode-Updates erneut `.venv/bin/python -m pip install .` ausführen.
Das System-Python wird nicht mit Projektpaketen verändert.

## 1. Telefonbuchzugriff prüfen

Der FRITZ!Box-Benutzer benötigt die Berechtigung für Sprach-/Faxnachrichten,
FRITZ!App Fon und Anrufliste. Ein angelegter Benutzer allein bestätigt diese Rechte noch nicht.
Zusätzlich muss der Zugriff für Anwendungen (TR-064) zugelassen sein.

```bash
.venv/bin/rufpass check --host fritz.box --user rufpass --phonebook Rufpass
```

Falls das zweite Telefonbuch anders heißt, den **exakten Namen** hinter `--phonebook`
angeben; Namen mit Leerzeichen in Anführungszeichen setzen. Wenn `fritz.box` nicht
aufgelöst wird, die LAN-IP der FRITZ!Box hinter `--host` angeben.

Das Kennwort wird verdeckt im Terminal abgefragt, nicht als Kommandozeilenargument.
Die Ausgabe enthält Telefonbuchnamen und IDs sowie die Anzahl der Einträge im
Zielbuch. Sie enthält keine Kontaktnamen oder Telefonnummern.

Erwarteter Abschluss: `OK: Ziel-Telefonbuch lesbar, ID …, … Einträge.`
Dieser Test bestätigt **Leserechte**, noch keine Schreibrechte oder lokale Buchart.

## 2. Wählversuch ohne Annahme prüfen

An einem mit der FRITZ!Box verbundenen Telefon einmal `#96*5*` wählen, um den
Callmonitor zu aktivieren. Danach auf Ubuntu starten:

```bash
.venv/bin/rufpass monitor --host fritz.box
```

Sobald `Verbunden` erscheint, über die FRITZ!Box eine kontrollierte externe Nummer
anrufen und wieder auflegen, **ohne dass die Gegenstelle abnimmt**.
Erwartung: `Wählversuch erkannt: [maskiert]`.
Damit prüfen wir den für Rufpass entscheidenden Wählbeginn, unabhängig von CONNECT.

Bei Bedarf für den eigenen lokalen Vergleich:

```bash
.venv/bin/rufpass monitor --host fritz.box --show-numbers
```

Diese Option zeigt vollständige Zielnummern im Terminal. Keine solchen Ausgaben
in öffentliche Issues kopieren. Der Monitor benötigt kein Kennwort; er verwendet
einen separaten TCP-Zugang auf Port 1012. Abbruch mit Strg+C.

Interne Nummern und Wähl-Steuercodes werden in dieser Diagnose nicht ausgewertet.
Eine erkannte Zielnummer ist noch keine auf Rückrufbarkeit geprüfte Freigabe.

## Fehler und nächste Schritte

- `check` scheitert: Host, TR-064-Freigabe, Benutzer, Rechte und Kennwort prüfen.
- Zielbuch fehlt: Telefonbuchnamen in der Ausgabe mit `--phonebook` abgleichen.
- `monitor` scheitert: Callmonitor-Aktivierung und Erreichbarkeit von TCP 1012 prüfen.
- Verbindung bricht ab: Die Bibliothek versucht kurz erneut zu verbinden; danach
  beendet Rufpass die Diagnose mit Fehlerstatus. Verpasste Wählereignisse sind verloren.

Für die nächste Implementierung genügen Ziel-Telefonbuch-ID, erfolgreiche/fehlgeschlagene
Prüfung und die Information, ob der erfolglose Wählversuch erkannt wurde.
Kennwort und vollständige Telefonnummern bleiben lokal.

## Automatisierte Tests

```bash
.venv/bin/python -m unittest discover -s tests -v
```

Die Tests verwenden synthetische Daten und simulierte Schnittstellen. Sie ersetzen
keinen Gerätetest. Die Bibliotheks-API ist in der
[fritzconnection-Dokumentation](https://fritzconnection.readthedocs.io/en/latest/) beschrieben.
