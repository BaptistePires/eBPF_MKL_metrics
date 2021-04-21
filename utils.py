import os
import constants as const
from plot_utils import *
import subprocess as subp


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
    

def benchmark_jit_verifier(config: dict) -> bool:
    """
        Will insert multiple times an eBPF program and retrieve functions' 
        durations.
    """
    config_bpf = config["bpf"]
    if not __setup_ftrace():
        print("Aborting, can't config ftrace...")
        return False

    make_sp = subp.Popen(["make"], cwd=config_bpf["dir"])
    
    make_sp.wait()
    if make_sp.returncode != 0:
        print("Error while invoking `make` in dir %s", config_bpf["dir"])
        return False
    
    bpf_abs_path = os.path.join(config_bpf["dir"],config_bpf["bpf_filename"])
    
    for i in range(const.TOTAL_INSERT_RUN):
        loader_sb = subp.Popen(["./loader", bpf_abs_path], cwd="tools")
        loader_sb.wait()

    durations = __parse_ftrace_trace()
    if durations is None:
        return False

    all_values = []
    for func_name in durations: all_values += durations[func_name]
    min_val = min(all_values)
    
    if min_val == 0:
        min_val = -10
    else:
        print("mint_val", min_val)
        min_val *= 0.8
    
    max_val = max(all_values) * 1.2

    save_path = plot_boxplot(values=durations, x_lim=(min_val, max_val), 
    title="Execution times of functions", show=True)

    print("Figure for insertion saved at %s" % save_path)

    
    

