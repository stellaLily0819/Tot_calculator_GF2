import pandas as pd
import streamlit as st


# ---------------------
# 페이지 기본 설정
# ---------------------
st.set_page_config(
    page_title="특수 점수 계산기",
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

    [data-testid="stSidebar"] {
        background-color: #e5e7eb !important;
    }

    .block-container {
        padding-top: 4rem;
        padding-bottom: 3rem;
        max-width: 1100px;
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
# 누적 보너스 계산
# =========================================================
def compute_a(P: int) -> int:
    """
    누적 활동치 P에 따른 누적 보너스 a(P).
    기존 보너스 구간 그대로 사용.
    """
    bonus_table = [
        ([1200, 2400, 3600], 40),
        ([6000, 12000, 20000, 32000, 48000], 100),
        ([60000, 80000, 96000, 120000], 160),
        ([168000, 240000, 320000, 440000], 2000),
        (
            [
                500000, 560000, 640000, 720000, 800000,
                900000, 1050000, 1200000, 1400000, 1600000, 1800000
            ],
            300,
        ),
    ]

    bonus = 0

    for thresholds, value in bonus_table:
        for threshold in thresholds:
            if P >= threshold:
                bonus += value

    return bonus


def compute_P(days: int, k: int, n: int) -> int:
    """
    누적 활동치 공식.

    P = 650 + days × k × n + 10 × days
    """
    return 650 + days * k * n + 10 * days


def infer_best_k(target_P: int, days: int, n: int) -> dict:
    """
    입력된 누적 활동치 target_P와 진행 일수 days 기준으로
    특정 하루 활동횟수 n에 대한 최적 단일 활동치 k를 추론.

    k는 정수로 반올림하여 사용.
    """
    raw_k = (target_P - 650 - 10 * days) / (days * n)

    rounded_k = round(raw_k)

    if rounded_k < 0:
        rounded_k = 0

    recalculated_P = compute_P(days=days, k=rounded_k, n=n)
    diff = recalculated_P - target_P
    abs_diff = abs(diff)

    bonus = compute_a(recalculated_P)

    return {
        "하루 활동횟수 n": n,
        "추론 k 원값": raw_k,
        "최적화 단일 활동치 k": rounded_k,
        "재계산 P": recalculated_P,
        "입력 P와 오차": diff,
        "절대 오차": abs_diff,
        "누적 보너스 a(P)": bonus,
    }


def build_result_table(target_P: int, days: int) -> pd.DataFrame:
    """
    n = 1 ~ 30 전체에 대한 최적 k 추론 결과표.
    """
    rows = []

    for n in range(1, 31):
        rows.append(infer_best_k(target_P=target_P, days=days, n=n))

    df = pd.DataFrame(rows)

    df["추론 k 원값"] = df["추론 k 원값"].round(4)

    return df


# =========================================================
# Streamlit 앱
# =========================================================
def main():
    st.markdown(
        """
        <div>
            <div class="main-title">특수 점수 계산기</div>
            <div class="main-subtitle">
                누적 활동치 P와 진행 일수를 기준으로, 하루 활동횟수 1~30별 최적 단일 활동치 k를 추론합니다.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.sidebar.markdown(
        "<p style='text-align: center; font-size: 12px; color: gray;'>Made by Caleo01</p>",
        unsafe_allow_html=True,
    )

    st.markdown("<div class='calculator-card'>", unsafe_allow_html=True)

    st.markdown("### 📊 하루 활동횟수별 단일 활동치 k 추론")

    st.markdown(
        """
입력한 **누적 활동치 P**와 **진행 일수 days**를 기준으로,  
하루 활동횟수 `n = 1 ~ 30` 각각에 대해 최적화된 단일 활동치 `k`를 계산합니다.

계산식:

`P = 650 + days × k × n + 10 × days`

역산식:

`k = (P - 650 - 10 × days) / (days × n)`

정수 k가 필요하므로, 코드에서는 각 n별로 k를 반올림한 뒤 다시 P를 계산하고 오차를 표시합니다.
""",
        unsafe_allow_html=True,
    )

    st.subheader("1. 입력값")

    col1, col2 = st.columns(2)

    with col1:
        target_P = st.number_input(
            "누적 활동치 P",
            min_value=0,
            max_value=10_000_000,
            value=500000,
            step=100,
        )

    with col2:
        days = st.number_input(
            "진행 일수 days",
            min_value=1,
            max_value=365,
            value=8,
            step=1,
        )

    st.markdown("---")

    df = build_result_table(target_P=target_P, days=days)

    input_bonus = compute_a(target_P)

    best_row = df.loc[df["절대 오차"].idxmin()]

    st.subheader("2. 요약")

    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

    with metric_col1:
        st.metric("입력 누적 활동치 P", f"{target_P:,}")

    with metric_col2:
        st.metric("진행 일수", f"{days}일")

    with metric_col3:
        st.metric("입력 P 기준 누적 보너스", f"{input_bonus:,}")

    with metric_col4:
        st.metric("최소 오차", f"{int(best_row['절대 오차']):,}")

    st.markdown("---")

    st.subheader("3. 하루 활동횟수 1~30별 k 추론 결과")

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("---")

    st.subheader("4. 오차가 가장 작은 조합")

    best_col1, best_col2, best_col3, best_col4 = st.columns(4)

    with best_col1:
        st.metric("하루 활동횟수 n", f"{int(best_row['하루 활동횟수 n'])}")

    with best_col2:
        st.metric("최적화 단일 활동치 k", f"{int(best_row['최적화 단일 활동치 k']):,}")

    with best_col3:
        st.metric("재계산 P", f"{int(best_row['재계산 P']):,}")

    with best_col4:
        st.metric("누적 보너스 a(P)", f"{int(best_row['누적 보너스 a(P)']):,}")

    st.markdown("---")

    st.subheader("5. 하루 활동횟수별 추론 k 변화")

    chart_df = df.set_index("하루 활동횟수 n")[
        [
            "최적화 단일 활동치 k",
            "절대 오차",
            "누적 보너스 a(P)",
        ]
    ]

    st.line_chart(chart_df)

    st.markdown(
        """
**메모**

- 이 코드는 사용자가 제공한 `P`와 `days`를 기준으로 `n = 1 ~ 30` 전체를 계산합니다.
- 각 n마다 최적화된 단일 활동치 `k`를 추론합니다.
- 누적 보너스 `a(P)`는 기존 보너스 구간을 그대로 사용합니다.
- `k`는 정수로 반올림하여 적용합니다.
- CSV 다운로드 기능은 없습니다.
""",
        unsafe_allow_html=True,
    )

    st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
