from pydbus import SystemBus
from pathlib import Path
from xdg.DesktopEntry import DesktopEntry
import sys
import shutil
import subprocess
import json

 # Using subprocess is way faster than listing units with dbus
 
def list_systemd_units():
    command = ["systemctl", "list-unit-files", "-o", "json"]
    
    output = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=True,
        timeout=5
    )
    return json.loads(output.stdout)

def get_unit_active_status(unit_name):
    bus = SystemBus()
    systemd = bus.get(".systemd1", "/org/freedesktop/systemd1")
    try:
        unit_path = systemd.LoadUnit(unit_name)
        unit = bus.get(".systemd1", unit_path)
        return unit.ActiveState
    except Exception:
        return "activation is not possible"

def get_unit_description(unit_name):
    try:
        bus = SystemBus()
        systemd = bus.get(".systemd1", "/org/freedesktop/systemd1")
        unit_path = systemd.GetUnit(unit_name)
        unit_obj = bus.get(".systemd1", unit_path)
        return unit_obj.Description
        
    except Exception as e:
        return "No description"

def get_unit_exit_status(unit_name):
    try:
        bus = SystemBus()
        systemd = bus.get(".systemd1", "/org/freedesktop/systemd1")
        unit_path = systemd.GetUnit(unit_name)
        props = bus.get(".systemd1", unit_path)
        
        code = getattr(props, "ExecMainCode", None)
        status = getattr(props, "ExecMainStatus", None)
        result = getattr(props, "Result", None)
        
        return {
            "code": code,
            "status": status,
            "result": result
        }

    except:
        return {
            "code": "Unavailable",
            "status": "Unavailable",
            "result": "Unavailable"
        }

def get_unit_logs(unit_name):
    try:
        command = ["journalctl", "-u", unit_name, "--no-pager"]
        
        output = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
            timeout=5
        )
        
        return output.stdout
        
    except subprocess.CalledProcessError as e:
        return "Error while getting logs"

def get_unit_file_path(unit_name):
        bus = SystemBus()
        systemd = bus.get(".systemd1", "/org/freedesktop/systemd1")
        unit_path = systemd.LoadUnit(unit_name)
        props = bus.get(".systemd1", unit_path)
        return getattr(props, "FragmentPath", "")

def run_systemctl_command(action, unit_name):
    try:
        cmd = ["pkexec", "systemctl", action, unit_name]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode == 0:
            return True
        else:
            return False
            
    except Exception:
        return False

def unit_enable(unit_name):
    return run_systemctl_command("enable", unit_name)

def unit_disable(unit_name):
    return run_systemctl_command("disable", unit_name)

def unit_start(unit_name):
    return run_systemctl_command("start", unit_name)

def unit_stop(unit_name):
    return run_systemctl_command("stop", unit_name)

def unit_restart(unit_name):
    return run_systemctl_command("restart", unit_name)

def save_logs_to_temporary_file(unit_name):
    logs = get_unit_logs(unit_name)
    logfile = Path("/tmp") / f"log-{unit_name}.txt"
    with open(logfile, "w", encoding="UTF_8") as f:
        f.write(logs)
    
    return logfile

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

def remove_autostart_entry_file(entry):
    entry.unlink(missing_ok=True)