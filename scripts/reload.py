#!/usr/bin/python3
import sys
import requests
import json
import os
import configparser
import subprocess
from pathlib import Path

import setup_printer
from setup_printer import add_template_file, COMMON_PATH
from branch_check import moonraker_klipper_branch_check

url = "http://localhost"
home_path = Path(__file__).parent.resolve().parent.parent

klipper_scripts = Path(__file__).parent.resolve()
klipper_config_path = home_path / "klipper_config"
fgf_config_path = klipper_config_path / "fgf"
fff_config_path = klipper_config_path / "fff"

def read_master_config():
    master_config_path = klipper_config_path / ".master.cfg"
    if not master_config_path.exists():
        print(".master.cfg is missing! autogenerating to default")
        add_template_file(COMMON_PATH / "master.cfg", master_config_path)

    master_config = configparser.ConfigParser(inline_comment_prefixes="#")
    master_config.read(str(master_config_path))
    return master_config
    # for p in printer_config: print(p)

def wait_on_moonraker():
    print("Waiting on moonraker...")
    from requests.adapters import HTTPAdapter, Retry
    s = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[ 502, 503, 504 ])
    s.mount('http://', HTTPAdapter(max_retries=retries))
    s.get(url + "/server/database/list")

#Reloading UI configuration
def reload_ui():
    default_json_file = klipper_config_path / ".theme/default.json"
    with open(default_json_file) as f:
        defaults = json.load(f)
    namespaces = [name for name in defaults]

    for name in namespaces:
        default_value = defaults[name]
        print("{} Namespace Default: {}".format(name, default_value))
        print("--- DELETING {} NAMESPACE ---".format(name))
        delete_url = url+"/server/database/item?namespace=mainsail&key="+name
        delete_response = requests.delete(delete_url)
        print(delete_response.text)

        print("--- POSTING NEW DEFAULT INTO {} NAMESPACE ---".format(name))
        post_url = url+"/server/database/item"
        body = {"namespace": "mainsail", "key": name, "value": defaults[name]}
        post_response = requests.post(post_url, json=body)
        print(post_response.text)
    
def check_network_availability():
    try:
        request = requests.get("http://www.google.com", timeout=5)
        print("Network Available")
        return True
    except:
        print("Network Unavailable, skipping dependency checking")
        return False

def reboot_services():
    os.system("service moonraker restart")
    os.system("service klipper restart")
    os.system("service lightdm restart")

def main():
    master_config = read_master_config()

    #Determine deposition type
    if "fff" in master_config:
        deposition_type = "fff"
        printer_config = master_config["fff"]
    elif "fgf" in master_config:
        deposition_type = "fgf"
        printer_config = master_config["fgf"]

    if not deposition_type:
        print("fff or fgf section is not defined in master.cfg. Please enable one of the sections.")
        return
    elif not printer_config:
        print("Configuration section for {deposition_type} does not exist!")
        return
    
    # Validate board type
    board = printer_config.get("board_type", "")
    valid_board = ["azteeg", "archimajor"]
    if board not in valid_board:
        print("WARN: Invalid board type in master.cfg, defaulting to archimajor")
        board = "archimajor"
    
    #Validate platform type
    platform = printer_config.get("platform_type", "")
    valid_platform = ["regular", "xlt", "terabot"]
    if platform not in valid_platform:
        print("Invalid platform type in master.cfg, defaulting to regular")
        platform = "regular"

    print("Setting up printer as a {} {} {} machine".format(deposition_type, board, platform))
    setup_printer.setup_printer(deposition_type, board, platform)

    #Serial Setup
    serial_out = subprocess.run([str(klipper_scripts / "get_serial.sh")], capture_output=True)
    print(serial_out.stdout.decode("utf-8"))
    
    #Block until moonraker system service comes up. 
    wait_on_moonraker()
    if check_network_availability():
        moonraker_klipper_branch_check(master_config=master_config)

    setup_printer.main()
    reload_ui()
    reboot_services()

if __name__ == "__main__":
    main()

