
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
with open("bpf/time_values.csv", "r") as f:
    values = [int(x) for x in f.readlines()[0].split(',')]
    
    mean = int(np.mean(values))
    print(mean)
    fig,ax = plt.subplots()

    plt.xlabel("execution index")
    plt.ylabel("time in ns")
    
    max_v, max_id = (max(values), values.index(max(values)))
    min_v, min_id = (min(values), values.index(min(values)))

    plt.axis([0, 100, 0, max(values) + max_v * 0.3])
    ax.boxplot(x=values,'ro', markersize=3, label="data")
    ax.plot([0, 100], [mean] * 2, linestyle='--', label="mean")
    ax.text(x=101, y=mean, s=str(mean))
    
    ax.plot(min_v, min_id, c="#FFFFFF")
    
    legend = ax.legend(loc='upper right')
    plt.savefig('test.png')
    plt.show()
    
