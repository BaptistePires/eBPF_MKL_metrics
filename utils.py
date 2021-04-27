import os
import constants as const
from plot_utils import *
import subprocess as subp
import time
import random
import string
import signal

"""
    JIT & Verifier benchmarks
"""

def __write_to_jit(is_enabled: int) -> bool:
    if is_enabled != 1 and is_enabled != 0:
        print("write_to_jit accepts [0; 1] only")
        return False

    with open(const.BPF_JIT_ENABLE, "w") as f:
        f.write(str(is_enabled))

    return True
def deactivate_jit() -> bool:
    return __write_to_jit(0)

def activate_jit() -> bool:
    return __write_to_jit(1)

def __setup_ftrace() -> bool:

    # Checks that `grap-function` is allowed
    try:
        with open(const.AVAILABLE_TRACERS, "r") as f:
            tracers = f.readlines()[0]
            if const.GRAPH_TRACER not in tracers:
                print("This program needs %s to be available as a tracer in ftrace." % const.GRAPH_TRACER)
                return False
    except OSError as e:
        print("Error reading %s.", const.AVAILABLE_TRACERS)
        print(e)
        return False

    # Set tracer
    try:
        with open(const.CURRENT_TRACER, "w+") as f:
            f.write(const.GRAPH_TRACER)
    except OSError as e:
        print("Error writing to %s.", const.CURRENT_TRACER)
        print(e)
        return False


    # Set function traced
    try:
        with open(const.SET_FTRACE_FILTER, "w+") as f:
            f.write(' '.join(const.FTRACE_FILTERS))
    except OSError as e:
        print("Error writing to %s.", const.SET_FTRACE_FILTER)
        print(e)
        return False

    # Clean trace
    try:
        with open(const.TRACE_PIPE, "w") as f:
            f.write("")
    except OSError as e:
        print("Error writing to %s.", const.TRACE_PIPE)
        print(e)
        return False

    # Enable duration tracing
    with open(const.TRACING_OPTIONS_FILE, "w") as f:
        f.write("funcgraph-duration")

    return True

def __parse_ftrace_trace() -> dict:
    # TODO : Ensure trace_options are set the right way
    func_durations = {func_name:[] for func_name in const.FTRACE_FILTERS}
    with open(const.TRACE_PIPE, "r") as f:
        lines = f.readlines()

        for l in lines:
            l = l.strip()

            for func_name in func_durations:
                if func_name in l:
                    try:
                        duration = float(l.split(' ')[2])
                    except ValueError as e:
                        print("ftrace options may be misconfigured, can't retrieve functions' duration.")
                        print("Line retrieved : %s" % l)
                        return None
                    func_durations[func_name].append(duration)


    return func_durations
    

def benchmark_jit_verifier(config: dict, do_compile=False) -> dict:
    """
        Will insert multiple times an eBPF program and retrieve functions' 
        durations.
    """
    config_bpf = config["bpf"]
    if not __setup_ftrace():
        print("Aborting, can't config ftrace...")
        return False

    returned_data = {
        "status": 0,
        "compile": 0.0,
        "insertion_total": [],
        "insertion_funcs" : None
    }

    if do_compile:
        t0 = time.time_ns()
        make_sp = subp.Popen(["make"], cwd=config_bpf["dir"], stdout=subp.PIPE)
        make_sp.wait()
        delta = (time.time_ns() - t0) / 1e+6

        if make_sp.returncode != 0:
            print("Error while invoking `make` in dir %s", config_bpf["dir"])
            returned_data["status"] = -1
            return returned_data
        returned_data["compile"] = delta

    bpf_abs_path = os.path.join(os.getcwd(), config_bpf["dir"],config_bpf["bpf_filename"])
    
    for i in range(const.TOTAL_INSERT_RUN):
        t0 = time.time_ns()
        loader_sb = subp.Popen(["./loader", bpf_abs_path], cwd="tools", stdout=subp.PIPE)
        loader_sb.wait()
        # Convert ns to ms
        returned_data["insertion_total"].append((time.time_ns() - t0) / 1e+6)

    durations = __parse_ftrace_trace()
    if durations is None:
        returned_data["status"] = -1
        return returned_data
    returned_data["insertion_funcs"] = durations

    all_values = []
    for func_name in durations: all_values += durations[func_name]
    min_val = min(all_values)
    
    if min_val == 0:
        min_val = -10
    else:
        min_val *= 0.8
    
    max_val = max(all_values) * 1.2

    save_path = plot_boxplot(values=durations, x_lim=(min_val, max_val), 
    title="Execution times of functions", show=True)

    print("Figure for insertion saved at %s" % save_path)

    return returned_data

