import argparse
import datetime
import importlib.metadata
import json
import os
import platform
import ssl
import subprocess
import sys
import time
import urllib.request
import webbrowser
import random

import rumps
from qbittorrentapi import Client

from macmenuqbt.ee1 import ee1
from macmenuqbt.ee2 import ee2
from macmenuqbt.ee3 import ee3
from macmenuqbt.ee4 import ee4
from macmenuqbt.utils import get_icon
from macmenuqbt.sorting_options import main as sorting_options_window

if getattr(sys, 'frozen', False):
    BASE_PATH = sys._MEIPASS
else:
    BASE_PATH = os.path.dirname(os.path.abspath(__file__))

CONFIG_FILE = os.path.expanduser("~/Library/Application Support/MMqBt/qbt_menu_config.json")
SETTINGS_FILE = os.path.expanduser("~/Library/Application Support/MMqBt/qbt_settings.json")
PLUGINS_DIR = os.path.expanduser("~/Library/Application Support/MMqBt/plugins")
PLUGINS_SETTINGS_FILE = os.path.expanduser("~/Library/Application Support/MMqBt/plugins_settings.json")
EE_FILE = os.path.expanduser("~/Library/Application Support/MMqBt/ee.json")

STATUS_ICONS = {
    "allocating": "📦",
    "checkingDL": "🔍",
    "checkingResumeData": "🔍",
    "checkingUP": "🔍",
    "downloading": "⬇️",
    "error": "❌",
    "forcedDL": "⬇️",
    "forcedUP": "⬆️",
    "metaDL": "📥",
    "missingFiles": "⚠️",
    "moving": "📦",
    "stoppedDL": "⏸️",
    "stoppedUP": "⏸️",
    "queuedDL": "⏳",
    "queuedUP": "⏳",
    "stalledDL": "⚠️",
    "stalledUP": "⚠️",
    "unknown": "❓",
    "uploading": "⬆️"
}


DEFAULT_ELEMENTS = [
    {"name": "Status", "state": True},
    {"name": "Progress (%)", "state": True},
    {"name": "DL speed", "state": True},
    {"name": "UP speed", "state": True},
    {"name": "ETA", "state": True},
    {"name": "DL/UP/Tot Size", "state": False},
    {"name": "Ratio UP/DL", "state": False},
    {"name": "Seeds/Leechers", "state": False},
    {"name": "Category", "state": False},
    {"name": "Added on", "state": False},
]

DEFAULT_SETTINGS_FILE_CONTENT = {
    "monochrome": 0,
    "text_menu": 1,
    'percentage_menu': 1,
    "Launch qBittorrent": 0,
    "Standby": 0,
    "Notification": 1,
    "Notification sound": 1,
    "host": "localhost",
    "port": 8080,
    "username": "admin",
    "password": "123456"
}

EE_FILE_CONTENT = {
    "ee1": 0,
    "ee2": 0,
    'ee3': 0,
    "ee4": 0,
}


def check_for_update(package_name="macmenuqbt"):
    try:
        current_version = importlib.metadata.version(package_name)
        context = ssl._create_unverified_context()
        with urllib.request.urlopen(f"https://pypi.org/pypi/{package_name}/json", context=context) as response:
            data = json.load(response)
            latest_version = data["info"]["version"]

        if current_version != latest_version:
            return True, f"🎉 A new update is available {current_version} → {latest_version} - Click me"
        return False, current_version

    except Exception as e:
        print(e)
        return None, None


def install_update(_):
    webbrowser.open("https://github.com/Jumitti/MacMenu-qBittorrent/releases")


def launch_qbittorrent():
    system = platform.system()

    if system == "Darwin":
        app_path = "/Applications/qbittorrent.app"
        if os.path.exists(app_path):
            subprocess.Popen(["open", app_path])
            return None
        else:
            return "qBittorrent.app not found in /Applications"
    else:
        return "qBittorrent.app not found in /Applications"


def format_speed(speed_bytes_per_s):
    kb_s = speed_bytes_per_s / 1024
    if kb_s >= 500:
        mb_s = kb_s / 1024
        return f"{mb_s:.2f} Mo/s"
    else:
        return f"{kb_s:.1f} Ko/s"


def format_eta(seconds):
    if seconds < 0:
        return "∞"
    return str(datetime.timedelta(seconds=seconds))


