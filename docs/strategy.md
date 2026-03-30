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

# Technische Strategie

<div class="callout"><strong>Info:</strong> Diese Dokumentation ist für GitHub Pages aufgebaut. Bilder und Styles liegen bewusst in separaten Verzeichnissen, damit sie ohne Änderungen an den Markdown-Dateien ausgetauscht werden können.</div>

## Technologie-Stack und Begründung

### Python als Basissprache

Das Projekt wurde in Python umgesetzt, weil das Team in dieser Sprache die größte praktische Erfahrung besitzt. Diese Entscheidung ist methodisch sinnvoll, denn Produktivität und Fehlervermeidung hängen in Projektarbeiten stark davon ab, ob ein Team seine Werkzeuge sicher beherrscht. Python erlaubt eine vergleichsweise schnelle Entwicklung, eine gut lesbare Struktur und eine problemlose Integration externer Bibliotheken für GUI, Datenbankzugriff und HTTP-Kommunikation.

Im Vergleich zu deutlich komplexeren Alternativen wie einer verteilten Web-Architektur mit Frontend-Framework und Backend-Service reduziert Python hier den organisatorischen und technischen Overhead. Für den gewählten Projektumfang überwiegt deshalb der Nutzen einer schnelleren, direkteren Umsetzung.

### CustomTkinter für die Benutzeroberfläche

Für die GUI wurde CustomTkinter eingesetzt. Gegenüber klassischem Tkinter bietet es eine modernere Optik, konsistentere Komponenten und mehr gestalterische Freiheit, ohne dass dafür ein vollwertiges Web-Frontend gebaut werden muss. Gerade für ein Projekt, das mehrere Dashboards mit unterschiedlicher Gewichtung und klaren Arbeitsbereichen besitzt, ist diese Flexibilität sinnvoll.

Eine Alternative wäre beispielsweise ein Web-Frontend auf Basis von React oder Vue gewesen. Das hätte langfristig Vorteile bei plattformunabhängiger Bereitstellung und responsivem Layout bieten können, wäre für dieses Projekt jedoch mit deutlich höherem Entwicklungsaufwand verbunden gewesen. Für eine fokussierte Desktop-Lösung war CustomTkinter deshalb die pragmatischere Wahl.

### MariaDB als relationale Datenbasis

Die Anwendung speichert ihre fachlichen Daten nicht in einfachen lokalen Dateien, sondern in einer relationalen Datenbank. Das ist für ein System mit Benutzern, Rollen, Teamzuordnungen, Finanzdaten und Planungsobjekten fachlich angemessen. Eine relationale Struktur unterstützt klare Beziehungen, Wiederverwendbarkeit von Daten und eine bessere Konsistenz als lose JSON-Dateien.

Alternativ wäre eine vollständig dateibasierte Lösung schneller aufgebaut gewesen, hätte aber bei Mehrbenutzerkontext, Datenintegrität und auswertbaren Beziehungen schnell Nachteile gezeigt. Gerade für Rollen- und Zuordnungslogik ist eine relationale Datenbank die robustere Grundlage.

## Bewertung nach Softwarequalitätskriterien

### Wartbarkeit

Die Codebasis ist in klar erkennbare Module gegliedert. Login, Routing, Konfiguration, Sicherheit, Datenbank und externe API-Integrationen sind voneinander getrennt. Diese Aufteilung erleichtert spätere Erweiterungen und reduziert das Risiko, dass jede Änderung Seiteneffekte in unzusammenhängenden Bereichen auslöst.

### Skalierbarkeit

liveXtrem ist nicht als massiv verteiltes Plattformprodukt konzipiert, sondern als fokussierte Desktop-Anwendung für ein konkretes Einsatzfeld. Innerhalb dieses Rahmens ist die Architektur dennoch skalierbar genug, weil Daten zentral gespeichert werden und Dashboards rollenspezifisch arbeiten. Würde das Projekt später zu einer größeren Plattform ausgebaut, wäre vor allem die Trennung zwischen GUI, Fachlogik und Datenhaltung ein guter Ausgangspunkt für weitere Modularisierung.

### Performance

Für den vorhandenen Funktionsumfang ist der gewählte Stack performant genug. Datenbankabfragen und HTTP-Aufrufe bleiben überschaubar, während eine lokale Desktop-Oberfläche unmittelbare Rückmeldung bietet. Kritisch sind vor allem externe Abhängigkeiten wie Twitch-Anfragen oder die Verarbeitung grosserer VOD-Daten. Diese Bereiche wurden bereits logisch gekapselt, was gezielte Optimierungen später erleichtert.

## Herausforderungen und Workarounds

### Sichere Behandlung von Zugangsdaten

Ein zentrales Thema ist der Umgang mit Konfigurationswerten wie Datenbankzugang und Twitch-Credentials. Das Projekt löst dies über ein Fallback-Modell aus Umgebungsvariablen und lokaler JSON-Datei. Für eine Demo- oder Messeumgebung ist das praktisch, weil nicht jeder Nutzer zuerst eine Shell-Konfiguration anlegen muss. Gleichzeitig bleibt das Prinzip erhalten, sensible Werte aus dem Hauptcode herauszuhalten.

### OAuth in einer Desktop-Anwendung

Die Twitch-Anmeldung wird über einen Browser-Flow mit lokalem Callback gelöst. Das ist in Desktop-Projekten anspruchsvoller als in klassischen Webanwendungen, weil Browser, lokaler HTTP-Server und Programmlogik sauber zusammenspielen müssen. Der implementierte Ansatz mit lokalem Callback auf `localhost` ist fachlich nachvollziehbar und für den Einsatzzweck geeignet.

### Rollen- und Kontextlogik

Eine inhaltlich anspruchsvolle Aufgabe ist die Trennung zwischen technischer Benutzerrolle und fachlichem Streamer-Kontext. liveXtrem löst das über eine Session-Struktur, die nicht nur den Benutzer identifiziert, sondern auch festhält, für welchen Streamer fachlich gearbeitet wird. Dadurch bleiben Rollenwechsel konsistent und Daten werden nicht versehentlich im falschen Kontext angezeigt.

### Umgang mit bekannten Desktop-Problemen

Bei Python-Desktop-Anwendungen treten in der Praxis häufig Themen wie Packaging, Theme-Dateien, DPI-Skalierung oder Callback-Verhalten auf. Die Projektstruktur zeigt bereits, dass solche Punkte bewusst behandelt wurden, etwa durch zentrale Theme-Dateien, getrennte Konfiguration und klar abgegrenzte Startlogik. Das ist kein glamouröser Teil der Softwareentwicklung, aber genau dort entscheidet sich oft, ob eine Anwendung in der Praxis stabil wirkt oder auseinanderfällt wie ein billiger Gartenstuhl.

## Gesamtbewertung der Strategie

Die technische Strategie von liveXtrem ist bewusst pragmatisch: Sie setzt auf bekannte Werkzeuge, klare Verantwortungsbereiche und einen Architekturzuschnitt, der zum Projektziel passt. Für eine schulische Projektarbeit ist das kein Mangel an Ambition, sondern eine vernünftige Ingenieursentscheidung. Die gewählte Kombination aus Python, CustomTkinter, MariaDB und Twitch-Integration ermöglicht einen sichtbaren Nutzen, ohne das Projekt durch unnötige technologische Komplexität zu überladen.
