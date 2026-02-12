"""
OpenClaw GUI – Flask-basierte Web-Oberfläche für OpenClaw.
Ermöglicht die intuitive Bedienung von OpenClaw über den Browser.
Kann als standalone EXE ausgeführt werden (PyInstaller-kompatibel).
"""

import json
import os
import subprocess
import sys
import threading
import time
import webbrowser
from pathlib import Path

from flask import Flask, jsonify, redirect, render_template, request, send_from_directory, url_for


def resource_path(relative_path: str) -> str:
    """Pfad zu gebündelten Ressourcen (PyInstaller-kompatibel)."""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), relative_path)


app = Flask(
    __name__,
    template_folder=resource_path("templates"),
    static_folder=resource_path("static"),
)

# ---------------------------------------------------------------------------
# Konfigurationspfade
# ---------------------------------------------------------------------------
OPENCLAW_HOME = Path.home() / ".openclaw"
OPENCLAW_CONFIG = OPENCLAW_HOME / "openclaw.json"

# Gateway-Prozess-Handle
gateway_process: subprocess.Popen | None = None
gateway_log: list[str] = []


# ---------------------------------------------------------------------------
# Hilfsfunktionen
# ---------------------------------------------------------------------------

def run_openclaw(*args: str, timeout: int = 30) -> dict:
    """Führt einen OpenClaw-CLI-Befehl aus und gibt stdout/stderr zurück."""
    cmd = ["openclaw", *args]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding="utf-8",
            errors="replace",
        )
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "returncode": result.returncode,
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "stdout": "", "stderr": "Timeout", "returncode": -1}
    except FileNotFoundError:
        return {
            "success": False,
            "stdout": "",
            "stderr": "openclaw nicht gefunden – bitte zuerst installieren.",
            "returncode": -1,
        }


