from config_utils import *
from utils import benchmark_jit_verifier, benchmark_linux_module_ins, benchmark_bpf_execution
from os import getgid, path, mkdir
from sys import argv

if getgid() != 0:
    print("Please run as sudo")

config_create = "--create_config" in argv or "-c" in argv

if config_create:
    generate_config_file()
    exit()

bench_loading = "--loading" in argv or "-l" in argv
bench_execution = "--execution" in argv or "-e" in argv


if not bench_loading and not bench_execution:
    print("Usage :")
    print("To benchmark eBPF and module loading use --loading or -l")
    print("To benchmark eBPF and module execution time use --execution or -e")
    exit()

config = get_config()

if config is None: exit()
# if not check_config_dirs(config): exit()

if not path.exists("figures"):
    mkdir("figures")

if not path.exists("out"):
    mkdir("out")

print("Starting benchmark with config :", config, sep="\n")
if bench_loading:
    ebpf_data = benchmark_jit_verifier(config)
    if ebpf_data["status"] == 0:
        filepath = "out" + sep + "ebpf_values_loading.json"
        with open(filepath, "w") as f:
            json.dump(ebpf_data, f)
        print("ebpf data retrived saved at %s " % filepath)
        
    module_data = benchmark_linux_module_ins(config)
    if module_data["status"] == 0:
        filepath = "out" + sep + "module_values_loading.json"
        with open(filepath, "w") as f:
            json.dump(module_data, f)
        print("module data retrived saved at %s " % filepath)

if bench_execution:
    ebpf_data = benchmark_bpf_execution(config)
    if ebpf_data["status"] == 0:
        filepath = "out" + sep + "ebpf_values_exec.json"
        with open(filepath, "w") as f:
            json.dump(ebpf_data, f)
        print("ebpf data retrived saved at %s " % filepath)

if bench_execution:
    print("execution benchmark")