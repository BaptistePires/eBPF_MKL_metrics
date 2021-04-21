from utils import *
import constants
import os
import threading
import subprocess as sb
from time import sleep

tmp_bpf_dir = "bpf"
running = True


with open(const.AVAILABLE_TRACERS, "r") as f:
    tracers = f.readlines()[0]
    if const.GRAPH_TRACER not in tracers:
        print("This program needs %s to be available as a tracer in ftrace." % const.GRAPH_TRACER)
        exit()
    
try:
    with open(const.CURRENT_TRACER, "w+") as f:
        f.write(const.GRAPH_TRACER)
except OSError as e:    
    print("%s tracer seems not to be allowed in ftrace" % const.GRAPH_TRACER)
    exit()

with open(const.SET_FTRACE_FILTER, "w+") as f:
    f.write(' '.join(const.FTRACE_FILTERS))

with open(const.TRACE_PIPE, "w") as f:
    f.write("")

with open(const.TRACING_OPTIONS_FILE, "w") as f:
    f.write("funcgraph-duration")


make_sb = sb.Popen(["make", "-C", tmp_bpf_dir])
make_sb.wait()

for i in range(10):
    loader_sb = sb.Popen(["./monitor-exec", "wrapper.o", "", "", tmp_bpf_dir], cwd=tmp_bpf_dir, stdin=sb.PIPE)
    loader_sb.wait()


bpf_check = []
bpf_prog_select_runtime = []
func_data = {func_name:{"entries": [], "average": 0.0} for func_name in const.FTRACE_FILTERS}

with open(const.TRACE_PIPE, "r") as f:
    for l in f.readlines():
        l = l.strip()
        for func_name in func_data:
            if func_name in l:
                func_data[func_name]["entries"].append(l)



for func_name in func_data:
    entry_sz = len(func_data[func_name]["entries"])
    if entry_sz > 0:
        func_data[func_name]["average"] = sum([float(l.split(' ')[2]) for l in func_data[func_name]["entries"]]) / entry_sz
        print("Average time for %s, called %s times : %s us" % (func_name, str(entry_sz), str(func_data[func_name]["average"])))


    

    