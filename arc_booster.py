#!/usr/bin/env python3
"""
Arc Booster - ARC Raiders Performance Optimizer
Version 1.0.0

A lightweight configuration tool to improve ARC Raiders gameplay fluidity and
frame rate stability by applying system and game-specific tweaks.

Requirements: Windows 10/11 (64-bit), Python 3.8+
"""

import ctypes
import json
import os
import subprocess
import sys
import threading
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import messagebox, ttk
from typing import Tuple

# ---------------------------------------------------------------------------
# Application constants
# ---------------------------------------------------------------------------

APP_NAME = "Arc Booster"
APP_VERSION = "1.0.0"
APP_SUBTITLE = "ARC Raiders Performance Optimizer"

CONFIG_DIR = Path(os.environ.get("APPDATA", str(Path.home()))) / "ArcBooster"
BACKUP_FILE = CONFIG_DIR / "applied_tweaks.json"

# ---------------------------------------------------------------------------
# Colour palette (dark gaming aesthetic)
# ---------------------------------------------------------------------------

C = {
    "bg":           "#0d0d0d",
    "surface":      "#141414",
    "card":         "#1c1c1c",
    "card_hover":   "#222222",
    "border":       "#2a2a2a",
    "accent":       "#e8460a",
    "accent_dim":   "#b33508",
    "text":         "#f0f0f0",
    "text_dim":     "#888888",
    "text_muted":   "#555555",
    "success":      "#4caf50",
    "warning":      "#ff9800",
    "error":        "#f44336",
    "badge_admin":  "#7b2d2d",
    "badge_cat":    "#1e3a4f",
    "scrollbar":    "#2a2a2a",
    "log_bg":       "#0a0a0a",
}

# ---------------------------------------------------------------------------
# Tweak definitions
# ---------------------------------------------------------------------------
# Each tweak has:
#   id          – unique identifier used in the backup file
#   name        – short display name
#   description – one-sentence explanation shown in the UI
#   category    – grouping header
#   admin       – True if the tweak requires elevated privileges
#   apply_cmd   – PowerShell command string to apply the tweak
#   restore_cmd – PowerShell command string to undo the tweak (None = irreversible)
# ---------------------------------------------------------------------------

