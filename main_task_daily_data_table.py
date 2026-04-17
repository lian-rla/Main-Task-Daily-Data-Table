import os, glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.gridspec as gridspec

import tkinter as tk
from tkinter import filedialog, messagebox

def select_folder():
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    folder = filedialog.askdirectory(title="분석할 메인 폴더를 선택하세요 (예: .../T-maze/50/main_task/)")
    root.destroy()
    if not folder:
        raise SystemExit("폴더 선택이 취소되어 프로그램을 종료합니다.")
    return folder

class InputDialog(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("T-maze Main Task Figure Program")
        self.geometry("360x220")
        self.resizable(False, False)

        row = 0
        tk.Label(self, text="LE :").grid(row=row, column=0, sticky="e", padx=10, pady=8)
        self.le_var = tk.StringVar()
        tk.Entry(self, textvariable=self.le_var).grid(row=row, column=1, sticky="we", padx=10, pady=8)

        row += 1
        tk.Label(self, text="Current weight:").grid(row=row, column=0, sticky="e", padx=10, pady=8)
        self.weight_var = tk.StringVar()
        tk.Entry(self, textvariable=self.weight_var).grid(row=row, column=1, sticky="we", padx=10, pady=8)

        row += 1
        tk.Label(self, text="change weight:").grid(row=row, column=0, sticky="e", padx=10, pady=8)
        self.change_var = tk.StringVar()
        tk.Entry(self, textvariable=self.change_var).grid(row=row, column=1, sticky="we", padx=10, pady=8)

        row += 1
        tk.Label(self, text="Pellet:").grid(row=row, column=0, sticky="e", padx=10, pady=8)
        self.pellet_var = tk.StringVar()
        tk.Entry(self, textvariable=self.pellet_var).grid(row=row, column=1, sticky="we", padx=10, pady=8)

        row += 1
        tk.Label(self, text="Day:").grid(row=row, column=0, sticky="e", padx=10, pady=8)
        self.day_var = tk.StringVar()
        tk.Entry(self, textvariable=self.day_var).grid(row=row, column=1, sticky="we", padx=10, pady=8)

        row += 1
        btn = tk.Button(self, text="확인", command=self.on_submit)
        btn.grid(row=row, column=0, columnspan=2, pady=12)

        self.result = None
        self.columnconfigure(1, weight=1)
        self.attributes('-topmost', True)

    def on_submit(self):
        le = self.le_var.get().strip()
        weight = self.weight_var.get().strip()
        change = self.change_var.get().strip()
        pellet = self.pellet_var.get().strip()
        day = self.day_var.get().strip()

        if not le:
            messagebox.showerror("입력 오류", "LE 값을 입력해 주세요.")
            return

        try:
            le_int = int(le)
        except ValueError:
            le_int = None

        self.result = {
            "LE": le,
            "LE_int": le_int,
            "weight": weight,
            "change weight": change, 
            "pellet": pellet,
            "day": day,
        }
        self.destroy()

def get_user_inputs():
    app = InputDialog()
    app.mainloop()
    if app.result is None:
        raise SystemExit("입력이 취소되어 프로그램을 종료합니다.")
    return app.result

def filter_skipped(df):
    skip_cols = ['TrialCorrection', 'TrialRepetition', 'TrialVoid', 'TrialSkipped']
    for col in skip_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.upper()
            df = df[df[col] != 'YES']
    return df

def draw_figure_test2(ax, csv_file):
    df = pd.read_csv(csv_file)
    df = filter_skipped(df)
    df['Alpha'] = pd.to_numeric(df['Latency_stbox'], errors='coerce')
    df['Beta']  = pd.to_numeric(df['Latency_inter'], errors='coerce') - df['Alpha']
    df['Gamma'] = pd.to_numeric(df['Latency'], errors='coerce') - pd.to_numeric(df['Latency_inter'], errors='coerce')

    ax.boxplot([df['Alpha'], df['Beta'], df['Gamma']],
               positions=[1, 2, 3], widths=0.2, patch_artist=True,
               boxprops=dict(facecolor="lightgray", color="black"),
               medianprops=dict(color="black"),
               whiskerprops=dict(color="black"),
               capprops=dict(color="black"),
               flierprops=dict(marker='', alpha=0))

    for _, row in df[['Alpha','Beta','Gamma']].iterrows():
        vals = [row['Alpha'], row['Beta'], row['Gamma']]
        if not np.isfinite(vals).all():
            continue
        max_index = int(np.nanargmax(vals))
        y_val = vals[max_index]
        x_jitter = np.random.normal(max_index + 1, 0.05)
        ax.scatter(x_jitter, y_val, color='yellow', edgecolors='black', s=30, zorder=3)

    ax.set_xticks([1, 2, 3])
    ax.set_xticklabels(['Alpha', 'Beta', 'Gamma'])
    ax.set_ylim(0, 6)
    ax.set_ylabel("Latency")
    ax.set_xlabel("Sections")
    ax.set_title("Latency Distribution (Section)")

def draw_stacked_ratio(ax, df_latest_sorted, legend_x=0.2, legend_y=-0.12):
    alpha = pd.to_numeric(df_latest_sorted['Latency_stbox'], errors='coerce')
    beta  = pd.to_numeric(df_latest_sorted['Latency_inter'], errors='coerce') - alpha
    gamma = pd.to_numeric(df_latest_sorted['Latency'], errors='coerce') - pd.to_numeric(df_latest_sorted['Latency_inter'], errors='coerce')

    total = alpha + beta + gamma
    valid = total > 0
    trials = df_latest_sorted.loc[valid, 'Trial#'].astype(int).values
    a_ratio = (alpha[valid] / total[valid]).values
    b_ratio = (beta[valid]  / total[valid]).values
    g_ratio = (gamma[valid] / total[valid]).values

    ax.bar(trials, a_ratio, color='#F39C12', label='Alpha (α)')
    ax.bar(trials, b_ratio, bottom=a_ratio, color='#27AE60', label='Beta (β)')
    ax.bar(trials, g_ratio, bottom=a_ratio + b_ratio, color='#1DA1F2', label='Gamma (γ)')

    ax.set_ylim(0, 1.0)
    ax.set_ylabel("Proportion")
    ax.set_xlabel("Trial", labelpad=24)
    ax.set_title("Section Proportion Trial")
    ax.legend(loc='upper center', bbox_to_anchor=(legend_x, legend_y), ncol=3, frameon=True)

def main():
    folder_path = select_folder()
    ui = get_user_inputs()
    le_str = ui["LE"]
    le_int = ui["LE_int"]
    weight_str = ui["weight"]
    change_str = ui["change weight"]
    pellet_str = ui["pellet"]
    day_str = ui["day"]

    csv_files = glob.glob(os.path.join(folder_path, "*_Rat*_VSM.csv"))
    if not csv_files:
        raise SystemExit("선택한 폴더에 *_Rat*_VSM.csv 파일이 없습니다.")

    latest_file = max(csv_files, key=lambda f: int(os.path.basename(f).split("_")[0]))
    df_latest = pd.read_csv(latest_file)
    df_latest = filter_skipped(df_latest)
    df_latest['Trial#'] = df_latest['Trial#'].astype(str).str.extract(r'(\d+)')
    df_latest = df_latest.dropna(subset=['Trial#'])
    df_latest['Trial#'] = df_latest['Trial#'].astype(int)
    df_latest['Direction'] = df_latest['Direction'].astype(str).str.lower()
    df_latest['Correctness'] = df_latest['Correctness'].astype(str).str.upper()
    df_latest['Scene'] = df_latest['Scene'].astype(str).str.lower()
    df_latest['Latency'] = pd.to_numeric(df_latest['Latency'], errors='coerce')

    left_ratio = (df_latest['Direction'] == 'left').mean() * 100
    right_ratio = (df_latest['Direction'] == 'right').mean() * 100
    accuracy_latest = (df_latest['Correctness'] == 'CORRECT').mean() * 100

    scene_days, zebra_ratio, pebble_ratio = [], [], []
    days, trial_counts, norm_metric, accuracy_list, latency_list = [], [], [], [], []

    for file in csv_files:
        df = pd.read_csv(file)
        df = filter_skipped(df)
        df['Trial#'] = df['Trial#'].astype(str).str.extract(r'(\d+)')
        df = df.dropna(subset=['Trial#'])
        df['Trial#'] = df['Trial#'].astype(int)
        df['Direction'] = df['Direction'].astype(str).str.lower()
        df['Correctness'] = df['Correctness'].astype(str).str.upper()
        df['Scene'] = df['Scene'].astype(str).str.lower()
        df['Latency'] = pd.to_numeric(df['Latency'], errors='coerce')

        day = int(os.path.basename(file).split("_")[0])
        zebra_df = df[df['Scene'] == 'zebra']
        pebble_df = df[df['Scene'] == 'pebbles']
        scene_days.append(day)
        zebra_ratio.append((zebra_df['Correctness'] == 'CORRECT').mean() if len(zebra_df) else np.nan)
        pebble_ratio.append((pebble_df['Correctness'] == 'CORRECT').mean() if len(pebble_df) else np.nan)

        days.append(day)
        trial_counts.append(len(df))
        norm_metric.append(abs((df['Direction'] == 'right').sum() - (df['Direction'] == 'left').sum()) / len(df) if len(df) else 0)
        accuracy_list.append((df['Correctness'] == 'CORRECT').mean())

        for _, row in df.dropna(subset=['Latency']).iterrows():
            latency_list.append({"Day": day, "Latency": row['Latency'], "Correctness": row['Correctness']})

    df_scene_ratio = pd.DataFrame({"Day": scene_days, "Zebra": zebra_ratio, "Pebbles": pebble_ratio}).sort_values("Day")
    df_trials = pd.DataFrame({"Day": days, "TotalTrials": trial_counts}).sort_values("Day")
    df_metric = pd.DataFrame({"Day": days, "NormDiff": norm_metric, "Accuracy": accuracy_list}).sort_values("Day")
    df_latency_all = pd.DataFrame(latency_list)

    if le_int == 49:
        comp = "(reward vs no reward)"
    elif le_int == 50:
        comp = "(reward vs quinine)"
    else:
        comp = "(reward comparison)"

    main_title = f"LE{le_str} {comp} Summary"

    fig = plt.figure(figsize=(18, 13))
    gs_main = gridspec.GridSpec(3, 1, figure=fig, height_ratios=[1.0, 1.05, 0.85])
    fig.suptitle(main_title, fontsize=15, fontweight="bold")

    meta_text = "  |  ".join([
        f"Current weight: {weight_str}g" if weight_str else "Current weight: -",
        f"Change weight: {change_str}g" if change_str else "change weight: -",
        f"Pellet: {pellet_str}g" if pellet_str else "Pellet: -",
        f"Day: {day_str}" if day_str else "Day: -",
    ])
    fig.text(0.995, 0.985, meta_text, ha='right', va='top', fontsize=10)

    gs_row1 = gridspec.GridSpecFromSubplotSpec(1, 2, subplot_spec=gs_main[0], width_ratios=[1, 1])
    gs_fig1 = gridspec.GridSpecFromSubplotSpec(2, 1, subplot_spec=gs_row1[0], height_ratios=[3, 1])
    ax1_line = fig.add_subplot(gs_fig1[0])
    ax1_dots = fig.add_subplot(gs_fig1[1], sharex=ax1_line)

    ax1_line.plot(df_latest['Trial#'], df_latest['Latency'], marker='o', color='black', markersize=3)
    ax1_line.set_title("Latency Trial")
    ax1_line.set_ylabel("Latency")
    ax1_line.set_ylim(0, max(15, np.nanmax(df_latest['Latency']) * 1.1))

    ax1_dots.set_xlabel("Trial")
    for _, r in df_latest.iterrows():
        face_color = 'blue' if r['Direction'] == 'left' else 'red'
        y_pos = 0.08 if r['Direction'] == 'left' else 0.02
        if r['Scene'] == 'zebra':
            edge_color, lw = 'black', 1.5
        else:
            edge_color, lw = face_color, 0
        ax1_dots.scatter(r['Trial#'], y_pos, marker='o', color=face_color, edgecolors=edge_color, linewidths=lw, s=28, zorder=3)
    ax1_dots.set_ylim(0, 0.1)
    ax1_dots.set_yticks([])
    ax1_dots.text(1.02, 0.90, f"Right: {right_ratio:.1f}%", transform=ax1_dots.transAxes, fontsize=8)
    ax1_dots.text(1.02, 0.72, f"Left: {left_ratio:.1f}%", transform=ax1_dots.transAxes, fontsize=8)
    ax1_dots.text(1.02, 0.52, "Red: Right (Down)\nBlue: Left (Up)\nBlack edge: Zebra",
                  transform=ax1_dots.transAxes, fontsize=8, va='top',
                  bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.3'))

    ax46_left = fig.add_subplot(gs_row1[1])
    ax46_right = ax46_left.twinx()
    line4, = ax46_left.plot(df_trials["Day"], df_trials["TotalTrials"], marker="o", color="black", label="Total Trials")
    ax46_left.set_title("Total Trials & Choice Bias")
    ax46_left.set_xlabel("Day")
    ax46_left.set_ylabel("Total Trials")
    if len(df_trials):
        ymin = max(0, np.nanmin(df_trials["TotalTrials"]) - 2)
        ymax = np.nanmax(df_trials["TotalTrials"]) + 2
        ax46_left.set_ylim(0, 50)
    line6, = ax46_right.plot(df_metric["Day"], df_metric["NormDiff"], marker="o", color="crimson",
                             linestyle="--", label="Choice Bias")
    ax46_right.set_ylabel("Bias Ratio")
    ax46_right.set_ylim(0, 1)
    all_days = sorted(set(df_trials["Day"]).union(set(df_metric["Day"])))
    ax46_left.set_xticks(all_days)
    ax46_left.legend([line4, line6], [line4.get_label(), line6.get_label()], loc="upper right", frameon=True)

    gs_row2 = gridspec.GridSpecFromSubplotSpec(1, 2, subplot_spec=gs_main[1], width_ratios=[0.65, 0.35])
    ax5 = fig.add_subplot(gs_row2[0])
    ax5.plot(df_metric["Day"], df_metric["Accuracy"], marker="o", color="blue", label="Total Correctness")
    ax5.plot(df_scene_ratio["Day"], df_scene_ratio["Zebra"], marker="o", color="green", label="Zebra scene")
    ax5.plot(df_scene_ratio["Day"], df_scene_ratio["Pebbles"], marker="o", color="orange", label="Pebbles scene")
    ax5.axhline(0.75, color="red", linestyle="--", label="Criterion")
    ax5.set_ylim(0, 1)
    ax5.set_title("Scene Correctness Days")
    ax5.set_xlabel("Day")
    ax5.set_ylabel("Correctness")
    ax5.legend()
    ax5.text(0.80, 1.05, f"Accuracy: {accuracy_latest:.1f}%", transform=ax5.transAxes, fontsize=9)

    ax7 = fig.add_subplot(gs_row2[1])
    sns.boxplot(x="Day", y="Latency", data=df_latency_all, width=0.2, showcaps=True, showfliers=False,
                boxprops=dict(alpha=0.5, facecolor="gray"), ax=ax7)
    sns.stripplot(x="Day", y="Latency", data=df_latency_all[df_latency_all['Correctness'] == 'CORRECT'],
                  color="blue", size=3, jitter=True, alpha=0.6, ax=ax7)
    sns.stripplot(x="Day", y="Latency", data=df_latency_all[df_latency_all['Correctness'] == 'WRONG'],
                  color="red", size=3, jitter=True, alpha=0.6, ax=ax7)
    ax7.set_title("Latency Distribution")
    ax7.set_xlabel("Day")
    ax7.set_ylabel("Latency")
    ax7.set_ylim(0, 50)

    gs_row3 = gridspec.GridSpecFromSubplotSpec(1, 2, subplot_spec=gs_main[2], width_ratios=[0.65, 0.35])
    ax_stack = fig.add_subplot(gs_row3[0])
    df_latest_sorted = df_latest.sort_values('Trial#').reset_index(drop=True)
    draw_stacked_ratio(ax_stack, df_latest_sorted, legend_x=0.2, legend_y=-0.12)

    ax9 = fig.add_subplot(gs_row3[1])
    draw_figure_test2(ax9, latest_file)

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.show()

if __name__ == "__main__":
    main()
