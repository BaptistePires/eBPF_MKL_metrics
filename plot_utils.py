from os import path
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import tempfile

from constants import FIGURES_DIR

"""
    JIT function
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
    
    df = pd.DataFrame.from_dict(values)
    # bp = sns.boxplot(x="Function nampe", y="Execution time (ms)", data=df)
    plt.title(title)
    boxplot = pd.DataFrame.boxplot(df)
    
    

    plt.xlabel("Function name")
    plt.ylabel("Execution time (ms)")
    
    
    title = title.replace(' ', '_') + '.png'
    save_path = path.join(FIGURES_DIR, title) 
    plt.savefig(save_path)
    if show: plt.show()
    return save_path
