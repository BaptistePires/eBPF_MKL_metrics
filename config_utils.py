import json
from constants import CONFIG_FILENAME, REQUIRED_CONFIG_DEF, BASE_CONFIG
from os import path, sep, getcwd

def generate_config_file():
    """
        Generate default config file.
    """
    if path.exists(CONFIG_FILENAME):
        u_input = None
        while u_input not in ["y", "n"]:
            u_input = input("Config file exists, override ?")
        
        if u_input == "n": return 

    file_path = path.join(getcwd(), CONFIG_FILENAME)
    with open(file_path, "w") as f:
        json.dump(BASE_CONFIG, f)

    
    print("New config file saved at : %s" % file_path)

def get_config(only_bpf=False) -> dict:
    """
        Load config file from config.json and returns it as a dict.
    """
    config = None
    try:
        with open(CONFIG_FILENAME, "r") as config_file:
            config = json.load(config_file)        
    except FileNotFoundError as e:
        print("You need to provide config file named config.json.")

    except json.JSONDecodeError as e:
        print("There was an error while reading config.json, please make sure it's formatted properly.")

    except Exception as e:
        print("An error occured while reading config file.")
        print("Please check that you own the file")

    if config is None: return config

    all_keys = True
    missing_keys = []
    for conf_key in REQUIRED_CONFIG_DEF:
        
        # Missing main key 
        if conf_key not in config.keys():
            
            all_keys = False
            missing_keys.append(conf_key)
        else:
            # Check for inner keys
            for inner_key in REQUIRED_CONFIG_DEF[conf_key]:
                if inner_key not in config[conf_key].keys():
                    all_keys = False
                    missing_keys.append("{%s : %s}" % (conf_key, inner_key))
        

    if not all_keys:
        print("(%s), are missing in your config file." % missing_keys)
        config = None

    return config


def check_config_dirs(config: dict) -> bool:
    """ 
        Check that config directories exist and contains tools to compile
        files.
    """

    # eBPF
    bpf_conf = config["bpf"]
    if not path.exists(bpf_conf["dir"]):
        print("Dir %s doesn't exist." % bpf_conf["dir"])
        return False
    
    if not path.exists(bpf_conf["dir"] + sep + "Makefile"):
        print("eBPF Makefile is missing.")
        return False
    
    ebpf_file = path.exists(path.join(bpf_conf["dir"], bpf_conf["bpf_filename"]))
    if not ebpf_file:
        print("eBPF File not found %s" % ebpf_file)
        return False

    # Linux moodule
    mod_conf = config["module"]
    if not path.exists(mod_conf["dir"]):
        print("Dir %s doesn't exist." % mod_conf["dir"])
        return False
    
    if not path.exists(mod_conf["dir"] + sep + "Makefile"):
        print("Linux module Makefile is missing.")
        return False
    
    return True