from os import path
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt

import numpy as np
import tempfile

from constants import FIGURES_DIR


"""
    Stats functions
"""
def remove_outliers(arr):
    mean = np.mean(arr)
    std_dev = np.std(arr)
    mean_dst = abs(arr - mean)
    max_dev = 2
    not_outlier = mean_dst < max_dev * std_dev
    return arr[not_outlier]




"""
    Plot functions
"""
def generate_figure(output_name:str):
    with open("bpf/time_values.csv", "r") as f:
        lines = f.readlines()
        if len(lines) <= 0: return
        
        values = [int(x) for x in lines[0].split(',')]
        
        mean = int(np.mean(values))
        print(mean)
        fig,ax = plt.subplots()

        plt.xlabel("execution index")
        plt.ylabel("time in ns")
        
        max_v, max_id = (max(values), values.index(max(values)))
        min_v, min_id = (min(values), values.index(min(values)))
        
        ax.plot(values,'ro', markersize=3, label="data")
        ax.plot([0, 100], [mean] * 2, linestyle='--', label="mean")
        ax.text(x=101, y=mean, s=str(mean))        
        legend = ax.legend(loc='upper right')
        plt.savefig(output_name)
        # print("Saved figure at %s" % output_name)
        # plt.show()
        # plt.axis([0, 100, 0, max(values) + max_v * 0.3])
        # # ax.boxplot(x=values,'ro', markersize=3, label="data")
        # ax.plot([0, 100], [mean] * 2, linestyle='--', label="mean")
        # ax.text(x=101, y=mean, s=str(mean))
        
        # ax.plot(min_v, min_id, c="#FFFFFF")
        
        # legend = ax.legend(loc='upper right')
        
        # legend = ax.legend(loc='upper right')
        # plt.savefig(output_name)
        # # plt.show()
        # print("Generated figure at %s" % output_name)
       
def plot_boxplot(values, x_lim, title, show=False) -> str:
    if len(values) == 0:
        return None
    
    

    sns.set_style("darkgrid")
    df = pd.DataFrame(values)
    # bp = sns.boxplot(x="Function nampe", y="Execution time (ms)", data=df)
    plt.title(title)
    # boxplot = pd.DataFrame.boxplot(df)
    ax = sns.boxplot(data=df, width=0.5,boxprops={'facecolor':'None'},)
    ax2 = sns.swarmplot(data=df, s=4, zorder=.5) 
    
                                        
    y_ticks = [min(values["bpf_check"]), min(values["bpf_int_jit_compile"])]
    

    plt.xlabel("Function name")
    plt.ylabel("Execution time (µs)")
    
    
    title = title.replace(' ', '_') + '.png'
    save_path = path.join("out", title) 
    plt.savefig(save_path)
    if show: plt.show()
    return save_path

def plot_durations(durations: list, label: str, title: str, filename: str):
    if len(durations) == 0:
        print("duratoins array has a 0 size")
        return

    plt.cla()
    plt.clf()
    sns.set_style("darkgrid")
    
    durations = np.array(durations)
    durations = remove_outliers(durations)
    max_value = max(durations)
    min_value = min(durations)

    data_dict = {
        label: durations
    }

    delta = (max_value - min_value) // 10
    y_ticks = [min_value+delta*i for i in range(11)]
    y_ticks.insert(0, min_value)
    y_ticks.append(max_value)

    df = pd.DataFrame(data_dict)

    ax = sns.swarmplot(data=df, s=4)
    ax2 = sns.boxplot(data=df, boxprops={'facecolor':'None'}, width=0.3)
    ax.set_yticks(y_ticks)
    plt.title(title)
    plt.savefig(filename)

def plot_insmod_loadBPF(insmod_values: list, loadBPF_values: list):
    sns.set_style("darkgrid")
    data_dict = {
        "insmod":remove_outliers(np.array(insmod_values)),
        "insert eBPF": remove_outliers(np.array(loadBPF_values))
    }

    min_len = min(len(data_dict["insmod"]), len(data_dict["insert eBPF"]))
    data_dict["insmod"] = data_dict["insmod"][:min_len]
    data_dict["insert eBPF"] = data_dict["insert eBPF"][:min_len]

    plt.cla()
    plt.clf()
    df = pd.DataFrame((data_dict))

    ax = sns.boxplot(data=df, width=0.5,boxprops={'facecolor':'None'},)
    ax2 = sns.swarmplot(data=df, s=4, zorder=.5) 
    plt.xlabel("Loader")
    plt.ylabel("Total insertion time in ms")

    plt.title("Loading time (ms): insmod vs eBPF loader")
    plt.show()
    plt.savefig("out/insmod_vs_ebpf.png")

def plot_module_vs_eBPF(mod_values:list, bpf_values: list, title: str):

    mod_values = remove_outliers(np.array(mod_values))
    bpf_values = remove_outliers(np.array(bpf_values))
    min_len = min(len(mod_values), len(bpf_values))
    if min_len == 0:
        print("Can't generate figure for module vs eBPF")
        return


    plt.cla()
    plt.clf()
    sns.set_style("darkgrid")
    
    mod_values = np.array(mod_values[:min_len])
    bpf_values = np.array(bpf_values[:min_len])
    data_dict = {
        "Linux Module": mod_values,
        "eBPF Program": bpf_values
    }

    y_ticks = []
    min_val = min(mod_values.min(), bpf_values.min())
    max_val = max(mod_values.max(), bpf_values.max())
    y_ticks.append(min_val)
    y_ticks.append(max_val)
    # y_ticks.append([x for x in np.quantile(mod_values, q=[0.25, 0.5, 0.75])])
    # y_ticks.append([x for x in np.quantile(bpf_values, q=[0.25, 0.5, 0.75])])

    delta = (max_val - min_val) // 10
    
    y_ticks.append(np.median(mod_values))
    y_ticks.append(np.median(bpf_values))
    
    for i in range(10): 
        y_ticks.append(min_val + (i * delta))
        
    df = pd.DataFrame(data_dict)
    ax = sns.boxplot(data=df, width=0.3,boxprops={'facecolor':'None'},)
    ax2 = sns.swarmplot(data=df, s=4, zorder=.5)
    
    # Le min n'est peut être pas intéressant à afficher
    # Afficher le max permet, si la seule valeur extrême est celle à l'index 0
    # De montrer que ça vient problablement d'un cache miss
    plt.text(0.2, max(mod_values), ','.join([str(x) for i,x in enumerate(sorted(np.where(mod_values == max(mod_values))[0])) if i < 3]))

    plt.text(1.2, max(bpf_values), ','.join([str(x) for i,x in enumerate(sorted(np.where(bpf_values == max(bpf_values)))[0]) if i < 3]))
    ax.set_yticks(y_ticks)  
    plt.xlabel("Program")
    plt.ylabel("Execution time in ns")
    plt.title(title)
    plt.savefig("out/module_vs_ebpf_overhead.png")