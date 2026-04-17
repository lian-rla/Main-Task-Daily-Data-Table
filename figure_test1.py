import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

file_path = "E:/T-maze/49/main_task/10_Rat49_VSM.csv"
df = pd.read_csv(file_path)

skip_cols = ['TrialCorrection', 'TrialRepetition', 'TrialVoid', 'TrialSkipped']
for col in skip_cols:
    if col in df.columns:
        df[col] = df[col].astype(str).str.upper()
        df = df[df[col] != 'YES']

correct_trials = df[df['Correctness'].astype(str).str.upper() == 'CORRECT'].index.to_numpy()

alpha = df['Latency_stbox'].values
beta = (df['Latency_inter'] - df['Latency_stbox']).values
gamma = (df['Latency'] - df['Latency_inter']).values

trials = len(df)
data = np.vstack([alpha, beta, gamma]).T

emphasized = np.zeros_like(data, dtype=float)
for i in range(trials):
    row = data[i]
    row_min, row_max = np.min(row), np.max(row)
    emphasized[i] = (row - row_min) / (row_max - row_min) if row_max - row_min > 1e-9 else 0.0

heatmap_matrix = np.zeros((trials, 3))
heatmap_matrix[:, 0] = emphasized[:, 0]
heatmap_matrix[:, 1] = emphasized[:, 1]
heatmap_matrix[:, 2] = emphasized[:, 2]

masked_heatmap = np.ma.masked_where(heatmap_matrix == 0, heatmap_matrix)


cmap = mcolors.LinearSegmentedColormap.from_list(
    "custom_purple_blue_yellow", ["#220044", "#00ccff", "#ffff00"]
)
cmap.set_bad(color="#220044")


fig, ax = plt.subplots(figsize=(10, 5))
im = ax.imshow(masked_heatmap, aspect=0.1, cmap=cmap, origin='lower', vmin=0, vmax=1)
ax.set_xlim(-0.5, 2.5)
ax.set_xticks([0, 1, 2])
ax.set_xticklabels(['Alpha', 'Beta', 'Gamma'])
ax.set_yticks([0, trials - 1])
ax.set_yticklabels([1, trials])
ax.set_xlabel('Sections')
ax.set_ylabel('Trials')
ax.set_title('Section Latency')

cbar = plt.colorbar(im, ax=ax, label='Intensity (0~1)')


bbox_ax = ax.get_position()      
bbox_cb = cbar.ax.get_position() 
mid_x = (bbox_ax.x1 + bbox_cb.x0) / 2  


ax2 = fig.add_axes([mid_x - 0.005, bbox_ax.y0, 0.01, bbox_ax.height])  
ax2.set_ylim(0, trials - 1)
ax2.set_xlim(0, 1)
ax2.axis('off') 


for t in correct_trials:
    ax2.plot(0.5, t, '*', color='blue', markersize=4)

plt.show()