"""
    eBPF benchmark
"""
def benchmark_bpf_execution(config: dict) -> dict:
    config_bpf = config["bpf"]

    returned_data = {
        "status": 0,
        "exec_times": []
    }
    
    bpf_abs_path = os.path.join(os.getcwd(), config_bpf["dir"],config_bpf["bpf_filename"])
    
    # r/w pipes used to communicate with the subprocess
    r_sub, w_sub = os.pipe()
    r_main, w_main = os.pipe()
    out_sub = os.fdopen(r_sub, 'r')
    in_sub = os.fdopen(w_main, 'w')
    pipe_read_name = "/tmp/%s" % ''.join(random.choice(string.ascii_lowercase) for i in range(10))
    pipe_write_name = "/tmp/%s" % ''.join(random.choice(string.ascii_lowercase) for i in range(10))
    # Load eBPF 
    loader_sb = subp.Popen(["./monitor-exec", config_bpf["bpf_filename"], pipe_read_name, pipe_write_name], cwd=config_bpf["dir"], stdout=os.fdopen(w_sub, 'w'), stdin=os.fdopen(r_main, 'r'))
    

    # Check if eBPF loading went OK
    
    try:
        value = out_sub.read(1)
        value = int(value[0])
    except ValueError as e:
        print("Error while reading loader output in eBPF loader")
        print(e)
        print(out_sub.read())
        returned_data["status"] = -1
        return returned_data
    
    if value < 0:
        print("Value returned by eBPF loader < 0")
        returned_data["status"] = -1
        return returned_data

    # Generate events to trigger eBPF program
    events_sb = subp.Popen(["sudo", "sh", config["tester"]])
    events_sb.wait()
    if events_sb.returncode != 0:
        print("Process running %s returned non-zero value : %s" % (config["tester"], events_sb.returncode))
        returned_data["status"] = -1
        return returned_data

    loader_sb.send_signal(signal.SIGCONT)
    
    in_sub.write("1")
    

    # Check if eBPF loading went OK
    
    try:
        value = int(out_sub.read())      
    except ValueError as e:
        print("Error while reading loader output in eBPF loader")
        print(e)
        returned_data["status"] = -1
        return returned_data
    
    if value != 1:
        print("There was an error while retrieving values in eBPF maps.")
        returned_data["status"] = -1
        return returned_data
    
    time_file_path = path.join(os.getcwd(), config_bpf["dir"], "time_values.csv")
    with open(time_file_path, "r") as f:
        lines = f.readlines()
        if len(lines) == 0:
            print("sssNo time values in file %s." % time_file_path)
            returned_data["status"] = -1
            return returned_data
        
        time_values = [int(x) for x in lines[0].split(',') if int(x) != 0]
        if len(time_values) <= 0:
            print("No time values in file %s." % time_file_path)
            returned_data["status"] = -1
            return returned_data

        returned_data["exec_times"] = time_values
    return returned_data


"""
    Linux modules related functions
"""
def benchmark_linux_module_ins(config: dict, do_compile=False) -> bool:
    # TODO : Chercher les fonctions qui pourraient être intéressantes à mesurer
    # lors de l'insertion d'un module
    module_config = config["module"]
    
    returned_data = {
        "status": 0,
        "compile": 0.0,
        "insertion_total": []
    }
    # Compile
    if do_compile:
        t0 = time.time_ns()
        make_sp = subp.Popen(["make"], cwd=module_config["dir"], stdout=subp.PIPE)
        make_sp.wait()
        returned_data["compile"] = (time.time_ns() - t0) / 1e+6

        if make_sp.returncode != 0:
            print("Error while invoking `make` in dir %s"% module_config["dir"])
            returned_data["status"] = -1
            return returned_data
        print("Module compilation took %s ms" % times["compile"])

    # Load module
    mod_file = module_config["name"]
    mod_name = ""
    if not mod_file.endswith(".ko"):
        mod_file += ".ko"

    mod_name = mod_file.split('.')[0]
    for i in range(const.TOTAL_INSERT_RUN):
        t0 = time.time_ns()
        loader_sp = subp.Popen(["insmod", mod_file], cwd=module_config["dir"], stdout=subp.PIPE)
        loader_sp.wait()
        returned_data["insertion_total"].append((time.time_ns() - t0) / 1e+6)
        
        if loader_sp.returncode != 0:
            print("There was an error while inserting module, can't retrieve values.")
            print("File : %s" % mod_file)
            returned_data["status"] = -1
            return returned_data

        

        rmmod_sb = subp.Popen(["rmmod", mod_name], stdout=subp.PIPE)
        rmmod_sb.wait()

        if rmmod_sb.returncode != 0:
            print("There was an error while removing module named %s" % mod_name)
            returned_data["status"] = -1
            return returned_data

    return returned_data


def benchmark_module_execution(config: dict) -> dict:
    mod_config = config["module"]

    returned_data = {
        "status": 0,
        "exec_times": []
    }

    mod_file = mod_config["name"]
    mod_name = ""
    if not mod_file.endswith(".ko"):
        mod_file += ".ko"

    mod_name = mod_file.split('.')[0]
    loader_sp = subp.Popen(["insmod", mod_file], cwd=mod_config["dir"], stdout=subp.PIPE)
    loader_sp.wait()

    if loader_sp.returncode != 0:
        print("An error ocurred while inserting module %s" % mod_config["name"])
        returned_data["status"] = -1
        return returned_data

    events_sb = subp.Popen(["sudo", "sh", config["tester"]])
    events_sb.wait()
    if events_sb.returncode != 0:
        print("Process running %s returned non-zero value : %s" % (config["tester"], events_sb.returncode))
        returned_data["status"] = -1
        return returned_data

    # Reading kobj
    kobj_path = path.join("/sys/kernel", mod_config["kobj_name"])
    with open(kobj_path, "r") as f:
        line = f.readline()
        values = line.split(',')
        if len(values) == 0:
            print("No values retrieved from kobject : %s" % kobj_path)
            returned_data["status"] = -1
            return returned_data

        returned_data["exec_times"] = [int(x) for x in values if x != 0]
    

    rmmod_sb = subp.Popen(["rmmod", mod_name], stdout=subp.PIPE)
    rmmod_sb.wait()

    if rmmod_sb.returncode != 0:
        print("There was an error while removing module named %s" % mod_name)
        returned_data["status"] = -1
        return returned_data

    
    return returned_data