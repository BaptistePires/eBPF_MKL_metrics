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
    
    

    df = pd.DataFrame(values)
    # bp = sns.boxplot(x="Function nampe", y="Execution time (ms)", data=df)
    plt.title(title)
    # boxplot = pd.DataFrame.boxplot(df)
    ax = sns.boxplot(data=df, width=0.5,boxprops={'facecolor':'None'},)
    ax2 = sns.swarmplot(data=df, s=4, zorder=.5) 
    
    
    y_ticks = []
    

    plt.xlabel("Function name")
    plt.ylabel("Execution time (ms)")
    
    
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