# -*- coding: utf-8 -*-

import sys
import json
from pykeepass import PyKeePass

from q_wrapper.src.sshagent import SSH_Agent


def create_ssh_agent(workers_num, path):
    """Example function for loading ssh credentials.
    Avoid loading passwords from file. Load passwords with tool like keepass.
    Because it is example file, pykeepass is not included in requirements.txt,
    also no unit tests are provided for container folder.
    
    """
    ssh_agent = SSH_Agent(path=path, n_jobs=workers_num)

    db_path = "/home/hermanda/Dropbox/Security/herman.kdbx"
    password_path = input("Password: ")
    keyfile_path = "/home/hermanda/Documents/info/img/star_trek.jpg"

    with open("../info/addresses.json") as f:
        data = json.load(f)

    credentials_l = []
    for address in data:
        if data[address] not in credentials_l:
            credentials_l.append(data[address])

    with open(password_path, "r") as f:
        password = f.read().replace("\n", "")

    credentials = {}
    kp = PyKeePass(db_path, password=password, keyfile=keyfile_path)
    for login_title in credentials_l:
        entry = kp.find_entries(title="ms", first=True)
        credentials[login_title] = {
            "username": entry.username,
            "password": entry.password,
        }

    for address in data:
        title = data[address]
        ssh_agent.add_address(
            ip_address=address,
            username=credentials[title]["username"],
            password=credentials[title]["password"],
            group_name=title,
        )

    return ssh_agent
