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

# Installation

<div class="callout"><strong>Info:</strong> Diese Dokumentation ist für GitHub Pages aufgebaut. Bilder und Styles liegen bewusst in separaten Verzeichnissen, damit sie ohne Änderungen an den Markdown-Dateien ausgetauscht werden können.</div>

## Ziel dieses Abschnitts

Diese Seite beschreibt die Inbetriebnahme der bereitgestellten Windows-Version von liveXtrem. Der Fokus liegt bewusst auf der lauffähigen Anwendung und nicht auf einer Entwicklungsumgebung. Damit kann die Software ohne Build-Prozess getestet und genutzt werden, was insbesondere für Vorführungen, Abgaben und eine unkomplizierte Erstinstallation sinnvoll ist.

## Voraussetzungen

- Windows 10 oder neuer
- Berechtigung, ZIP-Dateien zu entpacken und eine Desktop-Verknüpfung anzulegen
- Ein Zielverzeichnis, in dem die Anwendung dauerhaft abgelegt bleibt

Da die Anwendung als vorkompilierte `exe` bereitgestellt wird, müssen auf dem Zielsystem keine Python-Abhängigkeiten manuell installiert werden. Wichtig ist jedoch, dass die entpackte Ordnerstruktur erhalten bleibt. Die Datei `livextrem.exe` darf nicht aus ihrem Verzeichnis herauskopiert werden, weil die Anwendung auf zusätzliche Dateien im gleichen Projektordner zugreift.

## Download

<a class="download-button" href="https://github.com/FanlytiX/livextrem/blob/main/livextrem_v1.0.zip">livextrem_v1.0.zip herunterladen</a>

## Schritt-für-Schritt-Anleitung

### 1. Archiv herunterladen

Laden Sie zunächst die Datei `livextrem_v1.0.zip` aus dem Repository herunter. Das Archiv enthält die lauffähige Anwendung mitsamt der benötigten Begleitdateien.

### 2. Archiv an einem festen Speicherort entpacken

Entpacken Sie den heruntergeladenen ZIP-Ordner in ein Verzeichnis, das nicht versehentlich verschoben oder gelöscht wird. Als praktikable Ablage eignet sich beispielsweise ein Unterordner im Laufwerk `C:` innerhalb des Programmverzeichnisses. Der Hintergrund ist simpel: liveXtrem arbeitet nicht nur mit der `exe`, sondern auch mit weiteren Dateien, die relativ zu diesem Speicherort gefunden werden müssen.

### 3. Verknüpfung zur Anwendung erstellen

Öffnen Sie den entpackten Ordner und suchen Sie die Datei `livextrem.exe`. Erstellen Sie von dieser Datei eine Verknüpfung und legen Sie diese auf dem Desktop ab. So bleibt die eigentliche Anwendung an ihrem vorgesehenen Ort, während der Start im Alltag bequem über die Verknüpfung erfolgt.

### 4. Anwendung starten

Starten Sie liveXtrem anschließend über die erstellte Desktop-Verknüpfung. Die Anwendung sollte nun ohne weitere Installationsschritte geöffnet werden können.

## Warum die `exe` im Ordner bleiben muss

Desktop-Anwendungen dieser Art werden häufig zusammen mit weiteren Ressourcen ausgeliefert, etwa Bildern, Theme-Dateien oder Konfigurationen. Wird nur die eigentliche Programmdatei verschoben, fehlen diese Abhängigkeiten am erwarteten Speicherort. Die Folge sind Startprobleme oder unvollständige Oberflächen. Die saubere Vorgehensweise besteht deshalb darin, stets den gesamten entpackten Ordner an seinem Platz zu belassen und lediglich eine Verknüpfung zu nutzen.

<div class="callout warning"><strong>Wichtig:</strong> Zugangsdaten, Datenbankpasswörter und API-Keys gehören nicht in ein öffentliches Repository. In der Dokumentation werden deshalb nur Platzhalter und sichere Konfigurationsmuster beschrieben.</div>

## Abgrenzung zur Entwicklerinstallation

Die bereitgestellte ZIP-Datei dient der Nutzung der fertigen Anwendung. Informationen zur späteren Einrichtung von Datenbank, API-Zugängen und einem möglichen Quellcode-Setup werden getrennt auf der Seite [Setup](setup.md) vorbereitet, damit Installation und technische Konfiguration nicht vermischt werden.
