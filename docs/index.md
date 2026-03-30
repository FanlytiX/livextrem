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

# liveXtrem

<div class="doc-hero">
  <img src="{{ '/assets/images/logo.png' | relative_url }}" alt="liveXtrem Logo" style="max-width: 260px; margin-bottom: 1rem;">
  <p><strong>liveXtrem</strong> ist eine Desktop-Anwendung fuer kleine bis mittelgrosse Streamer, die organisatorische und betriebswirtschaftliche Aufgaben nicht mehr auf mehrere Einzelloesungen verteilen moechten. Die Software verbindet Streamplanung, Finanzverwaltung und Teamkoordination in einer gemeinsamen Arbeitsumgebung. Dadurch wird ein Bereich adressiert, fuer den viele bestehende Tools entweder zu technisch, zu teuer oder zu stark auf groessere Creator-Teams zugeschnitten sind.</p>
</div>

<div class="badges">
  <img alt="Build" src="https://img.shields.io/badge/Build-Fertig-success">
  <img alt="Lizenz" src="https://img.shields.io/badge/Lizenz-MIT-blue">
  <img alt="Version" src="https://img.shields.io/badge/Version-1.0-informational">
  <img alt="Deployment" src="https://img.shields.io/badge/Deployment-fertig%20%2F%20nutzbar-brightgreen">
</div>

{% include info.md %}

## Problemstellung

Kleine und mittelgrosse Streaming-Kanaele arbeiten haeufig mit improvisierten Werkzeugketten. Streamthemen werden in Notizen verwaltet, Einnahmen und Ausgaben in separaten Tabellen gepflegt und organisatorische Aufgaben zwischen Streamer, Moderation und Management manuell abgestimmt. Dieser Medienbruch fuehrt zu doppelter Pflege, unklaren Verantwortlichkeiten und einer erhoehten Fehleranfaelligkeit.

## Zielgruppe

Die Anwendung richtet sich primaer an kleine bis mittelgrosse Streamer, die ihren Kanal professioneller organisieren moechten, ohne dafuer eine komplexe Enterprise-Loesung einzufuehren. Gleichzeitig beruecksichtigt liveXtrem, dass Streamer selten allein arbeiten. Moderatoren und Manager werden deshalb als eigenstaendige Rollen mit passenden Arbeitsbereichen mitgedacht.

## Loesungsansatz

liveXtrem buendelt organisatorische Kernprozesse in einer Anwendung mit rollenbezogenen Dashboards. Das Streamer-Dashboard deckt operative Themen wie To-do-Verwaltung, Content-Planung, Teamverwaltung und Finanzuebersicht ab. Das Manager-Dashboard unterstuetzt bei Kalender- und Terminplanung, waehrend das Moderator-Dashboard Twitch-nahe Moderationsaufgaben aufgreift und um einen Chat-Monitor auf Basis von VOD-Daten erweitert. Die Kombination aus lokaler Desktop-Oberflaeche, Datenbankanbindung und Twitch-Integration schafft eine durchgaengige Arbeitsumgebung statt isolierter Einzelloesungen.

## Dokumentationsuebersicht

Diese Dokumentation fuehrt von der Einordnung des Produkts ueber die Installation und technische Vorbereitung bis zur Architektur, den zentralen Codebausteinen und der Bedienung. Sie ist so aufgebaut, dass sowohl fachliche Leser als auch technisch versierte Dritte die Anwendung nachvollziehen und einordnen koennen.

- [Installation](installation.md): Bezug der lauffaehigen Windows-Version
- [Setup](setup.md): Vorbereitung fuer spaetere Quellcode-, Datenbank- und API-Bereitstellung
- [Architektur](architecture.md): Aufbau des Systems und Zusammenspiel der Komponenten
- [API & Code](api.md): Dokumentation der wichtigsten Module, Klassen und Integrationsstellen
- [User Guide](user-guide.md): Nutzungsszenarien aus Sicht der Anwender
- [Technische Strategie](strategy.md): Begruendung der Technologieentscheidungen und Workarounds
