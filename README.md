# REAPER Preference Setter

A Python script to quickly configure REAPER DAW preferences on any machine. Useful for touring, studio setups, or maintaining consistent settings across multiple installs.

## What it configures

- **Startup behavior** — Opens a new project on launch (instead of loading the last project)
- **Project template** — Sets a default `.RPP` template for new projects
- **Prompt to save** — Ensures you're always prompted to save new projects
- **Default save path** — Sets where new projects are saved
- **Media path** — Sets the relative media recording folder (e.g., `Audio`)
- **Peak files** — Stores `.reapeaks` in a `peaks/` subfolder relative to media

## Usage

```bash
python3 configure_reaper.py
```

The script will:
1. Locate your `reaper.ini` (macOS, Windows, and Linux supported)
2. Show your current settings
3. Create a timestamped backup of `reaper.ini`
4. Prompt you for the save path and project template
5. Apply all settings

### Dry run

Preview changes without modifying anything:

```bash
python3 configure_reaper.py --dry-run
```

## Requirements

- Python 3.6+
- REAPER should be **closed** before running (the script will warn you if it's open)

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
