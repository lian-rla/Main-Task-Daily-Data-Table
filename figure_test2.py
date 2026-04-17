import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

file_path = "E:/T-maze/49/main_task/10_Rat49_VSM.csv"
df = pd.read_csv(file_path)

skip_cols = ['TrialCorrection', 'TrialRepetition', 'TrialVoid', 'TrialSkipped']
for col in skip_cols:
    if col in df.columns:
        df[col] = df[col].astype(str).str.upper() 
        df = df[df[col] != 'YES']                   

df['Alpha'] = df['Latency_stbox']
df['Beta'] = df['Latency_inter'] - df['Latency_stbox']
df['Gamma'] = df['Latency'] - df['Latency_inter']

plt.figure(figsize=(7, 5))
box_positions = [1, 2, 3]

plt.boxplot([df['Alpha'], df['Beta'], df['Gamma']],
            positions=box_positions, widths=0.3, patch_artist=True,
            boxprops=dict(facecolor="lightgray", color="black"),
            medianprops=dict(color="black"),
            whiskerprops=dict(color="black", linewidth=1.2),
            capprops=dict(color="black", linewidth=1.2),
            flierprops=dict(marker='', alpha=0))

for idx, row in df.iterrows():
    values = [row['Alpha'], row['Beta'], row['Gamma']]
    max_index = np.argmax(values)         
    x_pos = max_index + 1                 
    y_pos = values[max_index]             
    x_jitter = np.random.normal(x_pos, 0.05)  
    plt.scatter(x_jitter, y_pos, color='yellow', edgecolors='black',
                s=30, alpha=0.9, zorder=3)   

plt.xticks([1, 2, 3], ['Alpha', 'Beta', 'Gamma'])
plt.ylabel("Latency")
plt.ylim(0, 8)
plt.title("Latency Section")
plt.grid(False)

plt.tight_layout()
plt.show()
