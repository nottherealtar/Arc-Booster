# Arc Booster — ARC Raiders Performance Optimizer

A lightweight configuration tool designed to improve gameplay fluidity and frame
rate stability in **ARC Raiders** by applying system and game-specific
optimizations.  It only adjusts existing Windows and game settings — it does not
modify game files or memory.

---

## Overview

Arc Booster presents a clear GUI menu of optional performance tweaks.  You
choose exactly which tweaks to apply, and a built-in **Restore Defaults**
function undoes every change that can be automatically reversed.

---

## Requirements

| Requirement | Detail |
|---|---|
| **OS** | Windows 10 / 11 (64-bit) |
| **Privileges** | Standard user for most tweaks; Administrator for system-level tweaks |
| **Python** | 3.8 or later (only needed to run from source or build the .exe) |
| **Game** | ARC Raiders — live / public version |

---

## Quick Start — run from source

```bat
python arc_booster.py
```

Right-click and choose **Run as administrator** to unlock all tweaks.

---

## Building a standalone .exe (Windows)

```bat
build.bat
```

That's it.  The script will:

1. Verify Python is on `PATH`.
2. Install **PyInstaller** via `pip` (internet required on first run).
3. Compile `arc_booster.py` into `dist\ArcBooster.exe` — a single file with
   no runtime dependencies.

The output folder opens automatically when the build succeeds.

---

## Available Tweaks

### System

| Tweak | Admin? | Reversible? |
|---|:---:|:---:|
| High Performance Power Plan | ✔ | ✔ |
| Enable Windows Game Mode | — | ✔ |
| Disable Xbox Game Bar | — | ✔ |
| Maximise System Responsiveness for Games | ✔ | ✔ |
| Optimize Games Scheduling Profile | ✔ | ✔ |
| Optimize CPU Priority Separation | ✔ | ✔ |
| Optimize Visual Effects for Performance | — | ✔ |
| Disable SysMain (Superfetch) | ✔ | ✔ |
| Disable Background App Refresh | — | ✔ |

### Network

| Tweak | Admin? | Reversible? |
|---|:---:|:---:|
| Disable Network Throttling Index | ✔ | ✔ |
| Disable Nagle's Algorithm (TCP No-Delay) | ✔ | ✔ |

### Graphics

| Tweak | Admin? | Reversible? |
|---|:---:|:---:|
| Disable Fullscreen Optimizations | — | ✔ |
| Clear GPU Shader Cache | — | ⚠ one-way |

> **One-way** tweaks cannot be automatically reversed (the shader cache
> rebuilds itself automatically when the game or GPU driver next starts).

---

## How It Works

1. Launch `ArcBooster.exe` (or `python arc_booster.py`).
2. Arc Booster asks to restart as Administrator if it detects limited
   privileges — this is optional but recommended.
3. Tick the tweaks you want to apply and click **▶ Apply Selected Tweaks**.
4. Applied tweaks are saved to  
   `%APPDATA%\ArcBooster\applied_tweaks.json`  
   so that **↩ Restore Defaults** knows exactly what to undo, even after a
   reboot.
5. To undo everything, click **↩ Restore Defaults**.

---

## Disclaimer

This tool only modifies Windows registry values and service states that are
documented and reversible.  It does not touch any game files.  Use at your own
risk.  Always run the game's official repair/verify tool if you experience
issues after applying tweaks.

---

## License

MIT — see [LICENSE](LICENSE).