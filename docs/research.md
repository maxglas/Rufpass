# Quellen und verifizierte Ausgangspunkte

Recherche: 26.10.2026. Keine Validierung an der konkreten FRITZ!Box durchgeführt.

- [FRITZ!: Rufsperren, Modell 7690](https://fritz.com/apps/knowledge-base/FRITZ-Box-7690/142_rufsperren-fur-ankommende-und-ausgehende-anrufe-z-b-0900-nummern-einrichten)
  beschreibt die Regel „Nicht im Telefonbuch“. Das Verhalten mit einem zweiten Buch
  wird vor Umsetzung ausdrücklich manuell getestet.
- [Home Assistant: FRITZ!Box Call Monitor](https://www.home-assistant.io/integrations/fritzbox_callmonitor/)
  dokumentiert Port 1012, Wählzustände und Aktivierung. Home Assistant ist keine Voraussetzung unseres Dienstes.
- [FRITZ!: TR-064 Telefonie-Schnittstelle](https://fritz.support/resources/TR-064_Contact_SCPD.pdf)
  dokumentiert Telefonbuchzugriff und gezieltes Anlegen/Ändern/Löschen von Einträgen.
  Schreibzugriffe erfordern Phone-Rechte; Online-Telefonbücher sind nicht das Schreibziel.
- [FRITZ!: Fehlende Einträge in der Anrufliste](https://fritz.com/service/wissensdatenbank/dok/FRITZ-Box-7590/772_In-Anrufliste-fehlen-Eintrage/)
  weist darauf hin, dass ausgehende, nicht angenommene Anrufe nicht in der Anrufliste erscheinen.
- [FRITZ!: Benutzerkonten](https://fritz.com/apps/knowledge-base/fritz-box-7590/1522_Im-Heimnetz-uber-Benutzerkonten-auf-FRITZ-Box-zugreifen)
  beschreibt die Trennung allgemeiner Einstellungsrechte von Telefonie-Rechten.

## Ähnliche Projekte

- [SpamBlockUp](https://spamblockup.jimdofree.com/2021/04/15/kurz-und-b%C3%BCndig-das-alles-kann-spamblockup/):
  ausgehende Nummern anzeigen und manuell in ein Whitelist-Telefonbuch übernehmen.
- [fbcallrouter](https://github.com/blacksenator/fbcallrouter):
  Callmonitor-Hintergrunddienst mit Spamprüfung und optionaler Übernahme öffentlich identifizierbarer Nummern.

Keines dieser Projekte wurde lokal installiert oder für unseren Einsatzzweck getestet.

## Interne Einträge in Telefonbuchdaten

Die [TR-064-Dokumentation](https://fritz.support/resources/TR-064_Contact_SCPD.pdf)
zeigt auch Kontakte mit `number type="intern"` im Telefonbuch-XML.
[fbtr64toolbox](https://github.com/MarcusRoeckrath/fbtr64toolbox/blob/main/fbtr64toolbox.txt)
beschreibt bei `phonebookinfo`, dass zusätzliche interne Nummern zu einer
Abweichung von der Kontaktzahl der Weboberfläche führen können. Rufpass zählt
normale Kontakte und interne Einträge deshalb getrennt. Die konkrete Zahl
der internen Einträge einer Box muss mit `check` bestätigt werden.
