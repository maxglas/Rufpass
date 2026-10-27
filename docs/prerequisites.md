# Voraussetzungen für Rufpass

Diese Schritte bereiten FRITZ!Box und Ubuntu vor. Rufpass wird erst anschließend
nach der [Installationsanleitung](operations.md#rufpass-installieren) installiert.

## FRITZ!Box vorbereiten

1. Unter **Telefonie → Telefonbuch** ein zusätzliches **lokales** Telefonbuch
   anlegen, beispielsweise `Rufpass`. Das normale persönliche Telefonbuch bleibt
   bestehen. Rufpass benötigt den exakten Namen und die ID des zusätzlichen Buchs;
   das Standardbuch mit ID 0 ist als Schreibziel ausgeschlossen.
2. Die gewünschte Rufsperre für Anrufer einrichten, die nicht im Telefonbuch stehen.
   Mit einer eigenen externen Testnummer prüfen, dass ein Eintrag im zusätzlichen
   Buch tatsächlich einen Rückruf erlaubt. Rufpass richtet keine Sperrregeln ein.
3. Unter **System → FRITZ!Box-Benutzer** einen eigenen Benutzer, etwa `rufpass`,
   mit den Rechten für Sprach-/Faxnachrichten, FRITZ!App Fon und Anrufliste anlegen.
   FRITZ!Box-Rechte können nicht auf ein einzelnes Telefonbuch beschränkt werden.
   Der gleichnamige spätere Linux-Dienstbenutzer ist ein anderes Konto.
4. Den Zugriff für Anwendungen (TR-064) zulassen. Je nach FRITZ!OS heißt die Option
   **Zugriff für Anwendungen zulassen** oder **Zugriff für Apps erlauben**. Sie ist
   unter **Heimnetz → Netzwerk → Netzwerkeinstellungen**, gegebenenfalls in den
   erweiterten Einstellungen/Heimnetzfreigaben, zu finden.
   [FRITZ!-Anleitung](https://fritz.com/de-at/apps/knowledge-base/FRITZ-Box-7690/251_FRITZ-App-Fon-einrichten/).
5. Von einem direkt verbundenen Telefon einmal `#96*5*` wählen. Dadurch wird der
   eingebaute Callmonitor auf TCP-Port 1012 aktiviert. Er ist kein zusätzliches
   Programm und muss nicht auf Ubuntu installiert werden.
   [Callmonitor-Einrichtung](https://www.home-assistant.io/integrations/fritzbox_callmonitor/).
6. Das vorhandene Telefonbuch über die FRITZ!Box-Oberfläche sichern.

Die grundlegenden Schnittstellen sind an einer FRITZ!Box 7690 mit FRITZ!OS 8.25
geprüft. Andere Modelle sind noch nicht bestätigt. Name und ID lassen sich bei
Bedarf mit dem lesenden [Diagnosebefehl `check`](diagnostics.md#1-telefonbuchzugriff-prüfen)
ermitteln. Die einzelnen Diagnose- und Schreibtests sind für die normale Installation
keine Pflichtschritte.

## Ubuntu vorbereiten

- Ubuntu 24.04 LTS mit Python 3.12 oder neuer und systemd.
- Ein dauerhaft eingeschalteter Rechner mit Zugang zum Heimnetz der FRITZ!Box.
  Ein normaler Benutzer mit `sudo`-Berechtigung für die einmalige Einrichtung.
- Ausgehender Zugriff auf die TR-064-Schnittstelle der Box (standardmäßig TCP 49000),
  die von ihr gelieferten Telefonbuch-URLs und TCP 1012. Im Gastnetz ist der Zugriff
  üblicherweise nicht möglich. Keine dieser Schnittstellen ins Internet freigeben.
- Internetzugang für GitHub und die Python-Paketinstallation. Im Betrieb benötigt
  nur die optionale Wikidata-Namenssuche Internetzugang; die Freigabeverwaltung arbeitet lokal.

Systempakete einmalig installieren:

```bash
sudo apt update
sudo apt install -y git python3 python3-venv ca-certificates
python3 --version
```

Die Versionsausgabe muss mindestens `Python 3.12` zeigen. Ubuntu 22.04 mit seinem
Standard-Python 3.10 erfüllt diese Voraussetzung nicht. Anschließend folgt die
[Installation unseres Codes](operations.md#rufpass-installieren).

Ein Reverse Proxy, Caddy, MQTT, Docker, Home Assistant oder eine Weboberfläche
werden für Rufpass nicht benötigt. Auf der FRITZ!Box wird nichts installiert.