def is_dark_mode():
    cmd = ["defaults", "read", "-g", "AppleInterfaceStyle"]
    try:
        output = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode().strip()
        return output.lower() == "dark"
    except subprocess.CalledProcessError:
        return False


class QBitTorrentMenuApp(rumps.App):
    def __init__(self, host, port, username, password, interval=5, qbt=True, credentials=True):
        self.color_icon = get_icon("color.png")
        self.light_icon = get_icon("light.png")
        self.dark_icon = get_icon("dark.png")
        self.warning_icon = get_icon("warning_color.png")
        super().__init__("MMqBt", icon=self.color_icon)
        self.host, self.port, self.username, self.password, self.interval = host, port, username, password, interval
        self.qbt, self.credentials = qbt, credentials
        self.client, self.is_update, self.msg_version_update = None, None, None
        self.list_torrent = None
        self.current_torrents = None
        self.previous_torrents = None
        self.plugins = {}

        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                self.elements = json.load(f)

            default_names = {e["name"] for e in DEFAULT_ELEMENTS}
            existing_names = {e["name"] for e in self.elements}

            for default_elem in DEFAULT_ELEMENTS:
                if default_elem["name"] not in existing_names:
                    self.elements.append(default_elem)

            self.elements = [e for e in self.elements if e["name"] in default_names]

            with open(CONFIG_FILE, "w") as f:
                json.dump(self.elements, f, indent=2)

        else:
            self.elements = DEFAULT_ELEMENTS.copy()
            with open(CONFIG_FILE, "w") as f:
                json.dump(self.elements, f, indent=2)

        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r") as f:
                self.settings_data = json.load(f)

            for key, value in DEFAULT_SETTINGS_FILE_CONTENT.items():
                if key not in self.settings_data:
                    self.settings_data[key] = value

            self.settings_data = {k: self.settings_data[k] for k in DEFAULT_SETTINGS_FILE_CONTENT.keys()}

            with open(SETTINGS_FILE, "w") as f:
                json.dump(self.settings_data, f, indent=2)

        else:
            self.settings_data = DEFAULT_SETTINGS_FILE_CONTENT.copy()
            self.settings_data["host"] = host
            self.settings_data["port"] = port
            self.settings_data["username"] = username
            self.settings_data["password"] = password

            with open(SETTINGS_FILE, "w") as f:
                json.dump(self.settings_data, f, indent=2)

        if not os.path.exists(PLUGINS_DIR):
            os.makedirs(PLUGINS_DIR)

        for filename in os.listdir(PLUGINS_DIR):
            if filename.endswith(".py"):
                plugin_path = os.path.join(PLUGINS_DIR, filename)
                spec = importlib.util.spec_from_file_location(filename[:-3], plugin_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                self.plugins[filename[:-3]] = module

        if os.path.exists(PLUGINS_SETTINGS_FILE):
            with open(PLUGINS_SETTINGS_FILE, "r") as f:
                self.plugins_settings = json.load(f)
        else:
            self.plugins_settings = {name: 0 for name in self.plugins.keys()}
            with open(PLUGINS_SETTINGS_FILE, "w") as f:
                json.dump(self.plugins_settings, f, indent=2)

        for name in self.plugins.keys():
            if name not in self.plugins_settings:
                self.plugins_settings[name] = 0

        obsolete_plugins = [name for name in self.plugins_settings if name not in self.plugins]
        for name in obsolete_plugins:
            del self.plugins_settings[name]

        with open(PLUGINS_SETTINGS_FILE, "w") as f:
            json.dump(self.plugins_settings, f, indent=2)

        if os.path.exists(EE_FILE):
            with open(EE_FILE, "r") as f:
                self.ee_data = json.load(f)

            for key, value in EE_FILE_CONTENT.items():
                if key not in self.ee_data:
                    self.ee_data[key] = value

            self.ee_data = {k: self.ee_data[k] for k in EE_FILE_CONTENT.keys()}

            with open(EE_FILE, "w") as f:
                json.dump(self.ee_data, f, indent=2)

        else:
            self.ee_data = EE_FILE_CONTENT.copy()

            with open(EE_FILE, "w") as f:
                json.dump(self.ee_data, f, indent=2)

        if self.settings_data['Launch qBittorrent']:
            launch_qbittorrent()
            time.sleep(2)

        if not self.settings_data['Standby']:
            self.connected, self.msg_connection = self.connect_to_qbittorrent()

            if self.connected:
                self.list_torrent = self.client.torrents_info()

        self.menu.clear()
        self.build_menu()
        self.timer = rumps.Timer(self.update_menu, self.interval)
        self.timer.start()

    def build_menu(self):
        self.menu.add(None)
        self.menu.add(rumps.MenuItem("🏷️ Display and Sorting Options", callback=self.sorting_options))

        self.menu.add(None)
        total_plugins = len(self.plugins_settings)
        active_plugins = sum(1 for state in self.plugins_settings.values() if state)
        if total_plugins > 0:
            plugin_text = f"🧩 Plugins {active_plugins}/{total_plugins} (beta)"
        else:
            plugin_text = f"🧩 Plugins (beta)"

        plugins_menu = rumps.MenuItem(plugin_text, callback=self.open_plugins)
        for plugin_name, module in self.plugins.items():
            plugin_menu = rumps.MenuItem(plugin_name, callback=self.toggle_plugins if hasattr(module, "settings") else None)
            plugin_menu.state = self.plugins_settings[plugin_name]
            if hasattr(module, "settings"):
                module.settings(self, plugin_menu)

            plugins_menu.add(plugin_menu)

        self.menu.add(None)
        self.menu.add(plugins_menu)

        self.menu.add(None)
        # standby_item = rumps.MenuItem("Standby (prevent from MMqBt lagging)", callback=self.toggle_standby)
        # standby_item.state = self.settings_data["Standby"]
        # self.menu.add(standby_item)

        menu_bar_display = rumps.MenuItem("🔵Menu bar display")
        monochrome_menu = rumps.MenuItem("🔲 Monochrome icons", callback=self.toggle_monochrome)
        monochrome_menu.state = self.settings_data["monochrome"]
        text_menu = rumps.MenuItem("🔤 qBittorrent display", callback=self.toggle_text_menu)
        text_menu.state = self.settings_data["text_menu"]
        percentage_menu = rumps.MenuItem('% Percentage display', callback=self.toggle_percentage_menu)
        percentage_menu.state = self.settings_data["percentage_menu"]
        menu_bar_display.add(monochrome_menu)
        menu_bar_display.add(text_menu)
        menu_bar_display.add(percentage_menu)
        self.menu.add(menu_bar_display)

        if self.qbt is True:
            launch_item = rumps.MenuItem("🌀 Launch qBittorrent", callback=self.toggle_launch_qbt)
            launch_item.state = self.settings_data["Launch qBittorrent"]
            self.menu.add(launch_item)

        notification = rumps.MenuItem("🔔 Notification", callback=self.toggle_notification)
        notification.state = self.settings_data["Notification"]
        notification_sound = rumps.MenuItem("🎵 Notification sound", callback=self.toggle_notification_sound)
        notification_sound.state = self.settings_data["Notification sound"]
        notification.add(notification_sound)
        self.menu.add(notification)

        if self.credentials is True:
            self.menu.add(rumps.MenuItem("👥 Credentials login", callback=self.open_qbt_settings))

        self.menu.add(None)
        self.is_update, self.msg_version_update = check_for_update()
        if not self.is_update:
            version_item = rumps.MenuItem(f"🆚 v{self.msg_version_update}", callback=self.ee)
        else:
            version_item = rumps.MenuItem(self.msg_version_update, callback=install_update)
        made_with = rumps.MenuItem("Made with ❤️ by Minniti Julien", callback=self.open_github)
        bmc = rumps.MenuItem("☕ Buy me a Coffee", callback=self.open_bmc)
        version_item.add(made_with)
        version_item.add(bmc)
        version_item.add(None)
        found_count = sum(1 for state in self.ee_data.values() if state == 1)
        total_count = len(self.ee_data)
        version_item.add(rumps.MenuItem(f"🐰 Easter Eggs {found_count}/{total_count}"))
        for idx, (ee_key, state) in enumerate(self.ee_data.items(), start=1):
            if state == 1:
                item = rumps.MenuItem(f"🥚 Easter Egg {idx}", callback=lambda sender, key=ee_key: self.ee_run(key))
                version_item.add(item)

        self.menu.add(version_item)

        self.menu.add(None)
        self.menu.add(rumps.MenuItem("🚪 Quit", callback=rumps.quit_application))

    def sorting_options(self, sender):
        sorting_options_window()
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                self.elements = json.load(f)

            default_names = {e["name"] for e in DEFAULT_ELEMENTS}
            existing_names = {e["name"] for e in self.elements}

            for default_elem in DEFAULT_ELEMENTS:
                if default_elem["name"] not in existing_names:
                    self.elements.append(default_elem)

            self.elements = [e for e in self.elements if e["name"] in default_names]

    # def toggle_standby(self, sender):
    #     sender.state = not sender.state
    #     self.settings_data["Standby"] = sender.state
    #     with open(SETTINGS_FILE, "w") as f:
    #         json.dump(self.settings_data, f, indent=2)
    #     if sender.state == 0:
    #         self.connected, self.msg_connection = self.connect_to_qbittorrent()
    #
    #         if self.connected:
    #             self.list_torrent = self.client.torrents_info()

    def toggle_launch_qbt(self, sender):
        sender.state = not sender.state
        self.settings_data["Launch qBittorrent"] = sender.state
        with open(SETTINGS_FILE, "w") as f:
            json.dump(self.settings_data, f, indent=2)
        if sender.state:
            launch_qbittorrent()

    def toggle_monochrome(self, sender):
        sender.state = not sender.state
        self.settings_data["monochrome"] = sender.state
        with open(SETTINGS_FILE, "w") as f:
            json.dump(self.settings_data, f, indent=2)

    def toggle_text_menu(self, sender):
        sender.state = not sender.state
        self.settings_data["text_menu"] = sender.state
        with open(SETTINGS_FILE, "w") as f:
            json.dump(self.settings_data, f, indent=2)

    def toggle_percentage_menu(self, sender):
        sender.state = not sender.state
        self.settings_data["percentage_menu"] = sender.state
        with open(SETTINGS_FILE, "w") as f:
            json.dump(self.settings_data, f, indent=2)

    def toggle_notification(self, sender):
        sender.state = not sender.state
        self.settings_data["Notification"] = sender.state
        with open(SETTINGS_FILE, "w") as f:
            json.dump(self.settings_data, f, indent=2)

    def toggle_notification_sound(self, sender):
        sender.state = not sender.state
        self.settings_data["Notification sound"] = sender.state
        with open(SETTINGS_FILE, "w") as f:
            json.dump(self.settings_data, f, indent=2)

    def open_plugins(self, sender):
        if os.path.exists(PLUGINS_DIR):
            subprocess.Popen(["open", PLUGINS_DIR])

        for filename in os.listdir(PLUGINS_DIR):
            if filename.endswith(".py"):
                plugin_path = os.path.join(PLUGINS_DIR, filename)
                spec = importlib.util.spec_from_file_location(filename[:-3], plugin_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                self.plugins[filename[:-3]] = module

        for name in self.plugins.keys():
            if name not in self.plugins_settings:
                self.plugins_settings[name] = 0

        obsolete_plugins = [name for name in self.plugins_settings if name not in self.plugins]
        for name in obsolete_plugins:
            del self.plugins_settings[name]

        with open(PLUGINS_SETTINGS_FILE, "w") as f:
            json.dump(self.plugins_settings, f, indent=2)

    def toggle_plugins(self, sender):
        plugin_name = sender.title
        sender.state = not sender.state
        self.plugins_settings[plugin_name] = sender.state
        with open(PLUGINS_SETTINGS_FILE, "w") as f:
            json.dump(self.plugins_settings, f, indent=2)

    def connect_to_qbittorrent(self):
        try:
            self.client = Client(host=self.settings_data['host'], port=self.settings_data['port'],
                                 username=self.settings_data['username'], password=self.settings_data['password'])
            self.client.auth_log_in()
            return True, None
        except Exception as e:
            return False, f"Failed to connect: {e}"

    def open_qbt_settings(self, sender):
        if not os.path.exists(SETTINGS_FILE):
            rumps.alert("Settings file not found.")
            return

        with open(SETTINGS_FILE, "r") as f:
            settings = json.load(f)

        default_text = (
            f"Host: {settings.get('host', 'localhost')}\n"
            f"Port: {settings.get('port', 8080)}\n"
            f"Username: {settings.get('username', 'admin')}\n"
            f"Password: {settings.get('password', '')}"
        )

        window = rumps.Window(
            title="qBittorrent Settings",
            message="Edit your qBittorrent Web UI credentials",
            ok="Save",
            cancel="Cancel",
            dimensions=(400, 75),
            default_text=default_text
        )

        response = window.run()

        if response.clicked:
            try:
                lines = response.text.splitlines()
                settings.update({
                    "host": lines[0].split(":", 1)[1].strip(),
                    "port": int(lines[1].split(":", 1)[1].strip()),
                    "username": lines[2].split(":", 1)[1].strip(),
                    "password": lines[3].split(":", 1)[1].strip()
                })

                with open(SETTINGS_FILE, "w") as f:
                    json.dump(settings, f, indent=2)

                with open(SETTINGS_FILE, "r") as f:
                    self.settings_data = json.load(f)

                self.connected, _ = self.connect_to_qbittorrent()

                rumps.alert("Settings saved!")
            except Exception as e:
                rumps.alert(f"Error saving settings:\n{e}")

    @staticmethod
    def open_github(self):
        webbrowser.open("https://github.com/Jumitti/MacMenu-qBittorrent")

    @staticmethod
    def open_bmc(self):
        webbrowser.open("https://www.buymeacoffee.com/Jumitti")

    def ee(self, sender):
        ee_functions = [ee1, ee2, ee3, ee4]
        ee_keys = ["ee1", "ee2", "ee3", "ee4"]
        weights = [60, 30, 20, 10]
        idx = random.choices(range(4), weights=weights, k=1)[0]
        key = ee_keys[idx]

        if self.ee_data[key] == 0:
            self.ee_data[key] = 1

            with open(EE_FILE, "w") as f:
                json.dump(self.ee_data, f, indent=2)

            self.ee_data = {k: self.ee_data[k] for k in EE_FILE_CONTENT.keys()}

        ee_functions[idx]()

    @staticmethod
    def ee_run(ee_key):
        globals()[ee_key]()

    @staticmethod
    def change_state_torrent(torrent):
        if torrent.state == "stoppedDL":
            torrent.resume()
        else:
            torrent.pause()

    def toggle_all_torrents(self, _):
        torrents = self.client.torrents_info()
        hashes = "|".join(t.hash for t in torrents)
        if hashes:
            if any(t.state in ["downloading", "uploading", "forcedDL", "forcedUP", "running"] for t in torrents):
                self.client.torrents_pause(hashes=hashes)
            else:
                self.client.torrents_resume(hashes=hashes)

    @rumps.timer(1)
    def update_menu(self, _=None):
        if self.settings_data["monochrome"]:
            if is_dark_mode():
                self.icon = self.light_icon
            else:
                self.icon = self.dark_icon
        else:
            self.icon = self.color_icon
        # if self.settings_data['Standby']:
        #     self.title = "💤 qBittorrent"
        #     self.menu.clear()
        #     self.menu.add("💤 MMqBt is in standby")
        #     self.menu.add(None)
        #     self.build_menu()
        if not self.client.is_logged_in:
            if self.settings_data["text_menu"]:
                self.title = "qBittorrent"
            else:
                self.title = ""
            self.icon = self.warning_icon
            self.menu.clear()
            self.menu.add("⚠️ Connection qBittorrent lost")
            self.menu.add("Start qBittorrent or verify your login credentials")
            self.menu.add(None)
            self.build_menu()
            with open(SETTINGS_FILE, "r") as f:
                self.settings_data = json.load(f)
            self.connect_to_qbittorrent()
        else:
            if os.path.exists(PLUGINS_SETTINGS_FILE):
                with open(PLUGINS_SETTINGS_FILE, "r") as f:
                    self.plugins_settings = json.load(f)
            try:
                torrents = self.client.torrents_info()
                self.current_torrents = {t.hash: t for t in torrents}
                if self.list_torrent is None:
                    self.previous_torrents = self.current_torrents
                else:
                    self.previous_torrents = {t.hash: t for t in self.list_torrent}

                self.list_torrent = torrents

                for hash_, old_t in self.previous_torrents.items():
                    if hash_ not in self.current_torrents:
                        if self.settings_data['Notification']:
                            rumps.notification(
                                "🎉 Torrent finished !",
                                subtitle=None,
                                message=old_t.name,
                                sound=self.settings_data['Notification sound']
                            )

                self.menu.clear()
                if not torrents:
                    self.menu.add("⚪ No torrent found")
                    self.menu.add(None)
                else:
                    total_progress = sum(t.progress for t in torrents) / len(torrents)
                    if self.settings_data["text_menu"]:
                        if self.settings_data["percentage_menu"]:
                            self.title = f"qBittorrent {total_progress * 100:.1f}%"
                        else:
                            self.title = "qBittorrent"
                    else:
                        if self.settings_data["percentage_menu"]:
                            self.title = f"{total_progress * 100:.1f}%"
                        else:
                            self.title = ""

                    for t in torrents:
                        parts = [t.name]
                        for elem in self.elements:
                            if not elem["state"]:
                                continue
                            if elem["name"] == "Status":
                                status_icon = STATUS_ICONS.get(t.state, "❓")
                                parts.append(f"{status_icon}")

                            elif elem["name"] == "DL/UP/Tot Size":
                                total_size = t.size / 1024 ** 3
                                downloaded_size = t.downloaded / 1024 ** 3
                                uploaded_size = t.uploaded / 1024 ** 3
                                parts.append(
                                    f"📥 {t.downloaded / 1024 ** 3:.2f} / 📤{t.uploaded / 1024 ** 3:.2f} / 📦{t.size / 1024 ** 3:.2f} Go")

                            elif elem["name"] == "Progress (%)":
                                parts.append(f"🏃🏽{t.progress * 100:.1f}%")

                            elif elem["name"] == "Ratio UP/DL":
                                parts.append(f"📊 {t.ratio * 100:.1f}%")

                            elif elem["name"] == "DL speed":
                                parts.append(f"⬇️ {format_speed(t.dlspeed)}")

                            elif elem["name"] == "UP speed":
                                parts.append(f"⬆️ {format_speed(t.upspeed)}")

                            elif elem["name"] == "ETA":
                                parts.append(f"⏳ {format_eta(t.eta)}")

                            elif elem["name"] == "Seeds/Leechers":
                                parts.append(f"🌱{t.num_seeds}/🧲{t.num_leechs}")

                            elif elem["name"] == "Category":
                                parts.append(f"🏷️ {t.category}")

                            elif elem["name"] == "Added on":
                                dt = datetime.datetime.fromtimestamp(t.added_on)
                                parts.append(f"📆 {dt.strftime('%Y-%m-%d %H:%M')}")

                        menu_text = " | ".join(parts)

                        self.menu.add(
                            rumps.MenuItem(menu_text, callback=lambda sender, torrent=t: self.change_state_torrent(torrent)))

                self.menu.add(None)
                self.menu.add(rumps.MenuItem("Pause/Resume All", callback=self.toggle_all_torrents))

                for plugin_name, module in self.plugins.items():
                    if self.plugins_settings.get(plugin_name, 0) == 1:
                        if hasattr(module, "run"):
                            module.run(self)

                self.build_menu()
                self.menu.add(None)
                self.is_update, self.msg_version_update = check_for_update()
                if self.is_update:
                    version = rumps.MenuItem(self.msg_version_update, callback=install_update)
                    self.menu.add(version)

            except Exception as e:
                self.menu.clear()
                self.menu.add(f"⚠️ Error: {str(e)}")
                self.build_menu()


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="qBittorrent macOS Menu Bar App")
    parser.add_argument("-H", "--host", default="localhost")
    parser.add_argument("-P", "--port", type=int, default=8080)
    parser.add_argument("-U", "--username", default="admin")
    parser.add_argument("-PSW", "--password", default="123456")
    parser.add_argument("-I", "--interval", type=int, default=5)
    try:
        version = importlib.metadata.version("macmenuqbt")
    except importlib.metadata.PackageNotFoundError:
        version = "unknown"
    parser.add_argument("-V", "--version", action="version", version=f"MacMenu-qBittorrent {version}")
    return parser.parse_args(argv)


def main(host=None, port=None, username=None, password=None, interval=None, qbt=True, credentials=True):
    if all(arg is None for arg in [host, port, username, password, interval]):
        args = parse_args()
        host, port, username, password, interval = args.host, args.port, args.username, args.password, args.interval

    app = QBitTorrentMenuApp(host, port, username, password, interval, qbt, credentials)
    app.run()


if __name__ == "__main__":
    main()
