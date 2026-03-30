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

# API und Code-Struktur

<div class="callout"><strong>Info:</strong> Diese Dokumentation ist für GitHub Pages aufgebaut. Bilder und Styles liegen bewusst in separaten Verzeichnissen, damit sie ohne Änderungen an den Markdown-Dateien ausgetauscht werden können.</div>

## Einordnung

liveXtrem stellt keine klassische Web-API mit öffentlichen REST-Endpunkten bereit. Stattdessen basiert die Anwendung auf einer internen Modul- und Funktionsschnittstelle. Für die technische Dokumentation ist deshalb nicht die URL-Struktur einer Serveranwendung entscheidend, sondern die Frage, welche Module welche Verantwortung tragen und wie Daten zwischen GUI, Datenbank und Twitch-Integration fliessen.

## Einstieg und Steuerung

### `login.py`

Dieses Modul bildet den Einstieg in das Anwendungssystem. Es verwaltet die Login-Oberfläche, führt Benutzeranmeldung und Registrierung durch und erzeugt nach erfolgreicher Authentifizierung ein Sitzungsobjekt. Bemerkenswert ist, dass Dashboards nicht aus einem Hintergrundthread gestartet werden, sondern sauber über den Main-Thread, was für Tkinter-basierte Anwendungen wichtig ist.

### `session_user.py`

`SessionUser` und `TwitchIdentity` modellieren die aktuell angemeldete Sitzung. Neben den offensichtlichen Benutzerdaten enthält die Session auch fachliche Informationen wie den aktiven Streamer-Kontext und Berechtigungen für Manager- oder Moderator-Dashboards. Diese Kapselung vereinfacht rollenbezogene Entscheidungen in der gesamten Anwendung.

### `router.py`

Der Router ist die Vermittlungsschicht zwischen Login und Fachoberfläche. Er entscheidet, welches Dashboard geöffnet wird, und prüft dabei zugleich Rollenrechte. Die Datei ist klein, aber architektonisch wichtig, weil sie die Startlogik zentralisiert und direkte Kopplungen reduziert.

## Konfiguration und Sicherheit

### `config.py`

Das Konfigurationsmodul liest Datenbank- und Twitch-Parameter entweder aus Umgebungsvariablen oder aus einer lokalen JSON-Datei. Es validiert ausserdem, ob alle Pflichtwerte vorhanden sind. Dadurch wird Konfiguration nicht über den Code verteilt, sondern an einer zentralen Stelle kontrolliert.

### `security.py`

Dieses Modul kümmert sich um die Passwortverarbeitung. Neue Passwörter werden mit PBKDF2-SHA256 und Salt gehasht. Zusätzlich ist eine Rückwärtskompatibilität für ältere SHA256-Hashes vorgesehen, sodass bestehende Daten migriert werden können, ohne Benutzerkonten unbrauchbar zu machen. Für eine Desktop-Anwendung ist das eine erfreulich saubere Sicherheitsentscheidung, weil Klartextpasswörter und triviale Hashes vermieden werden.

## Datenbankzugriff

### `database_connection.py`

Hier wird die technische Verbindung zur MariaDB aufgebaut. Das Modul stellt Hilfsfunktionen bereit, um Abfragen auszuführen, Tabelleninformationen auszulesen und Verbindungen wieder sauber zu schliessen. Es dient als Basis für höherliegende Abfragemodule.

### `database_queries.py`

Dieses Modul enthält Datenbanklogik für fachliche Abfragen rund um Benutzer- und Streamer-bezogene Daten. Dazu gehören aus Sicht des Projekts insbesondere Daten, die für Dashboards und Auswertungen gebraucht werden. Die Trennung in ein eigenes Query-Modul verhindert, dass SQL-Logik direkt in GUI-Ereignisfunktionen verteilt wird.

### `database_queries_moderator.py`

Die Moderator-Logik kombiniert lokale Historienverwaltung mit Twitch-bezogenen Moderationsfunktionen. Hier werden Chat-Nachrichten aus VODs aufbereitet, Moderationsaktionen lokal festgehalten und fachlich relevante Rückgabestrukturen für das Dashboard erzeugt. Der entscheidende Vorteil liegt darin, dass die GUI nicht direkt mit Rohantworten der Twitch-API arbeiten muss.

