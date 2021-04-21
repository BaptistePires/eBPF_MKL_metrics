CONFIG_FILENAME = "config.json"
BASE_CONFIG = {
    "bpf":{
        "dir": ""
    },
    "module": {
        "dir": ""
    }
}
REQUIRED_CONFIG_DEF = {"bpf":["dir"], "module": ["dir"]}

TMP_DIR = "tmp"
FIGURES_DIR = "figures"
OUT_BPF_FILENAME = "out.o"

TRACING_FS = "/sys/kernel/tracing"
CURRENT_TRACER = TRACING_FS + "/current_tracer"
AVAILABLE_TRACERS = TRACING_FS + "/available_tracers"
AVAILABLE_EVENTS = TRACING_FS + "/available_events"
AVAILABLE_FILTER_FUNCS = TRACING_FS + "/available_filter_functions"
TRACING_OPTIONS_FILE = TRACING_FS + "/trace_options"
TRACE_PIPE = TRACING_FS + "/trace"
FTRACE_FILTERS = ["bpf_check", "bpf_int_jit_compile"]

SET_FTRACE_PID = TRACING_FS + "/set_ftrace_pid"
SET_FTRACE_FILTER = TRACING_FS + "/set_ftrace_filter"
BPF_JIT_ENABLE = "/proc/sys/net/core/bpf_jit_enable"



OUTPUT_FILE_FIGURE = "time_exec.png"
GRAPH_TRACER = "function_graph"
MAKE = ["make"]
MAKE_CLEAN = ["make", "clean"]
TOTAL_INSERT_RUN = 100