#!/usr/bin/env python

# Script to clone VMs in parallel using govc
import subprocess
import os
import sys
from time import sleep
import threading

def exec_shell(command, realTime=False):
    p = subprocess.Popen(command, shell=True,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)

    std_out, std_err = p.communicate()
    rc = p.returncode
    if rc == 0:
        result = True
        output = std_out
    else:
        result = False
        output = std_err
    return (result, output)


class myThread (threading.Thread):
    def __init__(self, name, counter, first_vm_name, datastore, pool, uname):
        threading.Thread.__init__(self)
        self.counter = counter
        self.name = name
        self.sourceVM = first_vm_name
        self.datastore = datastore
        self.pool = pool
        self.uname = uname

    def run(self):
        this_vm_name = str(self.uname) + "-" + str(self.counter)
        cmd="govc vm.clone -vm " + self.sourceVM + " -on=false -ds=" + self.datastore + " -pool=\"" + self.pool + "\" -net=\"VM Network\" " + this_vm_name
        print "Command : " + cmd + "\n"
        res,out=exec_shell(cmd)

# Main function starts here

if len(sys.argv) != 6:
    print "Usage: ./clone_vms.py <template> <num_clones> <resource_pool> <datastore> <unique_name>"
    sys.exit(1)
template = sys.argv[1]
num_clones = int(sys.argv[2])
pool = sys.argv[3]
datastore = sys.argv[4]
uname = sys.argv[5]

first_vm_name = str(uname)+"-1"
cmd="govc vm.clone -vm " + template + " -on=false -ds=" + datastore + " -pool=\"" + pool + "\" -net=\"VM Network\" " + first_vm_name
print "Command : " + cmd + "\n"
res,out=exec_shell(cmd)

# Lets statically run 8 clones in parallel for now
to_be_done = num_clones - 1
counter = 1

while to_be_done > 0:
    names = locals()
    if to_be_done > 8:
        num_threads = 8
    else:
        num_threads = to_be_done
    for x in range(num_threads):
        counter = counter + 1
        names["thread%s"%x] = myThread("Thread", counter, first_vm_name, datastore, pool, uname)

    # Start a new thread for every clone
    for x in range(num_threads):
        names["thread%s"%x].start()
        #sleep(1)

    for x in range(num_threads):
        names["thread%s"%x].join()
    
    to_be_done = to_be_done - 8

print "Quitting"
