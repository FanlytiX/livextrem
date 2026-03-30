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

# API und Code-Struktur

{% include info.md %}

## Einordnung

liveXtrem stellt keine klassische Web-API mit oeffentlichen REST-Endpunkten bereit. Stattdessen basiert die Anwendung auf einer internen Modul- und Funktionsschnittstelle. Fuer die technische Dokumentation ist deshalb nicht die URL-Struktur einer Serveranwendung entscheidend, sondern die Frage, welche Module welche Verantwortung tragen und wie Daten zwischen GUI, Datenbank und Twitch-Integration fliessen.

## Einstieg und Steuerung

### `login.py`

Dieses Modul bildet den Einstieg in das Anwendungssystem. Es verwaltet die Login-Oberflaeche, fuehrt Benutzeranmeldung und Registrierung durch und erzeugt nach erfolgreicher Authentifizierung ein Sitzungsobjekt. Bemerkenswert ist, dass Dashboards nicht aus einem Hintergrundthread gestartet werden, sondern sauber ueber den Main-Thread, was fuer Tkinter-basierte Anwendungen wichtig ist.

### `session_user.py`

`SessionUser` und `TwitchIdentity` modellieren die aktuell angemeldete Sitzung. Neben den offensichtlichen Benutzerdaten enthaelt die Session auch fachliche Informationen wie den aktiven Streamer-Kontext und Berechtigungen fuer Manager- oder Moderator-Dashboards. Diese Kapselung vereinfacht rollenbezogene Entscheidungen in der gesamten Anwendung.

### `router.py`

Der Router ist die Vermittlungsschicht zwischen Login und Fachoberflaeche. Er entscheidet, welches Dashboard geoeffnet wird, und prueft dabei zugleich Rollenrechte. Die Datei ist klein, aber architektonisch wichtig, weil sie die Startlogik zentralisiert und direkte Kopplungen reduziert.

## Konfiguration und Sicherheit

### `config.py`

Das Konfigurationsmodul liest Datenbank- und Twitch-Parameter entweder aus Umgebungsvariablen oder aus einer lokalen JSON-Datei. Es validiert ausserdem, ob alle Pflichtwerte vorhanden sind. Dadurch wird Konfiguration nicht ueber den Code verteilt, sondern an einer zentralen Stelle kontrolliert.

### `security.py`

Dieses Modul kuemmert sich um die Passwortverarbeitung. Neue Passwoerter werden mit PBKDF2-SHA256 und Salt gehasht. Zusaetzlich ist eine Rueckwaertskompatibilitaet fuer aeltere SHA256-Hashes vorgesehen, sodass bestehende Daten migriert werden koennen, ohne Benutzerkonten unbrauchbar zu machen. Fuer eine Desktop-Anwendung ist das eine erfreulich saubere Sicherheitsentscheidung, weil Klartextpasswoerter und triviale Hashes vermieden werden.

## Datenbankzugriff

### `database_connection.py`

Hier wird die technische Verbindung zur MariaDB aufgebaut. Das Modul stellt Hilfsfunktionen bereit, um Abfragen auszufuehren, Tabelleninformationen auszulesen und Verbindungen wieder sauber zu schliessen. Es dient als Basis fuer hoeherliegende Abfragemodule.

### `database_queries.py`

Dieses Modul enthaelt Datenbanklogik fuer fachliche Abfragen rund um Benutzer- und Streamer-bezogene Daten. Dazu gehoeren aus Sicht des Projekts insbesondere Daten, die fuer Dashboards und Auswertungen gebraucht werden. Die Trennung in ein eigenes Query-Modul verhindert, dass SQL-Logik direkt in GUI-Ereignisfunktionen verteilt wird.

### `database_queries_moderator.py`

Die Moderator-Logik kombiniert lokale Historienverwaltung mit Twitch-bezogenen Moderationsfunktionen. Hier werden Chat-Nachrichten aus VODs aufbereitet, Moderationsaktionen lokal festgehalten und fachlich relevante Rueckgabestrukturen fuer das Dashboard erzeugt. Der entscheidende Vorteil liegt darin, dass die GUI nicht direkt mit Rohantworten der Twitch-API arbeiten muss.

