# Rufpass auf Ubuntu betreiben

## Installation und Updates

Im vertrauenswürdigen lokalen Checkout:

```bash
git pull --ff-only
sudo bash scripts/install.sh
```

Der Installer benötigt Administratorrechte für Paketinstallation, Systembenutzer
und systemd. Er führt nicht selbst `git pull` aus und benötigt kein GitHub-Token.
Bei der ersten Installation werden Host, Telefonie-Benutzer, zusätzliches lokales
Telefonbuch, Landes-/Ortsvorwahl und Gültigkeit abgefragt. Das Kennwort wird verdeckt
eingegeben. Alle Zugangsdaten bleiben auf dem Server.

Voreinstellung: `fritz.box`, Benutzer `rufpass`, Buch `Rufpass`, ID 1,
Landesvorwahl 49 und 365 Tage Gültigkeit. Die Ortsvorwahl muss zur überwachten
FRITZ!Box passen, damit lokale Wählziele korrekt zugeordnet werden.

Der Installer erzeugt eine neue Python-Umgebung unter `/opt/rufpass/releases/`,
prüft lesenden Telefonbuchzugriff und Erreichbarkeit des Callmonitors und schaltet
anschließend `/opt/rufpass/current` auf diese Version. Bei Updates bleibt die bisherige
Version während des Paketbaus aktiv. Anschließend wird der Dienst neu gestartet.
Bei einem sofort erkannten Startfehler wird, soweit vorhanden, die vorherige
Programmversion wieder ausgewählt. Alte Umgebungen werden nicht automatisch gelöscht.

Ein vorhandener Benutzer namens `rufpass` wird verwendet; auf einem gemeinsam
verwalteten Server vorher prüfen, ob dieser Name bereits anderweitig belegt ist.
Dieser Installer richtet keine Sperrregel ein und verändert keine Router-Benutzerrechte.

## Erfolg prüfen

```bash
sudo systemctl status rufpass --no-pager
sudo journalctl -u rufpass -n 30 --no-pager
```

Nach einem eigenen Wählversuch zu einer noch unbekannten normalen Nummer erscheint
ein Kontakt `Rufpass JJJJ-MM-TT Name unbekannt` im zusätzlichen Telefonbuch. Weder
Gesprächsannahme noch eine bestimmte Gesprächsdauer sind erforderlich. Das Datum
bezeichnet den ersten erfassten Wählversuch dieser Freigabe in der lokalen Zeitzone
des Servers. Bei erneutem Wählen bleibt dieses Datum erhalten; die Gültigkeit wird
ab dem neuen Wählversuch verlängert. Bestehende Einträge behalten ihren Namen.
Vor jeder neuen Anlage liest Rufpass alle von der FRITZ!Box bereitgestellten Telefonbücher
und vergleicht normalisierte Nummern. Ist ein Buch nicht lesbar, wird keine neue
Freigabe angelegt. Die Prüfung und das Schreiben sind keine atomare Router-Operation;
eine gleichzeitig manuell hinzugefügte Nummer kann daher trotzdem eine Dublette erzeugen.

Eine externe Rückwärtssuche ist noch nicht angebunden. Derzeit wird kein Wählziel an
einen Auskunftsanbieter übertragen. Für die automatische Namensübernahme muss zunächst
ein geeigneter Anbieter mit passendem API-Zugang festgelegt werden.

Wichtig: Bereits vorhandene Kontakte, auch `Rufpass Schreibtest …` aus `probe --keep`,
werden nicht zusätzlich angelegt oder mit einem Ablaufdatum versehen. Für einen
End-to-End-Test einen solchen Testkontakt zuerst manuell löschen und die kontrollierte
Testnummer erneut vom Festnetz aus wählen. Danach vom Testanschluss zurückrufen.

## Dateien

| Pfad | Zweck |
| --- | --- |
| `/etc/rufpass/config.toml` | Konfiguration und FRITZ!Box-Kennwort; root:rufpass, Modus 640 |
| `/var/lib/rufpass/state.sqlite3` | Eigene Freigaben, Nummern, Kennungen und Ablaufzeiten |
| `/var/lib/rufpass/state.sqlite3.lock` | Sperre gegen eine zweite Dienstinstanz |
| `/opt/rufpass/current` | Symlink auf die aktuelle isolierte Python-Umgebung |
| `/etc/systemd/system/rufpass.service` | Dienstdefinition |

