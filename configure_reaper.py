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
import glob
import re
from datetime import datetime
from pathlib import Path


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
    # Deduplicate (case-insensitive match on macOS)
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

    # Key not found — insert before section end
    lines.insert(section_end, f"{key}={value}\n")
    return lines, section_end + 1


def prompt_path(prompt_text, default=None):
    """Prompt user for a filesystem path with tab completion."""
    if default:
        prompt_text += f" [{default}]: "
    else:
        prompt_text += " (or Enter to skip): "

    while True:
        try:
            user_input = input(prompt_text).strip()
        except (EOFError, KeyboardInterrupt):
            print()
            sys.exit(1)

        if not user_input:
            return default  # Returns None if no default

        path = os.path.expanduser(user_input)
        if os.path.isdir(path):
            return path

        print(f"  Directory not found: {path}")
        try:
            create = input("  Create it? [y/N]: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            sys.exit(1)
        if create == "y":
            try:
                os.makedirs(path, exist_ok=True)
                print(f"  Created: {path}")
                return path
            except OSError as e:
                print(f"  Could not create directory: {e}")
        print()


def prompt_template(templates, current_template=None):
    """Prompt user to select a project template."""
    if not templates:
        print("  No .RPP templates found in ProjectTemplates folder.")
        custom = input("  Enter full path to template file (or press Enter to skip): ").strip()
        if custom and os.path.isfile(custom):
            return custom
        return None

    print("\n  Available project templates:")
    for i, t in enumerate(templates, 1):
        marker = " (current)" if current_template and t.name in current_template else ""
        print(f"    {i}. {t.name}{marker}")

    print(f"    {len(templates) + 1}. Enter custom path")
    print(f"    {len(templates) + 2}. Skip (don't change)")

    while True:
        try:
            choice = input(f"\n  Select template [1-{len(templates) + 2}]: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            sys.exit(1)

        if not choice:
            continue
        try:
            idx = int(choice)
        except ValueError:
            continue

        if 1 <= idx <= len(templates):
            return str(templates[idx - 1])
        elif idx == len(templates) + 1:
            custom = input("  Enter full path to template: ").strip()
            if os.path.isfile(custom):
                return custom
            print(f"  File not found: {custom}")
        elif idx == len(templates) + 2:
            return None


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


def main():
    dry_run = "--dry-run" in sys.argv

    print("=" * 60)
    print("  REAPER Preferences Configurator")
    if dry_run:
        print("  (DRY RUN — no changes will be written)")
    print("=" * 60)

    # Check if REAPER is running
    if check_reaper_running():
        print("\n  WARNING: REAPER appears to be running.")
        print("  Close REAPER before running this script,")
        print("  otherwise your changes may be overwritten.")
        proceed = input("\n  Continue anyway? [y/N]: ").strip().lower()
        if proceed != "y":
            sys.exit(0)

    # Find reaper.ini
    ini_path = find_reaper_ini()
    if not ini_path:
        print("\n  ERROR: Could not find reaper.ini")
        print("  Searched in the default location for your platform.")
        sys.exit(1)

    print(f"\n  Found: {ini_path}")

    # Read current config
    lines = read_ini(ini_path)
    section_start = find_reaper_section(lines)
    if section_start is None:
        print("  ERROR: Could not find [REAPER] section in reaper.ini")
        sys.exit(1)

    section_end = find_next_section(lines, section_start)

    # Show current values
    current_loadlast = get_value(lines, section_start, section_end, "loadlastproj")
    current_defsavepath = get_value(lines, section_start, section_end, "defsavepath")
    current_template = get_value(lines, section_start, section_end, "newprojtmpl")
    current_newprojdo = get_value(lines, section_start, section_end, "newprojdo")
    current_recpath = get_value(lines, section_start, section_end, "projdefrecpath")
    current_peakmode = get_value(lines, section_start, section_end, "peakcachegenmode")

    print("\n  Current settings:")
    print(f"    Startup project:    loadlastproj = {current_loadlast}")
    print(f"    Default save path:  defsavepath = {current_defsavepath or '(empty)'}")
    print(f"    Project template:   newprojtmpl = {current_template or '(empty)'}")
    print(f"    New project action: newprojdo = {current_newprojdo}")
    print(f"    Media path:         projdefrecpath = {current_recpath or '(empty)'}")
    print(f"    Peak cache mode:    peakcachegenmode = {current_peakmode}")

    # Backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = ini_path.with_name(f"reaper.ini.backup_{timestamp}")
    shutil.copy2(ini_path, backup_path)
    print(f"\n  Backup saved to: {backup_path}")

    # --- Prompt for settings ---

    print("\n" + "-" * 60)
    print("  Configure settings (press Enter to keep current value)")
    print("-" * 60)

    # 1. Default save path for new projects
    print(f"\n  1. Default path to save new projects")
    print(f"     Current: {current_defsavepath or '(empty)'}")
    new_savepath = prompt_path("     New path", default=current_defsavepath or None)

    # 2. Project template
    print(f"\n  2. Default project template")
    print(f"     Current: {current_template or '(none)'}")
    templates = find_project_templates()
    selected_template = prompt_template(templates, current_template)

    # 3. Media recording path (relative)
    print(f"\n  3. Media save path (relative to project folder)")
    print(f"     Current: {current_recpath or '(empty)'}")
    try:
        new_recpath = input(f"     New path [Audio]: ").strip()
    except (EOFError, KeyboardInterrupt):
        print()
        sys.exit(1)
    if not new_recpath:
        new_recpath = "Audio"

    # --- Apply settings ---

    print("\n" + "-" * 60)
    print("  Applying settings...")
    print("-" * 60)

    changes = []

    # 1. Open new project on startup
    #    loadlastproj: bit 0 = load last project, bit 1 = open with new project
    #    Value 0 = new project on startup; value with bit 0 set = load last
    #    We want "New project" = set to 0 (or 16 depending on other bits)
    #    Looking at the screenshot, "New project" is selected in the dropdown
    #    Based on actual values seen (19 = 0b10011), we clear bit 0 to not load last
    if current_loadlast is not None:
        val = int(current_loadlast)
        new_val = val & ~1  # Clear "load last project" bit
        new_val = new_val & ~2  # Clear "prompt" bit if any
        # Keep other flag bits intact
    else:
        new_val = 0
    lines, section_end = set_value(lines, section_start, section_end, "loadlastproj", str(new_val))
    changes.append(f"  loadlastproj = {new_val} (open new project on startup)")

    # 2. Default save path
    if new_savepath:
        lines, section_end = set_value(lines, section_start, section_end, "defsavepath", new_savepath)
        changes.append(f"  defsavepath = {new_savepath}")

    # 3. Project template
    if selected_template:
        resource_path = find_reaper_resource_path()
        template_path = Path(selected_template)

        # Store relative to resource path if possible
        try:
            rel = template_path.relative_to(resource_path)
            tmpl_value = str(rel)
        except ValueError:
            tmpl_value = str(template_path)

        lines, section_end = set_value(lines, section_start, section_end, "newprojtmpl", tmpl_value)
        lines, section_end = set_value(lines, section_start, section_end, "newprojdo", "1")
        changes.append(f"  newprojtmpl = {tmpl_value}")
        changes.append(f"  newprojdo = 1 (use template for new projects)")

    # 4. Prompt to save on new project
    #    saveopts bit 0 = prompt to save
    if current_saveopts := get_value(lines, section_start, section_end, "saveopts"):
        saveopts_val = int(current_saveopts) | 1  # Set bit 0
    else:
        saveopts_val = 1
    lines, section_end = set_value(lines, section_start, section_end, "saveopts", str(saveopts_val))
    changes.append(f"  saveopts = {saveopts_val} (prompt to save on new project)")

    # 5. Media recording path
    lines, section_end = set_value(lines, section_start, section_end, "projdefrecpath", new_recpath)
    changes.append(f"  projdefrecpath = {new_recpath}")

    # 6. Peak files in subfolder relative to media
    #    peakcachegenmode: bit 0 (value 1) = put peaks in subfolder
    if current_peakmode is not None:
        peak_val = int(current_peakmode) | 1  # Set bit 0
    else:
        peak_val = 3  # Default: subfolder + fallback to alt path
    lines, section_end = set_value(lines, section_start, section_end, "peakcachegenmode", str(peak_val))
    changes.append(f"  peakcachegenmode = {peak_val} (peaks in subfolder relative to media)")

    # Write changes
    print()
    for c in changes:
        print(f"  {c}")

    if dry_run:
        print("\n  DRY RUN — no changes written.")
        print(f"  Would have written to: {ini_path}")
    else:
        write_ini(ini_path, lines)
        print(f"\n  Settings written to: {ini_path}")
        print(f"  Backup at: {backup_path}")
        print("\n  Done! Launch REAPER to verify your settings.")


if __name__ == "__main__":
    main()
