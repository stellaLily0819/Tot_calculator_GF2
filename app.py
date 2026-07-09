import pandas as pd
import streamlit as st


# ---------------------
# 페이지 설정
# ---------------------
st.set_page_config(
    page_title="활동치 역산 계산기",
    page_icon="📊",
    layout="wide",
)


# ---------------------
# CSS
# ---------------------
st.markdown(
    """
    <style>
    html, body {
        background-color: #f3f4f6 !important;
    }

    .stApp {
        background: radial-gradient(circle at top left, #e0f2fe 0, #fdf2ff 35%, #ffffff 100%) !important;
    }

    [data-testid="stAppViewContainer"] {
        background: transparent !important;
    }

    [data-testid="stHeader"] {
        background: transparent !important;
    }

    .block-container {
        padding-top: 4rem;
        padding-bottom: 3rem;
        max-width: 1200px;
    }

    html, body, .stApp, .block-container {
        color: #111827;
    }

    * {
        color: #111827 !important;
    }

    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        letter-spacing: -0.03em;
        margin-bottom: 0.3rem;
    }

    .main-subtitle {
        font-size: 0.95rem;
        color: #4b5563;
        margin-bottom: 1.4rem;
    }

    .calculator-card {
        background: rgba(255, 255, 255, 0.96);
        border-radius: 20px;
        padding: 1.6rem 1.9rem;
        border: 1px solid rgba(148, 163, 184, 0.2);
        box-shadow: 0 18px 45px rgba(15, 23, 42, 0.10);
        backdrop-filter: blur(10px);
        margin-bottom: 1.5rem;
    }

    input, textarea {
        background-color: #ffffff !important;
        color: #111827 !important;
    }

    .stNumberInput input {
        background-color: #ffffff !important;
        color: #111827 !important;
    }

    [data-baseweb="input"] > div {
        background-color: #ffffff !important;
        color: #111827 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 누적 전투 점수 보너스
# =========================================================
def compute_bonus(cumulative_battle_score: int) -> int:
    """
    누적 전투 점수 구간에 따른 추가 활동치 보너스.
    """
    bonus_table = [
        ([1200, 2400, 3600], 40),
        ([6000, 12000, 20000, 32000, 48000], 100),
        ([60000, 80000, 96000, 120000], 160),
        ([168000, 240000, 320000, 440000], 200),
        (
            [
                500000, 560000, 640000, 720000, 800000,
                900000, 1050000, 1200000, 1400000,
                1600000, 1800000
            ],
            300,
        ),
    ]

    bonus = 0

    for thresholds, value in bonus_table:
        for threshold in thresholds:
            if cumulative_battle_score >= threshold:
                bonus += value

    return bonus


# =========================================================
# 전투 점수 → 1회 활동치 k
# =========================================================
def compute_k_from_battle_score(battle_score: int) -> int:
    """
    전투 점수에 따른 1회 활동치 k.

    - 전투 점수 6000점 미만: 0
    - 전투 점수 6000점 이상: 최소 27
    - 6000점 이후 120점마다 +1
    """
    if battle_score < 6000:
        return 0

    return 27 + ((battle_score - 6000) // 120)


# =========================================================
# 총 활동치 계산
# =========================================================
def compute_total_activity(
    battle_score: int,
    days: int,
    n: int,
) -> dict:
    """
    특정 전투 점수, 진행 일수, 하루 횟수 n 기준 총 활동치 계산.
    """
    base_activity = 650 + 10 * days

    k = compute_k_from_battle_score(battle_score)

    battle_count = days * n
    cumulative_battle_score = battle_score * battle_count

    battle_activity = k * battle_count
    bonus_activity = compute_bonus(cumulative_battle_score)

    total_activity = base_activity + battle_activity + bonus_activity

    return {
        "전투 점수": battle_score,
        "1회 활동치 k": k,
        "전투 횟수 합계": battle_count,
        "누적 전투 점수": cumulative_battle_score,
        "전투 활동치 합계": battle_activity,
        "누적 보너스 활동치": bonus_activity,
        "계산 tot": total_activity,
    }


# =========================================================
# n별 최적 전투 점수 / k 탐색
# =========================================================
def find_best_for_n(
    target_tot: int,
    days: int,
    n: int,
    battle_score_min: int = 6000,
    battle_score_max: int = 20000,
    battle_score_step: int = 10,
) -> dict:
    """
    특정 n에 대해 입력 tot에 가장 가까운 전투 점수와 k를 탐색.
    """
    best = None

    for battle_score in range(
        battle_score_min,
        battle_score_max + 1,
        battle_score_step,
    ):
        result = compute_total_activity(
            battle_score=battle_score,
            days=days,
            n=n,
        )

        diff = result["계산 tot"] - target_tot
        abs_diff = abs(diff)

        row = {
            "하루 횟수 n": n,
            **result,
            "입력 tot": target_tot,
            "오차": diff,
            "절대 오차": abs_diff,
        }

        if best is None:
            best = row
            continue

        if row["절대 오차"] < best["절대 오차"]:
            best = row
        elif row["절대 오차"] == best["절대 오차"]:
            # 오차가 같으면 더 낮은 전투 점수 우선
            if row["전투 점수"] < best["전투 점수"]:
                best = row

    return best


def build_result_table(
    target_tot: int,
    days: int,
    battle_score_min: int,
    battle_score_max: int,
    battle_score_step: int,
) -> pd.DataFrame:
    """
    n = 1~30 전체에 대해 최적 결과표 생성.
    """
    rows = []

    for n in range(1, 31):
        rows.append(
            find_best_for_n(
                target_tot=target_tot,
                days=days,
                n=n,
                battle_score_min=battle_score_min,
                battle_score_max=battle_score_max,
                battle_score_step=battle_score_step,
            )
        )

    return pd.DataFrame(rows)


# =========================================================
# Streamlit 앱
# =========================================================
def main():
    st.markdown(
        """
        <div>
            <div class="main-title">활동치 역산 계산기</div>
            <div class="main-subtitle">
                총 활동치 tot와 진행 일수를 기준으로, 하루 횟수 1~30별 최적 전투 점수와 1회 활동치 k를 추론합니다.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div class='calculator-card'>", unsafe_allow_html=True)

    st.markdown("### 📊 하루 횟수별 전투 점수 / 활동치 k 추론")

    st.markdown(
        """
입력값은 **총 활동치 tot**와 **진행 일수 days**입니다.

계산 구조:

`기본 활동치 = 650 + 10 × days`

`1회 활동치 k = 27 + floor((전투 점수 - 6000) / 120)`

`누적 전투 점수 = 전투 점수 × days × n`

`총 활동치 = 기본 활동치 + k × days × n + 누적 보너스`

누적 보너스는 기존 누적 전투 점수 구간을 그대로 사용합니다.
""",
        unsafe_allow_html=True,
    )

    st.subheader("1. 입력값")

    col1, col2 = st.columns(2)

    with col1:
        target_tot = st.number_input(
            "총 활동치 tot",
            min_value=0,
            max_value=100_000,
            value=1202,
            step=1,
        )

    with col2:
        days = st.number_input(
            "진행 일수 days",
            min_value=1,
            max_value=365,
            value=1,
            step=1,
        )

    st.subheader("2. 탐색 범위")

    col3, col4, col5 = st.columns(3)

    with col3:
        battle_score_min = st.number_input(
            "전투 점수 최소값",
            min_value=0,
            max_value=1_000_000,
            value=6000,
            step=100,
        )

    with col4:
        battle_score_max = st.number_input(
            "전투 점수 최대값",
            min_value=battle_score_min,
            max_value=1_000_000,
            value=20000,
            step=100,
        )

    with col5:
        battle_score_step = st.number_input(
            "전투 점수 탐색 간격",
            min_value=1,
            max_value=1000,
            value=10,
            step=1,
        )

    st.markdown("---")

    df = build_result_table(
        target_tot=target_tot,
        days=days,
        battle_score_min=battle_score_min,
        battle_score_max=battle_score_max,
        battle_score_step=battle_score_step,
    )

    best_row = df.loc[df["절대 오차"].idxmin()]

    st.subheader("3. 전체 최적 결과")

    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

    with metric_col1:
        st.metric("입력 tot", f"{target_tot:,}")

    with metric_col2:
        st.metric("최적 n", f"{int(best_row['하루 횟수 n'])}")

    with metric_col3:
        st.metric("전투 점수", f"{int(best_row['전투 점수']):,}")

    with metric_col4:
        st.metric("1회 활동치 k", f"{int(best_row['1회 활동치 k'])}")

    st.markdown(
        f"""
**최적 조합 상세**

- 입력 tot: `{target_tot:,}`
- 진행 일수: `{days}`일
- 하루 횟수 n: `{int(best_row['하루 횟수 n'])}`
- 전투 점수: `{int(best_row['전투 점수']):,}`
- 1회 활동치 k: `{int(best_row['1회 활동치 k'])}`
- 전투 횟수 합계: `{int(best_row['전투 횟수 합계'])}`
- 누적 전투 점수: `{int(best_row['누적 전투 점수']):,}`
- 전투 활동치 합계: `{int(best_row['전투 활동치 합계']):,}`
- 누적 보너스 활동치: `{int(best_row['누적 보너스 활동치']):,}`
- 계산 tot: `{int(best_row['계산 tot']):,}`
- 오차: `{int(best_row['오차']):,}`
"""
    )

    st.markdown("---")

    st.subheader("4. 하루 횟수 1~30별 추론 결과")

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("---")

    st.subheader("5. 입력 tot에 가까운 순서")

    sorted_df = df.sort_values(
        by=["절대 오차", "하루 횟수 n"],
        ascending=[True, True],
    )

    st.dataframe(
        sorted_df,
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("---")

    st.subheader("6. 예시 검증")

    example_battle_score = 7560
    example_n = 3
    example = compute_total_activity(
        battle_score=example_battle_score,
        days=1,
        n=example_n,
    )

    st.markdown(
        f"""
`days=1`, `n=3`, `전투 점수={example_battle_score}` 기준:

- 1회 활동치 k: `{example['1회 활동치 k']}`
- 누적 전투 점수: `{example['누적 전투 점수']:,}`
- 누적 보너스 활동치: `{example['누적 보너스 활동치']:,}`
- 전투 활동치 합계: `{example['전투 활동치 합계']:,}`
- 계산 tot: `{example['계산 tot']:,}`

즉 `tot=1202`와 비교하면 오차는 `{example['계산 tot'] - 1202}`입니다.
"""
    )

    st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
