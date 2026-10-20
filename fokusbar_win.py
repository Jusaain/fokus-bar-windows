#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FokusBar für Windows (Windows 10 / 11)
1:1 Feature-Parität mit der macOS-Version:
- Fokus-Timer, Countdown, Stoppuhr & Pause + schwebende, größenverstellbare LED-Timeruhr
- 7 echte Natur-Sounds (.m4a über Windows winmm.dll) + 13 Spotify-Playlists (Courten, Deep Work, Jazz House) im Hintergrund
- App-Blocker (WhatsApp, Discord, Telegram + VPNs + Anti-Detect-Browser wie Dolphin Anty, AdsPower, GoLogin, Multilogin)
- Website-Blocker (Instagram, YouTube, X.com, TikTok, Reddit, Netflix etc.) inkl. Erkennung in Proxy-Profilen (Anty.exe, SunBrowser.exe, Orbita)
- Fokus-Schutz: 30-90 Sek. Durchatmen-Übung mit Checkpoints + Bestätigungssatz gegen vorzeitiges Pausieren/Abbrechen
- Aufgaben, Projekte, Prioritäten, Schnelleingabe (#Projekt @morgen !) & Tagesziel
"""

from __future__ import annotations

import ctypes
import datetime as dt
import json
import math
import os
import pathlib
import platform
import re
import subprocess
import sys
import threading
import time
import urllib.parse
import uuid
import webbrowser

try:
    import tkinter as tk
    from tkinter import ttk, messagebox, filedialog
except ImportError:
    tk = None  # type: ignore
    ttk = None  # type: ignore
    messagebox = None  # type: ignore
    filedialog = None  # type: ignore

IS_WINDOWS = platform.system() == "Windows"

if IS_WINDOWS:
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Pfade & Ressourcen (funktioniert sowohl aus dem Repo als auch als .exe)
# ---------------------------------------------------------------------------

def resource_root() -> pathlib.Path:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return pathlib.Path(getattr(sys, "_MEIPASS"))
    here = pathlib.Path(__file__).resolve().parent
    if (here.parent / "Resources" / "Sounds").is_dir():
        return here.parent
    return here


def app_data_dir() -> pathlib.Path:
    if IS_WINDOWS:
        base = pathlib.Path(os.environ.get("APPDATA", str(pathlib.Path.home() / "AppData/Roaming")))
    else:
        base = pathlib.Path.home() / ".config"
    folder = base / "FokusBar"
    folder.mkdir(parents=True, exist_ok=True)
    return folder


STATE_FILE = app_data_dir() / "state.json"


# ---------------------------------------------------------------------------
# Sounds & Spotify-Playlists (1:1 wie macOS FokusBar)
# ---------------------------------------------------------------------------

FOCUS_SOUNDS = [
    {"id": "off", "group": "Aus", "title": "Stumm (Kein Ton)", "short": "Aus", "desc": "Keine Hintergrundmusik während des Fokus.", "file": None, "spotify": None},
    # Natur & Entspannte Klänge
    {"id": "rain-gentle", "group": "Natur & Entspannte Klänge", "title": "Sanfter Sommerregen", "short": "Sanfter Regen", "desc": "Echte Naturaufnahme · Warmer, gleichmäßiger Sommerregen", "file": "rain-gentle.m4a", "spotify": None},
    {"id": "forest-nature", "group": "Natur & Entspannte Klänge", "title": "Waldruhe & Vögel", "short": "Wald & Vögel", "desc": "Echte Naturaufnahme · Ruhige Waldlichtung mit sanftem Vogelgesang", "file": "forest-nature.m4a", "spotify": None},
    {"id": "forest-stream", "group": "Natur & Entspannte Klänge", "title": "Waldbach & Blätterwind", "short": "Waldbach", "desc": "Echte Naturaufnahme · Klarer Gebirgsbach im tiefen Wald", "file": "forest-stream.m4a", "spotify": None},
    {"id": "rain-window", "group": "Natur & Entspannte Klänge", "title": "Regen am Fenster", "short": "Fensterregen", "desc": "Echte Feldaufnahme · Gemütlicher Regen auf dem Fenstersims", "file": "rain-window.m4a", "spotify": None},
    {"id": "ocean-waves", "group": "Natur & Entspannte Klänge", "title": "Meereswellen · Küste", "short": "Meereswellen", "desc": "Echte Küstenaufnahme · Ruhige Brandung für entspannten Fokus", "file": "ocean-waves.m4a", "spotify": None},
    {"id": "fireplace-cozy", "group": "Natur & Entspannte Klänge", "title": "Kaminfeuer & Regen", "short": "Kaminfeuer", "desc": "Echte Aufnahme · Warm knisterndes Kaminholz", "file": "fireplace-cozy.m4a", "spotify": None},
    {"id": "cafe-lounge", "group": "Natur & Entspannte Klänge", "title": "Entspanntes Café", "short": "Café-Atmosphäre", "desc": "Echte Aufnahme · Dezente, warme Café-Kulisse zum Arbeiten", "file": "cafe-lounge.m4a", "spotify": None},
    # Spotify · Courten & Deep Work
    {"id": "spotify-courten-radio", "group": "Spotify · Courten & Deep Work", "title": "Courten Radio", "short": "Courten Radio", "desc": "Spotify · Offizielles Courten-Radio für fokussierten Flow", "file": None, "spotify": "37i9dQZF1E4viP52QtYaG5"},
    {"id": "spotify-this-is-courten", "group": "Spotify · Courten & Deep Work", "title": "This Is Courten", "short": "This Is Courten", "desc": "Spotify · Alle Courten-Tracks in einer Playlist", "file": None, "spotify": "37i9dQZF1DZ06evO29wWby"},
    {"id": "spotify-courten-penthouse", "group": "Spotify · Courten & Deep Work", "title": "Courten · Penthouse Radio", "short": "Penthouse Radio", "desc": "Spotify · Melodischer Deep-House & elektronischer Fokus", "file": None, "spotify": "37i9dQZF1E8MYiee1jfrBS"},
    {"id": "spotify-deep-focus", "group": "Spotify · Courten & Deep Work", "title": "Deep Focus · Deep Work", "short": "Deep Focus", "desc": "Spotify · Ruhige Ambient- & Post-Rock-Gitarren für langes Arbeiten", "file": None, "spotify": "37i9dQZF1DWZeKCadgRdKQ"},
    {"id": "spotify-focus-flow", "group": "Spotify · Courten & Deep Work", "title": "Focus Flow · Lock-In", "short": "Focus Flow", "desc": "Spotify · Treibende instrumentale Beats für produktiven Tunnelblick", "file": None, "spotify": "37i9dQZF1DWZZbwlv3Vmtr"},
    {"id": "spotify-house-focus", "group": "Spotify · Courten & Deep Work", "title": "House Focus · Deep Work", "short": "House Focus", "desc": "Spotify · Gleichmäßiger 4/4-Groove ohne Gesang", "file": None, "spotify": "37i9dQZF1DX8wtrGDH81Oa"},
    {"id": "spotify-beats-to-think-to", "group": "Spotify · Courten & Deep Work", "title": "Beats to Think To", "short": "Beats to Think", "desc": "Spotify · Elektronische Deep-Work-Beats für Programmieren & Konzeption", "file": None, "spotify": "37i9dQZF1DXa2SPUyWl8Y5"},
    # Spotify · Jazz House & Jazz Lounge
    {"id": "spotify-jazz-house", "group": "Spotify · Jazz House & Jazz Lounge", "title": "Jazz House & Soft Lounge", "short": "Jazz House", "desc": "Spotify · Warme Saxophon- & Rhodes-Chords auf sanftem House-Groove", "file": None, "spotify": "37i9dQZF1DX82pCGH5USnM"},
    {"id": "spotify-smooth-jazz-beats", "group": "Spotify · Jazz House & Jazz Lounge", "title": "Smooth Jazz Beats", "short": "Smooth Jazz", "desc": "Spotify · Entspannte Jazz-Instrumentals & Rhodes-Grooves", "file": None, "spotify": "37i9dQZF1DX06817kK7cRP"},
    {"id": "spotify-jazz-vibes", "group": "Spotify · Jazz House & Jazz Lounge", "title": "Jazz Vibes · Chill Beats", "short": "Jazz Vibes", "desc": "Spotify · Lässige Jazz-Hop- & Chill-Beats für entspanntes Arbeiten", "file": None, "spotify": "37i9dQZF1DX0SM0LYsmbMT"},
    {"id": "spotify-coffee-table-jazz", "group": "Spotify · Jazz House & Jazz Lounge", "title": "Coffee Table Jazz", "short": "Coffee Jazz", "desc": "Spotify · Sanfter Akustik-Jazz wie im ruhigen Lieblingscafé", "file": None, "spotify": "37i9dQZF1DWVqfgj8NZEp1"},
    {"id": "spotify-jazz-background", "group": "Spotify · Jazz House & Jazz Lounge", "title": "Jazz in the Background", "short": "Background Jazz", "desc": "Spotify · Unaufdringlicher Lounge-Jazz für konzentrierte Stunden", "file": None, "spotify": "37i9dQZF1DWV7EzJMK2FUI"},
    {"id": "spotify-lofi-jazz", "group": "Spotify · Jazz House & Jazz Lounge", "title": "Lo-Fi Jazz Café", "short": "Lo-Fi Jazz", "desc": "Spotify · Warme Jazz-Samples mit entspanntem Lo-Fi-Beat", "file": None, "spotify": "37i9dQZF1DX9RwfGbeGQwP"},
]

SOUND_BY_ID = {s["id"]: s for s in FOCUS_SOUNDS}


# ---------------------------------------------------------------------------
# App- & Website-Blocker Presets (inkl. VPN, Proxy & Anti-Detect-Browser)
# ---------------------------------------------------------------------------

WEBSITE_PRESETS = [
    ("instagram.com", "Instagram"),
    ("youtube.com", "YouTube"),
    ("x.com", "X.com (Twitter)"),
    ("tiktok.com", "TikTok"),
    ("reddit.com", "Reddit"),
    ("netflix.com", "Netflix"),
    ("facebook.com", "Facebook"),
    ("twitch.tv", "Twitch"),
    ("linkedin.com", "LinkedIn"),
]

DOMAIN_MIRRORS = {
    "x.com": ["x.com", "twitter.com", "mobile.twitter.com", "nitter.net", "nitter.poast.org", "nitter.privacydev.net", "xcancel.com"],
    "youtube.com": ["youtube.com", "youtu.be", "m.youtube.com", "youtube-nocookie.com", "yewtu.be", "invidious.io", "inv.nadeko.net", "piped.video", "piped.kavin.rocks"],
    "instagram.com": ["instagram.com", "instagr.am", "imginn.com", "pixwox.com", "picuki.com", "dumpor.io", "anonyig.com"],
    "tiktok.com": ["tiktok.com", "vm.tiktok.com", "proxitok.pabloferreiro.es", "urlebird.com", "tikwm.com"],
    "reddit.com": ["reddit.com", "old.reddit.com", "redd.it", "libredd.it", "redlib.catsarch.com", "teddit.net"],
    "facebook.com": ["facebook.com", "fb.com", "m.facebook.com", "messenger.com"],
    "twitch.tv": ["twitch.tv", "m.twitch.tv"],
    "netflix.com": ["netflix.com"],
    "linkedin.com": ["linkedin.com"],
}

WEB_PROXY_DOMAINS = [
    "croxyproxy.com", "croxyproxy.rocks", "proxysite.com", "hide.me", "hidester.com",
    "kproxy.com", "whoer.net", "4everproxy.com", "blockaway.net", "plainproxies.com",
    "filterbypass.me", "vpnbook.com", "proxium.com", "tubeblock.com"
]

COMMON_WINDOWS_APPS = [
    ("Discord.exe", "Discord"),
    ("WhatsApp.exe", "WhatsApp"),
    ("Telegram.exe", "Telegram"),
    ("Slack.exe", "Slack"),
    ("Teams.exe", "Microsoft Teams"),
    ("ms-teams.exe", "Microsoft Teams"),
    ("Signal.exe", "Signal"),
    ("Steam.exe", "Steam"),
    ("EpicGamesLauncher.exe", "Epic Games"),
    ("Battle.net.exe", "Battle.net"),
    ("OUTLOOK.EXE", "Outlook"),
    ("olk.exe", "Outlook"),
    # VPNs & Proxies
    ("NordVPN.exe", "NordVPN"),
    ("ProtonVPN.exe", "ProtonVPN"),
    ("Mullvad VPN.exe", "Mullvad VPN"),
    ("ExpressVPN.exe", "ExpressVPN"),
    ("Surfshark.exe", "Surfshark VPN"),
    ("Windscribe.exe", "Windscribe VPN"),
    ("Clash for Windows.exe", "Clash Proxy"),
    ("Proxifier.exe", "Proxifier"),
    # Anti-Detect Browsers
    ("Dolphin Anty.exe", "Dolphin{anty}"),
    ("AdsPower Global.exe", "AdsPower"),
    ("GoLogin.exe", "GoLogin"),
    ("Multilogin.exe", "Multilogin"),
    ("Incogniton.exe", "Incogniton"),
    ("OctoBrowser.exe", "Octo Browser"),
    ("MoreLogin.exe", "MoreLogin"),
    ("Undetectable.exe", "Undetectable"),
]

# Child processes spawned by Anti-Detect Browsers when a user opens a proxy profile
ANTI_DETECT_PARENT_TO_CHILDREN = {
    "dolphin anty.exe": ["anty.exe", "chrome.exe"],
    "adspower global.exe": ["sunbrowser.exe", "flowerbrowser.exe"],
    "gologin.exe": ["orbita.exe", "chrome.exe"],
    "multilogin.exe": ["mimic.exe", "stealthfox.exe"],
    "octobrowser.exe": ["octium.exe"],
    "morelogin.exe": ["morebrowser.exe"],
}

BROWSER_PROCESS_NAMES = {
    "chrome.exe", "msedge.exe", "brave.exe", "opera.exe", "vivaldi.exe", "arc.exe",
    "firefox.exe", "zen.exe", "waterfox.exe", "librewolf.exe", "duckduckgo.exe",
    # Anti-Detect Browser Profile Engines
    "anty.exe", "sunbrowser.exe", "flowerbrowser.exe", "orbita.exe",
    "mimic.exe", "stealthfox.exe", "octium.exe", "morebrowser.exe"
}

BYPASS_BROWSER_PROCESS_NAMES = {
    "tor.exe", "firefox.exe"  # Tor Browser uses firefox.exe inside Tor Browser folder
}

PROTECTED_PROCESS_NAMES = {
    "explorer.exe", "taskmgr.exe", "cmd.exe", "powershell.exe", "pwsh.exe",
    "python.exe", "pythonw.exe", "fokusbar.exe", "fokusbar-windows.exe",
    "svchost.exe", "csrss.exe", "winlogon.exe", "dwm.exe", "systemsettings.exe"
}


# ---------------------------------------------------------------------------
# Audio-Steuerung für Windows (MCI für .m4a + Hintergrund-Spotify)
# ---------------------------------------------------------------------------

class WindowsAudioController:
    def __init__(self) -> None:
        self.active_sound_id: str | None = None
        self.volume: float = 0.45
        self._mci_open = False

    def _mci(self, command: str) -> int:
        if not IS_WINDOWS:
            return 0
        try:
            buf = ctypes.create_unicode_buffer(256)
            return ctypes.windll.winmm.mciSendStringW(command, buf, 255, 0)
        except Exception:
            return -1

    def sync(self, should_play: bool, sound_id: str, volume: float) -> None:
        self.volume = max(0.05, min(1.0, float(volume)))
        sound = SOUND_BY_ID.get(sound_id, SOUND_BY_ID["off"])
        if not should_play or sound["id"] == "off":
            self.stop()
            return

        if self.active_sound_id == sound["id"]:
            self.set_volume(self.volume)
            return

        self.stop()
        self.active_sound_id = sound["id"]

        if sound["file"]:
            sound_path = resource_root() / "Resources" / "Sounds" / sound["file"]
            if sound_path.exists() and IS_WINDOWS:
                self._mci("close fokussound")
                rc = self._mci(f'open "{sound_path}" type mpegvideo alias fokussound')
                if rc == 0:
                    self._mci_open = True
                    vol_int = int(round(self.volume * 1000))
                    self._mci(f"setaudio fokussound volume to {vol_int}")
                    self._mci("play fokussound repeat")
        elif sound["spotify"]:
            self._start_spotify_background(sound["spotify"])

    def set_volume(self, volume: float) -> None:
        self.volume = max(0.05, min(1.0, float(volume)))
        if self._mci_open and IS_WINDOWS:
            vol_int = int(round(self.volume * 1000))
            self._mci(f"setaudio fokussound volume to {vol_int}")

    def stop(self) -> None:
        if self._mci_open and IS_WINDOWS:
            self._mci("stop fokussound")
            self._mci("close fokussound")
            self._mci_open = False
        self.active_sound_id = None

    def _start_spotify_background(self, playlist_id: str) -> None:
        uri = f"spotify:playlist:{playlist_id}"
        web_url = f"https://open.spotify.com/playlist/{playlist_id}"
        if IS_WINDOWS:
            # Save currently focused window so we can immediately restore focus if Spotify pops up
            fg_hwnd = ctypes.windll.user32.GetForegroundWindow()
            try:
                os.startfile(uri)
            except Exception:
                webbrowser.open(web_url)
                return

            def _restore_and_play() -> None:
                time.sleep(1.2)
                if fg_hwnd:
                    try:
                        ctypes.windll.user32.SetForegroundWindow(fg_hwnd)
                    except Exception:
                        pass
                # Send Media Play/Pause or Next Track virtual key if needed
                time.sleep(1.0)
                if fg_hwnd:
                    try:
                        ctypes.windll.user32.SetForegroundWindow(fg_hwnd)
                    except Exception:
                        pass

            threading.Thread(target=_restore_and_play, daemon=True).start()
        else:
            webbrowser.open(web_url)


# ---------------------------------------------------------------------------
# Windows App- & Website-Blocker (inkl. Anti-Detect-Browser & Proxies)
# ---------------------------------------------------------------------------

class WindowsBlockerController:
    def __init__(self, on_notice=None) -> None:
        self.on_notice = on_notice
        self.is_blocking = False
        self.blocked_apps: list[dict] = []
        self.blocked_websites: list[str] = []
        self._last_notice: dict[str, float] = {}
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None

    def sync(self, is_blocking: bool, blocked_apps: list[dict], blocked_websites: list[str]) -> None:
        self.is_blocking = is_blocking and (bool(blocked_apps) or bool(blocked_websites))
        self.blocked_apps = list(blocked_apps)
        self.blocked_websites = [w.strip().lower() for w in blocked_websites if w.strip()]
        if self.is_blocking:
            self.enforce_once()
            if self._thread is None or not self._thread.is_alive():
                self._stop_event.clear()
                self._thread = threading.Thread(target=self._watchdog_loop, daemon=True)
                self._thread.start()
        else:
            self._stop_event.set()

    def _watchdog_loop(self) -> None:
        while not self._stop_event.is_set():
            if self.is_blocking:
                try:
                    self.enforce_once()
                except Exception:
                    pass
            time.sleep(1.4)

    def enforce_once(self) -> None:
        if not IS_WINDOWS or not self.is_blocking:
            return
        self._enforce_apps()
        if self.blocked_websites:
            self._enforce_websites()

    def _enforce_apps(self) -> None:
        target_exes: dict[str, str] = {}
        for item in self.blocked_apps:
            exe = item.get("exe", "").strip().lower()
            name = item.get("name", exe)
            if not exe or exe in PROTECTED_PROCESS_NAMES:
                continue
            target_exes[exe] = name
            for child in ANTI_DETECT_PARENT_TO_CHILDREN.get(exe, []):
                if child != "chrome.exe":
                    target_exes[child] = f"{name} (Profil-Browser)"

        if not target_exes:
            return

        running = self.list_running_processes()
        for proc_name, pid in running:
            lower = proc_name.lower()
            if lower in target_exes and lower not in PROTECTED_PROCESS_NAMES:
                try:
                    subprocess.run(
                        ["taskkill", "/F", "/PID", str(pid)],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        creationflags=0x08000000,  # CREATE_NO_WINDOW
                    )
                    self._notify(f"App gesperrt: {target_exes[lower]}", key=f"app:{lower}")
                except Exception:
                    pass

    def _enforce_websites(self) -> None:
        keywords: list[tuple[str, str]] = []
        for domain in self.blocked_websites:
            base = domain.split(".")[0]
            if len(base) >= 3:
                keywords.append((base, domain))
            if domain == "x.com":
                keywords.append(("twitter", "x.com"))
                keywords.append((" / x", "x.com"))
            for mirror in DOMAIN_MIRRORS.get(domain, []):
                m_base = mirror.split(".")[0]
                if len(m_base) >= 4:
                    keywords.append((m_base, domain))
        for proxy in WEB_PROXY_DOMAINS:
            p_base = proxy.split(".")[0]
            if len(p_base) >= 5:
                keywords.append((p_base, f"Proxy ({proxy})"))

        if not keywords:
            return

        # Enumerate all visible windows on Windows; if a Browser or Anti-Detect Browser window
        # (Chrome, Edge, Brave, Firefox, Dolphin Anty's Anty.exe, AdsPower's SunBrowser.exe, GoLogin's Orbita)
        # has a blocked website in its title, send Ctrl+W or minimize/close the tab immediately.
        user32 = ctypes.windll.user32
        WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)

        pid_to_exe = {pid: name.lower() for name, pid in self.list_running_processes()}

        def callback(hwnd, _lparam):
            if not user32.IsWindowVisible(hwnd):
                return True
            length = user32.GetWindowTextLengthW(hwnd)
            if length <= 0:
                return True
            buf = ctypes.create_unicode_buffer(length + 1)
            user32.GetWindowTextW(hwnd, buf, length + 1)
            title = buf.value.lower()

            pid = ctypes.c_ulong()
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            exe_name = pid_to_exe.get(pid.value, "")

            # Check if it's a browser or anti-detect profile browser window
            is_browser = (
                exe_name in BROWSER_PROCESS_NAMES
                or any(tag in title for tag in [" - google chrome", " - microsoft​ edge", " - edge", " - brave", " - mozilla firefox", " - vivaldi", " - opera", " - anty", " - sunbrowser", " - orbita"])
            )
            if not is_browser:
                return True

            for kw, label in keywords:
                # Match whole word or domain token in window title
                if re.search(rf"\b{re.escape(kw)}\b", title) or (kw == " / x" and " / x" in title):
                    # Minimize window or send Ctrl+W if foreground
                    if user32.GetForegroundWindow() == hwnd:
                        # Send Ctrl+W to close the active blocked tab
                        VK_CONTROL = 0x11
                        VK_W = 0x57
                        KEYEVENTF_KEYUP = 0x0002
                        user32.keybd_event(VK_CONTROL, 0, 0, 0)
                        user32.keybd_event(VK_W, 0, 0, 0)
                        user32.keybd_event(VK_W, 0, KEYEVENTF_KEYUP, 0)
                        user32.keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0)
                    else:
                        SW_MINIMIZE = 6
                        user32.ShowWindow(hwnd, SW_MINIMIZE)
                    self._notify(f"Webseite im Fokus gesperrt: {label}", key=f"web:{label}")
                    break
            return True

        user32.EnumWindows(WNDENUMPROC(callback), 0)

    def _notify(self, text: str, key: str) -> None:
        now = time.time()
        if now - self._last_notice.get(key, 0.0) > 3.0:
            self._last_notice[key] = now
            if self.on_notice:
                self.on_notice(text)

    @staticmethod
    def list_running_processes() -> list[tuple[str, int]]:
        if not IS_WINDOWS:
            return []
        try:
            out = subprocess.check_output(
                ["tasklist", "/FO", "CSV", "/NH"],
                text=True,
                errors="ignore",
                creationflags=0x08000000,
            )
            result = []
            for line in out.splitlines():
                parts = [p.strip('"') for p in line.split('","')]
                if len(parts) >= 2 and parts[1].isdigit():
                    result.append((parts[0], int(parts[1])))
            return result
        except Exception:
            return []


# ---------------------------------------------------------------------------
# Persistenz & Datenmodell
# ---------------------------------------------------------------------------

def default_state() -> dict:
    return {
        "tasks": [],
        "entries": [],
        "completedFocusSessions": 0,
        "preferences": {
            "focusMinutes": 25,
            "shortBreakMinutes": 5,
            "longBreakMinutes": 15,
            "dailyGoalMinutes": 240,
            "focusSound": "rain-gentle",
            "focusSoundVolume": 0.45,
            "appBlockerEnabled": True,
            "blockedApps": [],
            "blockedWebsites": ["instagram.com", "youtube.com", "x.com"],
            "focusGuardEnabled": True,
            "focusGuardDurationSeconds": 60,
            "floatingTimer": True,
            "floatingTimerScale": 1.0,
        },
    }


def load_state() -> dict:
    state = default_state()
    if STATE_FILE.exists():
        try:
            raw = json.loads(STATE_FILE.read_text(encoding="utf-8"))
            if isinstance(raw, dict):
                state["tasks"] = raw.get("tasks", state["tasks"])
                state["entries"] = raw.get("entries", state["entries"])
                state["completedFocusSessions"] = int(raw.get("completedFocusSessions", 0))
                if isinstance(raw.get("preferences"), dict):
                    state["preferences"].update(raw["preferences"])
        except Exception:
            pass
    return state


def save_state(state: dict) -> None:
    try:
        tmp = STATE_FILE.with_suffix(".tmp")
        tmp.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
        tmp.replace(STATE_FILE)
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Haupt-Anwendung (Dashboard + Schwebende, größenverstellbare LED-Timeruhr)
# ---------------------------------------------------------------------------

class FokusBarWindowsApp:
    CONFIRM_PHRASE = "Ich unterbreche meinen Fokus bewusst"

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("FokusBar")
        self.root.geometry("1040x740")
        self.root.minsize(900, 660)
        self.root.configure(bg="#F3F5F9")

        self.state = load_state()
        self.active_timer: dict | None = None  # {mode, title, project, target, accumulated, start_ts, running}
        self.notice_var = tk.StringVar(value="")

        self.audio = WindowsAudioController()
        self.blocker = WindowsBlockerController(on_notice=self._set_notice_threadsafe)

        self.led_window: tk.Toplevel | None = None
        self.guard_window: tk.Toplevel | None = None

        self._build_ui()
        self._tick()

    def _set_notice_threadsafe(self, msg: str) -> None:
        self.root.after(0, lambda: self._show_notice(msg))

    def _show_notice(self, msg: str) -> None:
        self.notice_var.set(msg)
        self.root.after(4000, lambda: self.notice_var.set("") if self.notice_var.get() == msg else None)

    # -----------------------------------------------------------------------
    # UI-Aufbau (Blaues FokusBar-Design)
    # -----------------------------------------------------------------------

    def _build_ui(self) -> None:
        # Layout: Linke Sidebar (330px) + Rechter Aufgaben-/Einstellungsbereich
        self.main_pane = tk.Frame(self.root, bg="#F3F5F9")
        self.main_pane.pack(fill="both", expand=True)

        self.sidebar = tk.Frame(self.main_pane, bg="#E8ECF4", width=350, padx=16, pady=16)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        self.content = tk.Frame(self.main_pane, bg="#F3F5F9", padx=24, pady=20)
        self.content.pack(side="left", fill="both", expand=True)

        self._build_sidebar()
        self._build_content()

    def _build_sidebar(self) -> None:
        for w in self.sidebar.winfo_children():
            w.destroy()

        # Header
        hdr = tk.Frame(self.sidebar, bg="#E8ECF4")
        hdr.pack(fill="x", pady=(0, 12))
        icon_lbl = tk.Label(hdr, text="✓", font=("Segoe UI", 14, "bold"), bg="#1F5EFF", fg="white", width=2)
        icon_lbl.pack(side="left", padx=(0, 8))
        title_box = tk.Frame(hdr, bg="#E8ECF4")
        title_box.pack(side="left")
        tk.Label(title_box, text="FokusBar", font=("Segoe UI", 14, "bold"), bg="#E8ECF4", fg="#0F172A").pack(anchor="w")
        today_mins = self._today_focus_minutes()
        goal_mins = self.state["preferences"].get("dailyGoalMinutes", 240)
        tk.Label(
            title_box,
            text=f"Heute: {today_mins} Min. von {goal_mins} Min. Ziel",
            font=("Segoe UI", 9),
            bg="#E8ECF4",
            fg="#475569",
        ).pack(anchor="w")

        if self.active_timer is not None:
            self._build_active_timer_card(self.sidebar)
        else:
            self._build_start_timer_card(self.sidebar)

    def _build_start_timer_card(self, parent: tk.Widget) -> None:
        card = tk.Frame(parent, bg="white", padx=14, pady=14, highlightbackground="#CBD5E1", highlightthickness=1)
        card.pack(fill="x", pady=(0, 10))

        tk.Label(card, text="Fokus-Session starten", font=("Segoe UI", 12, "bold"), bg="white", fg="#0F172A").pack(anchor="w", pady=(0, 8))

        # Modus-Auswahl
        self.mode_var = getattr(self, "mode_var", tk.StringVar(value="focus"))
        modes_frame = tk.Frame(card, bg="white")
        modes_frame.pack(fill="x", pady=(0, 10))
        for m_id, m_label in [("focus", "🎯 Fokus"), ("countdown", "⏳ Countdown"), ("stopwatch", "⏱ Stoppuhr"), ("rest", "☕ Pause")]:
            btn = tk.Radiobutton(
                modes_frame,
                text=m_label,
                variable=self.mode_var,
                value=m_id,
                indicatoron=False,
                font=("Segoe UI", 9, "bold"),
                selectcolor="#1F5EFF",
                bg="#EEF2F9",
                fg="#1E293B",
                padx=6,
                pady=5,
                bd=0,
            )
            btn.pack(side="left", expand=True, fill="x", padx=2)

        # Fokus-Dauer Presets (15 / 25 / 45 / 60 / 90 Min.)
        dur_hdr = tk.Frame(card, bg="white")
        dur_hdr.pack(fill="x", pady=(2, 4))
        tk.Label(dur_hdr, text="Fokus-Dauer (Minuten):", font=("Segoe UI", 9, "bold"), bg="white", fg="#334155").pack(side="left")
        self.duration_var = getattr(self, "duration_var", tk.IntVar(value=int(self.state["preferences"].get("focusMinutes", 25))))
        dur_spin = tk.Spinbox(dur_hdr, from_=1, to=240, textvariable=self.duration_var, width=5, font=("Segoe UI", 9, "bold"))
        dur_spin.pack(side="right")

        presets_row = tk.Frame(card, bg="white")
        presets_row.pack(fill="x", pady=(0, 10))
        for mins in [15, 25, 45, 60, 90]:
            tk.Button(
                presets_row,
                text=f"{mins}m",
                font=("Segoe UI", 8, "bold"),
                bg="#E2E8F0",
                fg="#0F172A",
                bd=0,
                padx=6,
                pady=3,
                command=lambda m=mins: self._set_focus_minutes(m),
            ).pack(side="left", expand=True, fill="x", padx=1)

        # Fokus-Musik & Playlists
        snd_box = tk.Frame(card, bg="#F8FAFC", padx=10, pady=8, highlightbackground="#E2E8F0", highlightthickness=1)
        snd_box.pack(fill="x", pady=(0, 10))
        tk.Label(snd_box, text="🎧 Fokus-Musik & Playlists (Shuffle)", font=("Segoe UI", 9, "bold"), bg="#F8FAFC", fg="#1F5EFF").pack(anchor="w")

        current_sound_id = self.state["preferences"].get("focusSound", "rain-gentle")
        self.sound_var = tk.StringVar(value=current_sound_id)
        sound_titles = [f'{s["title"]} ({s["group"].split("·")[0].strip()})' for s in FOCUS_SOUNDS]
        sound_ids = [s["id"] for s in FOCUS_SOUNDS]

        self.sound_combo = ttk.Combobox(snd_box, values=sound_titles, state="readonly", font=("Segoe UI", 9))
        try:
            idx = sound_ids.index(current_sound_id)
        except ValueError:
            idx = 1
        self.sound_combo.current(idx)
        self.sound_combo.pack(fill="x", pady=(4, 6))

        def on_sound_selected(_event=None):
            sel_idx = self.sound_combo.current()
            if 0 <= sel_idx < len(sound_ids):
                sid = sound_ids[sel_idx]
                self.state["preferences"]["focusSound"] = sid
                save_state(self.state)

        self.sound_combo.bind("<<ComboboxSelected>>", on_sound_selected)

        # Schnellwahl-Chips (Natur / Deep Work / Jazz)
        quick_snd = tk.Frame(snd_box, bg="#F8FAFC")
        quick_snd.pack(fill="x", pady=(0, 4))
        for sid, lbl in [
            ("rain-gentle", "🌧 Regen"),
            ("forest-nature", "🌲 Wald"),
            ("spotify-courten-radio", "📻 Courten"),
            ("spotify-jazz-house", "🎷 Jazz House"),
        ]:
            tk.Button(
                quick_snd,
                text=lbl,
                font=("Segoe UI", 8),
                bg="#E2E8F0",
                fg="#0F172A",
                bd=0,
                padx=5,
                pady=2,
                command=lambda s=sid: self._select_sound_by_id(s, sound_ids),
            ).pack(side="left", expand=True, fill="x", padx=1)

        # Lautstärke
        vol_row = tk.Frame(snd_box, bg="#F8FAFC")
        vol_row.pack(fill="x")
        tk.Label(vol_row, text="🔊", bg="#F8FAFC", font=("Segoe UI", 9)).pack(side="left")
        self.vol_scale = tk.Scale(
            vol_row,
            from_=5,
            to=100,
            orient="horizontal",
            bg="#F8FAFC",
            highlightthickness=0,
            bd=0,
            showvalue=True,
            command=self._on_volume_slider,
        )
        self.vol_scale.set(int(round(self.state["preferences"].get("focusSoundVolume", 0.45) * 100)))
        self.vol_scale.pack(side="left", fill="x", expand=True)

        # App- & Web-Blocker
        blk_box = tk.Frame(card, bg="#F8FAFC", padx=10, pady=8, highlightbackground="#E2E8F0", highlightthickness=1)
        blk_box.pack(fill="x", pady=(0, 10))
        self.blocker_enabled_var = tk.BooleanVar(value=bool(self.state["preferences"].get("appBlockerEnabled", True)))
        tk.Checkbutton(
            blk_box,
            text="🔒 App- & Website-Blocker im Fokus aktiv",
            variable=self.blocker_enabled_var,
            bg="#F8FAFC",
            fg="#1F5EFF",
            font=("Segoe UI", 9, "bold"),
            command=self._toggle_blocker_pref,
        ).pack(anchor="w")

        # 1-Klick Website-Pills
        web_row = tk.Frame(blk_box, bg="#F8FAFC")
        web_row.pack(fill="x", pady=(4, 4))
        blocked_sites = set(self.state["preferences"].get("blockedWebsites", []))
        for dom, lbl in WEBSITE_PRESETS[:4]:
            is_on = dom in blocked_sites
            tk.Button(
                web_row,
                text=f"{'🔒 ' if is_on else ''}{lbl}",
                font=("Segoe UI", 8, "bold" if is_on else "normal"),
                bg="#1F5EFF" if is_on else "#E2E8F0",
                fg="white" if is_on else "#1E293B",
                bd=0,
                padx=5,
                pady=2,
                command=lambda d=dom: self._toggle_website(d),
            ).pack(side="left", expand=True, fill="x", padx=1)

        # 1-Klick App-Pills
        app_row = tk.Frame(blk_box, bg="#F8FAFC")
        app_row.pack(fill="x", pady=(2, 2))
        blocked_exes = {a.get("exe", "").lower() for a in self.state["preferences"].get("blockedApps", [])}
        for exe, lbl in [("Discord.exe", "Discord"), ("WhatsApp.exe", "WhatsApp"), ("Telegram.exe", "Telegram"), ("Dolphin Anty.exe", "Dolphin")]:
            is_on = exe.lower() in blocked_exes
            tk.Button(
                app_row,
                text=f"{'🔒 ' if is_on else ''}{lbl}",
                font=("Segoe UI", 8, "bold" if is_on else "normal"),
                bg="#1F5EFF" if is_on else "#E2E8F0",
                fg="white" if is_on else "#1E293B",
                bd=0,
                padx=5,
                pady=2,
                command=lambda e=exe, n=lbl: self._toggle_blocked_app(e, n),
            ).pack(side="left", expand=True, fill="x", padx=1)

        # Start-Button
        tk.Button(
            card,
            text="▶ Fokus jetzt starten",
            font=("Segoe UI", 11, "bold"),
            bg="#1F5EFF",
            fg="white",
            activebackground="#1749CC",
            activeforeground="white",
            bd=0,
            pady=9,
            cursor="hand2",
            command=self.start_timer,
        ).pack(fill="x", pady=(4, 0))

    def _build_active_timer_card(self, parent: tk.Widget) -> None:
        active = self.active_timer
        if not active:
            return
        hero = tk.Frame(parent, bg="#1F5EFF", padx=16, pady=16)
        hero.pack(fill="x", pady=(0, 10))

        tk.Label(
            hero,
            text=f"🎯 {active['mode'].upper()} · {'LÄUFT' if active['running'] else 'PAUSIERT'}",
            font=("Segoe UI", 9, "bold"),
            bg="#1F5EFF",
            fg="#DBEAFE",
        ).pack(anchor="w")

        tk.Label(
            hero,
            text=active["title"],
            font=("Segoe UI", 13, "bold"),
            bg="#1F5EFF",
            fg="white",
            wraplength=290,
            justify="left",
        ).pack(anchor="w", pady=(4, 2))

        self.hero_clock_lbl = tk.Label(
            hero,
            text="25:00",
            font=("Consolas", 34, "bold"),
            bg="#1F5EFF",
            fg="white",
        )
        self.hero_clock_lbl.pack(anchor="w", pady=(2, 4))

        # -5m / +5m
        adj_row = tk.Frame(hero, bg="#1F5EFF")
        adj_row.pack(anchor="w", pady=(0, 8))
        tk.Button(adj_row, text="-5 Min.", font=("Segoe UI", 8, "bold"), bg="#3B73FF", fg="white", bd=0, padx=8, pady=3, command=lambda: self.adjust_active_minutes(-5)).pack(side="left", padx=(0, 6))
        tk.Button(adj_row, text="+5 Min.", font=("Segoe UI", 8, "bold"), bg="#3B73FF", fg="white", bd=0, padx=8, pady=3, command=lambda: self.adjust_active_minutes(5)).pack(side="left")

        # Blocker-Status
        n_apps = len(self.state["preferences"].get("blockedApps", []))
        n_sites = len(self.state["preferences"].get("blockedWebsites", []))
        tk.Label(
            hero,
            text=f"🔒 {n_apps} Apps & {n_sites} Webseiten gesperrt (inkl. VPN/Proxy-Schutz)",
            font=("Segoe UI", 8, "bold"),
            bg="#1749CC",
            fg="white",
            padx=8,
            pady=5,
        ).pack(fill="x", pady=(0, 10))

        # Pause / Stop (mit 🔒 Fokus-Schutz!)
        btn_row = tk.Frame(hero, bg="#1F5EFF")
        btn_row.pack(fill="x")
        guard_on = bool(self.state["preferences"].get("focusGuardEnabled", True)) and active["mode"] != "rest"
        lock_suffix = " 🔒" if guard_on and active["running"] else ""
        pause_text = f"⏸ Pausieren{lock_suffix}" if active["running"] else "▶ Fortsetzen"
        tk.Button(
            btn_row,
            text=pause_text,
            font=("Segoe UI", 10, "bold"),
            bg="white",
            fg="#1F5EFF",
            bd=0,
            pady=7,
            command=self.request_pause_or_resume,
        ).pack(side="left", expand=True, fill="x", padx=(0, 4))

        tk.Button(
            btn_row,
            text=f"⏹ Stoppen{lock_suffix}",
            font=("Segoe UI", 10, "bold"),
            bg="#1749CC",
            fg="white",
            bd=0,
            pady=7,
            command=self.request_stop_timer,
        ).pack(side="left", expand=True, fill="x", padx=(4, 0))

    def _build_content(self) -> None:
        for w in self.content.winfo_children():
            w.destroy()

        # Top Bar
        top = tk.Frame(self.content, bg="#F3F5F9")
        top.pack(fill="x", pady=(0, 14))
        tk.Label(top, text="Heute & Aufgaben", font=("Segoe UI", 20, "bold"), bg="#F3F5F9", fg="#0F172A").pack(side="left")

        # LED-Timer Größen-Steuerung oben rechts
        size_box = tk.Frame(top, bg="#F3F5F9")
        size_box.pack(side="right")
        tk.Label(size_box, text="LED-Timer Größe:", font=("Segoe UI", 9, "bold"), bg="#F3F5F9", fg="#475569").pack(side="left", padx=(0, 6))
        for pct in [65, 80, 100, 115]:
            tk.Button(
                size_box,
                text=f"{pct}%",
                font=("Segoe UI", 8, "bold"),
                bg="#E2E8F0",
                fg="#0F172A",
                bd=0,
                padx=6,
                pady=3,
                command=lambda p=pct / 100.0: self.set_led_scale(p),
            ).pack(side="left", padx=2)

        # Notice Banner
        notice_lbl = tk.Label(self.content, textvariable=self.notice_var, font=("Segoe UI", 9, "bold"), bg="#F3F5F9", fg="#DC2626")
        notice_lbl.pack(anchor="w")

        # Schnelleingabe
        add_box = tk.Frame(self.content, bg="white", padx=12, pady=10, highlightbackground="#CBD5E1", highlightthickness=1)
        add_box.pack(fill="x", pady=(4, 16))
        self.quick_entry_var = tk.StringVar()
        entry = tk.Entry(
            add_box,
            textvariable=self.quick_entry_var,
            font=("Segoe UI", 11),
            bd=0,
            bg="white",
            fg="#0F172A",
        )
        entry.pack(side="left", fill="x", expand=True)
        entry.bind("<Return>", lambda _e: self.add_task_from_entry())
        tk.Button(
            add_box,
            text="+ Aufgabe anlegen",
            font=("Segoe UI", 9, "bold"),
            bg="#1F5EFF",
            fg="white",
            bd=0,
            padx=12,
            pady=5,
            command=self.add_task_from_entry,
        ).pack(side="right", padx=(8, 0))

        # Aufgabenliste
        self.tasks_container = tk.Frame(self.content, bg="#F3F5F9")
        self.tasks_container.pack(fill="both", expand=True)
        self._render_tasks_list()

        # Unten: Eigene Webseite oder App zur Sperrliste hinzufügen
        custom_blk = tk.Frame(self.content, bg="white", padx=14, pady=12, highlightbackground="#CBD5E1", highlightthickness=1)
        custom_blk.pack(fill="x", pady=(12, 0))
        tk.Label(
            custom_blk,
            text="🛡 Eigene Webseite oder Windows-App (.exe) zur Fokus-Sperrliste hinzufügen:",
            font=("Segoe UI", 9, "bold"),
            bg="white",
            fg="#0F172A",
        ).pack(anchor="w", pady=(0, 6))

        row = tk.Frame(custom_blk, bg="white")
        row.pack(fill="x")
        self.custom_domain_var = tk.StringVar()
        tk.Entry(row, textvariable=self.custom_domain_var, font=("Segoe UI", 9), bg="#F8FAFC", width=28).pack(side="left", padx=(0, 6), ipady=3)
        tk.Button(
            row,
            text="+ Domain sperren",
            font=("Segoe UI", 8, "bold"),
            bg="#1F5EFF",
            fg="white",
            bd=0,
            padx=10,
            pady=4,
            command=self.add_custom_website,
        ).pack(side="left", padx=(0, 12))

        tk.Button(
            row,
            text="📁 Programm (.exe) auswählen …",
            font=("Segoe UI", 8, "bold"),
            bg="#E2E8F0",
            fg="#0F172A",
            bd=0,
            padx=10,
            pady=4,
            command=self.pick_custom_exe,
        ).pack(side="left")

        sites_str = ", ".join(self.state["preferences"].get("blockedWebsites", [])) or "Keine"
        apps_str = ", ".join(a.get("name", "") for a in self.state["preferences"].get("blockedApps", [])) or "Keine"
        tk.Label(
            custom_blk,
            text=f"Aktuell gesperrte Webseiten: {sites_str}\nAktuell gesperrte Apps: {apps_str}",
            font=("Segoe UI", 8),
            bg="white",
            fg="#475569",
            justify="left",
        ).pack(anchor="w", pady=(6, 0))

    def _render_tasks_list(self) -> None:
        for w in self.tasks_container.winfo_children():
            w.destroy()

        tasks = self.state.get("tasks", [])
        if not tasks:
            empty = tk.Frame(self.tasks_container, bg="white", padx=20, pady=24, highlightbackground="#E2E8F0", highlightthickness=1)
            empty.pack(fill="x")
            tk.Label(empty, text="Noch keine Aufgaben für heute", font=("Segoe UI", 11, "bold"), bg="white", fg="#334155").pack()
            tk.Label(empty, text="Tippe oben eine Aufgabe ein (z. B. „Store-Launch prüfen #Ecom !“) oder starte direkt links eine Fokus-Session.", font=("Segoe UI", 9), bg="white", fg="#64748B").pack(pady=(4, 0))
            return

        for task in tasks:
            row = tk.Frame(self.tasks_container, bg="white", padx=12, pady=10, highlightbackground="#E2E8F0", highlightthickness=1)
            row.pack(fill="x", pady=(0, 6))
            is_done = bool(task.get("completed"))
            chk = tk.Button(
                row,
                text="✓" if is_done else "○",
                font=("Segoe UI", 10, "bold"),
                bg="#1F5EFF" if is_done else "white",
                fg="white" if is_done else "#64748B",
                bd=0,
                width=3,
                command=lambda tid=task["id"]: self.toggle_task_done(tid),
            )
            chk.pack(side="left", padx=(0, 8))

            lbl = tk.Label(
                row,
                text=task["title"],
                font=("Segoe UI", 10, "overstrike" if is_done else "bold"),
                bg="white",
                fg="#94A3B8" if is_done else "#0F172A",
            )
            lbl.pack(side="left")

            if task.get("project"):
                tk.Label(row, text=f"#{task['project']}", font=("Segoe UI", 8, "bold"), bg="#EFF6FF", fg="#1F5EFF", padx=6, pady=2).pack(side="left", padx=8)

            if not is_done:
                tk.Button(
                    row,
                    text="▶ Fokus",
                    font=("Segoe UI", 8, "bold"),
                    bg="#EEF2F9",
                    fg="#1F5EFF",
                    bd=0,
                    padx=8,
                    pady=3,
                    command=lambda t=task: self.start_timer_for_task(t),
                ).pack(side="right")

    # -----------------------------------------------------------------------
    # Aktionen & Timer-Steuerung
    # -----------------------------------------------------------------------

    def _set_focus_minutes(self, mins: int) -> None:
        self.duration_var.set(mins)
        self.state["preferences"]["focusMinutes"] = mins
        save_state(self.state)

    def _select_sound_by_id(self, sound_id: str, sound_ids: list[str]) -> None:
        self.state["preferences"]["focusSound"] = sound_id
        save_state(self.state)
        if sound_id in sound_ids:
            self.sound_combo.current(sound_ids.index(sound_id))

    def _on_volume_slider(self, val: str) -> None:
        v = max(0.05, min(1.0, float(val) / 100.0))
        self.state["preferences"]["focusSoundVolume"] = v
        save_state(self.state)
        self.audio.set_volume(v)

    def _toggle_blocker_pref(self) -> None:
        self.state["preferences"]["appBlockerEnabled"] = bool(self.blocker_enabled_var.get())
        save_state(self.state)

    def _toggle_website(self, domain: str) -> None:
        sites = list(self.state["preferences"].get("blockedWebsites", []))
        if domain in sites:
            sites.remove(domain)
        else:
            sites.append(domain)
        self.state["preferences"]["blockedWebsites"] = sites
        save_state(self.state)
        self._build_sidebar()
        self._build_content()

    def _toggle_blocked_app(self, exe: str, name: str) -> None:
        apps = list(self.state["preferences"].get("blockedApps", []))
        existing = [a for a in apps if a.get("exe", "").lower() == exe.lower()]
        if existing:
            apps = [a for a in apps if a.get("exe", "").lower() != exe.lower()]
        else:
            apps.append({"exe": exe, "name": name})
        self.state["preferences"]["blockedApps"] = apps
        save_state(self.state)
        self._build_sidebar()
        self._build_content()

    def add_custom_website(self) -> None:
        raw = self.custom_domain_var.get().strip().lower()
        raw = re.sub(r"^https?://", "", raw).split("/")[0]
        if raw.startswith("www."):
            raw = raw[4:]
        if "." in raw and len(raw) >= 4:
            sites = list(self.state["preferences"].get("blockedWebsites", []))
            if raw not in sites:
                sites.append(raw)
                self.state["preferences"]["blockedWebsites"] = sites
                save_state(self.state)
            self.custom_domain_var.set("")
            self._build_sidebar()
            self._build_content()

    def pick_custom_exe(self) -> None:
        path = filedialog.askopenfilename(
            title="Windows-Programm (.exe) zum Sperren auswählen",
            filetypes=[("Programme", "*.exe"), ("Alle Dateien", "*.*")],
        )
        if path:
            p = pathlib.Path(path)
            exe = p.name
            name = p.stem
            self._toggle_blocked_app(exe, name)

    def add_task_from_entry(self) -> None:
        raw = self.quick_entry_var.get().strip()
        if not raw:
            return
        project = ""
        words = []
        for token in raw.split():
            if token.startswith("#") and len(token) > 1:
                project = token[1:]
            else:
                words.append(token)
        title = " ".join(words).strip() or raw
        self.state["tasks"].insert(
            0,
            {"id": str(uuid.uuid4()), "title": title, "project": project, "completed": False},
        )
        save_state(self.state)
        self.quick_entry_var.set("")
        self._render_tasks_list()

    def toggle_task_done(self, task_id: str) -> None:
        for t in self.state["tasks"]:
            if t["id"] == task_id:
                t["completed"] = not t.get("completed", False)
                break
        save_state(self.state)
        self._render_tasks_list()

    def start_timer_for_task(self, task: dict) -> None:
        self._start_session(mode="focus", title=task["title"], project=task.get("project", ""))

    def start_timer(self) -> None:
        mode = self.mode_var.get() if hasattr(self, "mode_var") else "focus"
        mins = int(self.duration_var.get()) if hasattr(self, "duration_var") else 25
        self.state["preferences"]["focusMinutes"] = mins
        save_state(self.state)
        default_titles = {
            "focus": "Deep Work Fokus",
            "countdown": "Countdown",
            "stopwatch": "Stoppuhr",
            "rest": "Pause",
        }
        self._start_session(mode=mode, title=default_titles.get(mode, "Fokus"), project="")

    def _start_session(self, mode: str, title: str, project: str) -> None:
        mins = int(self.state["preferences"].get("focusMinutes", 25))
        if mode == "rest":
            mins = int(self.state["preferences"].get("shortBreakMinutes", 5))
        target = 0 if mode == "stopwatch" else max(60, mins * 60)
        self.active_timer = {
            "mode": mode,
            "title": title,
            "project": project,
            "target": target,
            "accumulated": 0.0,
            "start_ts": time.time(),
            "running": True,
        }
        self._sync_subsystems()
        self._build_sidebar()
        self._ensure_led_window()

    def adjust_active_minutes(self, delta_mins: int) -> None:
        if not self.active_timer or self.active_timer["mode"] == "stopwatch":
            return
        self.active_timer["target"] = max(60, min(240 * 60, self.active_timer["target"] + delta_mins * 60))
        self._update_clocks()

    # -----------------------------------------------------------------------
    # Fokus-Schutz (60 Sek. Durchatmen + Bestätigungssatz)
    # -----------------------------------------------------------------------

    def request_pause_or_resume(self) -> None:
        if not self.active_timer:
            return
        if not self.active_timer["running"]:
            self.active_timer["start_ts"] = time.time()
            self.active_timer["running"] = True
            self._sync_subsystems()
            self._build_sidebar()
            return

        if self._requires_focus_guard():
            self._open_focus_guard_dialog(action="pause")
        else:
            self._perform_pause()

    def request_stop_timer(self) -> None:
        if not self.active_timer:
            return
        if self._requires_focus_guard():
            self._open_focus_guard_dialog(action="stop")
        else:
            self._perform_stop()

    def _requires_focus_guard(self) -> bool:
        if not self.active_timer:
            return False
        if self.active_timer["mode"] == "rest":
            return False
        return bool(self.state["preferences"].get("focusGuardEnabled", True))

    def _perform_pause(self) -> None:
        if not self.active_timer or not self.active_timer["running"]:
            return
        self.active_timer["accumulated"] += time.time() - self.active_timer["start_ts"]
        self.active_timer["running"] = False
        self._sync_subsystems()
        self._build_sidebar()

    def _perform_stop(self) -> None:
        if not self.active_timer:
            return
        elapsed = self._current_elapsed()
        if self.active_timer["mode"] != "rest" and elapsed >= 30:
            self.state["entries"].append(
                {
                    "title": self.active_timer["title"],
                    "seconds": int(elapsed),
                    "date": dt.date.today().isoformat(),
                }
            )
            save_state(self.state)
        self.active_timer = None
        self._sync_subsystems()
        if self.led_window is not None:
            self.led_window.destroy()
            self.led_window = None
        self._build_sidebar()
        self._build_content()

    def _open_focus_guard_dialog(self, action: str) -> None:
        if self.guard_window is not None and self.guard_window.winfo_exists():
            self.guard_window.lift()
            return

        total_secs = int(self.state["preferences"].get("focusGuardDurationSeconds", 60))
        win = tk.Toplevel(self.root)
        win.title("Fokus-Schutz · Erst durchatmen")
        win.geometry("460x410")
        win.configure(bg="#0F172A")
        win.attributes("-topmost", True)
        self.guard_window = win

        state = {
            "remaining": total_secs,
            "checkpoint_due": False,
            "ticks_since_checkpoint": 0,
        }

        tk.Label(
            win,
            text="🧘‍♂️ Fokus-Schutz aktiv: Erst durchatmen",
            font=("Segoe UI", 13, "bold"),
            bg="#0F172A",
            fg="white",
        ).pack(pady=(16, 4))

        tk.Label(
            win,
            text="Dein Fokus läuft weiter. Atme 60 Sekunden ruhig durch\nund bestätige alle 10 Sek. den Atem-Impuls.",
            font=("Segoe UI", 9),
            bg="#0F172A",
            fg="#94A3B8",
        ).pack(pady=(0, 12))

        phase_lbl = tk.Label(win, text="Tief durch die Nase einatmen …", font=("Segoe UI", 12, "bold"), bg="#1E293B", fg="#38BDF8", padx=16, pady=10)
        phase_lbl.pack(fill="x", padx=24, pady=(0, 8))

        countdown_lbl = tk.Label(win, text=f"Noch {total_secs}s Durchatmen", font=("Consolas", 18, "bold"), bg="#0F172A", fg="white")
        countdown_lbl.pack(pady=(0, 8))

        checkpoint_btn = tk.Button(
            win,
            text="✓ Ich atme ruhig weiter (hier klicken)",
            font=("Segoe UI", 9, "bold"),
            bg="#F59E0B",
            fg="#0F172A",
            bd=0,
            padx=12,
            pady=6,
        )

        def confirm_checkpoint():
            state["checkpoint_due"] = False
            state["ticks_since_checkpoint"] = 0
            checkpoint_btn.pack_forget()

        checkpoint_btn.configure(command=confirm_checkpoint)

        tk.Label(
            win,
            text=f'Bestätigungssatz abtippen:\n„{self.CONFIRM_PHRASE}“',
            font=("Segoe UI", 9),
            bg="#0F172A",
            fg="#CBD5E1",
        ).pack(pady=(8, 4))

        phrase_var = tk.StringVar()
        phrase_entry = tk.Entry(win, textvariable=phrase_var, font=("Segoe UI", 10), width=38, bg="#1E293B", fg="white", insertbackground="white")
        phrase_entry.pack(pady=(0, 12), ipady=4)
        # Prevent paste shortcut
        phrase_entry.bind("<Control-v>", lambda _e: "break")

        btn_bar = tk.Frame(win, bg="#0F172A")
        btn_bar.pack(fill="x", padx=24, pady=(6, 0))

        tk.Button(
            btn_bar,
            text="Weiter fokussieren",
            font=("Segoe UI", 10, "bold"),
            bg="#1F5EFF",
            fg="white",
            bd=0,
            padx=14,
            pady=7,
            command=win.destroy,
        ).pack(side="left", expand=True, fill="x", padx=(0, 6))

        unlock_btn = tk.Button(
            btn_bar,
            text="🔒 Gesperrt",
            font=("Segoe UI", 10, "bold"),
            bg="#334155",
            fg="#94A3B8",
            bd=0,
            padx=14,
            pady=7,
            state="disabled",
        )
        unlock_btn.pack(side="left", expand=True, fill="x", padx=(6, 0))

        def do_unlock():
            if state["remaining"] > 0 or phrase_var.get().strip().lower() != self.CONFIRM_PHRASE.lower():
                return
            win.destroy()
            if action == "pause":
                self._perform_pause()
            else:
                self._perform_stop()

        unlock_btn.configure(command=do_unlock)

        def update_guard():
            if not win.winfo_exists():
                return
            if state["remaining"] > 0:
                if not state["checkpoint_due"]:
                    state["remaining"] -= 1
                    state["ticks_since_checkpoint"] += 1
                    if state["ticks_since_checkpoint"] >= 10 and state["remaining"] > 0:
                        state["checkpoint_due"] = True
                        checkpoint_btn.pack(pady=(0, 8))
                cycle = (total_secs - state["remaining"]) % 12
                if cycle < 4:
                    phase_lbl.configure(text="🌬 Tief durch die Nase einatmen (4s) …")
                elif cycle < 8:
                    phase_lbl.configure(text="⏸ Atem ruhig halten (4s) …")
                else:
                    phase_lbl.configure(text="🍃 Langsam und entspannt ausatmen (4s) …")
                countdown_lbl.configure(
                    text="Bitte kurz bestätigen ↑" if state["checkpoint_due"] else f"Noch {state['remaining']}s Durchatmen"
                )
            else:
                countdown_lbl.configure(text="✓ Atemübung abgeschlossen")

            phrase_ok = phrase_var.get().strip().lower() == self.CONFIRM_PHRASE.lower()
            if state["remaining"] <= 0 and phrase_ok:
                unlock_btn.configure(
                    state="normal",
                    bg="#DC2626",
                    fg="white",
                    text="Jetzt pausieren" if action == "pause" else "Jetzt beenden",
                )
            else:
                unlock_btn.configure(state="disabled", bg="#334155", fg="#94A3B8", text="🔒 Gesperrt")

            win.after(1000, update_guard)

        update_guard()

    # -----------------------------------------------------------------------
    # Schwebende, frei verschiebbare & größenverstellbare LED-Timeruhr
    # -----------------------------------------------------------------------

    def set_led_scale(self, scale: float) -> None:
        clamped = max(0.55, min(1.35, round(scale, 2)))
        self.state["preferences"]["floatingTimerScale"] = clamped
        save_state(self.state)
        if self.led_window is not None and self.led_window.winfo_exists():
            self._apply_led_window_geometry()

    def _ensure_led_window(self) -> None:
        if not self.state["preferences"].get("floatingTimer", True):
            return
        if self.led_window is not None and self.led_window.winfo_exists():
            return

        win = tk.Toplevel(self.root)
        win.overrideredirect(True)
        win.attributes("-topmost", True)
        win.configure(bg="#0B0F17", highlightbackground="#38BDF8", highlightthickness=1)
        self.led_window = win

        self.led_mode_lbl = tk.Label(win, text="● FOKUS", font=("Consolas", 9, "bold"), bg="#0B0F17", fg="#38BDF8")
        self.led_mode_lbl.pack(anchor="w", padx=10, pady=(6, 0))

        self.led_digits_lbl = tk.Label(win, text="25:00", font=("Consolas", 26, "bold"), bg="#05080F", fg="#7DD3FC", padx=12, pady=4)
        self.led_digits_lbl.pack(fill="x", padx=10, pady=4)

        bot = tk.Frame(win, bg="#0B0F17")
        bot.pack(fill="x", padx=10, pady=(0, 6))
        self.led_task_lbl = tk.Label(bot, text="Deep Work", font=("Segoe UI", 8, "bold"), bg="#0B0F17", fg="#E2E8F0")
        self.led_task_lbl.pack(side="left")

        # Resize-Grip unten rechts (zum Kleiner-/Größerziehen mit der Maus!)
        grip = tk.Label(bot, text="↘ Größe ziehen", font=("Segoe UI", 7), bg="#0B0F17", fg="#64748B", cursor="size_nw_se")
        grip.pack(side="right")

        # Dragging to move
        drag_state = {"x": 0, "y": 0}

        def start_move(event):
            drag_state["x"] = event.x_root - win.winfo_x()
            drag_state["y"] = event.y_root - win.winfo_y()

        def do_move(event):
            nx = event.x_root - drag_state["x"]
            ny = event.y_root - drag_state["y"]
            win.geometry(f"+{nx}+{ny}")

        for widget in (win, self.led_mode_lbl, self.led_digits_lbl, self.led_task_lbl):
            widget.bind("<ButtonPress-1>", start_move)
            widget.bind("<B1-Motion>", do_move)

        # Dragging the grip to resize smoothly (55% to 135%)
        resize_state = {"start_x": 0, "start_scale": 1.0}

        def start_resize(event):
            resize_state["start_x"] = event.x_root
            resize_state["start_scale"] = float(self.state["preferences"].get("floatingTimerScale", 1.0))

        def do_resize(event):
            dx = event.x_root - resize_state["start_x"]
            new_scale = max(0.55, min(1.35, resize_state["start_scale"] + dx / 260.0))
            self.state["preferences"]["floatingTimerScale"] = round(new_scale, 2)
            self._apply_led_window_geometry(keep_origin=True)

        grip.bind("<ButtonPress-1>", start_resize)
        grip.bind("<B1-Motion>", do_resize)

        self._apply_led_window_geometry(keep_origin=False)

    def _apply_led_window_geometry(self, keep_origin: bool = True) -> None:
        if self.led_window is None or not self.led_window.winfo_exists():
            return
        scale = float(self.state["preferences"].get("floatingTimerScale", 1.0))
        w = int(round(270 * scale))
        h = int(round(118 * scale))
        digit_size = max(14, int(round(26 * scale)))
        self.led_digits_lbl.configure(font=("Consolas", digit_size, "bold"))
        if keep_origin:
            x = self.led_window.winfo_x()
            y = self.led_window.winfo_y()
        else:
            sw = self.root.winfo_screenwidth()
            x = max(20, sw - w - 24)
            y = 24
        self.led_window.geometry(f"{w}x{h}+{x}+{y}")

    # -----------------------------------------------------------------------
    # Subsystem-Sync & Sekundentakt
    # -----------------------------------------------------------------------

    def _sync_subsystems(self) -> None:
        prefs = self.state["preferences"]
        if self.active_timer and self.active_timer["running"] and self.active_timer["mode"] != "rest":
            self.audio.sync(
                should_play=True,
                sound_id=prefs.get("focusSound", "rain-gentle"),
                volume=prefs.get("focusSoundVolume", 0.45),
            )
            self.blocker.sync(
                is_blocking=bool(prefs.get("appBlockerEnabled", True)),
                blocked_apps=prefs.get("blockedApps", []),
                blocked_websites=prefs.get("blockedWebsites", []),
            )
        else:
            self.audio.stop()
            self.blocker.sync(False, [], [])

    def _current_elapsed(self) -> float:
        if not self.active_timer:
            return 0.0
        base = float(self.active_timer["accumulated"])
        if self.active_timer["running"]:
            base += time.time() - float(self.active_timer["start_ts"])
        return max(0.0, base)

    def _today_focus_minutes(self) -> int:
        today = dt.date.today().isoformat()
        secs = sum(int(e.get("seconds", 0)) for e in self.state.get("entries", []) if e.get("date") == today)
        return secs // 60

    def _update_clocks(self) -> None:
        if not self.active_timer:
            return
        elapsed = self._current_elapsed()
        if self.active_timer["mode"] == "stopwatch":
            disp = int(elapsed)
        else:
            rem = max(0.0, float(self.active_timer["target"]) - elapsed)
            disp = int(math.ceil(rem))
            if rem <= 0 and self.active_timer["running"]:
                self._perform_stop()
                return

        mins, secs = divmod(disp, 60)
        clock_str = f"{mins:02d}:{secs:02d}"
        if hasattr(self, "hero_clock_lbl") and self.hero_clock_lbl.winfo_exists():
            self.hero_clock_lbl.configure(text=clock_str)
        if self.led_window is not None and self.led_window.winfo_exists():
            self.led_digits_lbl.configure(text=clock_str)
            self.led_task_lbl.configure(text=self.active_timer["title"][:22])

    def _tick(self) -> None:
        self._update_clocks()
        self.root.after(500, self._tick)


def main() -> None:
    if "--self-test" in sys.argv:
        st = load_state()
        assert "preferences" in st
        assert len(FOCUS_SOUNDS) >= 20
        print("PASS: FokusBar Windows self-test OK")
        return

    root = tk.Tk()
    FokusBarWindowsApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
