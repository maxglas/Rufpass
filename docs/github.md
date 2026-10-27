# Öffentlicher Projektstand

## Abschlussprüfung vom 27.10.2026

- [x] Das Repository ist öffentlich: [maxglas/Rufpass](https://github.com/maxglas/Rufpass).
- [x] Der veröffentlichte Stand `7dc92d6` enthält README, Beispielbild, Voraussetzungen,
  Installation, systemd-Betrieb, Diagnose, Changelog und Beitragsanleitung.
- [x] Projektlizenz Apache-2.0 mit Commons Clause v1.0 ist in `LICENSE`, Dokumentation
  und Paket berücksichtigt. GitHub erkennt diese Kombination als „Other“.
- [x] GitHub Actions für diesen Stand ist unter Ubuntu und Windows erfolgreich:
  Paketinstallation, Unit-Tests und CLI-Start; unter Ubuntu zusätzlich Shell-Syntaxprüfung.
  [Geprüfter Testlauf](https://github.com/maxglas/Rufpass/actions/runs/40492124052).
- [x] Der Betreiber bestätigt die Installation als systemd-Dienst und den einwandfreien
  laufenden Ubuntu-Betrieb. [Validierungsstand](setup.md).
- [x] Eine heuristische Prüfung von 149 historischen Git-Blobs fand keine Treffer für
  die geprüften GitHub-Token-, private-Schlüssel-, AWS-Schlüssel-, privaten IP- und
  Benutzerpfadmuster. Dies ist kein vollständiger Geheimnisscan und keine Garantie
  für die Abwesenheit sämtlicher personenbezogener Daten.

Die Git-Autorenhistorie enthält eine private E-Mail-Adresse. Für zukünftige Commits
kann eine GitHub-`noreply`-Adresse verwendet werden; alte Commits ändern sich dadurch
nicht. Eine Umschreibung der veröffentlichten Historie erfolgt nur auf gesonderten
Auftrag und entfernt bereits angefertigte Kopien nicht.

Der frühe Teststand bleibt in der README sichtbar. Ein erfolgreicher Wikidata-Live-Treffer,
ein vollständiger 365-Tage-Ablauf sowie andere Router und Raspberry-Pi-Hardware sind
weiterhin nicht bestätigt. Branch-Regeln und private Sicherheitsmeldungen wurden nicht
verifiziert; sie sind keine Voraussetzung für ein öffentliches Repository.

## Optionale GitHub-Einstellungen

### Vertrauliche Sicherheitsmeldungen

„Private vulnerability reporting“ ermöglicht vertrauliche Meldungen an den Maintainer,
ohne Schwachstellendetails in öffentlichen Issues zu veröffentlichen. Der Status dieser
Einstellung ist nicht bestätigt. Aktivierung: **Settings → Advanced Security → Private
vulnerability reporting → Enable**. Je nach GitHub-Oberfläche liegt der Bereich unter
„Security and quality“. Das ist der bevorzugte Meldeweg aus [SECURITY.md](../SECURITY.md);
dort ist auch ein Ersatzweg beschrieben.

[GitHub-Anleitung](https://docs.github.com/en/code-security/how-tos/report-and-fix-vulnerabilities/configure-vulnerability-reporting/configure-for-a-repository).

### Auffindbarkeit und Präsentation

Die Kurzbeschreibung ist vorhanden: „Angerufene Telefonnummern automatisch freigeben“.
Topics und ein GitHub-Release sind zum Prüfzeitpunkt noch nicht vorhanden. Optional:

- Im Zahnrad neben **About** die Topics `fritzbox`, `telephony`, `call-monitor`,
  `tr-064`, `python` und `self-hosted` setzen.
- Die Kurzbeschreibung präzisieren: **Wer von dir angerufen wird, darf zurückrufen.
  Automatische Rückruf-Freigaben für die FRITZ!Box.**
- Im eigenen Profil anheften und bei Bedarf ein als Vorabversion markiertes Release
  erstellen. Versionsangaben im Changelog sind bisher keine GitHub-Releases.
- Optional unter den Repository-Einstellungen ein Social-Preview-Bild hinterlegen,
  das beim Teilen des Links verwendet werden kann.

Diese Punkte verbessern die Präsentation; sie sind keine offenen Installationsschritte.
Agenten committen nur lokal und pushen ausschließlich auf ausdrücklichen Auftrag.
