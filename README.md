# REAPER Preference Setter

A Python script to quickly configure REAPER DAW preferences on any machine. Useful for touring, studio setups, or maintaining consistent settings across multiple installs.

## What it configures

- **Startup behavior** — Opens a new project on launch (instead of loading the last project)
- **Project template** — Sets a default `.RPP` template for new projects
- **Prompt to save** — Ensures you're always prompted to save new projects
- **Default save path** — Sets where new projects are saved
- **Media path** — Sets the relative media recording folder (e.g., `Audio`)
- **Peak files** — Stores `.reapeaks` in a `peaks/` subfolder relative to media

## Download

Go to the [Releases page](https://github.com/nomismatt/reaper-preference-setter/releases) and download the executable for your OS:

- **REAPER-Preference-Setter-macOS** — Mac
- **REAPER-Preference-Setter-Windows.exe** — Windows
- **REAPER-Preference-Setter-Linux** — Linux

No Python installation required.

### macOS: first-time setup

macOS may block the downloaded executable. To allow it:

1. Try to open the file — macOS will show a warning
2. Go to **System Settings > Privacy & Security**
3. Scroll down — you'll see a message about the blocked app
4. Click **Open Anyway**

You only need to do this once.

## Alternative: run from source

If you have Python installed, you can run the script directly:

```bash
python3 configure_reaper.py
```

Or on macOS, double-click **`configure_reaper.command`** in Finder.

### Dry run

Preview changes without modifying anything:

```bash
python3 configure_reaper.py --dry-run
```

## What happens when you run it

1. Locates your `reaper.ini` (macOS, Windows, and Linux supported)
2. Shows your current settings
3. Creates a timestamped backup of `reaper.ini`
4. Prompts you for the save path and project template
5. Applies all settings

A backup is always created before any changes are made, so you can safely revert if needed.

## Requirements

- REAPER should be **closed** before running (the script will warn you if it's open)
- The standalone executables have no other requirements
- Running from source requires Python 3.6+

## How it works

The script directly modifies `reaper.ini`, which stores all of REAPER's preferences. Key mappings:

| Setting | reaper.ini key | Value |
|---------|---------------|-------|
| New project on startup | `loadlastproj` | Clears bits 0+1 |
| Project template | `newprojtmpl` | Relative path to `.RPP` |
| Use template | `newprojdo` | `1` |
| Prompt to save | `saveopts` | Sets bit 0 |
| Default save path | `defsavepath` | Absolute path |
| Media folder | `projdefrecpath` | Relative folder name |
| Peaks in subfolder | `peakcachegenmode` | Sets bit 0 |
