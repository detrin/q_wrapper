# -*- coding: utf-8 -*-

import sys
import paramiko
from scp import SCPClient
import time
import pickle
import threading

import queue 

class SSH_Agent:
    def __init__(self, path=None, password_file=None, username="hermanda", server_list=None, n_jobs=4):
        if path is None:
            raise Exception("Please enter the path on remote machine.")
        if password_file is None:
            raise Exception("Please enter the path to the file with password.")
        self.path = path
        self.is_connected = False
        with open(password_file, "r") as f:
            for row in f:
                password = row.replace("\n", "")
        self.password = password
        self.ssh_connections = [None for i in range(len(self.server_list))]
        self.n_jobs = n_jobs

    def createSSHClient(self, server, user, password):
        client = paramiko.SSHClient()
        # client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=server, username=user, password=password, allow_agent=False, look_for_keys=False, timeout=10)
        return client

    def progress(self, filename, size, sent):
        sys.stdout.write("%s\'s progress: %.2f%%   \r" % (filename, float(sent)/float(size)*100) )

    def connect_scp(self):
        self.ssh = self.createSSHClient(self.server_list[0], "hermanda", self.password)
        self.scp = SCPClient(self.ssh.get_transport(), progress=self.progress)
    
    def connect_ssh(self):
        for ind in range(self.n_jobs):
            self.ssh_connections[ind] = self.createSSHClient(self.server_list[ind], "hermanda", self.password)
            time.sleep(5)
    
    def connect_all(self):
        self.connect_scp()
        self.connect_ssh()

    def disconnect(self):
        self.ssh.close()
        for ind in range(self.n_jobs):
            self.ssh_connections[ind].close
            self.ssh_connections[ind] = None
    
    def put(self, localfile, remotefile):
        self.scp.put(localfile, self.path+remotefile, recursive=True)
    
    def get(self, remotefile, localfile):
        self.scp.get(self.path+remotefile, localfile, recursive=True)
    
    def exec_command(self, ind, command_str, worker_ind=-1):
        stdin, stdout, stderr = self.ssh_connections[worker_ind].exec_command(command_str)
        exit_status = stdout.channel.recv_exit_status() 
        filename = "transfer/results_"+str(ind)+".pkl"
        self.get(filename, filename)
        return exit_status
    
    def run_parallel(self, args):
        filename = "transfer/task.pkl"
        with open(filename, "wb") as f:
            pickle.dump(args, f)
        self.put(filename, filename)
        results = []
        q = SSH_Worker(num_workers=self.n_jobs)

        for ind in range(len(args)):
            q.add_task(self.exec_command, ind, "cd "+self.path+";python transfer_script.py --task_num "+str(ind))
        
        q.join() 

        if False:
            for run_ind in range(int(len(args) / self.n_jobs) + 1):
                threads = []
                max_iter = self.n_jobs
                if run_ind == int(len(args) / self.n_jobs):
                    max_iter = len(args) % self.n_jobs
                print(run_ind, max_iter)
                for ind in range(max_iter):
                    file_ind = run_ind *  self.n_jobs + ind 
                    t = threading.Thread(
                        target=self.exec_command, 
                        args=(ind, "cd "+self.path+";python transfer_script.py --task_num "+str(file_ind),)
                        )
                    t.start()
                    threads.append(t)
                for t in threads:
                    t.join()
                
        for ind in range(len(args)):
            filename = "transfer/results_"+str(ind)+".pkl"
            with open(filename, "rb") as f:
                result = pickle.load(f)
            results.append(result)

        return results


class SSH_Worker(queue.Queue):

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
                except:
                    attempts += 1
            print("Finished job", args[0])
            self.task_done()
