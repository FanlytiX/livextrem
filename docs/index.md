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

# liveXtrem

<div class="doc-hero">
  <img src="assets/images/logo.png" alt="liveXtrem Logo" style="max-width: 260px; margin-bottom: 1rem;">
  <p><strong>liveXtrem</strong> ist eine Desktop-Anwendung für kleine bis mittelgroße Streamer, die organisatorische und betriebswirtschaftliche Aufgaben nicht mehr auf mehrere Einzellösungen verteilen möchten. Die Software verbindet Streamplanung, Finanzverwaltung und Teamkoordination in einer gemeinsamen Arbeitsumgebung. Dadurch wird ein Bereich adressiert, für den viele bestehende Tools entweder zu technisch, zu teuer oder zu stark auf größere Creator-Teams zugeschnitten sind.</p>
</div>

<div class="badges">
  <img alt="Build" src="https://img.shields.io/badge/Build-Fertig-success">
  <img alt="Lizenz" src="https://img.shields.io/badge/Lizenz-MIT-blue">
  <img alt="Version" src="https://img.shields.io/badge/Version-1.0-informational">
  <img alt="Deployment" src="https://img.shields.io/badge/Deployment-fertig%20%2F%20nutzbar-brightgreen">
</div>

<div class="callout"><strong>Info:</strong> Diese Dokumentation ist für GitHub Pages aufgebaut. Bilder und Styles liegen bewusst in separaten Verzeichnissen, damit sie ohne Änderungen an den Markdown-Dateien ausgetauscht werden können.</div>

## Problemstellung

Kleine und mittelgroße Streaming-Kanäle arbeiten häufig mit improvisierten Werkzeugketten. Streamthemen werden in Notizen verwaltet, Einnahmen und Ausgaben in separaten Tabellen gepflegt und organisatorische Aufgaben zwischen Streamer, Moderation und Management manuell abgestimmt. Dieser Medienbruch führt zu doppelter Pflege, unklaren Verantwortlichkeiten und einer erhöhten Fehleranfälligkeit.

## Zielgruppe

Die Anwendung richtet sich primär an kleine bis mittelgroße Streamer, die ihren Kanal professioneller organisieren möchten, ohne dafür eine komplexe Enterprise-Lösung einzuführen. Gleichzeitig berücksichtigt liveXtrem, dass Streamer selten allein arbeiten. Moderatoren und Manager werden deshalb als eigenständige Rollen mit passenden Arbeitsbereichen mitgedacht.

## Lösungsansatz

liveXtrem bündelt organisatorische Kernprozesse in einer Anwendung mit rollenbezogenen Dashboards. Das Streamer-Dashboard deckt operative Themen wie To-do-Verwaltung, Content-Planung, Teamverwaltung und Finanzübersicht ab. Das Manager-Dashboard unterstützt bei Kalender- und Terminplanung, während das Moderator-Dashboard Twitch-nahe Moderationsaufgaben aufgreift und um einen Chat-Monitor auf Basis von VOD-Daten erweitert. Die Kombination aus lokaler Desktop-Oberfläche, Datenbankanbindung und Twitch-Integration schafft eine durchgängige Arbeitsumgebung statt isolierter Einzellösungen.

## Dokumentationsübersicht

Diese Dokumentation führt von der Einordnung des Produkts über die Installation und technische Vorbereitung bis zur Architektur, den zentralen Codebausteinen und der Bedienung. Sie ist so aufgebaut, dass sowohl fachliche Leser als auch technisch versierte Dritte die Anwendung nachvollziehen und einordnen können.

- [Installation](installation.md): Bezug der lauffähigen Windows-Version
- [Setup](setup.md): Vorbereitung für spätere Quellcode-, Datenbank- und API-Bereitstellung
- [Architektur](architecture.md): Aufbau des Systems und Zusammenspiel der Komponenten
- [API & Code](api.md): Dokumentation der wichtigsten Module, Klassen und Integrationsstellen
- [User Guide](user-guide.md): Nutzungsszenarien aus Sicht der Anwender
- [Technische Strategie](strategy.md): Begründung der Technologieentscheidungen und Workarounds
