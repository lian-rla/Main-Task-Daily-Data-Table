import os
import pandas as pd
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog

# ───────── CSV 파일 다중 선택 ─────────
def select_csv_files():
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    file_paths = filedialog.askopenfilenames(
        title="분석할 CSV 파일들을 선택하세요 (여러 개 선택 가능)",
        filetypes=[("CSV files", "*.csv")]
    )
    root.destroy()
    if not file_paths:
        raise SystemExit("파일 선택 취소")
    return list(file_paths)

# ───────── 데이터 필터 (원본 로직) ─────────
def filter_skipped(df):
    skip_cols = ['TrialCorrection', 'TrialRepetition', 'TrialVoid', 'TrialSkipped']
    for col in skip_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.upper()
            df = df[df[col] != 'YES']
    return df

# ───────── Figure 5 그리기 (원본 색상 적용) ─────────
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

# ───────── 메인 실행 ─────────
def main():
    csv_files = select_csv_files()

    for csv_path in csv_files:
        df = pd.read_csv(csv_path)
        df = filter_skipped(df)
        df['Trial#'] = df['Trial#'].astype(str).str.extract(r'(\d+)')
        df = df.dropna(subset=['Trial#'])
        df['Trial#'] = df['Trial#'].astype(int)
        df_sorted = df.sort_values('Trial#').reset_index(drop=True)

        fig, ax = plt.subplots(figsize=(10, 6))
        draw_stacked_ratio(ax, df_sorted, legend_x=0.2, legend_y=-0.12)

        base = os.path.basename(csv_path)
        ax.set_title(f"Section Proportion Trial — {base}")

    plt.show()

if __name__ == "__main__":
    main()
