import sys
import os
import requests
import socket
import ConfigParser as configparser
from gandi_api import GandiHandler

# name of the configuration file.
# If the full path is not given, gandi-ddns.py will check for this file in
# its current directory
config_file = "config.txt"

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

def get_ip():
    """ Get external IP """

    try:
        # Could be any service that just gives us a simple raw ASCII IP address (not HTML etc)
        http_response = requests.get("http://ipv4.myexternalip.com/raw")
        external_ip = http_response.text.strip()
    except Exception:
        sys.exit('Unable to external IP address.')

    return external_ip

def change_zone_ip(config, section, new_ip):
    """ Change the zone record to the new IP """

    api = config.get_api(section, "api")
    a_name = config.get(section, "a_name")
    apikey = config.get(section, "apikey")
    ttl = int(config.get(section, "ttl"))
    domain = config.get(section, "domain")

    gandi_handler = GandiHandler(api, apikey)
    gandi_handler.change_zone_a_record(new_ip, a_name, ttl, domain)


def read_config(config_path):
    """ Open the configuration file or create it if it doesn't exists """

    cfg = configparser.ConfigParser()
    cfg.read(config_path)

    if not cfg:
        raise IOError("Please fill in the 'config.txt' file")

    return cfg

def main():
    try:
        path = config_file
        if not path.startswith('/'):
            path = os.path.join(SCRIPT_DIR, path)
        config = read_config(path)
    except IOError as err:
        sys.exit(err)

    for section in config.sections():
        current_ip = socket.gethostbyname(config.get(section, "host"))
        if current_ip == '127.0.0.1':
            current_ip = get_ip()

        change_zone_ip(config, section, current_ip)

if __name__ == "__main__":
    main()