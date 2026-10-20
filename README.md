<div align="center">

# FokusBar für Windows (Windows 10 & 11)

**Dein Deep-Work-Timer, Natur- & Spotify-Shuffle-Player sowie App- & Webseiten-Blocker (inkl. VPN-, Proxy- & Anti-Detect-Browser-Schutz) für Windows.**

### [↓ FokusBar-Windows.exe herunterladen (Windows 10 & 11 · Standalone)](https://github.com/Jusaain/fokus-bar-windows/releases/latest/download/FokusBar-Windows.exe)

`Windows 10 & 11` · `Standalone .exe (keine Installation nötig)` · `100 % lokal` · `Keine Cloud / Telemetrie`

*(Auf der Suche nach der Mac-Version? → [Hier geht's zu FokusBar für macOS](https://github.com/Jusaain/fokus-bar))*

</div>

---

## Automatische Installation über Claude Code / Codex / Cursor

Gib einfach diesen Satz in Claude Code, Codex oder Cursor auf deinem Windows-PC ein:
> **„Installier und starte mir bitte diese App auf meinem PC: https://github.com/Jusaain/fokus-bar-windows“**

Der Agent führt automatisch `powershell -ExecutionPolicy Bypass -File .\install.ps1` aus, richtet FokusBar unter `%LOCALAPPDATA%\Programs\FokusBar` ein, legt eine **Desktop- & Startmenü-Verknüpfung** an und startet die App sofort.

---

## Manuelle Installation in 30 Sekunden

### Option A: Direkt als `.exe` starten (ohne Installation)
1. **[`FokusBar-Windows.exe` herunterladen](https://github.com/Jusaain/fokus-bar-windows/releases/latest/download/FokusBar-Windows.exe)** und per Doppelklick starten.
2. *(Falls Windows SmartScreen beim ersten Start fragt: Auf **„Weitere Informationen“ → „Trotzdem ausführen“** klicken).*

### Option B: 1-Befehl-Installation via PowerShell
```powershell
git clone https://github.com/Jusaain/fokus-bar-windows.git
cd fokus-bar-windows
powershell -ExecutionPolicy Bypass -File .\install.ps1
```

---

## Highlights (1:1 wie die Mac-Version)

- **Deep Work + To-Dos an einem Ort:** Starte Fokus-Sessions (15 / 25 / 45 / 60 / 90 Min. oder frei wählbar), Countdown, Stoppuhr oder Pausen und verknüpfe sie direkt mit deinen täglichen To-Dos & Projekten.
- **Schwebende, größenverstellbare LED-Timeruhr:** Bleibt immer im Vordergrund (`topmost`), lässt sich frei auf dem Bildschirm verschieben und unten rechts stufenlos kleiner oder größer ziehen (`55 %` bis `135 %` oder per `65% / 80% / 100% / 115%`-Buttons).
- **7 echte Natur-Sounds & 13 Spotify Deep-Work-/Jazz-Playlists:**
  - *Sanfter Sommerregen*, *Waldruhe & Vögel*, *Waldbach*, *Regen am Fenster*, *Meereswellen*, *Kaminfeuer* und *Café-Atmosphäre* sind direkt als Studio-Aufnahmen in der `.exe` enthalten (100 % offline nutzbar).
  - *Courten Radio*, *This Is Courten*, *Penthouse Radio*, *Deep Focus*, *Focus Flow*, *House Focus*, *Jazz House & Soft Lounge*, *Smooth Jazz Beats*, *Coffee Table Jazz* u.v.m. starten im Hintergrund über Spotify.
- **App- & Website-Blocker (inkl. VPN-, Proxy- & Anti-Detect-Browser-Schutz):**
  - Schließt gesperrte Programme (*Discord*, *WhatsApp*, *Telegram*, *Slack*, *Steam*, VPNs sowie Anti-Detect-Browser wie *Dolphin{anty}*, *AdsPower*, *GoLogin*, *Multilogin*, *Octo Browser*, *Incogniton*, *MoreLogin*, *Undetectable*) sofort beim Start der Fokus-Session.
  - Schließt gesperrte Webseiten (*Instagram*, *YouTube*, *X.com / Twitter*, *TikTok*, *Reddit*, *Netflix*, *Twitch* + eigene Domains) laufend in *Chrome*, *Edge*, *Brave*, *Firefox*, *Opera*, *Vivaldi* **und auch in Proxy-Profilen von Anti-Detect-Browsern (`Anty.exe`, `SunBrowser.exe`, `Orbita`)**.
- **Fokus-Schutz (60-Sekunden-Durchatmen-Hürde):**
  - Vorzeitiges Pausieren oder Abbrechen erfordert erst 60 Sekunden geführte Atemübung mit aktiven Klick-Checkpoints alle 10 Sekunden und das manuelle Abtippen von *„Ich unterbreche meinen Fokus bewusst“* (ohne Copy & Paste).
