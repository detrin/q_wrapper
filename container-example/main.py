# -*- coding: utf-8 -*-

import os

from os import listdir
from os.path import isfile, join

from connection import create_ssh_agent
from main_exec import test_fun

dirpath = os.getcwd()
foldername = os.path.basename(dirpath)
path = os.path.join("containers/", foldername) + "/"

# Take first 27 ip addresses
ssh_agent = create_ssh_agent(27, path)

ssh_agent.connect_all()

files_to_send = [f for f in listdir(".") if isfile(join(".", f))]
files_to_send = list(filter(lambda f: ".py" in f, files_to_send))
files_to_send += ["q_wrapper"]
ssh_agent.send_files(files_to_send, initial=True)

# Execute 1000 tasks
args = [[x, 2] for x in range(0, 1000)]
results = ssh_agent.run_parallel(test_fun, args)
print(results)

ssh_agent.disconnect_all()
