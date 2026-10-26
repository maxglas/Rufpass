# Erste Diagnose auf Ubuntu

`check` prüft den lesenden Telefonbuchzugriff und `monitor` die Live-Wählereignisse.
Beide Befehle verändern keine Einträge. Der getrennte Befehl `probe` führt einen
kontrollierten Schreibtest durch. Der neue automatische Dienst wird nach der
[Betriebsanleitung](operations.md) installiert. Diese Diagnosebefehle bleiben getrennt davon.

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
Die Ausgabe enthält Telefonbuchnamen und IDs sowie die Anzahl der normalen Kontakte
im Zielbuch. Interne Einträge der FRITZ!Box werden getrennt ausgewiesen.
Sie enthält keine Kontaktnamen oder Telefonnummern.

Erwarteter Abschluss: `OK: Ziel-Telefonbuch lesbar, ID …, … Kontakte.`
Darunter steht die Anzahl zusätzlicher interner Einträge im XML. Die Schnittstelle
kann interne Geräte- oder Rundrufnummern liefern, die in der normalen Kontaktansicht
nicht erscheinen. Ein leeres Buch kann daher 0 Kontakte und dennoch interne Einträge enthalten.
Die frühere Diagnose zählte beides ungetrennt als Einträge; das war irreführend.
Das heruntergeladene XML wird zusätzlich auf den erwarteten Telefonbuchnamen geprüft.
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

## 3. Schreibrechte gezielt prüfen

Voraussetzung: Zusätzliche lokale Telefonbuch-ID und Name wurden mit `check`
ermittelt. Der Probelauf mit `monitor` war erfolgreich. Vor dem ersten Schreibtest
das Ziel-Telefonbuch über die FRITZ!Box-Oberfläche sichern.

Das folgende Beispiel gilt für ein lokales Buch namens **Rufpass mit ID 1**:

```bash
.venv/bin/rufpass probe --phonebook-id 1 --phonebook Rufpass
```

Das Kennwort wird erneut verdeckt abgefragt. Der Befehl:

1. Prüft ID und Namen des Telefonbuchs; das Standardbuch mit ID 0 ist gesperrt.
2. Legt einen neuen Kontakt `Rufpass Schreibtest JJJJ-MM-TT <Zufallskennung>` an.
3. Verwendet ausschließlich die interne Rundrufnummer `**9`, ohne sie zu wählen.
4. Liest den Kontakt über die von der Box gelieferte UID zurück und prüft seine Identität.
5. Löscht ausschließlich diesen verifizierten Testkontakt und prüft, ob er entfernt ist.

Erwartung: `OK: Testkontakt angelegt, zurückgelesen und wieder entfernt.`

Bestehende Kontakte werden nicht bearbeitet. Bei Abbruch oder unklarer Antwort
wird das Anlegen nicht automatisch wiederholt. Ein Testkontakt kann dann zurückbleiben;
sein eindeutiger Name steht in der Ausgabe. Falls vorhanden, ausschließlich diesen
Kontakt im Zielbuch manuell entfernen. Es gibt keine pauschale Lösch- oder Wiederherstellungsfunktion.

## 4. Testkontakt sichtbar gespeichert lassen

Der ursprüngliche Schreibtest wurde auf einer FRITZ!Box 7690 mit FRITZ!OS 8.25
einschließlich Rücklesen und Entfernen erfolgreich ausgeführt. Für eine Sichtprüfung
gibt es einen zusätzlichen Modus:

```bash
.venv/bin/rufpass probe --phonebook-id 1 --phonebook Rufpass --keep
```

Der Befehl fragt zuerst eine **eigene externe Testnummer mit Vorwahl** ab,
beispielsweise die eigene Mobilfunknummer. Diese Nummer lokal eingeben; sie wird
nicht als Kommandozeilenargument benötigt und landet dadurch nicht in der Shell-Historie.
Danach wird das FRITZ!Box-Kennwort verdeckt abgefragt.

Es entsteht ein normaler Kontakt `Rufpass Schreibtest JJJJ-MM-TT <Zufallskennung>` mit der
eingegebenen Nummer. Nach dem Rücklesen bleibt er absichtlich gespeichert.
Die normale Telefonbuchansicht im Browser anschließend neu laden.

Erwartung: `OK: Testkontakt bleibt gespeichert.`

Es wird kein Anruf ausgelöst. Die Nummer ist durch den Telefonbucheintrag
für die bestehende Positivliste bekannt. Der Eintrag hat noch kein automatisches
Ablaufdatum und muss nach dem Test manuell gelöscht werden. Jeder erneute
Aufruf legt einen weiteren markierten Testkontakt an.

Dieser Modus verwendet eine externe Nummer, weil interne Nummern wie `**9`
in der Oberfläche gesondert behandelt werden und sich für die normale Kontaktansicht
nicht als Sichttest eignen. `monitor` bleibt weiterhin rein lesend.

## Welcher Befehl legt einen Kontakt an?

| Befehl | Verhalten |
| --- | --- |
| `check` | Liest und zählt Kontakte; keine Änderungen. |
| `monitor` | Zeigt Wählversuche an; legt keine Freigaben an. |
| `probe` | Legt einen temporären Testkontakt an und entfernt ihn wieder. |
| `probe --keep` | Lässt einen Testkontakt mit der lokal eingegebenen externen Nummer gespeichert. |

Nach `probe` ohne `--keep` ist das Zielbuch wieder leer, wenn es vorher leer war. Automatische Rückruf-Freigaben führt der neue Befehl `run` aus; siehe [Betrieb](operations.md).
Die installierte Paketversion lässt sich mit `.venv/bin/rufpass --version` prüfen.

## Fehler und nächste Schritte

- `check` scheitert: Host, TR-064-Freigabe, Benutzer, Rechte und Kennwort prüfen.
- Zielbuch fehlt: Telefonbuchnamen in der Ausgabe mit `--phonebook` abgleichen.
- `monitor` scheitert: Callmonitor-Aktivierung und Erreichbarkeit von TCP 1012 prüfen.
- Verbindung bricht ab: Die Bibliothek versucht kurz erneut zu verbinden; danach
  beendet Rufpass die Diagnose mit Fehlerstatus. Verpasste Wählereignisse sind verloren.

Für die nächste Implementierung genügt das Ergebnis des Schreibtests. Bei Fehlern
zusätzlich angeben, ob der Testkontakt zurückblieb und manuell entfernt wurde.
Kennwort und vollständige Telefonnummern bleiben lokal.

## Automatisierte Tests

```bash
.venv/bin/python -m unittest discover -s tests -v
```

Die Tests verwenden synthetische Daten und simulierte Schnittstellen. Sie ersetzen
keinen Gerätetest. Die Bibliotheks-API ist in der
[fritzconnection-Dokumentation](https://fritzconnection.readthedocs.io/en/latest/) beschrieben.
