# Rufpass auf Ubuntu betreiben

## Voraussetzungen

Zuerst [FRITZ!Box und Ubuntu vorbereiten](prerequisites.md). Dazu gehören das
zusätzliche lokale Telefonbuch, die passende Rufsperre, der FRITZ!Box-Benutzer,
TR-064, der Callmonitor sowie die Systempakete `git`, `python3`, `python3-venv`
und `ca-certificates`. Die Version von Python muss mindestens 3.12 sein.
Diese Vorbereitung ist von der Installation unseres Codes getrennt.

## Rufpass installieren

### Quellcode bereitstellen

Bei einer neuen Installation:

```bash
git clone https://github.com/maxglas/Rufpass.git
cd Rufpass
```

Bei einem bestehenden Checkout stattdessen in dieses Verzeichnis wechseln und
`git pull --ff-only` ausführen. Solange das Repository privat ist, sind GitHub-Anmeldedaten
erforderlich, etwa SSH oder ein Zugriffstoken. Das normale GitHub-Kennwort funktioniert
für Git über HTTPS nicht. Zugangsdaten nicht in die Repository-URL schreiben.

### Installer starten

Im lokalen Checkout:

```bash
sudo bash scripts/install.sh
```

Der Installer benötigt Administratorrechte für Systembenutzer, Installationsverzeichnisse
und systemd. Er installiert keine Ubuntu-Pakete, führt kein `git pull` aus und benötigt
selbst kein GitHub-Token. Fehlende Laufzeitvoraussetzungen werden vor der Einrichtung gemeldet.

Bei der Ersteinrichtung folgende Angaben im Terminal eingeben:

| Angabe | Vorgabe / Bedeutung |
| --- | --- |
| FRITZ!Box | `fritz.box`; alternativ LAN-IPv4-Adresse |
| FRITZ!Box-Benutzer | `rufpass`; das Konto in der FRITZ!Box |
| Kennwort dieses Benutzers | Direkt nach dem Namen, verdeckte Eingabe; kein allgemeines FRITZ!Box-Kennwort |
| Telefonbuchname | `Rufpass`; exakt wie in der Oberfläche |
| Telefonbuch-ID | `1`; bei abweichender ID den tatsächlichen Wert verwenden |
| Landesvorwahl | `49`, ohne `+` oder `00` |
| Ortsvorwahl | Eigene Ortsvorwahl, beispielsweise `030`; für die Speicherung wird die führende Null entfernt |
| Gültigkeit | `365` Tage seit dem letzten eigenen Wählversuch |

Enter übernimmt eine angezeigte Vorgabe. Kennwort und tatsächliche Nummern bleiben
im lokalen Terminal und gehören nicht in Issues oder Screenshots. Die standardmäßig
aktive Wikidata-Suche wird weiter unten erläutert und ist abschaltbar.

Der Installer führt danach ohne weitere Diagnose-Einzelschritte aus:

1. Einen eigenen Linux-Benutzer `rufpass` und geschützte Daten-/Konfigurationsverzeichnisse anlegen.
2. Eine neue Python-Umgebung unter `/opt/rufpass/releases/` erstellen und den lokalen
   Rufpass-Code samt `fritzconnection` und dessen Abhängigkeiten per pip installieren.
   Das System-Python und eine vorhandene Projekt-`.venv` erhalten keine Rufpass-Pakete.
3. Die Konfiguration unter `/etc/rufpass/config.toml` speichern, falls sie noch nicht
   existiert. Vorhandene Werte werden bei Updates nicht erneut abgefragt oder überschrieben.
4. Alle Telefonbücher lesend prüfen und die TCP-Verbindung zum Callmonitor testen.
   Dieser Schritt bestätigt keine Schreibrechte und legt keinen Testkontakt an.
5. Den systemd-Dienst installieren, `/opt/rufpass/current` umschalten und Autostart aktivieren.
6. Den Dienst starten und prüfen, ob systemd ihn als aktiv meldet. Ab dann werden neue
   Wählversuche automatisch als Freigaben verarbeitet. Alte Anrufe werden nicht nachgetragen.

Ein vorhandener Linux-Benutzer namens `rufpass` wird verwendet; vorab prüfen, dass
dieser Name nicht anderweitig belegt ist. Es handelt sich nicht um den FRITZ!Box-Benutzer.
Der Installer richtet keine Rufsperre und keine Router-Benutzerrechte ein.

## Updates

Im vorhandenen Checkout:

```bash
git pull --ff-only
sudo bash scripts/install.sh
```

Bei Updates bleibt die bisherige Version während des Paketbaus aktiv. Nach lesender
Schnittstellenprüfung wird der Dienst auf die neue Umgebung umgeschaltet und neu gestartet.
Bei einem sofort erkannten Startfehler wird, soweit vorhanden, die vorherige
Programmversion wieder ausgewählt. Das ist keine vollständige Wiederherstellung von
Datenbank, Konfiguration oder Dienstdefinition. Alte Umgebungen werden nicht automatisch
gelöscht. Die frühere Projekt-`.venv` wird durch den Dienstinstaller nicht aktualisiert.

## Erfolg prüfen

