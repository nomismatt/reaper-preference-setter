#!/usr/bin/env python3
"""
Configure REAPER preferences for a consistent setup.

Sets the following preferences:
  - Open new project on startup
  - Default project template
  - Prompt to save on new project
  - Default project save path
  - Media save path (relative "Audio" subfolder)
  - Put peak files in peaks/ subfolder relative to media
"""

import os
import sys
import shutil
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox


def find_reaper_ini():
    """Find reaper.ini based on platform."""
    if sys.platform == "darwin":
        path = Path.home() / "Library" / "Application Support" / "REAPER" / "reaper.ini"
    elif sys.platform == "win32":
        appdata = os.environ.get("APPDATA", "")
        path = Path(appdata) / "REAPER" / "reaper.ini"
    else:
        path = Path.home() / ".config" / "REAPER" / "reaper.ini"

    if path.exists():
        return path
    return None


def find_reaper_resource_path():
    """Find the REAPER resource directory."""
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "REAPER"
    elif sys.platform == "win32":
        appdata = os.environ.get("APPDATA", "")
        return Path(appdata) / "REAPER"
    else:
        return Path.home() / ".config" / "REAPER"


def find_project_templates():
    """Find available .RPP files in REAPER's ProjectTemplates folder."""
    resource_path = find_reaper_resource_path()
    templates_dir = resource_path / "ProjectTemplates"
    if not templates_dir.exists():
        return []
    templates = sorted(templates_dir.glob("*.RPP"))
    templates += sorted(templates_dir.glob("*.rpp"))
    seen = set()
    unique = []
    for t in templates:
        key = str(t).lower()
        if key not in seen:
            seen.add(key)
            unique.append(t)
    return unique


def read_ini(ini_path):
    """Read the INI file and return lines."""
    with open(ini_path, "r", encoding="utf-8", errors="replace") as f:
        return f.readlines()


def write_ini(ini_path, lines):
    """Write lines back to the INI file."""
    with open(ini_path, "w", encoding="utf-8", errors="replace") as f:
        f.writelines(lines)


def find_reaper_section(lines):
    """Find the start index of the [REAPER] section."""
    for i, line in enumerate(lines):
        if line.strip() == "[REAPER]":
            return i
    return None


def find_next_section(lines, start):
    """Find the start of the next section after the given index."""
    for i in range(start + 1, len(lines)):
        if lines[i].strip().startswith("[") and lines[i].strip().endswith("]"):
            return i
    return len(lines)


def get_value(lines, section_start, section_end, key):
    """Get the current value of a key in the section."""
    prefix = f"{key}="
    for i in range(section_start, section_end):
        if lines[i].startswith(prefix):
            return lines[i][len(prefix):].rstrip("\n")
    return None


def set_value(lines, section_start, section_end, key, value):
    """Set a key's value in the section. Returns (lines, new_section_end)."""
    prefix = f"{key}="
    for i in range(section_start, section_end):
        if lines[i].startswith(prefix):
            lines[i] = f"{key}={value}\n"
            return lines, section_end
    lines.insert(section_end, f"{key}={value}\n")
    return lines, section_end + 1


def check_reaper_running():
    """Check if REAPER is currently running."""
    if sys.platform == "darwin":
        result = os.popen("pgrep -x REAPER 2>/dev/null").read().strip()
        return bool(result)
    elif sys.platform == "win32":
        result = os.popen('tasklist /FI "IMAGENAME eq reaper.exe" 2>NUL').read()
        return "reaper.exe" in result.lower()
    else:
        result = os.popen("pgrep -x reaper 2>/dev/null").read().strip()
        return bool(result)


class ReaperConfigApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("REAPER Preference Setter")
        self.root.resizable(False, False)

        # Find reaper.ini
        self.ini_path = find_reaper_ini()
        if not self.ini_path:
            messagebox.showerror(
                "REAPER Not Found",
                "Could not find reaper.ini.\n\n"
                "Make sure REAPER is installed on this computer."
            )
            sys.exit(1)

        # Read current config
        self.lines = read_ini(self.ini_path)
        self.section_start = find_reaper_section(self.lines)
        if self.section_start is None:
            # Fresh install — create the section
            self.lines.append("\n[REAPER]\n")
            self.section_start = len(self.lines) - 1

        self.section_end = find_next_section(self.lines, self.section_start)

        # Get current values
        self.current = {
            "loadlastproj": get_value(self.lines, self.section_start, self.section_end, "loadlastproj"),
            "defsavepath": get_value(self.lines, self.section_start, self.section_end, "defsavepath") or "",
            "newprojtmpl": get_value(self.lines, self.section_start, self.section_end, "newprojtmpl") or "",
            "projdefrecpath": get_value(self.lines, self.section_start, self.section_end, "projdefrecpath") or "",
            "peakcachegenmode": get_value(self.lines, self.section_start, self.section_end, "peakcachegenmode"),
            "saveopts": get_value(self.lines, self.section_start, self.section_end, "saveopts"),
        }

        # Find templates
        self.templates = find_project_templates()
        self.resource_path = find_reaper_resource_path()

        self._build_ui()

        # Check if REAPER is running
        if check_reaper_running():
            messagebox.showwarning(
                "REAPER Is Running",
                "REAPER appears to be running.\n\n"
                "Close REAPER before applying changes,\n"
                "otherwise your changes may be overwritten."
            )

    def _build_ui(self):
        # Main frame with padding
        main = ttk.Frame(self.root, padding=20)
        main.grid(row=0, column=0, sticky="nsew")

        row = 0

        # Title
        title = ttk.Label(main, text="REAPER Preference Setter", font=("", 16, "bold"))
        title.grid(row=row, column=0, columnspan=3, pady=(0, 5))
        row += 1

        subtitle = ttk.Label(main, text=f"Config: {self.ini_path}", font=("", 10))
        subtitle.grid(row=row, column=0, columnspan=3, pady=(0, 15))
        row += 1

        # --- Default save path ---
        ttk.Label(main, text="Default project save path:").grid(row=row, column=0, sticky="w", pady=5)
        row += 1

        self.savepath_var = tk.StringVar(value=self.current["defsavepath"])
        savepath_entry = ttk.Entry(main, textvariable=self.savepath_var, width=50)
        savepath_entry.grid(row=row, column=0, columnspan=2, sticky="ew", padx=(0, 5))
        ttk.Button(main, text="Browse...", command=self._browse_savepath).grid(row=row, column=2)
        row += 1

        # --- Project template ---
        ttk.Label(main, text="Default project template:").grid(row=row, column=0, sticky="w", pady=(15, 5))
        row += 1

        template_names = ["(none)"] + [t.name for t in self.templates]
        self.template_var = tk.StringVar()

        # Set current template selection
        current_tmpl = self.current["newprojtmpl"]
        matched = False
        for t in self.templates:
            if current_tmpl and t.name in current_tmpl:
                self.template_var.set(t.name)
                matched = True
                break
        if not matched:
            self.template_var.set("(none)")

        template_combo = ttk.Combobox(main, textvariable=self.template_var, values=template_names,
                                       state="readonly", width=47)
        template_combo.grid(row=row, column=0, columnspan=2, sticky="ew", padx=(0, 5))
        ttk.Button(main, text="Browse...", command=self._browse_template).grid(row=row, column=2)
        row += 1

        # --- Media path ---
        ttk.Label(main, text="Media save path (relative to project):").grid(row=row, column=0, sticky="w", pady=(15, 5))
        row += 1

        self.recpath_var = tk.StringVar(value=self.current["projdefrecpath"] or "Audio")
        recpath_entry = ttk.Entry(main, textvariable=self.recpath_var, width=50)
        recpath_entry.grid(row=row, column=0, columnspan=2, sticky="ew")
        row += 1

        # --- Checkboxes ---
        separator = ttk.Separator(main, orient="horizontal")
        separator.grid(row=row, column=0, columnspan=3, sticky="ew", pady=15)
        row += 1

        self.startup_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(main, text="Open new project on startup", variable=self.startup_var).grid(
            row=row, column=0, columnspan=3, sticky="w", pady=2)
        row += 1

        self.prompt_save_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(main, text="Prompt to save on new project", variable=self.prompt_save_var).grid(
            row=row, column=0, columnspan=3, sticky="w", pady=2)
        row += 1

        self.peaks_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(main, text="Put peak files in peaks/ subfolder relative to media",
                        variable=self.peaks_var).grid(row=row, column=0, columnspan=3, sticky="w", pady=2)
        row += 1

        # --- Buttons ---
        btn_frame = ttk.Frame(main)
        btn_frame.grid(row=row, column=0, columnspan=3, pady=(20, 0))

        ttk.Button(btn_frame, text="Apply", command=self._apply).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Cancel", command=self.root.quit).pack(side="left", padx=5)

    def _browse_savepath(self):
        path = filedialog.askdirectory(title="Select default project save path")
        if path:
            self.savepath_var.set(path)

    def _browse_template(self):
        templates_dir = self.resource_path / "ProjectTemplates"
        initial_dir = str(templates_dir) if templates_dir.exists() else str(Path.home())
        path = filedialog.askopenfilename(
            title="Select project template",
            initialdir=initial_dir,
            filetypes=[("REAPER Project", "*.RPP *.rpp"), ("All Files", "*.*")]
        )
        if path:
            self.templates.append(Path(path))
            self.template_var.set(Path(path).name)

    def _apply(self):
        # Re-read the file fresh in case it changed
        self.lines = read_ini(self.ini_path)
        self.section_start = find_reaper_section(self.lines)
        self.section_end = find_next_section(self.lines, self.section_start)

        # Backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.ini_path.with_name(f"reaper.ini.backup_{timestamp}")
        shutil.copy2(self.ini_path, backup_path)

        changes = []

        # 1. Startup behavior
        if self.startup_var.get():
            current = get_value(self.lines, self.section_start, self.section_end, "loadlastproj")
            if current is not None:
                new_val = int(current) & ~1 & ~2
            else:
                new_val = 0
            self.lines, self.section_end = set_value(
                self.lines, self.section_start, self.section_end, "loadlastproj", str(new_val))
            changes.append("Open new project on startup")

        # 2. Default save path
        savepath = self.savepath_var.get().strip()
        if savepath:
            self.lines, self.section_end = set_value(
                self.lines, self.section_start, self.section_end, "defsavepath", savepath)
            changes.append(f"Save path: {savepath}")

        # 3. Project template
        template_name = self.template_var.get()
        if template_name and template_name != "(none)":
            # Find the full path
            template_path = None
            for t in self.templates:
                if t.name == template_name:
                    template_path = t
                    break

            if template_path:
                try:
                    rel = template_path.relative_to(self.resource_path)
                    tmpl_value = str(rel)
                except ValueError:
                    tmpl_value = str(template_path)

                self.lines, self.section_end = set_value(
                    self.lines, self.section_start, self.section_end, "newprojtmpl", tmpl_value)
                self.lines, self.section_end = set_value(
                    self.lines, self.section_start, self.section_end, "newprojdo", "1")
                changes.append(f"Template: {template_name}")

        # 4. Prompt to save
        if self.prompt_save_var.get():
            current = get_value(self.lines, self.section_start, self.section_end, "saveopts")
            saveopts_val = (int(current) | 1) if current else 1
            self.lines, self.section_end = set_value(
                self.lines, self.section_start, self.section_end, "saveopts", str(saveopts_val))
            changes.append("Prompt to save on new project")

        # 5. Media path
        recpath = self.recpath_var.get().strip()
        if recpath:
            self.lines, self.section_end = set_value(
                self.lines, self.section_start, self.section_end, "projdefrecpath", recpath)
            changes.append(f"Media path: {recpath}")

        # 6. Peaks subfolder
        if self.peaks_var.get():
            current = get_value(self.lines, self.section_start, self.section_end, "peakcachegenmode")
            peak_val = (int(current) | 1) if current else 3
            self.lines, self.section_end = set_value(
                self.lines, self.section_start, self.section_end, "peakcachegenmode", str(peak_val))
            changes.append("Peaks in subfolder relative to media")

        # Write
        write_ini(self.ini_path, self.lines)

        summary = "\n".join(f"  \u2022 {c}" for c in changes)
        messagebox.showinfo(
            "Settings Applied",
            f"The following settings were applied:\n\n{summary}\n\n"
            f"Backup saved to:\n{backup_path.name}\n\n"
            f"Launch REAPER to verify your settings."
        )
        self.root.quit()

    def run(self):
        self.root.mainloop()


def main():
    app = ReaperConfigApp()
    app.run()


if __name__ == "__main__":
    main()
