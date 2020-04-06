# -*- coding: utf-8 -*-

import sys
import paramiko
from scp import SCPClient
import time
import pickle
import threading

import queue


class SSH_Agent:
    """To distribute tasks over ssh to nodes we will use this method."""

    def __init__(self, path=None, n_jobs=4):
        """Initialize class with empaty sets and arrays."""
        if path is None:
            raise Exception("Please enter the path on remote machine.")

        self.path = path
        self.is_connected = False
        self.server_list = []
        #  List of all active connections
        self.ssh_connections = []
        self.scp_connections = []
        self.n_jobs = n_jobs
        self.usernames = {}
        self.passwords = {}
        # Save unique groups with ip addresses
        self.groups = {}
        # save group names by addresses
        self.group_names = {}

    def add_address(
        self, ip_address=None, username=None, password=None, group_name=None
    ):
        """Add one ip addres with username, password and group name."""
        if ip_address is None or username is None or password is None:
            raise Exception("Please state ip address, username and password.")

        if group_name is None:
            raise Exception("Please state ip group_name.")

        self.server_list.append(ip_address)
        self.usernames[ip_address] = username
        self.passwords[ip_address] = password
        self.group_names[ip_address] = group_name
        if group_name not in self.groups:
            self.groups[group_name] = ip_address

    def createSSHClient(self, server_ip, user, password):
        """Create one ssh client for scp or only ssh usage."""
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(
            hostname=server_ip,
            username=user,
            password=password,
            allow_agent=False,
            look_for_keys=False,
            timeout=10,
        )

        return client

    def progress(self, filename, size, sent):
        """Progress bar for file sending."""
        sys.stdout.write(
            "%s's progress: %.2f%%   \r" % (filename, float(sent) / float(size) * 100)
        )

    def connect_scp(self):
        """Connect to all groups with scp."""
        self.disconnect_scp()

        last_group_name = None

        for ind in range(self.n_jobs):
            server_ip = self.server_list[ind]
            username, password = self.usernames[server_ip], self.passwords[server_ip]
            ssh_ind = self.server_list.index(server_ip)
            ssh_client = self.ssh_connections[ssh_ind]
            scp_connection = SCPClient(
                ssh_client.get_transport(), progress=self.progress
            )
            self.scp_connections.append(scp_connection)

    def connect_ssh(self):
        """Connect to all machines with ssh."""
        self.disconnect_ssh()

        last_group_name = None

        for ind in range(self.n_jobs):
            server_ip = self.server_list[ind]
            group_name = self.group_names[server_ip]
            username, password = self.usernames[server_ip], self.passwords[server_ip]

            ssh_connection = self.createSSHClient(server_ip, username, password)
            self.ssh_connections.append(ssh_connection)

            if group_name == last_group_name:
                time.sleep(0.25)
            else:
                last_group_name = group_name

    def connect_all(self):
        """Connect to both scp and ssh."""
        self.connect_ssh()
        self.connect_scp()

    def disconnect_scp(self):
        """Disconnect all scp connections."""
        for client in self.scp_connections:
            client.close()

        self.scp_connections = []

    def disconnect_ssh(self):
        """"Disconnect all ssh connections."""
        for client in self.ssh_connections:
            client.close()

        self.ssh_connections = []

    def disconnect_all(self):
        """Disconnect all connections."""
        self.disconnect_scp()
        self.disconnect_ssh()

    def put(self, client, localfile, remotefile):
        """Send file through scp."""
        client.put(localfile, self.path + remotefile, recursive=True)

    def get(self, client, remotefile, localfile):
        """Get file though scp."""
        client.get(self.path + remotefile, localfile, recursive=True)

    def send_files(self, files, initial=False):
        """Sending files before any task execution."""
        last_group_name = None
        for ind in range(len(self.ssh_connections)):
            server_ip = self.server_list[ind]
            group_name = self.group_names[server_ip]
            if group_name != last_group_name:
                last_group_name = group_name
                ssh_client = self.ssh_connections[ind]
                scp_client = self.scp_connections[ind]
                if initial:
                    self.exec_command_plain(ssh_client, "mkdir -p " + self.path)
                    self.exec_command_plain(ssh_client, "rm -f "+self.path+"transfer/task.pkl")
                    self.exec_command_plain(
                        ssh_client, "rm " + self.path + "transfer/*"
                    )
                    self.exec_command_plain(
                        ssh_client, "mkdir " + self.path + "transfer"
                    )
                for file in files:
                    self.put(scp_client, file, file)

    def get_files(self, files):
        """Getting additional results back after task execution.
            This will work only in case files are present in all groups.
        """
        for scp_client in self.scp_connections:
            for file in files:
                self.get(scp_client, file, file)

    def exec_command(self, ind, command_str, worker_ind=-1):
        """"Execute command on worker with given index."""

        # Execute
        stdin, stdout, stderr = self.ssh_connections[worker_ind].exec_command(
            command_str
        )

        # Wait till finished
        exit_status = stdout.channel.recv_exit_status()

        # Get results
        scp_client = self.scp_connections[worker_ind]
        filename = "transfer/results_" + str(ind) + ".pkl"
        status = self.get(scp_client, filename, filename)

        return exit_status

    def exec_command_plain(self, client, command_str):
        """Plain command execution."""
        stdin, stdout, stderr = client.exec_command(command_str)
        exit_status = stdout.channel.recv_exit_status()
        return exit_status

    def kill_commands(self):
        """Kill running commands on all nodes."""
        for ssh_client in self.ssh_connections:
            self.exec_command_plain(ssh_client, "pkill -f transfer_script")

    def run_parallel(self, fun, fun_args):
        """Execute function with arguments from queue."""

        # Send arguments in file
        filename = "transfer/task.pkl"
        with open(filename, "wb") as f:
            pickle.dump((fun.__name__, fun_args), f)
        self.send_files([filename])

        # Prepare queue
        results = []
        q = SSH_Worker(num_workers=self.n_jobs)

        # Execute commands through ssh and transfer script
        for ind in range(len(fun_args)):
            q.add_task(
                self.exec_command,
                ind,
                "cd "
                + self.path
                + ";python transfer_script.py --task_num "
                + str(ind)
                + " ;cd ~",
            )

        q.join()

        # After execution real results locally and return results
        for ind in range(len(fun_args)):
            filename = "transfer/results_" + str(ind) + ".pkl"
            with open(filename, "rb") as f:
                result = pickle.load(f)
            results.append(result)

        return results


class SSH_Worker(queue.Queue):
    """Simple worker for task execution from queue."""

    def __init__(self, num_workers=1):
        queue.Queue.__init__(self)
        self.num_workers = num_workers
        self.start_workers()

    def add_task(self, task, *args, **kwargs):
        args = args or ()
        kwargs = kwargs or {}
        self.put((task, args, kwargs))

    def start_workers(self):
        for i in range(self.num_workers):
            t = threading.Thread(target=self.worker, args=(i,))
            t.daemon = True
            t.start()

    def worker(self, worker_ind):
        while True:
            item, args, kwargs = self.get()
            attempts, max_attempts = 0, 3
            while attempts < max_attempts:
                try:
                    item(*args, **kwargs, worker_ind=worker_ind)
                    attempts = max_attempts
                except Exception as e:
                    print(e)
                    attempts += 1

            # We want to keep progress of tasks in terminal
            print("Finished job", args[0])
            self.task_done()