TWEAKS = [
    # ── System ──────────────────────────────────────────────────────────────
    {
        "id": "power_plan_high",
        "name": "High Performance Power Plan",
        "description": (
            "Activates the High Performance power plan to prevent CPU frequency "
            "scaling during gameplay, reducing stutters caused by power management."
        ),
        "category": "System",
        "admin": True,
        "apply_cmd": (
            "powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c"
        ),
        "restore_cmd": (
            "powercfg /setactive 381b4222-f694-41f0-9685-ff5bb260df2e"
        ),
    },
    {
        "id": "game_mode_enable",
        "name": "Enable Windows Game Mode",
        "description": (
            "Turns on Windows Game Mode to prioritise CPU and GPU resources for "
            "the active game and suppress background task interference."
        ),
        "category": "System",
        "admin": False,
        "apply_cmd": (
            'Set-ItemProperty -Path "HKCU:\\Software\\Microsoft\\GameBar" '
            '-Name "AutoGameModeEnabled" -Value 1 -Type DWord -Force'
        ),
        "restore_cmd": (
            'Set-ItemProperty -Path "HKCU:\\Software\\Microsoft\\GameBar" '
            '-Name "AutoGameModeEnabled" -Value 0 -Type DWord -Force'
        ),
    },
    {
        "id": "disable_game_bar",
        "name": "Disable Xbox Game Bar",
        "description": (
            "Disables the Xbox Game Bar overlay which can cause micro-stutters "
            "and consume CPU/GPU resources during gameplay."
        ),
        "category": "System",
        "admin": False,
        "apply_cmd": (
            'Set-ItemProperty -Path '
            '"HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\GameDVR" '
            '-Name "AppCaptureEnabled" -Value 0 -Type DWord -Force; '
            'Set-ItemProperty -Path "HKCU:\\System\\GameConfigStore" '
            '-Name "GameDVR_Enabled" -Value 0 -Type DWord -Force'
        ),
        "restore_cmd": (
            'Set-ItemProperty -Path '
            '"HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\GameDVR" '
            '-Name "AppCaptureEnabled" -Value 1 -Type DWord -Force; '
            'Set-ItemProperty -Path "HKCU:\\System\\GameConfigStore" '
            '-Name "GameDVR_Enabled" -Value 1 -Type DWord -Force'
        ),
    },
    {
        "id": "system_responsiveness",
        "name": "Maximise System Responsiveness for Games",
        "description": (
            "Sets SystemResponsiveness to 0 so the Windows Multimedia scheduler "
            "dedicates maximum CPU time to the foreground game process."
        ),
        "category": "System",
        "admin": True,
        "apply_cmd": (
            '$p = "HKLM:\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion'
            '\\Multimedia\\SystemProfile"; '
            'If (-not (Test-Path $p)) { New-Item -Path $p -Force | Out-Null }; '
            'Set-ItemProperty -Path $p -Name "SystemResponsiveness" '
            '-Value 0 -Type DWord -Force'
        ),
        "restore_cmd": (
            '$p = "HKLM:\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion'
            '\\Multimedia\\SystemProfile"; '
            'Set-ItemProperty -Path $p -Name "SystemResponsiveness" '
            '-Value 20 -Type DWord -Force'
        ),
    },
    {
        "id": "games_scheduling_profile",
        "name": "Optimize Games Scheduling Profile",
        "description": (
            "Raises GPU priority to 8 and CPU priority to 6 in the Windows "
            "Multimedia SystemProfile Tasks\\Games key."
        ),
        "category": "System",
        "admin": True,
        "apply_cmd": (
            '$p = "HKLM:\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion'
            '\\Multimedia\\SystemProfile\\Tasks\\Games"; '
            'If (-not (Test-Path $p)) { New-Item -Path $p -Force | Out-Null }; '
            'Set-ItemProperty -Path $p -Name "GPU Priority" -Value 8 -Type DWord -Force; '
            'Set-ItemProperty -Path $p -Name "Priority" -Value 6 -Type DWord -Force; '
            'Set-ItemProperty -Path $p -Name "Scheduling Category" -Value "High" '
            '-Type String -Force; '
            'Set-ItemProperty -Path $p -Name "SFIO Priority" -Value "High" '
            '-Type String -Force'
        ),
        "restore_cmd": (
            '$p = "HKLM:\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion'
            '\\Multimedia\\SystemProfile\\Tasks\\Games"; '
            'If (Test-Path $p) { '
            'Set-ItemProperty -Path $p -Name "GPU Priority" -Value 2 -Type DWord -Force; '
            'Set-ItemProperty -Path $p -Name "Priority" -Value 2 -Type DWord -Force; '
            'Set-ItemProperty -Path $p -Name "Scheduling Category" -Value "Medium" '
            '-Type String -Force; '
            'Set-ItemProperty -Path $p -Name "SFIO Priority" -Value "Normal" '
            '-Type String -Force }'
        ),
    },
    {
        "id": "cpu_priority_separation",
        "name": "Optimize CPU Priority Separation",
        "description": (
            "Sets Win32PrioritySeparation to 38 (short, variable, foreground-boost) "
            "giving the game more CPU quanta over background processes."
        ),
        "category": "System",
        "admin": True,
        "apply_cmd": (
            'Set-ItemProperty -Path '
            '"HKLM:\\SYSTEM\\CurrentControlSet\\Control\\PriorityControl" '
            '-Name "Win32PrioritySeparation" -Value 38 -Type DWord -Force'
        ),
        "restore_cmd": (
            'Set-ItemProperty -Path '
            '"HKLM:\\SYSTEM\\CurrentControlSet\\Control\\PriorityControl" '
            '-Name "Win32PrioritySeparation" -Value 2 -Type DWord -Force'
        ),
    },
    {
        "id": "visual_effects_performance",
        "name": "Optimize Visual Effects for Performance",
        "description": (
            "Switches Windows desktop visual effects to 'Adjust for best performance', "
            "freeing up CPU and GPU cycles for the game."
        ),
        "category": "System",
        "admin": False,
        "apply_cmd": (
            'Set-ItemProperty -Path '
            '"HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects" '
            '-Name "VisualFXSetting" -Value 2 -Type DWord -Force'
        ),
        "restore_cmd": (
            'Set-ItemProperty -Path '
            '"HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects" '
            '-Name "VisualFXSetting" -Value 0 -Type DWord -Force'
        ),
    },
    {
        "id": "disable_sysmain",
        "name": "Disable SysMain (Superfetch)",
        "description": (
            "Stops and disables the SysMain service to reduce background disk I/O "
            "and RAM pre-loading activity during gaming sessions."
        ),
        "category": "System",
        "admin": True,
        "apply_cmd": (
            'Stop-Service -Name "SysMain" -ErrorAction SilentlyContinue; '
            'Set-Service -Name "SysMain" -StartupType Disabled -ErrorAction SilentlyContinue'
        ),
        "restore_cmd": (
            'Set-Service -Name "SysMain" -StartupType Automatic -ErrorAction SilentlyContinue; '
            'Start-Service -Name "SysMain" -ErrorAction SilentlyContinue'
        ),
    },
    {
        "id": "disable_background_apps",
        "name": "Disable Background App Refresh",
        "description": (
            "Prevents UWP (Microsoft Store) apps from running and refreshing in the "
            "background, freeing up CPU and memory for the game."
        ),
        "category": "System",
        "admin": False,
        "apply_cmd": (
            'Set-ItemProperty -Path '
            '"HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\BackgroundAccessApplications" '
            '-Name "GlobalUserDisabled" -Value 1 -Type DWord -Force'
        ),
        "restore_cmd": (
            'Set-ItemProperty -Path '
            '"HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\BackgroundAccessApplications" '
            '-Name "GlobalUserDisabled" -Value 0 -Type DWord -Force'
        ),
    },
    # ── Network ──────────────────────────────────────────────────────────────
    {
        "id": "disable_network_throttling",
        "name": "Disable Network Throttling Index",
        "description": (
            "Sets NetworkThrottlingIndex to unlimited, removing the Windows cap on "
            "network throughput that can increase in-game latency."
        ),
        "category": "Network",
        "admin": True,
        "apply_cmd": (
            '$p = "HKLM:\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion'
            '\\Multimedia\\SystemProfile"; '
            'If (-not (Test-Path $p)) { New-Item -Path $p -Force | Out-Null }; '
            'Set-ItemProperty -Path $p -Name "NetworkThrottlingIndex" '
            '-Value 0xFFFFFFFF -Type DWord -Force'
        ),
        "restore_cmd": (
            '$p = "HKLM:\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion'
            '\\Multimedia\\SystemProfile"; '
            'Set-ItemProperty -Path $p -Name "NetworkThrottlingIndex" '
            '-Value 10 -Type DWord -Force'
        ),
    },
    {
        "id": "disable_nagle",
        "name": "Disable Nagle's Algorithm (TCP No-Delay)",
        "description": (
            "Sets TcpAckFrequency=1 and TCPNoDelay=1 on all network interfaces to "
            "stop packet coalescing and reduce TCP latency during online play."
        ),
        "category": "Network",
        "admin": True,
        "apply_cmd": (
            '$ifaces = Get-ChildItem '
            '"HKLM:\\SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters\\Interfaces"; '
            'foreach ($i in $ifaces) { '
            'Set-ItemProperty -Path $i.PSPath -Name "TcpAckFrequency" '
            '-Value 1 -Type DWord -Force -ErrorAction SilentlyContinue; '
            'Set-ItemProperty -Path $i.PSPath -Name "TCPNoDelay" '
            '-Value 1 -Type DWord -Force -ErrorAction SilentlyContinue }'
        ),
        "restore_cmd": (
            '$ifaces = Get-ChildItem '
            '"HKLM:\\SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters\\Interfaces"; '
            'foreach ($i in $ifaces) { '
            'Remove-ItemProperty -Path $i.PSPath -Name "TcpAckFrequency" '
            '-ErrorAction SilentlyContinue; '
            'Remove-ItemProperty -Path $i.PSPath -Name "TCPNoDelay" '
            '-ErrorAction SilentlyContinue }'
        ),
    },
    # ── Graphics ─────────────────────────────────────────────────────────────
    {
        "id": "disable_fullscreen_optimizations",
        "name": "Disable Fullscreen Optimizations",
        "description": (
            "Turns off Windows Fullscreen Optimizations globally via GameConfigStore, "
            "which can cause frame-timing inconsistencies in some DirectX titles."
        ),
        "category": "Graphics",
        "admin": False,
        "apply_cmd": (
            'Set-ItemProperty -Path "HKCU:\\System\\GameConfigStore" '
            '-Name "GameDVR_FSEBehaviorMode" -Value 2 -Type DWord -Force; '
            'Set-ItemProperty -Path "HKCU:\\System\\GameConfigStore" '
            '-Name "GameDVR_HonorUserFSEBehaviorMode" -Value 1 -Type DWord -Force; '
            'Set-ItemProperty -Path "HKCU:\\System\\GameConfigStore" '
            '-Name "GameDVR_FSEBehavior" -Value 2 -Type DWord -Force'
        ),
        "restore_cmd": (
            'Remove-ItemProperty -Path "HKCU:\\System\\GameConfigStore" '
            '-Name "GameDVR_FSEBehaviorMode" -ErrorAction SilentlyContinue; '
            'Remove-ItemProperty -Path "HKCU:\\System\\GameConfigStore" '
            '-Name "GameDVR_HonorUserFSEBehaviorMode" -ErrorAction SilentlyContinue; '
            'Remove-ItemProperty -Path "HKCU:\\System\\GameConfigStore" '
            '-Name "GameDVR_FSEBehavior" -ErrorAction SilentlyContinue'
        ),
    },
    {
        "id": "clear_shader_cache",
        "name": "Clear GPU Shader Cache",
        "description": (
            "Deletes the DirectX, NVIDIA DXCache and GLCache shader stores. "
            "A fresh cache rebuild can resolve stutters from corrupted shader entries."
        ),
        "category": "Graphics",
        "admin": False,
        "apply_cmd": (
            '$paths = @('
            '"$env:LOCALAPPDATA\\D3DSCache",'
            '"$env:LOCALAPPDATA\\NVIDIA\\DXCache",'
            '"$env:LOCALAPPDATA\\NVIDIA\\GLCache",'
            '"$env:LOCALAPPDATA\\AMD\\DxcCache"'
            '); '
            'foreach ($p in $paths) { '
            'if (Test-Path $p) { '
            'Remove-Item -Path "$p\\*" -Recurse -Force -ErrorAction SilentlyContinue } }'
        ),
        "restore_cmd": None,  # one-way — cache rebuilds automatically on next launch
    },
]

