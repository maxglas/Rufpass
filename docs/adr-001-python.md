# ADR-001: Python als gemeinsame Implementierung

**Status:** Akzeptiert
**Datum:** 2026-10-26
**Entscheider:** Maximilian Glas

## Kontext

Rufpass soll selbst gewählte Nummern über den FRITZ!Box-Callmonitor erfassen und
zeitlich begrenzte Rückruf-Freigaben in einem separaten lokalen Telefonbuch verwalten.
Das erste Betriebsziel ist Ubuntu. Eine spätere öffentliche Veröffentlichung ist vorgesehen.

Python und C#/.NET wurden hinsichtlich Entwicklung, Laufzeitinstallation und
Dienstbetrieb unter Linux und Windows betrachtet. Beide können unter Linux über
systemd betrieben werden. Windows-Komfort rechtfertigt derzeit keine zweite Implementierung.

## Entscheidung

Rufpass wird in Python implementiert. Eine parallele .NET-Version wird nicht gepflegt.
Die Entscheidung wurde getroffen, bevor Anwendungscode implementiert wurde.

## Erwogene Optionen

| Option | Vorteil | Nachteil |
| --- | --- | --- |
| Python | Passend zum ersten Betriebsziel; vorhandene FRITZ!Box-Bibliotheken | Windows-Paket und Diensteinbindung verursachen Zusatzaufwand |
| C#/.NET | Gemeinsame Anwendung für Linux und Windows; gute Windows-Diensteinbindung | Wechsel auf eine andere Technologie ohne derzeit erforderlichen Betriebsnutzen |
| Beide Sprachen | Jeweils eigene Umsetzung pro Umgebung möglich | Doppelte Implementierung, Tests und Fehlerkorrekturen |

## Folgen

- Linux ist das erste Ziel für dokumentierten und getesteten Dauerbetrieb.
- Die Anwendung soll als normaler Vordergrundprozess startbar sein. Dienstverwaltung
  erfolgt außerhalb der Fachlogik; systemd ist der vorgeschlagene erste Betriebsweg.
- fritzconnection wird als Kandidat für TR-064 und Callmonitor am Gerät geprüft.
- SQLite ist für lokale Freigaben vorgesehen.
- Kein Windows-Installationspaket oder Windows-Service-Support im ersten Umfang.
- Docker ist eine mögliche spätere Verpackung, keine Voraussetzung der Fachlogik.

## Nächste Schritte

1. [ ] Sperrregel mit einem zweiten lokalen Telefonbuch am Testgerät prüfen.
2. [ ] Callmonitor und lesenden TR-064-Zugriff prüfen.
3. [ ] Einen Probelauf ohne Schreibzugriffe implementieren.
4. [ ] Freigabeverwaltung mit gezielten Telefonbuchänderungen und Tests implementieren.
5. [ ] Dienstbetrieb auf Ubuntu prüfen und dokumentieren.

Eine Neubewertung ist sinnvoll, wenn konkrete Anforderungen an Windows-Betrieb
vorliegen. Sie löst nicht automatisch eine zweite Implementierung aus.
