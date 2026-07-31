# Pardus System Services Manager

**A lightweight GUI application to manage systemd services and autostart applications on Pardus.**

[🇹🇷 Türkçe README için tıklayın](README.tr.md)

![License](https://img.shields.io/badge/license-GPL--3.0-blue.svg)
![Python](https://img.shields.io/badge/python-3-blue.svg)
![Qt](https://img.shields.io/badge/PySide6-Qt%20for%20Python-41cd52.svg)
![Platform](https://img.shields.io/badge/platform-Pardus%20%2F%20Debian--based-orange.svg)

---

## About

**Pardus System Services Manager** is a simple desktop tool built with **PySide6 (Qt for Python)** that lets you view and control `systemd` units and manage applications that start automatically with your session — all from one clean interface, without touching the terminal.

It was created to make everyday service management (enabling, disabling, starting, stopping, checking logs) and autostart configuration more approachable for Pardus users who prefer a graphical workflow.

## Features

### 🧩 systemd Unit Management
- Browse all systemd units in a searchable, sortable table (name, load state, active status, preset)
- Live status indicators — active (green), inactive (yellow), failed (red)
- Instant search/filter by unit name
- View detailed information for a selected unit (description, load state, active state)
- **Enable / disable** units
- **Start / restart / stop** units
- Open a unit's logs in your default log/text viewer
- Open the underlying unit file for manual editing (with a confirmation warning dialog, since editing unit files directly can affect system stability)
- Automatic background refresh of the unit list (every 5 seconds) without freezing the UI, thanks to dedicated worker threads

### 🚀 Autostart Application Management
- List all applications currently configured to autostart (`~/.config/autostart`)
- Browse and add any installed application (scans `/usr/share/applications`, `/usr/local/share/applications`, and `~/.local/share/applications`) to autostart
- View application details (name, description, icon, `.desktop` file path)
- Edit the `.desktop` entry file directly
- Remove an application from autostart

### ⚙️ Under the Hood
- Non-blocking UI: heavy operations (listing units, fetching descriptions) run on separate `QThread`s
- Built with the Qt Model/View architecture (`QStandardItemModel` + `QSortFilterProxyModel`) for efficient filtering and sorting
- Multi-language support via Qt Linguist translation files (`.ts` / `.qm`)
- Packaged and distributed as a native `.deb` package for Debian-based systems

## Requirements

- Python 3
- `dpkg` (for building the `.deb` package)
- A systemd-based Linux distribution (developed and tested for **Pardus**)

Python dependencies (installed automatically into a virtual environment by the build process):

```
altgraph
packaging
pyinstaller
pyinstaller-hooks-contrib
PySide6
PySide6_Addons
PySide6_Essentials
pyxdg
setuptools
shiboken6
```

See [`requirements.txt`](requirements.txt) (full, pinned versions) and [`requirements-lite.txt`](requirements-lite.txt) (used by the build system).

## Installation

### Option 1 — Build and install the `.deb` package (recommended)

```bash
git clone https://github.com/V6lhost/pardus-system-services-manager.git
cd pardus-system-services-manager
make build
sudo dpkg -i output_deb/pardus-system-services-manager-*.deb
```

This will:
1. Create an isolated Python virtual environment and install dependencies
2. Compile translation files
3. Bundle the application with PyInstaller
4. Package everything into a `.deb` file under `output_deb/`

### Option 2 — Run from source (development)

```bash
git clone https://github.com/V6lhost/pardus-system-services-manager.git
cd pardus-system-services-manager
make run
```

This creates a virtual environment (if it doesn't already exist), compiles translations, and launches the application directly with Python — no packaging step required.

### Cleaning build artifacts

```bash
make clean
```

Removes the virtual environment, build/dist folders, compiled translations, and the generated `.deb` output.

## Usage

Once installed, launch **Pardus System Services Manager** from your application menu, or run it directly from the terminal.

- Use the **Units** tab to search, inspect, and control systemd services.
- Use the **Autostart Applications** tab to manage which apps launch automatically at login.
- Select any item in the list to reveal its details panel with available actions.

## Project Structure

```
pardus-system-services-manager/
├── debian/          # Debian packaging metadata and file layout
├── src/             # Application source code (main.py, helper_functions.py, ...)
├── translations/    # Qt Linguist translation source (.ts) and compiled (.qm) files
├── ui/               # Qt Designer .ui files (MainWindow, dialogs)
├── Makefile          # Build, run, and packaging automation
├── requirements.txt
├── requirements-lite.txt
└── LICENSE
```

## Contributing

Contributions, bug reports, and feature suggestions are welcome!

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Commit your changes
4. Open a pull request describing what you changed and why

If you'd like to help translate the application into another language, check the `translations/` directory for the `.ts` files and use Qt Linguist (or the `pyside6-linguist` tool) to add your language.

## License

This project is licensed under the **GNU General Public License v3.0**. See [`LICENSE`](LICENSE) for the full text.

## Disclaimer

This is an **unofficial, community-made** tool. It is not developed, maintained, or endorsed by TÜBİTAK or the official Pardus project. Use at your own discretion, especially when editing or stopping system-critical services.

## Credits
- [Furkan Çolak](https://github.com/furkanclk3180) - Testing
- [topraklanbudev](https://github.com/Topraklanbudev) - Testing and motivation
- [ilgilenmek](https://github.com/keenon63) - Motivation
