# Öffentliche Veröffentlichung vorbereiten

## Stand der Prüfung vom 27.10.2026

Der lokale Stand enthält README, getrennte Voraussetzungen, Erstinstallation,
Updates, systemd-Betrieb, Diagnose, Architektur und Beitragsanleitung.
Der Quellcode verwendet `fritzconnection` (MIT); Pakete werden regulär über pip
installiert und nicht als kopierter Fremdcode in diesem Repository ausgeliefert.

Eine heuristische Prüfung von 95 historischen Git-Blobs fand keine Treffer für
typische GitHub-Tokens, private Schlüssel, AWS-Zugriffsschlüssel sowie die geprüften
privaten IP-/Benutzerpfadmuster. Dies ist kein vollständiger Geheimnisscan und keine
Garantie, dass sämtliche personenbezogenen Daten ausgeschlossen sind.
Die Git-Autorenhistorie enthält eine private E-Mail-Adresse; ihre Veröffentlichung
muss vor einem Sichtbarkeitswechsel bewusst entschieden werden. Eine Änderung
zukünftiger Git-Einstellungen ändert alte Commits nicht.

GitHub-Sichtbarkeit, Actions-Ergebnisse, Branch-Regeln und private Sicherheitsmeldungen
konnten mit dem verfügbaren Zugriff nicht verifiziert werden. Lokale Testresultate
sind kein Nachweis für einen erfolgreichen GitHub-Actions-Lauf.

## Vor dem öffentlichen Schalten abschließen

- [ ] Projektlizenz festlegen; vollständige `LICENSE` und Paketmetadaten ergänzen.
  [MIT und Apache-2.0 im Vergleich](licensing.md).
- [ ] Git-Autoren-E-Mail bewusst öffentlich zulassen oder Historie vor der Freigabe
  kontrolliert bereinigen. Historie nicht ohne gesonderte Entscheidung umschreiben.
- [ ] Ubuntu-Dienst einmal nach der [Betriebsanleitung](operations.md) installieren:
  Autostart aktiv, neue Freigabe sichtbar, Rückruf möglich, erneuter Anruf ohne Dublette.
  Neustart des Dienstes prüfen und Ergebnis im [Validierungsstand](setup.md) festhalten.
- [ ] Den tatsächlichen GitHub-Actions-Lauf des zu veröffentlichenden Commits prüfen.
  Der Workflow liegt unter `.github/workflows/tests.yml`.
- [ ] Vorbereitete Änderungen bewusst pushen; Agenten pushen nur auf ausdrücklichen Auftrag.
- [ ] Auf GitHub **Private vulnerability reporting** einschalten, damit der Meldeweg
  aus [SECURITY.md](../SECURITY.md) funktioniert.
- [ ] Die zu veröffentlichende Historie abschließend auf vertrauliche Daten prüfen,
  einschließlich eventueller späterer Commits, Anhänge und Branches.
- [ ] Erst danach die Sichtbarkeit in den Repository-Einstellungen ändern. Diese
  Anleitung führt keinen Push und keinen Sichtbarkeitswechsel aus.

Die noch offene Geräteprüfung verhindert nicht technisch ein öffentliches Repository.
Bis zu ihrem Abschluss muss der frühe Teststand aber sichtbar bleiben; eine belastbare
Ubuntu-Dienstempfehlung kann daraus noch nicht abgeleitet werden.

## Präsentation auf GitHub

- Name: **Rufpass**.
- Kurzbeschreibung: **Wer von dir angerufen wird, darf zurückrufen. Automatische
  Rückruf-Freigaben für die FRITZ!Box.**
- Topics: `fritzbox`, `telephony`, `call-monitor`, `tr-064`, `python`, `self-hosted`.
- Autor: [Maximilian Glas](https://github.com/maxglas).
- Nach der Veröffentlichung im eigenen Profil anheften und ein erstes als Vorabversion
  markiertes Release mit tatsächlich geprüfter Kompatibilität erstellen.
- Eine kurze Demo mit synthetischen Nummern ist hilfreich, aber kein Freigabeblocker.
  Badges erst ergänzen, wenn Lizenz und tatsächliche CI-Ergebnisse feststehen.

Ein Logo, eine Website, Docker und ein Windows-Dienst sind für die erste öffentliche
Version nicht erforderlich. Priorität haben verständliche Installation, nachvollziehbarer
Teststand und sichere Handhabung von Zugangsdaten.
