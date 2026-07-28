from pathlib import Path
from xdg.DesktopEntry import DesktopEntry
import sys
import shutil
import subprocess
import json

 
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
    try:
        result = subprocess.run(
            ["systemctl", "is-active", unit_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False  # if unit is stopped/failed this command will return error and cause problems. disable it using check=False
        )
        status = result.stdout.strip()
        if status:
            return status
        else:
            return "unknown"
    except Exception:
        return "unknown"
    
def get_unit_description(unit_name):
    return get_property(unit_name, "Description")

def get_unit_exit_status(unit_name):
    try:        
        code = get_property(unit_name, "ExecMainCode")
        status = get_property(unit_name, "ExecMainStatus")
        result = get_property(unit_name, "Result")
        
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