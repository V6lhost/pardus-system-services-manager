from pathlib import Path
from xdg.DesktopEntry import DesktopEntry
import sys
import shutil
import subprocess
import json

 
def list_systemd_units():
    command_unit_files = ["systemctl", "list-unit-files", "-o", "json"]
    output_unit_files = subprocess.run(
        command_unit_files,
        capture_output=True,
        text=True,
        check=True,
        timeout=5
    )
    unit_files = json.loads(output_unit_files.stdout)

    command_units = ["systemctl", "list-units", "--all", "-o", "json"]
    output_units = subprocess.run(
        command_units,
        capture_output=True,
        text=True,
        check=True,
        timeout=5
    )

    units = json.loads(output_units.stdout)

    allowed_suffixes = (".service", ".socket", ".timer", ".target")

    units = [unit for unit in units if unit.get("unit", "").endswith(allowed_suffixes)]
    unit_files = [unit_file for unit_file in unit_files if unit_file.get("unit_file", "").endswith(allowed_suffixes)]

    units_dict = {item.get("unit"): item for item in units}

    for unit_file in unit_files:
        unit_name = unit_file["unit_file"]
        
        if unit_name in units_dict:
            unit_info = units_dict[unit_name]
            unit_file["load"] = unit_info.get("load")
            unit_file["active"] = unit_info.get("active")
        
        else:
            unit_file["load"] = None,
            unit_file["active"] = "inactive"

    return unit_files

def list_unit_descriptions(units):
    static_details = {}
    for unit in units:
        unit_name = unit["unit_file"]
        static_details[unit_name] = {
            "description": get_property(unit_name, "Description")
        }

    return static_details

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
        return get_property(unit_name, "FragmentPath")

def get_property(unit_name, property):
    try:
        result = subprocess.run(
            ["systemctl", "show", unit_name, f"--property={property}", "--value"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except Exception:
        return "failed"

def run_systemctl_command_privileged(action, unit_name):
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
    return run_systemctl_command_privileged("enable", unit_name)

def unit_disable(unit_name):
    return run_systemctl_command_privileged("disable", unit_name)

def unit_start(unit_name):
    return run_systemctl_command_privileged("start", unit_name)

def unit_stop(unit_name):
    return run_systemctl_command_privileged("stop", unit_name)

def unit_restart(unit_name):
    return run_systemctl_command_privileged("restart", unit_name)

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

list_systemd_units()