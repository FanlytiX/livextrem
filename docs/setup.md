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

# Setup

{% include info.md %}

## Zweck dieser Seite

Diese Seite ist bewusst als vorbereitender Bereich fuer die technische Einrichtung des Projekts angelegt. Sie trennt die sofort nutzbare Windows-Installation von den Schritten, die fuer eine Entwicklungs- oder Administrationsumgebung relevant sind. Damit bleibt die Dokumentation sauber strukturiert: Anwender koennen die fertige Anwendung direkt installieren, waehrend technische Leser spaeter hier alle Informationen fuer Datenbank, API-Anbindung und Quellcodebezug vorfinden.

## Geplanter Umfang des technischen Setups

Der Ausbau dieses Abschnitts ist fuer drei Konfigurationsfelder vorgesehen. Die folgenden Unterkapitel sind bereits so formuliert, dass sie spaeter ohne strukturelle Aenderungen mit konkreten Werten, Screenshots oder Tabellen ergaenzt werden koennen.

### 1. Datenbankinstallation und Datenbankzugang

liveXtrem arbeitet mit einer relationalen Datenbank, in der Benutzerkonten, Rollen, Streamplanung, Finanzdaten und Teamzuordnungen abgelegt werden. Fuer eine vollstaendige Setup-Dokumentation muss hier spaeter beschrieben werden,

- welches Datenbanksystem verwendet wird,
- wie eine Instanz bereitgestellt oder verbunden wird,
- welche Tabellen oder Initialdaten benoetigt werden und
- wie Verbindungsdaten sicher hinterlegt werden.

Bereits aus dem Projekt ist erkennbar, dass die Anwendung Datenbankparameter wie Host, Port, Datenbankname, Benutzername und Passwort erwartet. Diese Angaben sollten in einer produktiven Dokumentation nicht als Klartext in den Quellcode geschrieben, sondern ueber eine lokale Konfigurationsdatei oder ueber Umgebungsvariablen gesetzt werden.

### 2. API-Anmeldung und Twitch-Konfiguration

Ein Teil des Funktionsumfangs setzt eine Verbindung zur Twitch-API voraus. Dazu gehoeren insbesondere OAuth-Anmeldung, das Lesen kanalbezogener Daten und Moderationsfunktionen. Spaeter sollten an dieser Stelle die erforderlichen Schritte fuer die Registrierung einer Twitch-Anwendung beschrieben werden, inklusive Redirect-URI, benoetigter Scopes und einer nachvollziehbaren Einordnung, wofuer die einzelnen Berechtigungen benoetigt werden.

Wichtig ist dabei der Sicherheitsaspekt: Client-ID und insbesondere Client-Secret sind keine Inhalte fuer oeffentliche Dokumentationsbeispiele mit echten Werten. Stattdessen sollte die Seite erklaeren, wo diese Daten lokal eingetragen werden und wie verhindert wird, dass sie versehentlich mit veroeffentlicht werden.

### 3. Projektbezug fuer eine Quellcode-Umgebung

Neben der lauffaehigen `exe` ist fuer die technische Weiterentwicklung ein Quellcode-Setup relevant. Dieser Teil sollte spaeter dokumentieren,

- wie das Repository bezogen wird,
- welche Python-Version vorgesehen ist,
- welche Bibliotheken installiert werden muessen und
- wie das Projekt lokal gestartet wird.

Aus dem Projekt ergeben sich bereits erkennbare Kernabhaengigkeiten wie `customtkinter`, `Pillow`, `mariadb`, `mysql.connector`, `requests` sowie optional `tkcalendar` und `reportlab`. Fuer eine spaetere Erweiterung dieser Seite bietet sich deshalb eine reproduzierbare Installationsanleitung mit `requirements.txt` oder einer vergleichbaren Paketliste an.

## Konfigurationsprinzip des Projekts

Das Projekt nutzt kein klassisches `.env`-Pflichtmodell, sondern eine Kombination aus Umgebungsvariablen und einer lokalen JSON-Konfiguration. In `config.py` ist festgelegt, dass Umgebungsvariablen Vorrang haben. Falls diese nicht vorhanden sind, wird eine lokale Datei `config_local.json` als Fallback gelesen. Dieses Vorgehen ist fuer eine Desktop-Demo praktisch, weil dadurch auch weniger erfahrene Nutzer ohne Shell-Konfiguration arbeiten koennen.

Die fachlich saubere Dokumentation dieses Mechanismus ist wichtig, weil er denselben Zweck wie eine `.env`-Datei erfuellt: sensible oder installationsspezifische Werte werden von der eigentlichen Programmlogik getrennt. Fuer eine spaetere Ausbaustufe sollten hier Beispielstrukturen mit Platzhaltern und ein klarer Hinweis zur sicheren Aufbewahrung von Zugangsdaten ergaenzt werden.

{% include warning.md %}

## Empfohlene spaetere Ergaenzungen

Sobald Datenbankskripte, API-Registrierungsdaten und ein finaler Source-Setup-Prozess vorliegen, sollte diese Seite um konkrete Befehle, Screenshots und Beispielkonfigurationen ergaenzt werden. Die Struktur dieser Dokumentation ist bereits darauf vorbereitet, sodass die Inhalte spaeter direkt an der passenden Stelle eingepflegt werden koennen, ohne den Gesamtaufbau neu gestalten zu muessen.