def load_config() -> dict:
    """Lade die aktuelle OpenClaw-Konfiguration."""
    if OPENCLAW_CONFIG.exists():
        try:
            return json.loads(OPENCLAW_CONFIG.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def save_config(cfg: dict) -> None:
    """Speichere die OpenClaw-Konfiguration."""
    OPENCLAW_HOME.mkdir(parents=True, exist_ok=True)
    OPENCLAW_CONFIG.write_text(
        json.dumps(cfg, indent=2, ensure_ascii=False), encoding="utf-8"
    )


# ---------------------------------------------------------------------------
# Routen – Seiten
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    """Startseite / Dashboard."""
    version = run_openclaw("--version")
    health = run_openclaw("health")
    config = load_config()
    return render_template(
        "index.html",
        version=version.get("stdout", "unbekannt"),
        health=health,
        config=config,
    )


@app.route("/setup", methods=["GET", "POST"])
def setup():
    """Ersteinrichtung – Wizard Schritt 1: Grundkonfiguration."""
    if request.method == "POST":
        model = request.form.get("model", "anthropic/claude-opus-4-6")
        cfg = load_config()
        cfg.setdefault("agent", {})["model"] = model
        save_config(cfg)
        return redirect(url_for("setup_channels"))
    config = load_config()
    return render_template("setup.html", config=config)


@app.route("/setup/channels", methods=["GET", "POST"])
def setup_channels():
    """Wizard Schritt 2: Kanäle konfigurieren."""
    if request.method == "POST":
        cfg = load_config()
        channels = cfg.setdefault("channels", {})

        # WhatsApp
        if request.form.get("whatsapp_enabled"):
            allow_from = [
                s.strip()
                for s in request.form.get("whatsapp_allow", "").split(",")
                if s.strip()
            ]
            channels["whatsapp"] = {"allowFrom": allow_from}

        # Telegram
        if request.form.get("telegram_enabled"):
            token = request.form.get("telegram_token", "")
            if token:
                channels["telegram"] = {"botToken": token}

        # Discord
        if request.form.get("discord_enabled"):
            token = request.form.get("discord_token", "")
            if token:
                channels["discord"] = {"token": token}

        # Slack
        if request.form.get("slack_enabled"):
            bot_token = request.form.get("slack_bot_token", "")
            app_token = request.form.get("slack_app_token", "")
            if bot_token and app_token:
                channels["slack"] = {
                    "botToken": bot_token,
                    "appToken": app_token,
                }

        save_config(cfg)
        return redirect(url_for("setup_done"))
    config = load_config()
    return render_template("setup_channels.html", config=config)


@app.route("/setup/done")
def setup_done():
    """Wizard fertig."""
    return render_template("setup_done.html")


@app.route("/gateway")
def gateway_page():
    """Gateway-Verwaltung."""
    health = run_openclaw("health")
    return render_template("gateway.html", health=health, logs=gateway_log[-50:])


@app.route("/channels")
def channels_page():
    """Kanal-Übersicht."""
    status = run_openclaw("status")
    config = load_config()
    return render_template("channels.html", status=status, config=config)


@app.route("/messages", methods=["GET", "POST"])
def messages_page():
    """Nachrichten senden."""
    result = None
    if request.method == "POST":
        target = request.form.get("target", "")
        message = request.form.get("message", "")
        channel = request.form.get("channel", "")
        args = ["message", "send", "--target", target, "--message", message]
        if channel:
            args += ["--channel", channel]
        result = run_openclaw(*args)
    return render_template("messages.html", result=result)


@app.route("/agent", methods=["GET", "POST"])
def agent_page():
    """Mit dem Agenten sprechen."""
    result = None
    if request.method == "POST":
        message = request.form.get("message", "")
        thinking = request.form.get("thinking", "medium")
        args = ["agent", "--message", message, "--thinking", thinking]
        result = run_openclaw(*args, timeout=120)
    return render_template("agent.html", result=result)


@app.route("/sessions")
def sessions_page():
    """Sitzungsübersicht."""
    result = run_openclaw("sessions", "list", "--json")
    sessions = []
    if result["success"]:
        try:
            sessions = json.loads(result["stdout"])
        except json.JSONDecodeError:
            pass
    return render_template("sessions.html", sessions=sessions, raw=result)


@app.route("/models", methods=["GET", "POST"])
def models_page():
    """Modellkonfiguration."""
    if request.method == "POST":
        model = request.form.get("model", "")
        if model:
            cfg = load_config()
            cfg.setdefault("agent", {})["model"] = model
            save_config(cfg)
    config = load_config()
    return render_template("models.html", config=config)


@app.route("/skills")
def skills_page():
    """Skills-Verwaltung."""
    result = run_openclaw("skills", "list")
    return render_template("skills.html", result=result)


@app.route("/doctor")
def doctor_page():
    """Gesundheitscheck."""
    result = run_openclaw("doctor")
    return render_template("doctor.html", result=result)


@app.route("/logs")
def logs_page():
    """Logs anzeigen."""
    result = run_openclaw("logs", "--lines", "100")
    return render_template("logs.html", result=result)


@app.route("/config", methods=["GET", "POST"])
def config_page():
    """Konfiguration direkt bearbeiten."""
    message = None
    if request.method == "POST":
        raw = request.form.get("config_json", "{}")
        try:
            cfg = json.loads(raw)
            save_config(cfg)
            message = "Konfiguration gespeichert!"
        except json.JSONDecodeError as e:
            message = f"JSON-Fehler: {e}"
    config = load_config()
    config_json = json.dumps(config, indent=2, ensure_ascii=False)
    return render_template("config.html", config_json=config_json, message=message)


@app.route("/help")
def help_page():
    """Hilfeseite mit ausführlichen Erklärungen."""
    return render_template("help.html")


@app.route("/favicon.ico")
def favicon():
    """Favicon bereitstellen."""
    return send_from_directory(
        resource_path("static"), "favicon.ico", mimetype="image/x-icon"
    )


# ---------------------------------------------------------------------------
# API-Endpunkte
# ---------------------------------------------------------------------------

@app.route("/api/health")
def api_health():
    return jsonify(run_openclaw("health"))


@app.route("/api/status")
def api_status():
    return jsonify(run_openclaw("status"))


@app.route("/api/gateway/start", methods=["POST"])
def api_gateway_start():
    global gateway_process
    if gateway_process and gateway_process.poll() is None:
        return jsonify({"success": False, "message": "Gateway läuft bereits."})

    port = request.json.get("port", 18789) if request.is_json else 18789

    def _run():
        global gateway_process
        gateway_process = subprocess.Popen(
            ["openclaw", "gateway", "--port", str(port)],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        for line in gateway_process.stdout:
            gateway_log.append(line.rstrip())
            if len(gateway_log) > 500:
                gateway_log.pop(0)

    threading.Thread(target=_run, daemon=True).start()
    time.sleep(2)
    return jsonify({"success": True, "message": f"Gateway gestartet auf Port {port}."})


@app.route("/api/gateway/stop", methods=["POST"])
def api_gateway_stop():
    global gateway_process
    if gateway_process and gateway_process.poll() is None:
        gateway_process.terminate()
        gateway_process.wait(timeout=10)
        gateway_process = None
        return jsonify({"success": True, "message": "Gateway gestoppt."})
    return jsonify({"success": False, "message": "Kein laufender Gateway-Prozess."})


@app.route("/api/gateway/logs")
def api_gateway_logs():
    return jsonify({"logs": gateway_log[-100:]})


@app.route("/api/message/send", methods=["POST"])
def api_message_send():
    data = request.get_json(force=True)
    target = data.get("target", "")
    message = data.get("message", "")
    channel = data.get("channel", "")
    args = ["message", "send", "--target", target, "--message", message]
    if channel:
        args += ["--channel", channel]
    return jsonify(run_openclaw(*args))


@app.route("/api/agent", methods=["POST"])
def api_agent():
    data = request.get_json(force=True)
    message = data.get("message", "")
    thinking = data.get("thinking", "medium")
    args = ["agent", "--message", message, "--thinking", thinking]
    return jsonify(run_openclaw(*args, timeout=120))


@app.route("/api/config", methods=["GET", "POST"])
def api_config():
    if request.method == "POST":
        data = request.get_json(force=True)
        save_config(data)
        return jsonify({"success": True})
    return jsonify(load_config())


@app.route("/api/doctor")
def api_doctor():
    return jsonify(run_openclaw("doctor"))


@app.route("/api/version")
def api_version():
    return jsonify(run_openclaw("--version"))


# ---------------------------------------------------------------------------
# Start
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("OPENCLAW_GUI_PORT", 5000))
    host = os.environ.get("OPENCLAW_GUI_HOST", "127.0.0.1")

    # Im EXE-Modus: Browser automatisch öffnen
    if getattr(sys, "frozen", False):
        threading.Timer(1.5, lambda: webbrowser.open(f"http://{host}:{port}")).start()
        print(f"\n  OpenClaw GUI startet auf http://{host}:{port}")
        print("  Schließe dieses Fenster um die GUI zu beenden.\n")
        app.run(host=host, port=port, debug=False)
    else:
        app.run(host=host, port=port, debug=True)
