import rumps
import json
import os
import importlib
import subprocess
import sys

def ensure_package(package):
    try:
        importlib.import_module(package)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package, "--user"])


ensure_package("python-telegram-bot")

try:
    from telegram import Bot
except ImportError:
    Bot = None

try:
    from telegram import Bot
except ImportError:
    Bot = None

PLUGIN_NAME = "telegram_notify"
SETTINGS_FILE = os.path.join(os.path.dirname(__file__), f"{PLUGIN_NAME}_settings.json")

DEFAULT_SETTINGS = {
    "token": "",
    "chat_id": ""
}


def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    else:
        with open(SETTINGS_FILE, "w") as f:
            json.dump(DEFAULT_SETTINGS, f, indent=2)
        return DEFAULT_SETTINGS.copy()


def save_settings(settings):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=2)


def send_telegram_message(token, chat_id, text):
    try:
        bot = Bot(token=token)
        bot.send_message(chat_id=chat_id, text=text)
        return True
    except Exception as e:
        print(f"Erreur Telegram: {e}")
        return False


def settings(app):
    settings_data = load_settings()

    token_window = rumps.Window(
        message="Entrez votre token Telegram Bot",
        title="Configuration Telegram",
        default_text=settings_data["token"]
    )
    token_response = token_window.run()
    if token_response.clicked:
        settings_data["token"] = token_response.text

    chat_id_window = rumps.Window(
        message="Entrez votre Chat ID Telegram",
        title="Configuration Telegram",
        default_text=settings_data["chat_id"]
    )
    chat_response = chat_id_window.run()
    if chat_response.clicked:
        settings_data["chat_id"] = chat_response.text

    save_settings(settings_data)
    rumps.alert("Configuration Telegram enregistrée ✅")


def run(app):
    settings_data = load_settings()

    def send_message():
        if not settings_data["token"] or not settings_data["chat_id"]:
            rumps.alert("⚠️ Configurez le bot Telegram d'abord dans 'Settings'")
            return

        msg_window = rumps.Window(
            message="Entrez le message à envoyer",
            title="Message Telegram"
        )
        msg_response = msg_window.run()

        if msg_response.clicked and msg_response.text.strip():
            success = send_telegram_message(
                settings_data["token"],
                settings_data["chat_id"],
                msg_response.text.strip()
            )
            if success:
                rumps.alert("📨 Message envoyé avec succès !")
            else:
                rumps.alert("❌ Erreur lors de l'envoi du message.")

    app.menu.add(rumps.MenuItem("Envoyer message Telegram", callback=send_message))