## Twitch-nahe Funktionsmodule

### `fremdsys/oauth.py`

Dieses Modul implementiert den OAuth-Prozess fuer Twitch. Es startet einen lokalen HTTP-Callback, oeffnet den Browser fuer die Anmeldung, tauscht den Authorization Code gegen Tokens aus und liest anschliessend Benutzerinformationen aus. Die Loesung ist fuer eine Desktop-Anwendung geeignet, weil sie keinen separaten Webserver voraussetzt und den Login dennoch sauber ueber den offiziellen OAuth-Flow abwickelt.

### `fremdsys/tapi_data.py`

Hier liegen datenorientierte Twitch-Funktionen wie das Laden vergangener Streams, Follower- und Subscriber-Daten oder Kennzahlen zu VOD-Aufrufen. Diese Schnittstelle ist vor allem fuer analytische oder informationsbezogene Oberflaechen relevant.

### `fremdsys/tapi_mod.py`

Dieses Modul kapselt Moderationsfunktionen wie das Laden von VOD-Chatdaten sowie Ban-, Timeout- und Unban-Aktionen. Fachlich ist dies die Bruecke zwischen LiveXtrem und den Twitch-Moderationsschnittstellen.

## Zentrale GUI-Module

### `streamer_dashboard.py`

Das Streamer-Dashboard vereint mehrere Fachbereiche in einer Oberflaeche. Sichtbar sind unter anderem To-do-Liste, naechster Stream, geplante Streams, KI-Content-Assistent, Finanzbuchungen mit CSV- und PDF-Export sowie Team- und Rollenverwaltung. Das Modul ist dadurch kein reines View-Element, sondern ein zentraler Anwendungsknoten.

### `manager_gui.py`

Das Manager-Dashboard ist auf Termin- und Ressourcenkoordination ausgerichtet. Im Code sichtbar sind ein eigener `DataManager`, Kalendernavigation, Eventdialoge und Streamer-Verwaltung. Die Struktur deutet auf einen klaren Anwendungsfall hin: Management-Aufgaben sollen ohne Zugriff auf alle Streamer-Daten pauschal moeglich sein, sondern immer innerhalb zugaenglicher Zustaendigkeiten.

### `moderator_dashboard.py`

Dieses Modul bildet die Bedienlogik fuer Moderatoren ab. Neben einer Uebersicht ueber Statistik und Historie sind ein Chat-Monitor sowie Bedienflaechen fuer konkrete Eingriffe vorhanden. Die Trennung gegenueber den anderen Dashboards ist sinnvoll, weil Moderation andere Daten, andere Risiken und andere Berechtigungen betrifft.

## Technisch erkennbare fachliche Kerntabellen

Aus den im Quellcode verwendeten SQL-Abfragen ergeben sich insbesondere diese zentralen Tabellen:

| Tabelle | Zweck |
|---|---|
| `users` | Grundlegende Benutzerkonten |
| `user_roles` | Rollenmodell fuer Streamer, Moderatoren und Manager |
| `streamer` | Fachlicher Streamer-Kontext |
| `moderator` | Moderatorbezogene Zuordnung |
| `streamer_manager` | Verknuepfung zwischen Managern und Streamern |
| `streamer_moderator` | Verknuepfung zwischen Moderatoren und Streamern |
| `stream_planung` | Planung kommender Streams und Events |
| `streamer_finances` | Einnahmen- und Ausgabenverwaltung |
| `streamer_todos` | Aufgabenverwaltung im Streamer-Dashboard |
| `twitch_tokens` | Twitch-Identitaetsdaten je Benutzer |

## Fazit zur Code-Struktur

Die Codebasis ist funktional in klar erkennbare Verantwortungsbereiche gegliedert: Einstieg, Session, Routing, GUI, Datenbank und externe API-Integration. Diese Struktur ist fuer eine schulische Projektanwendung absolut sinnvoll, weil sie Komplexitaet sichtbar aufteilt und spaetere Erweiterungen oder Fehlersuchen erleichtert.
