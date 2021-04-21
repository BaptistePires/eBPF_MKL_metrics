from config_utils import *
from utils import benchmark_jit_verifier
from os import getgid, path, mkdir
from sys import argv
if getgid() != 0:
    print("Please run as sudo")

config_create = "--create_config" in argv or "-c" in argv

if config_create:
    generate_config_file()
    exit()

bench_loading = "--loading" in argv or "-l" in argv
bench_execution = "--execution" in argv or "-l" in argv

if not bench_loading and not bench_execution:
    print("Usage :")
    print("To get bpf loading functions duration use : '--loading' or '-l'")


config = get_config(only_bpf=True)

if config is None: exit()
if not check_config_dirs(config): exit()

if not path.exists("figures"):
    mkdir("figures")

print("Starting benchmark with config :", config, sep="\n")
benchmark_jit_verifier(config)