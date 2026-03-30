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

# Architektur

{% include info.md %}

## Architekturueberblick

liveXtrem ist als Desktop-Anwendung in Python umgesetzt und kombiniert eine grafische Oberflaeche mit einer relationalen Datenhaltung und einer externen Twitch-Anbindung. Die Architektur folgt keinem monolithischen Ein-Fenster-Ansatz, sondern trennt den Einstieg in das System von den fachlichen Arbeitsbereichen. Dadurch koennen die unterschiedlichen Rollen im Streaming-Umfeld mit jeweils passenden Dashboards abgebildet werden.

<figure>
  <img src="{{ '/assets/images/placeholder-architecture.png' | relative_url }}" alt="Platzhalter Architekturdiagramm">
  <figcaption>Platzhalter fuer das Architekturdiagramm. Die Datei kann spaeter durch eine finale Diagrammversion ersetzt werden.</figcaption>
</figure>

## Zentrale Komponenten

### Login und Session-Kontext

Der Einstieg erfolgt ueber `login.py`. Dort werden Benutzeranmeldung, Registrierung neuer Streamer und der Aufbau einer fachlichen Sitzung gebuendelt. Nach erfolgreicher Authentifizierung entsteht ein `SessionUser`, der nicht nur die technische Identitaet des eingeloggten Benutzers haelt, sondern auch den fachlichen Kontext, in dem spaetere Dashboards arbeiten. Dieser Punkt ist fuer liveXtrem besonders wichtig, weil Streamer bei Rollenwechseln weiterhin im eigenen Kontext arbeiten sollen.

### Router und Dashboard-Auswahl

`router.py` entkoppelt die Anmeldung von der konkreten Zieloberflaeche. Der Router entscheidet anhand der Rolle oder eines explizit uebergebenen Zieltyps, ob das Streamer-, Moderator- oder Manager-Dashboard geoeffnet wird. Damit bleibt die Einstiegsschicht schlank, waehrend die Zustandslogik zentral gebuendelt wird.

### Streamer-Dashboard

Das Streamer-Dashboard ist der umfangreichste Arbeitsbereich der Anwendung. Es vereint operative Funktionen wie To-do-Verwaltung, Streamplanung, Finanzbuchungen, Exportfunktionen und Teamverwaltung. Fachlich bildet dieses Modul das Zentrum der Anwendung, weil hier die meisten Daten erzeugt und gepflegt werden.

### Manager-Dashboard

Das Manager-Dashboard fokussiert sich auf koordinative Aufgaben. Im Mittelpunkt stehen Kalenderansichten, Termin- und Eventplanung sowie die Verwaltung zugeordneter Streamer. Die Daten werden nicht separat gepflegt, sondern aus dem gemeinsamen Datenbestand gelesen und rollenabhaengig gefiltert. Dadurch bleibt die Informationsbasis konsistent.

### Moderator-Dashboard

Das Moderator-Dashboard verbindet die Desktop-Anwendung mit Twitch-nahen Moderationsprozessen. Es bietet eine Uebersicht ueber Moderationsaktionen, einen Chat-Monitor auf Basis von VOD-Informationen und Oberflaechen fuer Timeout-, Ban- und Unban-Vorgaenge. Die Logik ist bewusst getrennt, weil hier neben Datenbankzugriffen auch externe API-Funktionen und Berechtigungen eine Rolle spielen.

### Datenbankschicht

Die relationale Datenhaltung wird ueber Datenbankmodule wie `database_connection.py`, `database_queries.py` und `database_queries_moderator.py` angebunden. Die Datenbank speichert unter anderem Benutzer, Rollen, Streamer-Profile, Teamzuordnungen, Planungsdaten, To-dos, Finanzinformationen und Twitch-bezogene Identitaetsdaten. Auf diese Weise bleiben fachliche Informationen dauerhaft verfuegbar und muessen nicht in lokalen Dateien pro Arbeitsplatz gepflegt werden.

### Twitch-Integration

Im Verzeichnis `fremdsys/` liegen die Module fuer OAuth und API-Kommunikation. `oauth.py` uebernimmt den Browser-basierten Login und den lokalen Callback, waehrend `tapi_data.py` und `tapi_mod.py` Fachfunktionen fuer Statistik-, VOD- und Moderationsdaten kapseln. Die Desktop-Anwendung muss dadurch die HTTP-Kommunikation nicht an mehreren Stellen selbst nachbauen.

## Zusammenspiel der Komponenten

Der typische Ablauf beginnt mit der Anmeldung eines Benutzers. Nach erfolgreicher Authentifizierung wird eine Session mit Rollen- und Kontextinformationen aufgebaut. Anschliessend oeffnet der Router das passende Dashboard. Dieses Dashboard laedt die benoetigten Daten aus der Datenbank und ergaenzt sie bei Bedarf um Twitch-Daten. Aenderungen, etwa an einem geplanten Stream oder an einer Finanzbuchung, werden wieder in die Datenbank zurueckgeschrieben und stehen dadurch auch anderen Rollen im selben fachlichen Kontext zur Verfuegung.

Aus architektonischer Sicht verfolgt liveXtrem damit einen klaren Grundsatz: Die GUI ist fuer Interaktion und Darstellung zustaendig, waehrend Persistenz und externe Integrationen in eigenen Modulen gekapselt werden. Das verbessert Nachvollziehbarkeit und Wartbarkeit gegenueber einer Vermischung aller Verantwortlichkeiten in einer einzelnen Datei.

## Datenmodell auf fachlicher Ebene

Die genaue Diagrammversion wird spaeter ersetzt. Aus dem Quellcode laesst sich jedoch bereits ein stabiles Kernmodell ableiten. Zentrale Entitaeten sind `users`, `user_roles`, `streamer`, `moderator`, `streamer_manager`, `streamer_moderator`, `stream_planung`, `streamer_finances`, `streamer_todos` und `twitch_tokens`. Diese Struktur zeigt, dass liveXtrem Benutzeridentitaet, Rollenlogik und fachliche Objekte bewusst trennt.

<figure>
  <img src="{{ '/assets/images/placeholder-db.png' | relative_url }}" alt="Platzhalter Datenbankmodell">
  <figcaption>Platzhalter fuer das logische Datenbankmodell. Die finale Version sollte Entitaeten, Schluessel und relevante Beziehungen sichtbar machen.</figcaption>
</figure>

{% include tip.md %}
