import os, glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.gridspec as gridspec

# --- GUI (tkinter) ---
import tkinter as tk
from tkinter import filedialog, messagebox

# =======================
# 1) 폴더 선택 다이얼로그
# =======================
def select_folder():
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    folder = filedialog.askdirectory(title="분석할 메인 폴더를 선택하세요 (예: .../T-maze/50/main_task/)")
    root.destroy()
    if not folder:
        raise SystemExit("폴더 선택이 취소되어 프로그램을 종료합니다.")
    return folder

# =======================
# 2) 입력 폼 다이얼로그
# =======================
class InputDialog(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("T-maze Main Task Figure Program")
        self.geometry("360x240")
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
        tk.Label(self, text="Change weight:").grid(row=row, column=0, sticky="e", padx=10, pady=8)
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

# =======================
# 3) 데이터 처리 + 플롯
# =======================
def filter_skipped(df):
    """Correction/반복/무효/스킵된 Trial 제거(집계용)"""
    skip_cols = ['TrialCorrection', 'TrialRepetition', 'TrialVoid', 'TrialSkipped']
    for col in skip_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.upper()
            df = df[df[col] != 'YES']
    return df

def draw_figure_test2(ax, csv_file):
    """Figure 6: 섹션별 Latency 박스플롯 + 최대 구간 노란 점 (원래 코드의 Figure 9)"""
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
    """Figure 5: 최신 CSV의 Trial별 α/β/γ 비율 스택 막대 (원래 Figure 8 방식)"""
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

# ── Figure 1 전용: 표시용 원본 데이터 + 지터 + Corr/Rep 플래그 ──
def prepare_latest_for_fig1(latest_file):
    """Figure 1 표시용 원본 df (필터 미적용) 생성 및 지터/플래그 계산"""
    d = pd.read_csv(latest_file)

    # 표시용이므로 필터 미적용
    d['Trial#'] = d['Trial#'].astype(str).str.extract(r'(\d+)')
    d = d.dropna(subset=['Trial#'])
    d['Trial#'] = d['Trial#'].astype(int)
    d['Direction'] = d['Direction'].astype(str).str.lower()
    d['Correctness'] = d['Correctness'].astype(str).str.upper()
    d['Scene'] = d['Scene'].astype(str).str.lower()
    d['Latency'] = pd.to_numeric(d['Latency'], errors='coerce')

    for col in ['TrialCorrection', 'TrialRepetition']:
        if col not in d.columns:
            d[col] = 'NO'
        d[col] = d[col].astype(str).str.strip().str.upper().fillna('NO')

    # 같은 Trial#의 중복 발생에 대해 발생순서(0,1,2,...)와 중앙정렬 지터
    d['_occ'] = d.groupby('Trial#').cumcount()
    counts = d['Trial#'].value_counts().to_dict()
    scale = 0.12  # 지터 크기
    def offset(row):
        n = counts.get(row['Trial#'], 1)
        if n == 1:
            return 0.0
        positions = np.linspace(-(n-1)/2, (n-1)/2, n) * scale
        return positions[int(row['_occ'])]
    d['_x'] = d['Trial#'] + d.apply(offset, axis=1)

    # Corr/Rep YES 여부
    d['_is_corr_or_rep'] = (d['TrialCorrection'] == 'YES') | (d['TrialRepetition'] == 'YES')

    return d

def main():
    # --- 폴더 선택 & 입력값 수집 ---
    folder_path = select_folder()
    ui = get_user_inputs()
    le_str = ui["LE"]
    le_int = ui["LE_int"]
    weight_str = ui["weight"]
    change_str = ui["change weight"]
    pellet_str = ui["pellet"]
    day_str = ui["day"]

    # --- CSV 목록 ---
    csv_files = glob.glob(os.path.join(folder_path, "*_Rat*_VSM.csv"))
    if not csv_files:
        raise SystemExit("선택한 폴더에 *_Rat*_VSM.csv 파일이 없습니다.")

    # --- 최신 파일 경로 ---
    latest_file = max(csv_files, key=lambda f: int(os.path.basename(f).split("_")[0]))

    # --- Figure 1 표시용 원본 df (필터링 없이) ---
    df_latest_raw = prepare_latest_for_fig1(latest_file)
    unique_trials = sorted(df_latest_raw['Trial#'].unique().tolist())
    # YES 발생(행)만 별도 추출
    flagged_rows = df_latest_raw[df_latest_raw['_is_corr_or_rep']].copy()

    # --- 집계용(다른 도표들) df (필터 적용) ---
    df_latest = pd.read_csv(latest_file)
    df_latest = filter_skipped(df_latest)
    df_latest['Trial#'] = df_latest['Trial#'].astype(str).str.extract(r'(\d+)')
    df_latest = df_latest.dropna(subset=['Trial#'])
    df_latest['Trial#'] = df_latest['Trial#'].astype(int)
    df_latest['Direction'] = df_latest['Direction'].astype(str).str.lower()
    df_latest['Correctness'] = df_latest['Correctness'].astype(str).str.upper()
    df_latest['Scene'] = df_latest['Scene'].astype(str).str.lower()
    df_latest['Latency'] = pd.to_numeric(df_latest['Latency'], errors='coerce')

    # --- 통계 (Figure 1의 주석은 최신/필터 적용 버전 기준) ---
    left_ratio = (df_latest['Direction'] == 'left').mean() * 100 if len(df_latest) else 0.0
    right_ratio = (df_latest['Direction'] == 'right').mean() * 100 if len(df_latest) else 0.0
    accuracy_latest = (df_latest['Correctness'] == 'CORRECT').mean() * 100 if len(df_latest) else 0.0

    # --- 여러 날짜 집계 ---
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

    # --- 제목 문구 구성 ---
    if le_int == 49:
        comp = "(reward vs no reward)"
    elif le_int == 50:
        comp = "(reward vs quinine)"
    else:
        comp = "(reward comparison)"
    main_title = f"LE{le_str} {comp} Summary"

    # ----------------- 레이아웃 -----------------
    fig = plt.figure(figsize=(18, 13))
    gs_main = gridspec.GridSpec(3, 1, figure=fig, height_ratios=[1.0, 1.05, 0.85])
    fig.suptitle(main_title, fontsize=15, fontweight="bold")

    # 제목 우상단 메타 정보
    meta_text = "  |  ".join([
        f"Current weight: {weight_str}g" if weight_str else "Current weight: -",
        f"Change weight: {change_str}g" if change_str else "Change weight: -",
        f"Pellet: {pellet_str}g" if pellet_str else "Pellet: -",
        f"Day: {day_str}" if day_str else "Day: -",
    ])
    fig.text(0.995, 0.985, meta_text, ha='right', va='top', fontsize=10)

    # ───────────────────────── Figure 1 ─────────────────────────
    gs_row1 = gridspec.GridSpecFromSubplotSpec(1, 2, subplot_spec=gs_main[0], width_ratios=[1, 1])
    gs_fig1 = gridspec.GridSpecFromSubplotSpec(2, 1, subplot_spec=gs_row1[0], height_ratios=[3, 1])
    ax1_line = fig.add_subplot(gs_fig1[0])
    ax1_dots = fig.add_subplot(gs_fig1[1], sharex=ax1_line)

    # (위) Latency per Trial — YES 발생(행)에 회색 세로 줄
    if df_latest_raw['Latency'].notna().any():
        y_max = max(15, np.nanmax(df_latest_raw['Latency']) * 1.1)
    else:
        y_max = 15
    ax1_line.set_ylim(0, y_max)

    for _, rr in flagged_rows.iterrows():
        ax1_line.axvline(rr['_x'], color='grey', linestyle='--', linewidth=1.0, alpha=0.6, zorder=0)

    # 지터된 x 순서로 라인 + 점
    ax1_line.plot(df_latest_raw['_x'], df_latest_raw['Latency'], color='black', linewidth=1.0, zorder=1)
    ax1_line.scatter(df_latest_raw['_x'], df_latest_raw['Latency'], s=18, color='black', zorder=2, linewidths=0)
    ax1_line.set_title("Latency Trial")
    ax1_line.set_ylabel("Latency")

    # (아래) 방향 점 + Scene 테두리, YES 발생(행) 세로 줄
    for _, rr in flagged_rows.iterrows():
        ax1_dots.axvline(rr['_x'], color='grey', linestyle='--', linewidth=1.0, alpha=0.6, zorder=0)

    ax1_dots.set_xlabel("Trial")
    for _, r in df_latest_raw.iterrows():
        face_color = 'blue' if r['Direction'] == 'left' else 'red'
        y_pos = 0.08 if r['Direction'] == 'left' else 0.02
        if r['Scene'] == 'zebra':
            edge_color, lw = 'black', 1.5
        else:
            edge_color, lw = face_color, 0
        ax1_dots.scatter(r['_x'], y_pos,
                         marker='o', color=face_color, edgecolors=edge_color,
                         linewidths=lw, s=28, zorder=2)

    # x축 눈금: 각 Trial 번호 표시(정수 위치)
    ax1_line.set_xticks(unique_trials)
    ax1_line.set_xticklabels([str(t) for t in unique_trials])
    ax1_dots.set_xticks(unique_trials)
    ax1_dots.set_xticklabels([str(t) for t in unique_trials])

    ax1_dots.set_ylim(0, 0.1)
    ax1_dots.set_yticks([])
    ax1_dots.text(1.02, 0.92, f"Right: {right_ratio:.1f}%", transform=ax1_dots.transAxes, fontsize=8)
    ax1_dots.text(1.02, 0.72, f"Left: {left_ratio:.1f}%", transform=ax1_dots.transAxes, fontsize=8)
    ax1_dots.text(1.02, 0.50, "Grey line: Corr/Rep \nRed: Right\nBlue: Left\nBlack: Zebra scene",
                  transform=ax1_dots.transAxes, fontsize=8, va='top',
                  bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.3'))

    # ───────────────────────── Figure 2 ─────────────────────────
    ax46_left = fig.add_subplot(gs_row1[1])
    ax46_right = ax46_left.twinx()
    line4, = ax46_left.plot(df_trials["Day"], df_trials["TotalTrials"], marker="o", color="black", label="Total Trials")
    ax46_left.set_title("Total Trials & Choice Bias")
    ax46_left.set_xlabel("Day")
    ax46_left.set_ylabel("Total Trials")
    ax46_left.set_ylim(0, 50)  # 고정 범위
    line6, = ax46_right.plot(df_metric["Day"], df_metric["NormDiff"], marker="o", color="crimson",
                             linestyle="--", label="Choice Bias")
    ax46_right.set_ylabel("Bias Ratio")
    ax46_right.set_ylim(0, 1)
    all_days = sorted(set(df_trials["Day"]).union(set(df_metric["Day"])))
    ax46_left.set_xticks(all_days)
    ax46_left.legend([line4, line6], [line4.get_label(), line6.get_label()], loc="upper right", frameon=True)

    # ───────────────────────── Figure 3 ─────────────────────────
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

    # ───────────────────────── Figure 4 ─────────────────────────
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

    # ───────────────────────── Figure 5 ─────────────────────────
    gs_row3 = gridspec.GridSpecFromSubplotSpec(1, 2, subplot_spec=gs_main[2], width_ratios=[0.65, 0.35])
    ax_stack = fig.add_subplot(gs_row3[0])
    df_latest_sorted = df_latest.sort_values('Trial#').reset_index(drop=True)
    draw_stacked_ratio(ax_stack, df_latest_sorted, legend_x=0.2, legend_y=-0.12)

    # ───────────────────────── Figure 6 ─────────────────────────
    ax9 = fig.add_subplot(gs_row3[1])
    draw_figure_test2(ax9, latest_file)

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.show()

if __name__ == "__main__":
    main()