## Twitch-nahe Funktionsmodule

### `fremdsys/oauth.py`

Dieses Modul implementiert den OAuth-Prozess für Twitch. Es startet einen lokalen HTTP-Callback, öffnet den Browser für die Anmeldung, tauscht den Authorization Code gegen Tokens aus und liest anschließend Benutzerinformationen aus. Die Lösung ist für eine Desktop-Anwendung geeignet, weil sie keinen separaten Webserver voraussetzt und den Login dennoch sauber über den offiziellen OAuth-Flow abwickelt.

### `fremdsys/tapi_data.py`

Hier liegen datenorientierte Twitch-Funktionen wie das Laden vergangener Streams, Follower- und Subscriber-Daten oder Kennzahlen zu VOD-Aufrufen. Diese Schnittstelle ist vor allem für analytische oder informationsbezogene Oberflächen relevant.

### `fremdsys/tapi_mod.py`

Dieses Modul kapselt Moderationsfunktionen wie das Laden von VOD-Chatdaten sowie Ban-, Timeout- und Unban-Aktionen. Fachlich ist dies die Brücke zwischen LiveXtrem und den Twitch-Moderationsschnittstellen.

## Zentrale GUI-Module

### `streamer_dashboard.py`

Das Streamer-Dashboard vereint mehrere Fachbereiche in einer Oberfläche. Sichtbar sind unter anderem To-do-Liste, nächster Stream, geplante Streams, KI-Content-Assistent, Finanzbuchungen mit CSV- und PDF-Export sowie Team- und Rollenverwaltung. Das Modul ist dadurch kein reines View-Element, sondern ein zentraler Anwendungsknoten.

### `manager_gui.py`

Das Manager-Dashboard ist auf Termin- und Ressourcenkoordination ausgerichtet. Im Code sichtbar sind ein eigener `DataManager`, Kalendernavigation, Eventdialoge und Streamer-Verwaltung. Die Struktur deutet auf einen klaren Anwendungsfall hin: Management-Aufgaben sollen ohne Zugriff auf alle Streamer-Daten pauschal möglich sein, sondern immer innerhalb zugänglicher Zuständigkeiten.

### `moderator_dashboard.py`

Dieses Modul bildet die Bedienlogik für Moderatoren ab. Neben einer Übersicht über Statistik und Historie sind ein Chat-Monitor sowie Bedienflächen für konkrete Eingriffe vorhanden. Die Trennung gegenüber den anderen Dashboards ist sinnvoll, weil Moderation andere Daten, andere Risiken und andere Berechtigungen betrifft.

## Technisch erkennbare fachliche Kerntabellen

Aus den im Quellcode verwendeten SQL-Abfragen ergeben sich insbesondere diese zentralen Tabellen:

| Tabelle | Zweck |
|---|---|
| `users` | Grundlegende Benutzerkonten |
| `user_roles` | Rollenmodell für Streamer, Moderatoren und Manager |
| `streamer` | Fachlicher Streamer-Kontext |
| `moderator` | Moderatorbezogene Zuordnung |
| `streamer_manager` | Verknüpfung zwischen Managern und Streamern |
| `streamer_moderator` | Verknüpfung zwischen Moderatoren und Streamern |
| `stream_planung` | Planung kommender Streams und Events |
| `streamer_finances` | Einnahmen- und Ausgabenverwaltung |
| `streamer_todos` | Aufgabenverwaltung im Streamer-Dashboard |
| `twitch_tokens` | Twitch-Identitätsdaten je Benutzer |

## Fazit zur Code-Struktur

Die Codebasis ist funktional in klar erkennbare Verantwortungsbereiche gegliedert: Einstieg, Session, Routing, GUI, Datenbank und externe API-Integration. Diese Struktur ist für eine schulische Projektanwendung absolut sinnvoll, weil sie Komplexität sichtbar aufteilt und spätere Erweiterungen oder Fehlersuchen erleichtert.
