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

# Installation

{% include info.md %}

## Ziel dieses Abschnitts

Diese Seite beschreibt die Inbetriebnahme der bereitgestellten Windows-Version von liveXtrem. Der Fokus liegt bewusst auf der lauffaehigen Anwendung und nicht auf einer Entwicklungsumgebung. Damit kann die Software ohne Build-Prozess getestet und genutzt werden, was insbesondere fuer Vorfuehrungen, Abgaben und eine unkomplizierte Erstinstallation sinnvoll ist.

## Voraussetzungen

- Windows 10 oder neuer
- Berechtigung, ZIP-Dateien zu entpacken und eine Desktop-Verknuepfung anzulegen
- Ein Zielverzeichnis, in dem die Anwendung dauerhaft abgelegt bleibt

Da die Anwendung als vorkompilierte `exe` bereitgestellt wird, muessen auf dem Zielsystem keine Python-Abhaengigkeiten manuell installiert werden. Wichtig ist jedoch, dass die entpackte Ordnerstruktur erhalten bleibt. Die Datei `livextrem.exe` darf nicht aus ihrem Verzeichnis herauskopiert werden, weil die Anwendung auf zusaetzliche Dateien im gleichen Projektordner zugreift.

## Download

<a class="download-button" href="https://github.com/FanlytiX/livextrem/blob/main/livextrem_v1.0.zip">livextrem_v1.0.zip herunterladen</a>

## Schritt-fuer-Schritt-Anleitung

### 1. Archiv herunterladen

Laden Sie zunaechst die Datei `livextrem_v1.0.zip` aus dem Repository herunter. Das Archiv enthaelt die lauffaehige Anwendung mitsamt der benoetigten Begleitdateien.

### 2. Archiv an einem festen Speicherort entpacken

Entpacken Sie den heruntergeladenen ZIP-Ordner in ein Verzeichnis, das nicht versehentlich verschoben oder geloescht wird. Als praktikable Ablage eignet sich beispielsweise ein Unterordner im Laufwerk `C:` innerhalb des Programmverzeichnisses. Der Hintergrund ist simpel: liveXtrem arbeitet nicht nur mit der `exe`, sondern auch mit weiteren Dateien, die relativ zu diesem Speicherort gefunden werden muessen.

### 3. Verknuepfung zur Anwendung erstellen

Oeffnen Sie den entpackten Ordner und suchen Sie die Datei `livextrem.exe`. Erstellen Sie von dieser Datei eine Verknuepfung und legen Sie diese auf dem Desktop ab. So bleibt die eigentliche Anwendung an ihrem vorgesehenen Ort, waehrend der Start im Alltag bequem ueber die Verknuepfung erfolgt.

### 4. Anwendung starten

Starten Sie liveXtrem anschliessend ueber die erstellte Desktop-Verknuepfung. Die Anwendung sollte nun ohne weitere Installationsschritte geoeffnet werden koennen.

## Warum die `exe` im Ordner bleiben muss

Desktop-Anwendungen dieser Art werden haeufig zusammen mit weiteren Ressourcen ausgeliefert, etwa Bildern, Theme-Dateien oder Konfigurationen. Wird nur die eigentliche Programmdatei verschoben, fehlen diese Abhaengigkeiten am erwarteten Speicherort. Die Folge sind Startprobleme oder unvollstaendige Oberflaechen. Die saubere Vorgehensweise besteht deshalb darin, stets den gesamten entpackten Ordner an seinem Platz zu belassen und lediglich eine Verknuepfung zu nutzen.

{% include warning.md %}

## Abgrenzung zur Entwicklerinstallation

Die bereitgestellte ZIP-Datei dient der Nutzung der fertigen Anwendung. Informationen zur spaeteren Einrichtung von Datenbank, API-Zugaengen und einem moeglichen Quellcode-Setup werden getrennt auf der Seite [Setup](setup.md) vorbereitet, damit Installation und technische Konfiguration nicht vermischt werden.
