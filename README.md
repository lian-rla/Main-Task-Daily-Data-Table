# T-maze Main Task — Daily Data Figure

T-maze 행동 실험(Main Task)의 일별 데이터를 시각화하는 Python 스크립트입니다.  
매 세션이 끝난 후 실행하여 당일 데이터와 누적 추이를 한 장의 Figure로 확인할 수 있습니다.

---

## Features

- 당일 세션의 Trial별 Latency 및 방향 선택 도트 시각화
- 누적 일별 Total Trials 및 Choice Bias 추이
- 누적 일별 Scene별(Zebra / Pebbles) Correctness 및 기준선(75%) 표시
- 누적 일별 Latency 분포 (Boxplot + Correct/Wrong strip)
- 당일 Trial별 구간 비율 적층 바 차트 (Alpha / Beta / Gamma)
- 당일 구간별 Latency 분포 Boxplot

---

## Requirements

```
Python >= 3.8
numpy
pandas
matplotlib
seaborn
tkinter  # Python 표준 라이브러리 (별도 설치 불필요)
```

설치:

```bash
pip install numpy pandas matplotlib seaborn
```

---

## Usage

```bash
python main_task_daily_data_table.py
```

실행하면 두 개의 GUI 창이 순서대로 열립니다.

---

### 1. 폴더 선택 창

분석할 세션 데이터가 들어있는 폴더를 선택합니다.  
예: `.../T-maze/50/main_task/`

---

### 2. 실험 정보 입력 창

![Input Dialog](input_dialog.png)

폴더 선택 후 아래와 같은 입력 창이 표시됩니다.

| 항목 | 설명 |
|------|------|
| **LE** | 실험 조건 번호. `49` = reward vs no reward, `50` = reward vs quinine. Figure 제목에 반영됨 **(필수)** |
| **Current weight** | 당일 측정한 쥐의 체중 (g). Figure 우측 상단 메타정보에 표시 |
| **Change weight** | 전일 대비 체중 변화량 (g). Figure 우측 상단 메타정보에 표시 |
| **Pellet** | 당일 제공한 식이 제한 펠릿 양 (g). Figure 우측 상단 메타정보에 표시 |
| **Day** | 실험 일차. Figure 우측 상단 메타정보에 표시 |

> **확인** 버튼을 누르면 Figure가 생성됩니다. LE 값은 필수 입력이며 비워두면 오류가 발생합니다.

---

## Input Data Format

선택한 폴더 내에 아래 패턴의 CSV 파일이 있어야 합니다.

```
{day}_Rat{id}_VSM.csv
```

예: `1_Rat01_VSM.csv`, `2_Rat01_VSM.csv`, ...

CSV에 필요한 컬럼:

| 컬럼명 | 설명 |
|--------|------|
| `Trial#` | 트라이얼 번호 |
| `Direction` | 선택 방향 (`left` / `right`) |
| `Correctness` | 정오 여부 (`CORRECT` / `WRONG`) |
| `Scene` | 배경 씬 (`zebra` / `pebbles`) |
| `Latency` | 전체 반응 시간 (초) |
| `Latency_stbox` | Start box 구간 Latency |
| `Latency_inter` | Intersection 구간까지의 누적 Latency |
| `TrialCorrection` / `TrialRepetition` / `TrialVoid` / `TrialSkipped` | 제외 트라이얼 플래그 (`YES`이면 분석에서 제외) |

---

## Output

![Figure Output](figure_output.png)

입력 완료 후 6개의 서브플롯으로 구성된 Figure가 표시됩니다.

---

### Figure 구성

#### ① Latency Trial *(좌측 상단)*

당일 세션에서 Trial 번호 순서대로 전체 Latency(초)를 꺾은선으로 표시합니다.  
하단의 도트 행에서 각 Trial의 방향 선택과 씬 정보를 함께 확인할 수 있습니다.

- **빨간 점**: 오른쪽(Right / Down) 선택
- **파란 점**: 왼쪽(Left / Up) 선택
- **검은 테두리**: Zebra 씬 Trial
- 테두리 없음: Pebbles 씬 Trial
- 우측에 Right / Left 선택 비율(%) 표시

---

#### ② Total Trials & Choice Bias *(우측 상단)*

누적 일별 두 지표를 이중 Y축으로 표시합니다.

- **검은 실선 (좌축)**: 일별 총 Trial 수 (Total Trials)
- **빨간 점선 (우축)**: Choice Bias — 좌/우 선택 편향 정도 (0 = 균등, 1 = 완전 편향)

---

#### ③ Scene Correctness Days *(좌측 중단)*

누적 일별 정확도(Correctness) 추이를 씬별로 표시합니다.

- **파란 선**: 전체 정확도 (Total Correctness)
- **초록 선**: Zebra 씬 정확도
- **주황 선**: Pebbles 씬 정확도
- **빨간 점선**: 기준선 (Criterion = 75%)
- 우측 상단에 당일 정확도(%) 표시

---

#### ④ Latency Distribution *(우측 중단)*

누적 일별 Latency 분포를 Boxplot과 개별 데이터 점으로 표시합니다.

- **회색 Boxplot**: 일별 Latency 전체 분포
- **파란 점**: 정답(CORRECT) Trial의 Latency
- **분홍/빨간 점**: 오답(WRONG) Trial의 Latency

---

#### ⑤ Section Proportion Trial *(좌측 하단)*

당일 세션의 Trial별 구간 점유 비율을 적층 바 차트로 표시합니다.

- **주황 (Alpha α)**: Start box 체류 구간
- **초록 (Beta β)**: Start box → Intersection 이동 구간
- **파란 (Gamma γ)**: Intersection → Goal box 이동 구간

각 Trial의 전체 Latency 중 각 구간이 차지하는 비율을 0~1 척도로 표시합니다.

---

#### ⑥ Latency Distribution (Section) *(우측 하단)*

당일 세션의 Alpha / Beta / Gamma 각 구간 Latency를 Boxplot으로 비교합니다.  
**노란 점**은 각 Trial에서 가장 오래 걸린 구간(최댓값)을 표시합니다.

---

## Notes

- `LE 49`: reward vs no reward 조건
- `LE 50`: reward vs quinine 조건
- Latency 구간 정의:
  - **Alpha (α)**: Start box 체류 시간 (`Latency_stbox`)
  - **Beta (β)**: Intersection 진입까지의 이동 시간
  - **Gamma (γ)**: Goal box 진입까지의 이동 시간
- Figure 저장: 창 하단 도구 모음의 저장 아이콘 사용

---

## Author

Lee Lab — T-maze Behavior Analysis
