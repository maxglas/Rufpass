# Projektlizenz auswählen

## Gewünschte Regelung

Der Autor hat folgendes Ziel festgelegt:

- Privat verwenden, anpassen und kostenlos weitergeben: erlaubt.
- In einer Firma, Werkstatt oder Praxis für deren eigene Telefonanlage nutzen: erlaubt.
- Rufpass selbst oder einen im Wesentlichen darauf beruhenden Fork als kostenpflichtiges
  Produkt oder als Dienst zur Gewinnerzielung anbieten: soll ausgeschlossen sein.

Das ist keine allgemeine Beschränkung auf nicht kommerzielle Nutzung. PolyForm
Noncommercial wäre ohne zusätzliche Erlaubnis zu weitgehend. MIT und Apache-2.0
allein verbieten den Verkauf dagegen nicht und passen ebenfalls nicht zu diesem Ziel.

Ein Kandidat ist **Apache-2.0 mit Commons Clause v1.0**. Die
[Commons Clause](https://commonsclause.com/) lässt interne Nutzung zu und schränkt
entgeltliche Angebote ein, deren Wert ganz oder wesentlich aus der Software stammt.
Ihre Verkaufsdefinition kann auch Hosting sowie Beratungs-/Supportleistungen erfassen.
Sie erlaubt nach den Erläuterungen außerdem größere eigene Produkte mit eigenständigem
Mehrwert. Diese Grenzen müssen zur endgültig gewünschten Regelung passen; die
Kombination wurde deshalb noch nicht als `LICENSE` eingesetzt.

Ein so beschränktes Projekt ist als **Source Available**, nicht als OSI Open Source,
zu bezeichnen. Eine vollständig selbst formulierte Klausel wäre rechtlich gesondert
zu prüfen. Die endgültige Lizenzentscheidung ist noch offen.

## Vergleich der vorher betrachteten Standardlizenzen
 Öffentlich sichtbarer Quellcode ist ohne
entsprechende Lizenz nicht automatisch frei zur Nutzung und Weitergabe freigegeben.
[GitHub: Lizenzierung](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository).

| Punkt | MIT | Apache-2.0 |
| --- | --- | --- |
| Kostenlose und kommerzielle Nutzung | Erlaubt | Erlaubt |
| Ändern und weitergeben | Erlaubt | Erlaubt |
| Geschlossene abgeleitete Software | Möglich | Möglich |
| Eigene Änderungen veröffentlichen | Nicht vorgeschrieben | Nicht vorgeschrieben |
| Bei Weitergabe erhalten | Copyright- und Lizenzhinweis | Lizenz, relevante Hinweise und gegebenenfalls NOTICE-Hinweise |
| Änderungen an Dateien kennzeichnen | Nicht ausdrücklich vorgeschrieben | Vorgeschrieben |
| Ausdrückliche Patentlizenz | Nicht enthalten | Für bestimmte Patentansprüche der Mitwirkenden enthalten |
| Patentklagen | Keine entsprechende ausdrückliche Regel | Patentlizenz endet bei bestimmten Klagen gegen das Werk |
| Umfang | Sehr kurz | Ausführlicher |

Beide Texte enthalten Gewährleistungs- und Haftungsausschlüsse; deren rechtliche
Wirkung hängt vom anwendbaren Recht ab. Keine der beiden Lizenzen verlangt eine
prominente Autorenwerbung in der Oberfläche eines abgeleiteten Produkts. Beide
erhalten relevante Urheberhinweise bei der Weitergabe nach ihren jeweiligen Regeln.

Die folgende Auswahl kann das gewünschte Verkaufsverbot allein nicht abbilden.
Maßgeblich sind die Lizenztexte: [MIT](https://opensource.org/license/mit),
[Apache-2.0](https://www.apache.org/licenses/LICENSE-2.0).

Nach der Entscheidung: vollständige Lizenzdatei im Repository ergänzen, README,
CONTRIBUTING und Paketmetadaten aktualisieren und die Lizenz beim Paketbau sowie
in der Installationskopie mitliefern. Abhängigkeiten behalten ihre eigenen Lizenzen.
