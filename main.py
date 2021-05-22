from os import getgid, path, mkdir
from sys import argv

from plot_utils import plot_durations, plot_insmod_loadBPF, plot_module_vs_eBPF
from config_utils import *
from utils import activate_jit, benchmark_jit_verifier, benchmark_linux_module_ins, benchmark_bpf_execution, benchmark_module_execution, deactivate_jit
from time import sleep

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
    module_data = benchmark_linux_module_ins(config)
    if ebpf_data["status"] == 0:
        filepath = "out" + sep + "ebpf_values_loading.json"
        with open(filepath, "w") as f:
            json.dump(ebpf_data, f)
        print("ebpf data retrived saved at %s " % filepath)
        
    
    if module_data["status"] == 0:
        filepath = "out" + sep + "module_values_loading.json"
        with open(filepath, "w") as f:
            json.dump(module_data, f)
        print("module data retrived saved at %s " % filepath)

    if ebpf_data["status"] == 0 and module_data["status"] == 0:
        plot_insmod_loadBPF(module_data["insertion_total"], ebpf_data["insertion_total"])

if bench_execution:
    deactivate_jit()
    ebpf_data_nojit = benchmark_bpf_execution(config)
    if ebpf_data_nojit["status"] == 0:
        filepath = "out" + sep + "ebpf_interpreted_values_exec.json"
        with open(filepath, "w") as f:
            json.dump(ebpf_data_nojit, f)
        print("ebpf data retrived saved at %s " % filepath)
        plot_durations(ebpf_data_nojit["exec_times"], "eBPF", "eBPF (interpreted) overhead in ns", "out/ebpf_interpreted_durations.png")

    activate_jit()
    sleep(1)
    ebpf_data = benchmark_bpf_execution(config)
    if ebpf_data["status"] == 0:
        filepath = "out" + sep + "ebpf_values_exec.json"
        with open(filepath, "w") as f:
            json.dump(ebpf_data, f)
        print("ebpf data retrived saved at %s " % filepath)
        plot_durations(ebpf_data["exec_times"], "eBPF", "eBPF overhead in ns", "out/ebpf_durations.png")

    sleep(1)
    module_data = benchmark_module_execution(config)
    if module_data["status"] == 0:
        filepath = "out" + sep + "module_values_exec.json"
        with open(filepath, "w") as f:
            json.dump(module_data, f)
        print("module data retrived saved at %s " % filepath)
        plot_durations(module_data["exec_times"], "Linux Module", "Linux Module overhead in ns", "out/linux_module_durations.png")

    if ebpf_data["status"] == 0 and module_data["status"] == 0 and ebpf_data_nojit["status"] == 0:
        plot_module_vs_eBPF(module_data["exec_times"], ebpf_data["exec_times"], ebpf_data_nojit["exec_times"], "Linux Module vs eBPF overhead",
            "module_vs_ebpf_overhead_jit.png")

    if ebpf_data["status"] == 0 and module_data["status"] == 0 and ebpf_data_nojit["status"] == 0:
        plot_module_vs_eBPF(module_data["exec_times"], ebpf_data["exec_times"], None, "Linux Module vs eBPF overhead", "module_vs_ebpf_overhead.png")

if bench_execution:
    print("execution benchmark")