Konfiguration und SQLite-Datei nicht in Git, öffentliche Issues oder Screenshots übernehmen.
Der Dienst läuft ohne root-Rechte. Der Installer muss als root laufen.

## Konfiguration ändern

```bash
sudoedit /etc/rufpass/config.toml
sudo systemctl restart rufpass
```

`ttl_days` ist standardmäßig 365 und kann zwischen 1 und 365 liegen. Bereits
gespeicherte Konfigurationen behalten ihren Wert; für ein Jahr dort `ttl_days = 365` setzen.
Eine Änderung wirkt beim nächsten eigenen
Wählversuch auf die betreffende Freigabe; vorhandene Ablaufzeiten werden nicht
pauschal umgeschrieben. Die Ortsvorwahl steht in `area_code` ohne führende 0, die
Landesvorwahl in `country_code` ohne `+` oder `00`.

Host, Telefonbuch-ID und -Name sind an die Datenbank gebunden. Ein anderer Zielrouter
oder ein anderes Zielbuch benötigt eine separate Datenbank, damit bestehende
Freigaben nicht versehentlich in einem anderen Buch bearbeitet werden.

## Anhalten und lokaler Status

```bash
sudo systemctl stop rufpass
sudo systemctl start rufpass
sudo /opt/rufpass/current/bin/rufpass status
```

Der lokale Status enthält nur Zähler. Er ersetzt keinen Live-Abgleich mit der Box.
Beim Stoppen bleiben Telefonbucheinträge erhalten; sie werden erst nach einem
erneuten Start weiter verwaltet.

## Wiederanlauf und Fehler

- Callmonitor-Ausfall: Der Dienst versucht erneut zu verbinden. In der Zwischenzeit
  nicht empfangene Wählereignisse können nicht rekonstruiert werden.
- TR-064-Ausfall: Bereits erfasste Wählversuche bleiben in SQLite vorgemerkt. Der
  Abgleich wird nach 30 Sekunden erneut versucht.
- Unklare Antwort beim Anlegen: Die vorab gespeicherte Kennung wird beim nächsten
  Abgleich gesucht, bevor ein weiterer Eintrag angelegt wird. Bei widersprüchlichen
  oder doppelten Kennungen wird der Kontakt nicht verändert.
- Volles Zielbuch: Ab 300 normalen XML-Kontakten wird konservativ nicht weiter
  angelegt. Frühere Geräte- oder globale Kapazitätsgrenzen können ebenfalls API-Fehler
  verursachen. Bestehende Kontakte werden nicht verdrängt.
- Manuell veränderter Kontakt: Rufpass gibt seine Verwaltung ab und erhält ihn.
- Manuell gelöschter Kontakt: Wird nicht laufend nachgefüllt. Ein neuer eigener
  Wählversuch kann erneut eine Freigabe erzeugen.
- Falsche Zugangsdaten: `/etc/rufpass/config.toml` mit `sudoedit` korrigieren.
- Nach einem Update weiterhin alte Diagnose: Der installierte Dienst verwendet
  `/opt/rufpass/current`; die frühere Projekt-`.venv` wird dadurch nicht aktualisiert.

Normale Logs enthalten Fehlerklassen, keine vollständigen Serverantworten oder Nummern.
Router-Zugriff erfolgt lokal über die vorhandenen FRITZ!Box-Schnittstellen; es wird
kein öffentlicher Web-Port benötigt.

## Sicherung und Deinstallation

Für eine konsistente Sicherung den Dienst stoppen, Konfiguration und Datenbank
geschützt sichern und anschließend wieder starten. Die Datenbank ist nötig, um
eigene vorhandene Freigaben nach einem Restore weiter zu verwalten.

Zum Deaktivieren:

```bash
sudo systemctl disable --now rufpass
```

Telefonbucheinträge, Konfiguration und Zustandsdatei bleiben dabei bewusst erhalten.
Die dauerhafte Entfernung dieser Daten ist ein eigener manueller Schritt. Ohne
Zustandsdatei übernimmt eine neue Installation alte Einträge nicht automatisch.
