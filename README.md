# 🦞 OpenClaw GUI

Eine moderne, benutzerfreundliche **Flask-Web-Oberfläche** für [OpenClaw](https://github.com/openclaw/openclaw) — den persönlichen KI-Assistenten, der auf deinem eigenen Rechner läuft.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.x-lightgrey?logo=flask)
![OpenClaw](https://img.shields.io/badge/OpenClaw-2026.x-FF4500?logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAxMDAgMTAwIj48dGV4dCB5PSIuOWVtIiBmb250LXNpemU9IjkwIj7wn6Z+PC90ZXh0Pjwvc3ZnPg==)
![License](https://img.shields.io/badge/Lizenz-MIT-green)

## Warum?

OpenClaw ist mächtig, aber die Bedienung läuft über die Kommandozeile. Diese GUI macht OpenClaw **für alle zugänglich** — auch ohne technische Vorkenntnisse.

## Features

- 🎨 **Modernes Dark-Mode UI** — Bootstrap 5, responsive, ansprechend
- 🧙 **Einrichtungsassistent** — Schritt-für-Schritt Wizard für Ersteinrichtung
- 🤖 **Agent-Chat** — Direkt mit dem KI-Assistenten kommunizieren
- 📡 **Gateway-Steuerung** — Start/Stop/Logs mit einem Klick
- 📱 **Kanal-Verwaltung** — WhatsApp, Telegram, Discord, Slack, Signal konfigurieren
- 💬 **Nachrichten senden** — Über alle verbundenen Kanäle
- 🧩 **Skills & Modelle** — Übersicht und Verwaltung
- 🩺 **Diagnose** — `openclaw doctor` im Browser
- ⚙️ **Konfiguration** — JSON-Editor mit Validierung
- 📖 **Hilfe & Doku** — Ausführliche Anleitungen, FAQ, Glossar
- 🔌 **REST API** — Alle Funktionen auch als JSON-API

## Screenshots

> Die GUI bietet ein Dashboard mit Statusübersicht, Schnellaktionen und einen 3-Schritte-Einrichtungsassistenten.

## Voraussetzungen

- **Node.js ≥ 22** (für OpenClaw)
- **OpenClaw** installiert (`npm install -g openclaw@latest`)
- **Python ≥ 3.10** (nur für Entwicklung, NICHT für die EXE nötig)

## Schnellstart (Standalone EXE)

1. Lade `OpenClaw-GUI.exe` aus dem [`dist/`](dist/) Ordner herunter
2. Stelle sicher dass **OpenClaw** installiert ist (`npm install -g openclaw@latest`)
3. Doppelklicke auf `OpenClaw-GUI.exe`
4. Der Browser öffnet sich automatisch unter **http://127.0.0.1:5000**

> Kein Python nötig! Die EXE enthält alles was benötigt wird.

## Installation (Entwicklung)

```bash
# 1. Repository klonen
git clone https://github.com/DerPoser/openclaw-gui.git
cd openclaw-gui

# 2. Python Virtual Environment erstellen
python -m venv venv

# Windows:
.\venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 3. Abhängigkeiten installieren
pip install -r requirements.txt

# 4. Starten
python app.py
```

Öffne dann **http://127.0.0.1:5000** im Browser.

### Windows Schnellstart

Doppelklicke einfach auf `start.bat` — fertig!

## Nutzung

1. **Einrichtung** → Klicke auf "Einrichtungsassistent" und folge den 3 Schritten
2. **Gateway starten** → Unter "Gateway" den Server starten
3. **Loslegen** → Sende Nachrichten, sprich mit dem Agenten, verwalte Skills

## API-Endpunkte

| Endpoint | Methode | Beschreibung |
|---|---|---|
| `/api/health` | GET | Gateway-Status |
| `/api/status` | GET | Kanal-Status |
| `/api/gateway/start` | POST | Gateway starten |
| `/api/gateway/stop` | POST | Gateway stoppen |
| `/api/gateway/logs` | GET | Gateway-Logs |
| `/api/message/send` | POST | Nachricht senden |
| `/api/agent` | POST | Agent-Anfrage |
| `/api/config` | GET/POST | Konfiguration lesen/schreiben |
| `/api/doctor` | GET | Diagnose ausführen |

## Projektstruktur

```
openclaw-gui/
├── app.py                 # Flask-Backend mit allen Routen & API
├── requirements.txt       # Python-Abhängigkeiten
├── start.bat              # Windows-Startskript
└── templates/
    ├── base.html           # Basis-Layout (Sidebar, CSS, JS)
    ├── index.html          # Dashboard
    ├── setup.html          # Wizard Schritt 1: Modell
    ├── setup_channels.html # Wizard Schritt 2: Kanäle
    ├── setup_done.html     # Wizard Schritt 3: Fertig
    ├── gateway.html        # Gateway-Verwaltung
    ├── channels.html       # Kanal-Übersicht
    ├── messages.html       # Nachrichten senden
    ├── agent.html          # Agent-Chat
    ├── sessions.html       # Sitzungen
    ├── models.html         # KI-Modelle
    ├── skills.html         # Skills
    ├── doctor.html         # Diagnose
    ├── logs.html           # Logs
    ├── config.html         # Konfiguration
    └── help.html           # Hilfe & Anleitung
```

## Technologie

- **Backend:** Python 3 + Flask
- **Frontend:** Bootstrap 5.3, Bootstrap Icons, Inter Font
- **OpenClaw:** CLI-Integration via `subprocess`
- **Design:** Dark Mode, Orange-Akzent (#FF4500), responsive Sidebar

## Lizenz

MIT License — siehe [LICENSE](LICENSE).

## Links

- [OpenClaw GitHub](https://github.com/openclaw/openclaw)
- [OpenClaw Docs](https://docs.openclaw.ai/)
- [OpenClaw Discord](https://discord.gg/clawd)
- [ClawHub Skills](https://clawhub.com/)
