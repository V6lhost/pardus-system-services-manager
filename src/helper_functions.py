from pydbus import SystemBus
from pathlib import Path
from xdg.DesktopEntry import DesktopEntry
import sys
import shutil

def list_systemd_units():
    bus = SystemBus()
    systemd = bus.get(".systemd1", "/org/freedesktop/systemd1")
    units = systemd.ListUnitFiles()
    return units

def get_unit_active_status(unit_name):
    bus = SystemBus()
    systemd = bus.get(".systemd1", "/org/freedesktop/systemd1")
    try:
        unit_path = systemd.LoadUnit(unit_name)
        unit = bus.get(".systemd1", unit_path)
        return unit.ActiveState
    except Exception:
        return "activation is not possible"

def list_desktop_entries(path):
    files = list(path.iterdir())
    entries = []
    for file in files:
        if file.suffix == ".desktop":
            entries.append(file)
    
    return entries

def get_application_details(path):
    application_data = {}
    entry = DesktopEntry(path)

    application_name = entry.getName()
    application_comment = entry.getComment()
    application_icon = entry.getIcon()

    application_data["name"] = application_name
    application_data["comment"] = application_comment if application_comment != "" else "No comment provided"
    application_data["icon"] = application_icon if application_icon != "" else "application-x-executable"

    return application_data

def copy_desktop_entry(source, destination):
    destination_file = destination / source.name
    if destination_file.exists():
        return
    
    shutil.copy(source, destination)