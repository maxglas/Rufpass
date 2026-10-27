# Rufpass manuell unter Windows ausführen

Die Hauptanleitung beschreibt den automatischen Dienstbetrieb unter Linux/Ubuntu.
Der Python-Prozess kann auch unter Windows laufen. Die grundlegenden
[FRITZ!Box-Voraussetzungen](prerequisites.md#fritzbox-vorbereiten) sind dieselben.
Der vollständige Betrieb mit Router ist unter Windows noch nicht bestätigt;
lokale Tests verwenden simulierte Schnittstellen und prüfen die native Instanzsperre.

## Python-Umgebung

Python 3.12 oder neuer installieren. Das folgende Beispiel verwendet `python`;
je nach Python-Installation kann der Befehl `py` heißen. Im lokalen Rufpass-Checkout
in PowerShell ausführen:

```powershell
python --version
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install .
.\.venv\Scripts\rufpass.exe configure
.\.venv\Scripts\rufpass.exe validate
.\.venv\Scripts\rufpass.exe run
```

Die FRITZ!Box und ihr Kennwort werden wie unter Ubuntu abgefragt. Der Benutzer
erhält unmittelbar nach seinem Namen die Frage nach seinem eigenen Kennwort.
`run` startet die Freigabeverwaltung im Vordergrund; das Terminal bleibt offen,
bis der Prozess beispielsweise mit Strg+C beendet wird.

Konfiguration, SQLite-Datenbank und Sperrdatei liegen standardmäßig unter
`%LOCALAPPDATA%\Rufpass`, also im Profil des ausführenden Windows-Benutzers.
Ihre Zugriffsrechte richten sich nach den Windows-Dateirechten; sie enthalten
Zugangsdaten und Rufnummern. Für eine abweichende Konfiguration bei jedem Befehl
`--config C:\Pfad\config.toml` angeben; `database` bei Bedarf in dieser Datei anpassen.

Für Updates den Checkout aktualisieren und das Paket erneut mit
`.\.venv\Scripts\python.exe -m pip install .` installieren. Einen zuvor gestarteten
Prozess anschließend neu starten. Der Ubuntu-Installer `scripts/install.sh` und
die systemd-Dienstdatei sind nicht für Windows vorgesehen. Ein fertiger
Windows-Dienstinstaller oder eine Anleitung zur Aufgabenplanung ist nicht enthalten.
