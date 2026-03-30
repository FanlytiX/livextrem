<link rel="stylesheet" href="{{ '/assets/styles/custom.css' | relative_url }}">

<nav class="doc-nav">
  <a href="{{ '/index' | relative_url }}">Start</a>
  <a href="{{ '/installation' | relative_url }}">Installation</a>
  <a href="{{ '/setup' | relative_url }}">Setup</a>
  <a href="{{ '/architecture' | relative_url }}">Architektur</a>
  <a href="{{ '/api' | relative_url }}">API & Code</a>
  <a href="{{ '/user-guide' | relative_url }}">User Guide</a>
  <a href="{{ '/strategy' | relative_url }}">Technische Strategie</a>
</nav>

# User Guide

{% include info.md %}

## Ziel dieses Handbuchs

Dieser Abschnitt beschreibt die Nutzung aus Sicht der Anwender. Ziel ist nicht nur, Menuepunkte zu benennen, sondern zu erklaeren, wie die wichtigsten Funktionen praktisch eingesetzt werden. Neue Nutzer sollen nach dem Lesen verstehen, wie sie mit liveXtrem arbeiten koennen und welche Rolle welche Aufgaben uebernimmt.

<figure>
  <img src="{{ '/assets/images/placeholder-ui.png' | relative_url }}" alt="Platzhalter UI-Screenshot">
  <figcaption>Platzhalter fuer spaetere Screenshots der Benutzeroberflaeche. Empfehlenswert sind Abbildungen des Login-Fensters sowie der drei Dashboards.</figcaption>
</figure>

## 1. Anmeldung und Einstieg

Nach dem Start der Anwendung erscheint das Login-Fenster. Bestehende Benutzer melden sich mit Benutzername und Passwort an. Neue Streamer koennen sich registrieren und den Account waehrend der Registrierung mit Twitch verknuepfen. Nach erfolgreicher Anmeldung oeffnet liveXtrem das zur Rolle passende Dashboard.

## 2. Arbeiten im Streamer-Dashboard

Das Streamer-Dashboard ist der zentrale Arbeitsbereich fuer die Kanalorganisation.

### To-do-Verwaltung

Aufgaben koennen direkt im Dashboard angelegt und gepflegt werden. Dadurch lassen sich organisatorische Punkte wie Vorbereitungen fuer Streams, Kooperationen oder technische Nacharbeiten zentral sammeln, statt sie in externe Notiztools auszulagern.

### Uebersicht des naechsten Streams

Ein eigener Bereich hebt den naechsten geplanten Stream hervor. Das ist besonders nuetzlich, wenn mehrere Inhalte vorbereitet werden und schnell ersichtlich sein soll, welches Thema oder welcher Termin als naechstes ansteht.

### Geplante Streams

Ueber die Planungsfunktion koennen neue Streamtermine angelegt, bearbeitet und bei Bedarf archiviert werden. Dadurch entsteht eine strukturierte Content-Pipeline anstelle einer losen Sammlung von Einzelideen.

### Finanzverwaltung

Buchungen fuer Einnahmen und Ausgaben werden im Dashboard erfasst und tabellarisch dargestellt. Fuer die Weiterverarbeitung stehen Exportfunktionen nach PDF und CSV zur Verfuegung. Das ist besonders hilfreich, wenn Uebersichten fuer Auswertungen, Dokumentationen oder einfache betriebswirtschaftliche Nachweise benoetigt werden.

### Team- und Rollenverwaltung

Der Streamer kann Moderatoren und Manager verwalten und deren Daten einsehen oder pflegen. Damit wird die Zusammenarbeit nicht ausserhalb der Anwendung organisiert, sondern direkt im fachlichen Kontext des Kanals.

## 3. Arbeiten im Manager-Dashboard

Das Manager-Dashboard richtet sich an organisatorische und koordinierende Aufgaben.

### Event- und Terminplanung

Hier werden Streams und Termine ueber eine Kalenderansicht verwaltet. Manager koennen kommende Inhalte planen, Termine bearbeiten und die Uebersicht ueber zustaendige Streamer behalten.

### Uebersicht aller Events

Neben der Kalenderansicht steht eine Listenansicht mit historischen und zukuenftigen Eintraegen zur Verfuegung. Diese Perspektive ist sinnvoll, wenn nach bestimmten Streamern oder bestehenden Eintraegen gesucht werden soll.

### Verwaltung zugeordneter Streamer

Manager arbeiten nicht global ueber alle moeglichen Datensaetze, sondern innerhalb ihrer Zuordnungen. Dadurch wird verhindert, dass organisatorische Rollen unkontrolliert auf fremde Kanaele zugreifen.

## 4. Arbeiten im Moderator-Dashboard

Das Moderator-Dashboard fokussiert sich auf Community-Management und Moderationsunterstuetzung.

### Dashboard und Historie

Zu Beginn werden Kennzahlen und die zuletzt ausgefuehrten Moderationsaktionen angezeigt. Dadurch ist unmittelbar erkennbar, welche Eingriffe zuletzt vorgenommen wurden und ob beispielsweise Timeouts noch aktiv sind.

### Chat Monitor

Der Chat-Monitor greift auf VOD-basierte Chatdaten zurueck. Das ist insbesondere dann hilfreich, wenn Gespraechsverlaeufe nachvollzogen oder problematische Situationen im Nachhinein eingeordnet werden sollen.

### Aktionen: Timeout, Ban und Unban

Moderatoren koennen Benutzer zeitweise sperren, dauerhaft bannen oder Sperren wieder aufheben. Die Oberflaeche fuehrt diese Aktionen als klar getrennte Arbeitsablaeufe und ist damit auch fuer Nutzer verstaendlich, die nicht direkt mit Rohaufrufen einer API arbeiten moechten.

## 5. Typische Nutzungsszenarien

### Szenario A: Ein Streamer plant die kommende Woche

Der Streamer legt zuerst neue Themen im Planungsbereich an, prueft anschliessend den naechsten Stream und uebernimmt offene Aufgaben in die To-do-Liste. Danach koennen bereits erste finanzielle Eintraege fuer Ausgaben oder Kooperationen dokumentiert werden. Auf diese Weise laufen organisatorische und kaufmaennische Vorbereitung in einer Oberflaeche zusammen.

### Szenario B: Ein Manager koordiniert mehrere Termine

Der Manager oeffnet die Kalenderansicht, plant neue Termine fuer zugeordnete Streamer und prueft in der Listenansicht, ob Ueberschneidungen oder offene Punkte vorhanden sind. Dadurch wird die Planung nicht nur reaktiv, sondern nachvollziehbar und zentral verwaltet.

### Szenario C: Ein Moderator arbeitet einen Vorfall nach

Der Moderator nutzt den Chat-Monitor, um einen problematischen Verlauf im VOD-Kontext nachzuvollziehen, und fuehrt danach bei Bedarf einen Timeout oder Bann durch. Die Aktion erscheint anschliessend in der Historie und bleibt fuer die weitere Moderationsarbeit nachvollziehbar.

{% include tip.md %}
