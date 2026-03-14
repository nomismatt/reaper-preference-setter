# REAPER Preference Setter

A simple app to configure REAPER DAW preferences on any machine. Useful for touring, studio setups, or maintaining consistent settings across multiple installs.

## What it configures

- **Startup behavior** — Opens a new project on launch (instead of loading the last project)
- **Project template** — Sets a default `.RPP` template for new projects
- **Prompt to save** — Ensures you're always prompted to save new projects
- **Default save path** — Sets where new projects are saved
- **Media path** — Sets the relative media recording folder (e.g., `Audio`)
- **Peak files** — Stores `.reapeaks` in a `peaks/` subfolder relative to media

## Download

Go to the [Releases page](https://github.com/nomismatt/reaper-preference-setter/releases) and download for your platform:

- **REAPER-Preference-Setter-macOS.dmg** — macOS (signed and notarized)
- **REAPER-Preference-Setter.exe** — Windows

No Python installation required.

### macOS

1. Open the `.dmg` file
2. Drag **REAPER Preference Setter** to your Applications folder (or run it directly)
3. The app is signed and notarized — it should open without Gatekeeper warnings

### Windows

1. Download the `.exe`
2. If SmartScreen shows a warning, click **More info** > **Run anyway**
3. This only happens once

## What happens when you run it

1. A window opens showing your current REAPER settings
2. Set your preferred project save path, template, and media folder
3. Toggle checkboxes for startup behavior, save prompts, and peak file organization
4. Click **Apply** — a backup of `reaper.ini` is created automatically
5. Launch REAPER to verify

## Alternative: run from source

If you have Python 3.6+ with tkinter:

```bash
python3 configure_reaper.py
```

## Requirements

- REAPER should be **closed** before applying changes (the app will warn you if it's open)
- macOS 10.15+ or Windows 10+
