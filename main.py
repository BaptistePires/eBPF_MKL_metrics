import argparse
import sys
import os
import tempfile
import subprocess
import string
import random
from ctypes import *
import signal

import constants as const
from utils import *

parser = argparse.ArgumentParser()
parser.add_argument("-d", "--dir", type=str, help="", default=".")
args = parser.parse_args()

if os.geteuid() != 0:
    print("Need to run with sudo")
    exit()

bpf_path = args.dir

if not os.path.exists(bpf_path):
    print("Directory %s doesn't exist" % bpf_path)
    exit()

print("Target directory %s" % bpf_path)
print("Activating JIT")
if not activate_jit():
    print("Error while activating JIT")
    exit()


pipe_read_name = "/tmp/%s" % ''.join(random.choice(string.ascii_lowercase) for i in range(10))
pipe_write_name = "/tmp/%s" % ''.join(random.choice(string.ascii_lowercase) for i in range(10))


r_sub, w_sub = os.pipe()
r_main, w_main = os.pipe()
loader_child = subprocess.Popen(["./monitor-exec", "wrapper.o", pipe_read_name, pipe_write_name], cwd=bpf_path, stdout=os.fdopen(w_sub, 'w'), stdin=os.fdopen(r_main, 'r'))

out_sub = os.fdopen(r_sub, 'r')

# pipe_read = open(pipe_r   ead_name, 'r')
print("Waiting for value in child stdout")
value = int(out_sub.read(1))
print("Value read %s ::" % value)

if value < 0:
    print("Error while inserting BPF program")
    
    child.wait()

# Generate events 
print("Generating events with module")
module_child = subprocess.Popen(["insmod", "helloWorld.ko"], cwd="./mod/")
module_child.wait()
module_child = subprocess.Popen(["rmmod", "helloWorld"], cwd="./mod/")
module_child.wait()
loader_child.send_signal(signal.SIGCONT)
# Notify loader to retrieve values

in_sub = os.fdopen(w_main, 'w')
in_sub.write("1")

generate_figure(const.OUTPUT_FILE_FIGURE)

os.close(w_main)