# Ordered category list for consistent display
CATEGORIES = ["System", "Network", "Graphics"]

# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------


def is_admin() -> bool:
    """Return True when the process holds Administrator privileges."""
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except AttributeError:
        # Not on Windows (e.g. dev/CI environment)
        return False


def run_powershell(command: str) -> Tuple[bool, str]:
    """
    Execute *command* in a hidden PowerShell session.

    Returns (success, output) where output is stdout on success or stderr on
    failure.  Never raises — all exceptions are captured and returned as errors.
    """
    try:
        result = subprocess.run(
            [
                "powershell.exe",
                "-NoProfile",
                "-NonInteractive",
                "-ExecutionPolicy", "Bypass",
                "-Command", command,
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode == 0:
            return True, result.stdout.strip()
        return False, (result.stderr.strip() or result.stdout.strip())
    except FileNotFoundError:
        return False, "powershell.exe not found — is this a Windows system?"
    except subprocess.TimeoutExpired:
        return False, "Command timed out after 60 s."
    except OSError as exc:
        return False, str(exc)


# ---------------------------------------------------------------------------
# Backup / state persistence
# ---------------------------------------------------------------------------


def load_applied_tweaks() -> set:
    """Return the set of tweak IDs currently marked as applied."""
    try:
        if BACKUP_FILE.exists():
            with BACKUP_FILE.open("r", encoding="utf-8") as fh:
                data = json.load(fh)
            return set(data.get("applied", []))
    except (json.JSONDecodeError, OSError):
        pass
    return set()


def save_applied_tweaks(applied: set) -> None:
    """Persist the set of applied tweak IDs to disk."""
    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with BACKUP_FILE.open("w", encoding="utf-8") as fh:
            json.dump(
                {
                    "applied": sorted(applied),
                    "last_modified": datetime.now().isoformat(timespec="seconds"),
                },
                fh,
                indent=2,
            )
    except OSError:
        pass  # Non-fatal — we just lose persistence across restarts


# ---------------------------------------------------------------------------
# GUI — custom widgets
# ---------------------------------------------------------------------------


class TweakCard(tk.Frame):
    """A single tweak row: checkbox + name + description + optional badges."""

    def __init__(self, parent, tweak: dict, var: tk.BooleanVar, **kwargs):
        super().__init__(parent, bg=C["card"], **kwargs)
        self.tweak = tweak
        self.var = var

        self.configure(cursor="hand2")
        self.bind("<Button-1>", self._toggle)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

        # Left: checkbox
        self._cb = tk.Checkbutton(
            self,
            variable=var,
            bg=C["card"],
            activebackground=C["card_hover"],
            fg=C["accent"],
            activeforeground=C["accent"],
            selectcolor=C["card"],
            cursor="hand2",
            bd=0,
            highlightthickness=0,
        )
        self._cb.grid(row=0, column=0, rowspan=2, padx=(12, 4), pady=10, sticky="ns")

        # Name + admin badge
        name_frame = tk.Frame(self, bg=C["card"])
        name_frame.grid(row=0, column=1, sticky="w", padx=(0, 12), pady=(10, 0))

        tk.Label(
            name_frame,
            text=tweak["name"],
            bg=C["card"],
            fg=C["text"],
            font=("Segoe UI", 10, "bold"),
            anchor="w",
        ).pack(side="left")

        if tweak["admin"]:
            tk.Label(
                name_frame,
                text="  ADMIN  ",
                bg=C["badge_admin"],
                fg="#ff8a80",
                font=("Segoe UI", 7, "bold"),
                padx=4,
                pady=1,
            ).pack(side="left", padx=(6, 0))

        if tweak["restore_cmd"] is None:
            tk.Label(
                name_frame,
                text="  ONE-WAY  ",
                bg="#2a2a00",
                fg="#ffeb3b",
                font=("Segoe UI", 7, "bold"),
                padx=4,
                pady=1,
            ).pack(side="left", padx=(6, 0))

        # Description
        tk.Label(
            self,
            text=tweak["description"],
            bg=C["card"],
            fg=C["text_dim"],
            font=("Segoe UI", 9),
            anchor="w",
            justify="left",
            wraplength=560,
        ).grid(row=1, column=1, sticky="w", padx=(0, 12), pady=(0, 10))

        self.columnconfigure(1, weight=1)
        for child in self.winfo_children():
            child.bind("<Button-1>", self._toggle)
            child.bind("<Enter>", self._on_enter)
            child.bind("<Leave>", self._on_leave)

    def _toggle(self, _event=None):
        self.var.set(not self.var.get())

    def _on_enter(self, _event=None):
        self._set_bg(C["card_hover"])

    def _on_leave(self, _event=None):
        self._set_bg(C["card"])

    def _set_bg(self, colour: str):
        self.configure(bg=colour)
        for child in self.winfo_children():
            try:
                child.configure(bg=colour)
            except tk.TclError:
                pass
        self._cb.configure(bg=colour, activebackground=colour, selectcolor=colour)


# ---------------------------------------------------------------------------
# GUI — main application window
# ---------------------------------------------------------------------------


class ArcBoosterApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title(f"{APP_NAME}  •  {APP_SUBTITLE}  v{APP_VERSION}")
        self.configure(bg=C["bg"])
        self.resizable(False, False)

        # State
        self._admin = is_admin()
        self._applied: set = load_applied_tweaks()
        self._vars: dict[str, tk.BooleanVar] = {}
        self._lock = threading.Lock()
        self._busy = False

        # Icon (best-effort — skipped if not available)
        try:
            self.iconbitmap(default="arc_booster.ico")
        except tk.TclError:
            pass

        self._build_ui()
        self._center_window()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self):
        # ── Header ───────────────────────────────────────────────────────
        header = tk.Frame(self, bg=C["accent"], height=4)
        header.pack(fill="x", side="top")

        title_bar = tk.Frame(self, bg=C["surface"], pady=16)
        title_bar.pack(fill="x")

        tk.Label(
            title_bar,
            text="⚡  ARC BOOSTER",
            bg=C["surface"],
            fg=C["accent"],
            font=("Segoe UI", 18, "bold"),
        ).pack(side="left", padx=20)

        version_frame = tk.Frame(title_bar, bg=C["surface"])
        version_frame.pack(side="right", padx=20)

        tk.Label(
            version_frame,
            text=f"v{APP_VERSION}",
            bg=C["surface"],
            fg=C["text_muted"],
            font=("Segoe UI", 9),
        ).pack(anchor="e")

        tk.Label(
            version_frame,
            text="ARC Raiders Performance Optimizer",
            bg=C["surface"],
            fg=C["text_dim"],
            font=("Segoe UI", 9),
        ).pack(anchor="e")

        # Admin / notice bar
        if not self._admin:
            notice = tk.Frame(self, bg="#2a1a00", pady=6)
            notice.pack(fill="x")
            tk.Label(
                notice,
                text=(
                    "⚠  Not running as Administrator — tweaks marked ADMIN will be skipped. "
                    "Right-click the .exe and choose 'Run as administrator'."
                ),
                bg="#2a1a00",
                fg=C["warning"],
                font=("Segoe UI", 9),
            ).pack(padx=14)

        # ── Tweak list ───────────────────────────────────────────────────
        list_outer = tk.Frame(self, bg=C["bg"])
        list_outer.pack(fill="both", expand=True, padx=0, pady=0)

        canvas = tk.Canvas(
            list_outer,
            bg=C["bg"],
            bd=0,
            highlightthickness=0,
            width=680,
            height=420,
        )
        scrollbar = tk.Scrollbar(
            list_outer,
            orient="vertical",
            command=canvas.yview,
            bg=C["scrollbar"],
            troughcolor=C["bg"],
            activebackground=C["accent_dim"],
        )
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        self._scroll_frame = tk.Frame(canvas, bg=C["bg"])
        canvas_window = canvas.create_window((0, 0), window=self._scroll_frame, anchor="nw")

        def _on_frame_configure(_e):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def _on_canvas_configure(e):
            canvas.itemconfig(canvas_window, width=e.width)

        self._scroll_frame.bind("<Configure>", _on_frame_configure)
        canvas.bind("<Configure>", _on_canvas_configure)
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))

        # Populate tweaks grouped by category
        by_cat: dict[str, list] = {cat: [] for cat in CATEGORIES}
        for tweak in TWEAKS:
            by_cat[tweak["category"]].append(tweak)

        for cat in CATEGORIES:
            tweaks = by_cat[cat]
            if not tweaks:
                continue

            # Category header
            cat_header = tk.Frame(self._scroll_frame, bg=C["bg"])
            cat_header.pack(fill="x", pady=(14, 4), padx=14)

            tk.Label(
                cat_header,
                text=f"  {cat.upper()}  ",
                bg=C["badge_cat"],
                fg="#7ecfff",
                font=("Segoe UI", 8, "bold"),
                padx=6,
                pady=3,
            ).pack(side="left")

            tk.Frame(cat_header, bg=C["border"], height=1).pack(
                side="left", fill="x", expand=True, padx=(8, 0), pady=6
            )

            for tweak in tweaks:
                var = tk.BooleanVar(value=False)
                self._vars[tweak["id"]] = var

                card = TweakCard(self._scroll_frame, tweak, var)
                card.pack(fill="x", padx=14, pady=3)

        # ── Bottom toolbar ───────────────────────────────────────────────
        toolbar = tk.Frame(self, bg=C["surface"], pady=12)
        toolbar.pack(fill="x", side="bottom")

        self._select_all_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            toolbar,
            text="Select all",
            variable=self._select_all_var,
            command=self._toggle_all,
            bg=C["surface"],
            fg=C["text_dim"],
            activebackground=C["surface"],
            activeforeground=C["text"],
            selectcolor=C["card"],
            font=("Segoe UI", 9),
            cursor="hand2",
            bd=0,
            highlightthickness=0,
        ).pack(side="left", padx=16)

        # Restore button (right-side, muted)
        self._restore_btn = tk.Button(
            toolbar,
            text="↩  Restore Defaults",
            command=self._on_restore,
            bg=C["card"],
            fg=C["text_dim"],
            activebackground=C["card_hover"],
            activeforeground=C["text"],
            font=("Segoe UI", 10),
            relief="flat",
            cursor="hand2",
            padx=14,
            pady=6,
        )
        self._restore_btn.pack(side="right", padx=(6, 16))

        # Apply button (primary)
        self._apply_btn = tk.Button(
            toolbar,
            text="▶  Apply Selected Tweaks",
            command=self._on_apply,
            bg=C["accent"],
            fg="white",
            activebackground=C["accent_dim"],
            activeforeground="white",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            cursor="hand2",
            padx=14,
            pady=6,
        )
        self._apply_btn.pack(side="right", padx=(0, 6))

        # ── Status log ───────────────────────────────────────────────────
        log_frame = tk.Frame(self, bg=C["log_bg"])
        log_frame.pack(fill="x", side="bottom")

        tk.Label(
            log_frame,
            text="STATUS LOG",
            bg=C["log_bg"],
            fg=C["text_muted"],
            font=("Segoe UI", 7, "bold"),
            anchor="w",
        ).pack(fill="x", padx=10, pady=(6, 0))

        self._log = tk.Text(
            log_frame,
            height=5,
            bg=C["log_bg"],
            fg=C["text_dim"],
            font=("Consolas", 8),
            relief="flat",
            state="disabled",
            wrap="word",
            insertbackground=C["text"],
            selectbackground=C["accent_dim"],
        )
        self._log.pack(fill="x", padx=10, pady=(2, 8))

        # Tag colours for log entries
        self._log.tag_configure("ok",      foreground=C["success"])
        self._log.tag_configure("err",     foreground=C["error"])
        self._log.tag_configure("warn",    foreground=C["warning"])
        self._log.tag_configure("info",    foreground=C["text_dim"])
        self._log.tag_configure("heading", foreground=C["text"])

        self._log_info(f"Arc Booster v{APP_VERSION} ready.  "
                       f"{'Running as Administrator.' if self._admin else 'Not Administrator.'}")
        if self._applied:
            self._log_info(f"{len(self._applied)} tweak(s) previously applied — "
                           "use 'Restore Defaults' to undo them.")

    def _center_window(self):
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"+{x}+{y}")

    # ------------------------------------------------------------------
    # Logging helpers
    # ------------------------------------------------------------------

    def _log_write(self, message: str, tag: str = "info"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        line = f"[{timestamp}]  {message}\n"
        self._log.configure(state="normal")
        self._log.insert("end", line, tag)
        self._log.see("end")
        self._log.configure(state="disabled")

    def _log_info(self, msg: str):
        self._log_write(msg, "info")

    def _log_ok(self, msg: str):
        self._log_write(f"✔  {msg}", "ok")

    def _log_err(self, msg: str):
        self._log_write(f"✘  {msg}", "err")

    def _log_warn(self, msg: str):
        self._log_write(f"⚠  {msg}", "warn")

    def _log_heading(self, msg: str):
        self._log_write(msg, "heading")

    # ------------------------------------------------------------------
    # UI actions
    # ------------------------------------------------------------------

    def _toggle_all(self):
        state = self._select_all_var.get()
        for var in self._vars.values():
            var.set(state)

    def _set_busy(self, busy: bool):
        self._busy = busy
        state = "disabled" if busy else "normal"
        self._apply_btn.configure(state=state)
        self._restore_btn.configure(state=state)

    # ------------------------------------------------------------------
    # Apply
    # ------------------------------------------------------------------

    def _on_apply(self):
        selected = [t for t in TWEAKS if self._vars[t["id"]].get()]
        if not selected:
            messagebox.showinfo(APP_NAME, "Please select at least one tweak to apply.")
            return
        threading.Thread(target=self._apply_worker, args=(selected,), daemon=True).start()

    def _apply_worker(self, selected: list):
        with self._lock:
            self.after(0, self._set_busy, True)
            self._log_heading(f"── Applying {len(selected)} tweak(s) ──────────────────")

            newly_applied = []
            skipped_admin = []

            for tweak in selected:
                tid = tweak["id"]
                if tweak["admin"] and not self._admin:
                    skipped_admin.append(tweak["name"])
                    self._log_warn(f"SKIP  {tweak['name']}  (requires Administrator)")
                    continue

                self._log_info(f"Applying: {tweak['name']} …")
                ok, output = run_powershell(tweak["apply_cmd"])

                if ok:
                    self._log_ok(tweak["name"])
                    newly_applied.append(tid)
                else:
                    self._log_err(f"{tweak['name']}  — {output or 'unknown error'}")

            # Persist state
            self._applied.update(newly_applied)
            save_applied_tweaks(self._applied)

            # Summary
            n_ok = len(newly_applied)
            n_skip = len(skipped_admin)
            n_err = len(selected) - n_ok - n_skip
            parts = []
            if n_ok:
                parts.append(f"{n_ok} applied")
            if n_skip:
                parts.append(f"{n_skip} skipped (need admin)")
            if n_err:
                parts.append(f"{n_err} failed")
            self._log_heading("── Done: " + ", ".join(parts) + " ──────────────────────")

            if skipped_admin:
                self.after(
                    0,
                    messagebox.showwarning,
                    APP_NAME,
                    "Some tweaks were skipped because they require Administrator rights:\n\n"
                    + "\n".join(f"  • {n}" for n in skipped_admin)
                    + "\n\nRestart the application as Administrator to apply them.",
                )

            self.after(0, self._set_busy, False)

    # ------------------------------------------------------------------
    # Restore
    # ------------------------------------------------------------------

    def _on_restore(self):
        restorable = [
            t for t in TWEAKS
            if t["id"] in self._applied and t["restore_cmd"] is not None
        ]
        irreversible = [
            t for t in TWEAKS
            if t["id"] in self._applied and t["restore_cmd"] is None
        ]

        if not restorable and not irreversible:
            messagebox.showinfo(
                APP_NAME,
                "No previously applied tweaks were found to restore.\n\n"
                "Arc Booster tracks tweaks applied in this and previous sessions.",
            )
            return

        lines = []
        if restorable:
            lines.append("The following tweaks will be RESTORED to Windows defaults:\n")
            lines.extend(f"  • {t['name']}" for t in restorable)
        if irreversible:
            lines.append("\nThe following tweaks cannot be automatically reversed:\n")
            lines.extend(f"  • {t['name']}  (one-way)" for t in irreversible)
        lines.append("\nProceed?")

        if not messagebox.askyesno(APP_NAME, "\n".join(lines), icon="warning"):
            return

        threading.Thread(
            target=self._restore_worker,
            args=(restorable,),
            daemon=True,
        ).start()

    def _restore_worker(self, restorable: list):
        with self._lock:
            self.after(0, self._set_busy, True)
            self._log_heading(f"── Restoring {len(restorable)} tweak(s) ─────────────────")

            restored = []
            for tweak in restorable:
                if tweak["admin"] and not self._admin:
                    self._log_warn(f"SKIP  {tweak['name']}  (requires Administrator)")
                    continue

                self._log_info(f"Restoring: {tweak['name']} …")
                ok, output = run_powershell(tweak["restore_cmd"])

                if ok:
                    self._log_ok(f"Restored  {tweak['name']}")
                    restored.append(tweak["id"])
                else:
                    self._log_err(f"{tweak['name']}  — {output or 'unknown error'}")

            # Remove successfully restored tweaks from the applied set
            for tid in restored:
                self._applied.discard(tid)
            save_applied_tweaks(self._applied)

            self._log_heading(
                f"── Done: {len(restored)}/{len(restorable)} restored ──────────────"
            )
            self.after(0, self._set_busy, False)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main():
    # Re-launch with elevation when not admin and user confirms
    if not is_admin():
        try:
            answer = messagebox.askyesno(
                APP_NAME,
                "Arc Booster works best with Administrator rights.\n\n"
                "Some tweaks require elevated privileges to apply.\n\n"
                "Would you like to restart as Administrator now?",
            )
            if answer:
                ctypes.windll.shell32.ShellExecuteW(
                    None, "runas", sys.executable, " ".join(sys.argv), None, 1
                )
                sys.exit(0)
        except AttributeError:
            pass  # Non-Windows — skip elevation

    app = ArcBoosterApp()
    app.mainloop()


if __name__ == "__main__":
    main()
