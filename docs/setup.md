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

# Setup

<div class="callout"><strong>Info:</strong> Diese Dokumentation ist für GitHub Pages aufgebaut. Bilder und Styles liegen bewusst in separaten Verzeichnissen, damit sie ohne Änderungen an den Markdown-Dateien ausgetauscht werden können.</div>

## Zweck dieser Seite

Diese Seite ist bewusst als vorbereitender Bereich für die technische Einrichtung des Projekts angelegt. Sie trennt die sofort nutzbare Windows-Installation von den Schritten, die für eine Entwicklungs- oder Administrationsumgebung relevant sind. Damit bleibt die Dokumentation sauber strukturiert: Anwender können die fertige Anwendung direkt installieren, während technische Leser später hier alle Informationen für Datenbank, API-Anbindung und Quellcodebezug vorfinden.

## Geplanter Umfang des technischen Setups

Der Ausbau dieses Abschnitts ist für drei Konfigurationsfelder vorgesehen. Die folgenden Unterkapitel sind bereits so formuliert, dass sie später ohne strukturelle Änderungen mit konkreten Werten, Screenshots oder Tabellen ergänzt werden können.

### 1. Datenbankinstallation und Datenbankzugang

liveXtrem arbeitet mit einer relationalen Datenbank, in der Benutzerkonten, Rollen, Streamplanung, Finanzdaten und Teamzuordnungen abgelegt werden. Für eine vollständige Setup-Dokumentation muss hier später beschrieben werden,

- welches Datenbanksystem verwendet wird,
- wie eine Instanz bereitgestellt oder verbunden wird,
- welche Tabellen oder Initialdaten benötigt werden und
- wie Verbindungsdaten sicher hinterlegt werden.

Bereits aus dem Projekt ist erkennbar, dass die Anwendung Datenbankparameter wie Host, Port, Datenbankname, Benutzername und Passwort erwartet. Diese Angaben sollten in einer produktiven Dokumentation nicht als Klartext in den Quellcode geschrieben, sondern über eine lokale Konfigurationsdatei oder über Umgebungsvariablen gesetzt werden.

### 2. API-Anmeldung und Twitch-Konfiguration

Ein Teil des Funktionsumfangs setzt eine Verbindung zur Twitch-API voraus. Dazu gehören insbesondere OAuth-Anmeldung, das Lesen kanalbezogener Daten und Moderationsfunktionen. Später sollten an dieser Stelle die erforderlichen Schritte für die Registrierung einer Twitch-Anwendung beschrieben werden, inklusive Redirect-URI, benötigter Scopes und einer nachvollziehbaren Einordnung, wofür die einzelnen Berechtigungen benötigt werden.

Wichtig ist dabei der Sicherheitsaspekt: Client-ID und insbesondere Client-Secret sind keine Inhalte für öffentliche Dokumentationsbeispiele mit echten Werten. Stattdessen sollte die Seite erklären, wo diese Daten lokal eingetragen werden und wie verhindert wird, dass sie versehentlich mit veröffentlicht werden.

### 3. Projektbezug für eine Quellcode-Umgebung

Neben der lauffähigen `exe` ist für die technische Weiterentwicklung ein Quellcode-Setup relevant. Dieser Teil sollte später dokumentieren,

- wie das Repository bezogen wird,
- welche Python-Version vorgesehen ist,
- welche Bibliotheken installiert werden müssen und
- wie das Projekt lokal gestartet wird.

Aus dem Projekt ergeben sich bereits erkennbare Kernabhängigkeiten wie `customtkinter`, `Pillow`, `mariadb`, `mysql.connector`, `requests` sowie optional `tkcalendar` und `reportlab`. Für eine spätere Erweiterung dieser Seite bietet sich deshalb eine reproduzierbare Installationsanleitung mit `requirements.txt` oder einer vergleichbaren Paketliste an.

## Konfigurationsprinzip des Projekts

Das Projekt nutzt kein klassisches `.env`-Pflichtmodell, sondern eine Kombination aus Umgebungsvariablen und einer lokalen JSON-Konfiguration. In `config.py` ist festgelegt, dass Umgebungsvariablen Vorrang haben. Falls diese nicht vorhanden sind, wird eine lokale Datei `config_local.json` als Fallback gelesen. Dieses Vorgehen ist für eine Desktop-Demo praktisch, weil dadurch auch weniger erfahrene Nutzer ohne Shell-Konfiguration arbeiten können.

Die fachlich saubere Dokumentation dieses Mechanismus ist wichtig, weil er denselben Zweck wie eine `.env`-Datei erfüllt: sensible oder installationsspezifische Werte werden von der eigentlichen Programmlogik getrennt. Für eine spätere Ausbaustufe sollten hier Beispielstrukturen mit Platzhaltern und ein klarer Hinweis zur sicheren Aufbewahrung von Zugangsdaten ergänzt werden.

<div class="callout warning"><strong>Wichtig:</strong> Zugangsdaten, Datenbankpasswörter und API-Keys gehören nicht in ein öffentliches Repository. In der Dokumentation werden deshalb nur Platzhalter und sichere Konfigurationsmuster beschrieben.</div>

## Empfohlene spätere Ergänzungen

Sobald Datenbankskripte, API-Registrierungsdaten und ein finaler Source-Setup-Prozess vorliegen, sollte diese Seite um konkrete Befehle, Screenshots und Beispielkonfigurationen ergänzt werden. Die Struktur dieser Dokumentation ist bereits darauf vorbereitet, sodass die Inhalte später direkt an der passenden Stelle eingepflegt werden können, ohne den Gesamtaufbau neu gestalten zu müssen.
