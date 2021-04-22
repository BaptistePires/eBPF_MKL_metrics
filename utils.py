import os
import constants as const
from plot_utils import *
import subprocess as subp
import time


"""
    JIT & Verifier benchmarks
"""

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

    

    
    
    

    return True