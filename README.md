# Rufpass

**Wer von dir angerufen wird, darf zurückrufen.**

Rufpass soll selbst gewählte Telefonnummern automatisch für Rückrufe an der
FRITZ!Box freigeben. Für alle anderen unbekannten Nummern bleibt die bestehende
Sperrregel aktiv.

## Warum Rufpass?

Nur Anrufe aus dem Telefonbuch zuzulassen bringt Ruhe vor Werbeanrufen. Es verhindert
aber auch erwünschte Rückrufe: Du rufst eine Werkstatt, Arztpraxis oder einen neuen
Kontakt an, erreichst niemanden und der spätere Rückruf wird blockiert.

Rufpass soll diese Lücke schließen, ohne dass jede selbst gewählte Nummer dauerhaft
in deinem persönlichen Telefonbuch landen muss.

> **Entwicklungsstand: erste Diagnoseversion.** `rufpass check` prüft den lesenden
> Telefonbuchzugriff; `rufpass monitor` erkennt ausgehende Wählversuche. Automatische
> Freigaben und ein dauerhaft installierter Dienst sind noch nicht implementiert.
> Das Durchstellen einer Nummer aus einem zweiten lokalen Telefonbuch wurde auf
> einer FRITZ!Box 7690 mit FRITZ!OS 8.25 manuell bestätigt.

## Diagnose ausprobieren

Die [Ubuntu-Anleitung](docs/diagnostics.md) führt durch Installation,
Telefonbuchprüfung und einen Testanruf ohne Gesprächsannahme. Benötigt wird Python 3.12
oder neuer. Die Diagnose führt keine Telefonbuchänderungen durch.

## So soll es funktionieren

1. **Du rufst jemanden an.** Rufpass erkennt bereits den Wählversuch, auch wenn niemand abnimmt.
2. **Die Nummer bekommt einen Rufpass.** Der Dienst speichert sie in einem separaten
   lokalen FRITZ!Box-Telefonbuch für Rückruf-Freigaben.
3. **Der Rückruf darf klingeln.** Die FRITZ!Box übernimmt weiterhin die Rufbehandlung.
4. **Die Freigabe läuft wieder ab.** Geplant sind zeitlich begrenzte Einträge;
   30 Tage sind der erste Entwurf. Erneutes Wählen verlängert die Freigabe.

Persönliche Kontakte sollen unverändert bleiben. Rufpass soll ausschließlich die
eigenen automatisch angelegten Einträge verwalten.

```mermaid
flowchart LR
    A[Eigener Wählversuch] --> B[FRITZ!Box Callmonitor]
    B --> C[Rufpass im Heimnetz]
    C -->|TR-064| D[Telefonbuch für Rückruf-Freigaben]
    D --> E[FRITZ!Box erlaubt Rückruf]
```

## Technischer Ansatz

Ein kleiner Python-Hintergrunddienst soll auf einem dauerhaft laufenden Rechner im
Heimnetz arbeiten. Der Callmonitor der FRITZ!Box meldet Wählversuche über TCP-Port
1012. Die authentifizierte TR-064-Schnittstelle dient zur Verwaltung des zusätzlichen
Telefonbuchs. SQLite speichert Freigaben und Ablaufzeiten lokal.

Für den Betrieb sind Docker Compose oder unter Linux systemd vorgesehen. Ein
Cloud-Dienst, MQTT-Broker oder Reverse Proxy ist für die Kernfunktion nicht erforderlich.

## Voraussetzungen und Kompatibilität

- Eine FRITZ!Box mit Telefoniefunktion, Callmonitor und passenden TR-064-Aktionen.
- Eine bestehende Sperrregel für Anrufer ohne Telefonbucheintrag.
- Ein zusätzliches **lokales** Telefonbuch sowie ein Benutzer mit Telefonie-Rechten.
- Ein dauerhaft laufender Rechner mit Netzwerkzugriff auf die FRITZ!Box.

**Erstes vorgesehenes Testgerät:** FRITZ!Box 7690 mit FRITZ!OS 8.25.
Manuell bestätigt ist das Durchstellen von Nummern aus einem zweiten lokalen Telefonbuch.
Gemeldete Zielumgebung: Ubuntu 24.04.4 LTS mit Python 3.12.3.
Die Diagnose und automatische Telefonbuchpflege sind dort noch nicht am Gerät geprüft;
weitere Modelle sind nicht getestet.

## Rechte und Grenzen

Ein eigener FRITZ!Box-Benutzer benötigt Telefonie-Rechte (Phone). Diese sind nicht
auf ein einzelnes Telefonbuch begrenzbar. Die Einschränkung auf die Ziel-Telefonbuch-ID
soll im Programm umgesetzt werden; sie ersetzt keine Berechtigungsgrenze der Box.

- Erfasst werden ausschließlich Anrufe, die über die überwachte FRITZ!Box laufen.
- Rückrufe von einer anderen oder unterdrückten Nummer werden nicht freigegeben.
- Während eines Ausfalls verpasste erfolglose Wählversuche lassen sich nicht
  zuverlässig aus der normalen Anrufliste nachholen.
- Bereits angelegte Telefonbucheinträge bleiben bei einem Dienstausfall bestehen.
- Zugangsdaten und echte Telefonnummern gehören nicht ins Repository oder in Fehlerberichte.

## Nächste Schritte

- [x] Durchstellen einer Nummer aus einem zweiten lokalen Telefonbuch manuell bestätigen.
- [x] Lesende Diagnose und Erkennung ausgehender Wählereignisse mit simulierten Schnittstellen testen.
- [ ] Wählereignisse am Callmonitor prüfen.
- [ ] Erfassung und Nummernnormalisierung implementieren.
- [ ] Gezielte Telefonbuchpflege und Ablaufverwaltung implementieren.
- [ ] Probelauf, automatisierte Tests und Gerätetests durchführen.
- [ ] Betrieb und Installation dokumentieren.

## Dokumentation und Mitarbeit

- [Architekturentscheidung: Python](docs/adr-001-python.md)
- [Architektur und Implementierungsgrenzen](docs/architecture.md)
- [Diagnose auf Ubuntu installieren und testen](docs/diagnostics.md)
- [Manueller Vorabtest und nächste Schritte](docs/setup.md)
- [Recherche und Quellen](docs/research.md)
- [Mitwirken und Fehler melden](CONTRIBUTING.md)

## Autor

Ein Projekt von [Maximilian Glas](https://github.com/maxglas).

Rufpass ist ein unabhängiges Projekt und kein offizielles Produkt von FRITZ!.

## Lizenz

Die Lizenz wird vor der öffentlichen Freigabe festgelegt und als `LICENSE` ergänzt.
