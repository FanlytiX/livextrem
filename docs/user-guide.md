<link rel="stylesheet" href="assets/styles/custom.css">

<nav class="doc-nav">
  <a href="./">Start</a>
  <a href="installation/">Installation</a>
  <a href="setup/">Setup</a>
  <a href="architecture/">Architektur</a>
  <a href="api/">API & Code</a>
  <a href="user-guide/">User Guide</a>
  <a href="strategy/">Technische Strategie</a>
</nav>

# User Guide

<div class="callout"><strong>Info:</strong> Diese Dokumentation ist für GitHub Pages aufgebaut. Bilder und Styles liegen bewusst in separaten Verzeichnissen, damit sie ohne Änderungen an den Markdown-Dateien ausgetauscht werden können.</div>

## Ziel dieses Handbuchs

Dieser Abschnitt beschreibt die Nutzung aus Sicht der Anwender. Ziel ist nicht nur, Menüpunkte zu benennen, sondern zu erklären, wie die wichtigsten Funktionen praktisch eingesetzt werden. Neue Nutzer sollen nach dem Lesen verstehen, wie sie mit liveXtrem arbeiten können und welche Rolle welche Aufgaben übernimmt.

<figure>
  <img src="assets/images/placeholder-ui.png" alt="Platzhalter UI-Screenshot">
  <figcaption>Platzhalter für spätere Screenshots der Benutzeroberfläche. Empfehlenswert sind Abbildungen des Login-Fensters sowie der drei Dashboards.</figcaption>
</figure>

## 1. Anmeldung und Einstieg

Nach dem Start der Anwendung erscheint das Login-Fenster. Bestehende Benutzer melden sich mit Benutzername und Passwort an. Neue Streamer können sich registrieren und den Account während der Registrierung mit Twitch verknüpfen. Nach erfolgreicher Anmeldung öffnet liveXtrem das zur Rolle passende Dashboard.

## 2. Arbeiten im Streamer-Dashboard

Das Streamer-Dashboard ist der zentrale Arbeitsbereich für die Kanalorganisation.

### To-do-Verwaltung

Aufgaben können direkt im Dashboard angelegt und gepflegt werden. Dadurch lassen sich organisatorische Punkte wie Vorbereitungen für Streams, Kooperationen oder technische Nacharbeiten zentral sammeln, statt sie in externe Notiztools auszulagern.

### Übersicht des nächsten Streams

Ein eigener Bereich hebt den nächsten geplanten Stream hervor. Das ist besonders nützlich, wenn mehrere Inhalte vorbereitet werden und schnell ersichtlich sein soll, welches Thema oder welcher Termin als nächstes ansteht.

### Geplante Streams

Über die Planungsfunktion können neue Streamtermine angelegt, bearbeitet und bei Bedarf archiviert werden. Dadurch entsteht eine strukturierte Content-Pipeline anstelle einer losen Sammlung von Einzelideen.

### Finanzverwaltung

Buchungen für Einnahmen und Ausgaben werden im Dashboard erfasst und tabellarisch dargestellt. Für die Weiterverarbeitung stehen Exportfunktionen nach PDF und CSV zur Verfügung. Das ist besonders hilfreich, wenn Übersichten für Auswertungen, Dokumentationen oder einfache betriebswirtschaftliche Nachweise benötigt werden.

### Team- und Rollenverwaltung

Der Streamer kann Moderatoren und Manager verwalten und deren Daten einsehen oder pflegen. Damit wird die Zusammenarbeit nicht ausserhalb der Anwendung organisiert, sondern direkt im fachlichen Kontext des Kanals.

## 3. Arbeiten im Manager-Dashboard

Das Manager-Dashboard richtet sich an organisatorische und koordinierende Aufgaben.

### Event- und Terminplanung

Hier werden Streams und Termine über eine Kalenderansicht verwaltet. Manager können kommende Inhalte planen, Termine bearbeiten und die Übersicht über zuständige Streamer behalten.

### Übersicht aller Events

Neben der Kalenderansicht steht eine Listenansicht mit historischen und zukünftigen Einträgen zur Verfügung. Diese Perspektive ist sinnvoll, wenn nach bestimmten Streamern oder bestehenden Einträgen gesucht werden soll.

### Verwaltung zugeordneter Streamer

Manager arbeiten nicht global über alle möglichen Datensätze, sondern innerhalb ihrer Zuordnungen. Dadurch wird verhindert, dass organisatorische Rollen unkontrolliert auf fremde Kanäle zugreifen.

## 4. Arbeiten im Moderator-Dashboard

Das Moderator-Dashboard fokussiert sich auf Community-Management und Moderationsunterstützung.

### Dashboard und Historie

Zu Beginn werden Kennzahlen und die zuletzt ausgeführten Moderationsaktionen angezeigt. Dadurch ist unmittelbar erkennbar, welche Eingriffe zuletzt vorgenommen wurden und ob beispielsweise Timeouts noch aktiv sind.

### Chat Monitor

Der Chat-Monitor greift auf VOD-basierte Chatdaten zurück. Das ist insbesondere dann hilfreich, wenn Gesprächsverläufe nachvollzogen oder problematische Situationen im Nachhinein eingeordnet werden sollen.

### Aktionen: Timeout, Ban und Unban

Moderatoren können Benutzer zeitweise sperren, dauerhaft bannen oder Sperren wieder aufheben. Die Oberfläche führt diese Aktionen als klar getrennte Arbeitsabläufe und ist damit auch für Nutzer verständlich, die nicht direkt mit Rohaufrufen einer API arbeiten möchten.

## 5. Typische Nutzungsszenarien

### Szenario A: Ein Streamer plant die kommende Woche

Der Streamer legt zuerst neue Themen im Planungsbereich an, prüft anschließend den nächsten Stream und übernimmt offene Aufgaben in die To-do-Liste. Danach können bereits erste finanzielle Einträge für Ausgaben oder Kooperationen dokumentiert werden. Auf diese Weise laufen organisatorische und kaufmännische Vorbereitung in einer Oberfläche zusammen.

### Szenario B: Ein Manager koordiniert mehrere Termine

Der Manager öffnet die Kalenderansicht, plant neue Termine für zugeordnete Streamer und prüft in der Listenansicht, ob Überschneidungen oder offene Punkte vorhanden sind. Dadurch wird die Planung nicht nur reaktiv, sondern nachvollziehbar und zentral verwaltet.

### Szenario C: Ein Moderator arbeitet einen Vorfall nach

Der Moderator nutzt den Chat-Monitor, um einen problematischen Verlauf im VOD-Kontext nachzuvollziehen, und führt danach bei Bedarf einen Timeout oder Bann durch. Die Aktion erscheint anschließend in der Historie und bleibt für die weitere Moderationsarbeit nachvollziehbar.

<div class="callout tip"><strong>Tipp:</strong> Wenn später echte Screenshots oder Diagramme vorliegen, können die vorhandenen Platzhalterdateien einfach ersetzt werden, solange Dateiname und Pfad erhalten bleiben.</div>
