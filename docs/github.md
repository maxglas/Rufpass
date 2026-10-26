# GitHub-Veröffentlichung vorbereiten

## Repository verbinden

Ein lokales Git-Repository kann nachträglich mit einem leeren GitHub-Repository
verbunden werden. GitHub benötigt dafür keinen separaten neuen Projektstart.

1. Auf GitHub ein Repository namens `Rufpass` erstellen, zunächst privat.
2. Dabei keine README, `.gitignore` oder Lizenz automatisch erzeugen lassen:
   Das lokale Projekt besitzt bereits einen Commit mit diesen Projektunterlagen.
3. Im lokalen Projektverzeichnis die von GitHub angezeigte URL verbinden:

```powershell
git remote add origin https://github.com/maxglas/Rufpass.git
git push -u origin main
```

Diese URL gilt, wenn das Repository tatsächlich unter `maxglas/Rufpass` erstellt
wurde. Vorher die von GitHub angezeigte Zieladresse prüfen. Noch existiert kein
bestätigtes Remote. Falls `origin` bereits existiert, zuerst `git remote -v` prüfen.

Danach ist der normale Ablauf `git add`, `git commit`, `git push`.
Ein zusätzliches Klonen in dasselbe Verzeichnis ist nicht erforderlich.

Quelle: [GitHub: Adding locally hosted code](https://docs.github.com/en/migrations/importing-source-code/using-the-command-line-to-import-source-code/adding-locally-hosted-code-to-github).

## Präsentation

- Name: **Rufpass**
- Kurzbeschreibung: **Wer von dir angerufen wird, darf zurückrufen. Automatische Rückruf-Freigaben für die FRITZ!Box.**
- Vorgeschlagene Topics: `fritzbox`, `telephony`, `call-monitor`, `tr-064`, `python`, `self-hosted`.
- Autor: [Maximilian Glas](https://github.com/maxglas).
- README mit Problem, Ablauf, verständlicher Grafik, Entwicklungsstand und Dokumentationslinks.
- Badges erst für tatsächlich vorhandene Tests, Releases und Lizenz hinzufügen.
- Später eine kurze Demo mit synthetischen Daten und ein nachvollziehbares erstes Release ergänzen.

## Vor dem öffentlichen Schalten

- Lizenz bewusst auswählen und als `LICENSE` ergänzen.
- Gerätetests durchführen und tatsächliche Kompatibilität dokumentieren.
- Gesamte zur Veröffentlichung vorgesehene Git-Historie auf Zugangsdaten,
  echte Telefonnummern und private Infrastrukturangaben prüfen.
- Git-Autorenangaben prüfen; bei Bedarf vor dem Push eine GitHub-No-Reply-Adresse verwenden.
- Bei Veröffentlichung das Repository optional im eigenen GitHub-Profil anheften.

Das Repository soll erst später öffentlich werden. Dieses Dokument führt weder
einen Push noch eine Änderung der Sichtbarkeit aus.
