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

# Technische Strategie

{% include info.md %}

## Technologie-Stack und Begruendung

### Python als Basissprache

Das Projekt wurde in Python umgesetzt, weil das Team in dieser Sprache die groesste praktische Erfahrung besitzt. Diese Entscheidung ist methodisch sinnvoll, denn Produktivitaet und Fehlervermeidung haengen in Projektarbeiten stark davon ab, ob ein Team seine Werkzeuge sicher beherrscht. Python erlaubt eine vergleichsweise schnelle Entwicklung, eine gut lesbare Struktur und eine problemlose Integration externer Bibliotheken fuer GUI, Datenbankzugriff und HTTP-Kommunikation.

Im Vergleich zu deutlich komplexeren Alternativen wie einer verteilten Web-Architektur mit Frontend-Framework und Backend-Service reduziert Python hier den organisatorischen und technischen Overhead. Fuer den gewaehlten Projektumfang ueberwiegt deshalb der Nutzen einer schnelleren, direkteren Umsetzung.

### CustomTkinter fuer die Benutzeroberflaeche

Fuer die GUI wurde CustomTkinter eingesetzt. Gegenueber klassischem Tkinter bietet es eine modernere Optik, konsistentere Komponenten und mehr gestalterische Freiheit, ohne dass dafuer ein vollwertiges Web-Frontend gebaut werden muss. Gerade fuer ein Projekt, das mehrere Dashboards mit unterschiedlicher Gewichtung und klaren Arbeitsbereichen besitzt, ist diese Flexibilitaet sinnvoll.

Eine Alternative waere beispielsweise ein Web-Frontend auf Basis von React oder Vue gewesen. Das haette langfristig Vorteile bei plattformunabhaengiger Bereitstellung und responsivem Layout bieten koennen, waere fuer dieses Projekt jedoch mit deutlich hoeherem Entwicklungsaufwand verbunden gewesen. Fuer eine fokussierte Desktop-Loesung war CustomTkinter deshalb die pragmatischere Wahl.

### MariaDB als relationale Datenbasis

Die Anwendung speichert ihre fachlichen Daten nicht in einfachen lokalen Dateien, sondern in einer relationalen Datenbank. Das ist fuer ein System mit Benutzern, Rollen, Teamzuordnungen, Finanzdaten und Planungsobjekten fachlich angemessen. Eine relationale Struktur unterstuetzt klare Beziehungen, Wiederverwendbarkeit von Daten und eine bessere Konsistenz als lose JSON-Dateien.

Alternativ waere eine vollstaendig dateibasierte Loesung schneller aufgebaut gewesen, haette aber bei Mehrbenutzerkontext, Datenintegritaet und auswertbaren Beziehungen schnell Nachteile gezeigt. Gerade fuer Rollen- und Zuordnungslogik ist eine relationale Datenbank die robustere Grundlage.

## Bewertung nach Softwarequalitaetskriterien

### Wartbarkeit

Die Codebasis ist in klar erkennbare Module gegliedert. Login, Routing, Konfiguration, Sicherheit, Datenbank und externe API-Integrationen sind voneinander getrennt. Diese Aufteilung erleichtert spaetere Erweiterungen und reduziert das Risiko, dass jede Aenderung Seiteneffekte in unzusammenhaengenden Bereichen ausloest.

### Skalierbarkeit

liveXtrem ist nicht als massiv verteiltes Plattformprodukt konzipiert, sondern als fokussierte Desktop-Anwendung fuer ein konkretes Einsatzfeld. Innerhalb dieses Rahmens ist die Architektur dennoch skalierbar genug, weil Daten zentral gespeichert werden und Dashboards rollenspezifisch arbeiten. Wuerde das Projekt spaeter zu einer groesseren Plattform ausgebaut, waere vor allem die Trennung zwischen GUI, Fachlogik und Datenhaltung ein guter Ausgangspunkt fuer weitere Modularisierung.

### Performance

Fuer den vorhandenen Funktionsumfang ist der gewaehlte Stack performant genug. Datenbankabfragen und HTTP-Aufrufe bleiben ueberschaubar, waehrend eine lokale Desktop-Oberflaeche unmittelbare Rueckmeldung bietet. Kritisch sind vor allem externe Abhaengigkeiten wie Twitch-Anfragen oder die Verarbeitung grosserer VOD-Daten. Diese Bereiche wurden bereits logisch gekapselt, was gezielte Optimierungen spaeter erleichtert.

## Herausforderungen und Workarounds

### Sichere Behandlung von Zugangsdaten

Ein zentrales Thema ist der Umgang mit Konfigurationswerten wie Datenbankzugang und Twitch-Credentials. Das Projekt loest dies ueber ein Fallback-Modell aus Umgebungsvariablen und lokaler JSON-Datei. Fuer eine Demo- oder Messeumgebung ist das praktisch, weil nicht jeder Nutzer zuerst eine Shell-Konfiguration anlegen muss. Gleichzeitig bleibt das Prinzip erhalten, sensible Werte aus dem Hauptcode herauszuhalten.

### OAuth in einer Desktop-Anwendung

Die Twitch-Anmeldung wird ueber einen Browser-Flow mit lokalem Callback geloest. Das ist in Desktop-Projekten anspruchsvoller als in klassischen Webanwendungen, weil Browser, lokaler HTTP-Server und Programmlogik sauber zusammenspielen muessen. Der implementierte Ansatz mit lokalem Callback auf `localhost` ist fachlich nachvollziehbar und fuer den Einsatzzweck geeignet.

### Rollen- und Kontextlogik

Eine inhaltlich anspruchsvolle Aufgabe ist die Trennung zwischen technischer Benutzerrolle und fachlichem Streamer-Kontext. liveXtrem loest das ueber eine Session-Struktur, die nicht nur den Benutzer identifiziert, sondern auch festhaelt, fuer welchen Streamer fachlich gearbeitet wird. Dadurch bleiben Rollenwechsel konsistent und Daten werden nicht versehentlich im falschen Kontext angezeigt.

### Umgang mit bekannten Desktop-Problemen

Bei Python-Desktop-Anwendungen treten in der Praxis haeufig Themen wie Packaging, Theme-Dateien, DPI-Skalierung oder Callback-Verhalten auf. Die Projektstruktur zeigt bereits, dass solche Punkte bewusst behandelt wurden, etwa durch zentrale Theme-Dateien, getrennte Konfiguration und klar abgegrenzte Startlogik. Das ist kein glamouroeser Teil der Softwareentwicklung, aber genau dort entscheidet sich oft, ob eine Anwendung in der Praxis stabil wirkt oder auseinanderfaellt wie ein billiger Gartenstuhl.

## Gesamtbewertung der Strategie

Die technische Strategie von liveXtrem ist bewusst pragmatisch: Sie setzt auf bekannte Werkzeuge, klare Verantwortungsbereiche und einen Architekturzuschnitt, der zum Projektziel passt. Fuer eine schulische Projektarbeit ist das kein Mangel an Ambition, sondern eine vernuenftige Ingenieursentscheidung. Die gewaehltе Kombination aus Python, CustomTkinter, MariaDB und Twitch-Integration ermoeglicht einen sichtbaren Nutzen, ohne das Projekt durch unnötige technologische Komplexitaet zu ueberladen.