Die vollständige Erstinstallation und der Dauerbetrieb sind am Gerät noch zu bestätigen.
Die folgenden Prüfungen sind der noch offene End-to-End-Test.

```bash
sudo systemctl status rufpass --no-pager
sudo systemctl is-enabled rufpass
sudo journalctl -u rufpass -n 30 --no-pager
```

Erwartung: `active (running)`, `enabled` und die Logmeldung `Callmonitor verbunden`.
Wiederkehrende Telefonbuchfehler müssen zuerst behoben werden; ein laufender Prozess
allein bestätigt noch keine funktionierende Router-Verbindung.

1. Über ein mit der FRITZ!Box verbundenes Telefon eine eigene externe Testnummer
   wählen, die in keinem Telefonbuch steht. Gesprächsannahme ist nicht erforderlich.
2. Den neuen Kontakt im zusätzlichen Telefonbuch prüfen und von der Testnummer zurückrufen.
   Beim erneuten Wählen derselben Nummer darf kein zweiter Kontakt entstehen.
3. `sudo systemctl restart rufpass` ausführen, Status/Logs erneut prüfen und die
   Testnummer noch einmal wählen. Der bestehende Kontakt muss weiterverwendet werden.
   Optional später einen Ubuntu-Neustart nutzen, um den tatsächlichen Autostart zu prüfen.

Es gibt keine verpflichtende Folge von `check`, `monitor` und `probe`: Diese Befehle
sind für die gezielte Fehlersuche gedacht. Die Ablaufbereinigung wird bisher durch
Simulationen geprüft; eine echte 365-Tage-Laufzeit ist nicht bestätigt.

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

Bei neuen unbekannten Nummern ist eine kostenlose Rückwärtssuche über den
[Wikidata Query Service](https://www.wikidata.org/wiki/Help:Data_access) aktiviert.
Die normalisierte Rufnummer und die öffentliche IP werden an `query.wikidata.org`
übertragen. Es werden keine FRITZ!Box-Zugangsdaten, lokalen Telefonbuchnamen oder
anderen Kontakte übertragen. Anmeldung und API-Schlüssel sind nicht erforderlich.
Die [strukturierten Daten stehen unter CC0](https://www.wikidata.org/wiki/Wikidata:Licensing).

Nur eine exakte Rufnummernzuordnung zu einem einzigen benannten Eintrag wird übernommen.
Direkt als Personen klassifizierte Einträge werden ausgeschlossen. Die Abdeckung
ist auf die in Wikidata erfassten Nummern begrenzt, vor allem Organisationen und
öffentliche Einrichtungen; kleine Betriebe und Privatnummern fehlen häufig.
Mehrdeutige Ergebnisse, fehlende Namen, ungültige Antworten oder Fehler ergeben
`Name unbekannt`. Eine Anfrage hat drei Sekunden Netzwerk-Timeout. Das ist keine
harte Obergrenze für DNS-Auflösung oder einen langsam tröpfelnden Antwortstrom.
Es gibt höchstens eine Anfrage pro Sekunde; bei HTTP 429 wird mindestens eine Minute
pausiert. Während einer Pause erhalten neue Kontakte sofort `Name unbekannt`.
Das Suchergebnis wird vor dem Router-Schreibzugriff gespeichert und beim Wiederanlauf
weiterverwendet. Bestehende Kontakte werden nicht nachträglich nachgeschlagen oder umbenannt.

Zum Abschalten in `/etc/rufpass/config.toml` setzen und den Dienst neu starten:

```toml
reverse_lookup = false
```

Ohne diese Einstellung ist die Suche standardmäßig eingeschaltet, auch bei älteren Konfigurationen.
Mit `reverse_lookup = true` kann sie wieder aktiviert werden.

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
Eine Änderung wirkt beim nächsten eigenen Wählversuch auf die betreffende Freigabe; vorhandene Ablaufzeiten werden nicht
pauschal umgeschrieben. Die Ortsvorwahl steht in `area_code` ohne führende 0, die
Landesvorwahl in `country_code` ohne `+` oder `00`.

Host, Telefonbuch-ID und -Name sind an die Datenbank gebunden. Ein anderer Zielrouter
oder ein anderes Zielbuch benötigt eine separate Datenbank, damit bestehende
Freigaben nicht versehentlich in einem anderen Buch bearbeitet werden.

Alle Konfigurationsfelder entsprechen den oben abgefragten Angaben. Zusätzlich:

| Schlüssel | Standard | Bedeutung |
| --- | --- | --- |
| `database` | `/var/lib/rufpass/state.sqlite3` | Lokale Freigaben; beim mitgelieferten Dienst im freigegebenen Zustandsverzeichnis belassen |
| `reverse_lookup` | `true` | Neue unbekannte Nummern bei Wikidata suchen; `false` verhindert diese Übertragung |

Eine neue Eingabe über `configure` ersetzt keine bestehende Datei. Änderungen daher
mit `sudoedit` vornehmen und den Dienst anschließend neu starten. Eine andere
Datenbank außerhalb von `/var/lib/rufpass` benötigt angepasste Verzeichnisrechte
und eine passende Freigabe in der systemd-Dienstdefinition.

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
