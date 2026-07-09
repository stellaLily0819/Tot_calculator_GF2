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
# 공통 CSS
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

    .stTextInput > div > div > input {
        background-color: #ffffff !important;
        color: #111827 !important;
    }

    .stNumberInput input {
        background-color: #ffffff !important;
        color: #111827 !important;
    }

    .stSelectbox div[role="combobox"] {
        background-color: #ffffff !important;
        color: #111827 !important;
    }

    .stTextArea textarea {
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
# 점수 계산 로직
# =========================================================
def compute_a(P: int) -> int:
    """
    누적 활동치 P에 따른 추가 평가점수 a(P)를 계산.
    각 마일스톤을 넘을 때마다 보너스를 누적해서 더함.
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

    a = 0
    for thresholds, bonus in bonus_table:
        for t in thresholds:
            if P >= t:
                a += bonus

    return a


def compute_m(k: int) -> int:
    """
    활동치 k에 따른 보너스 m(k) 계산.
    기존 실제 계산식 그대로 유지.
    """
    if k < 3800:
        return 0

    if k <= 6000:
        return 27

    extra = (k - 6000) // 120
    return 27 + extra


def compute_P(k: int, n: int, days: int) -> int:
    """
    days일 동안의 누적 활동치 P.
    """
    return days * k * n


def model_total_score(k: int, n: int, days: int) -> tuple[int, int, int, int]:
    """
    (k, n, days)에 따른 모델 총점과 구성요소 계산.

    total = 650 + m(k) + a(P)
    """
    P = compute_P(k, n, days)
    a = compute_a(P)
    m = compute_m(k)
    total = 650 + m + a

    return total, P, a, m


def build_result_table(k: int, days: int) -> pd.DataFrame:
    """
    하루 횟수 n = 1 ~ 30 전체 결과표 생성.
    """
    rows = []

    prev_a = None
    prev_total_score = None

    for n in range(1, 31):
        total_score, P, a, m = model_total_score(k=k, n=n, days=days)
        total_bonus = m + a

        if prev_a is None:
            a_diff = 0
            score_diff = 0
        else:
            a_diff = a - prev_a
            score_diff = total_score - prev_total_score

        rows.append(
            {
                "하루 횟수 n": n,
                f"누적 활동치 P = {days}×k×n": P,
                "활동 보너스 m(k)": m,
                "누적 보너스 a(P)": a,
                "총 보너스 m+a": total_bonus,
                "모델 총점 650+m+a": total_score,
                "이전 n 대비 a(P) 증가": a_diff,
                "이전 n 대비 총점 증가": score_diff,
            }
        )

        prev_a = a
        prev_total_score = total_score

    return pd.DataFrame(rows)


# =========================================================
# Streamlit 앱
# =========================================================
def main():
    st.markdown(
        """
        <div>
            <div class="main-title">특수 점수 계산기</div>
            <div class="main-subtitle">
                활동치 k와 진행 일수를 기준으로, 하루 횟수 1~30에 따른 모든 활동 보너스 값을 출력합니다.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.sidebar.markdown(
        "<p style='text-align: center; font-size: 12px; color: gray;'>Made by Caleo01</p>",
        unsafe_allow_html=True,
    )
    st.sidebar.markdown("---")
    st.sidebar.header("입력값 설정")

    k = st.sidebar.number_input(
        "활동치 k",
        min_value=0,
        max_value=2_000_000,
        value=3800,
        step=100,
    )

    days = st.sidebar.number_input(
        "진행 일수",
        min_value=1,
        max_value=365,
        value=8,
        step=1,
    )

    st.markdown("<div class='calculator-card'>", unsafe_allow_html=True)

    st.markdown("### 📊 하루 횟수별 활동 보너스 출력")

    st.markdown(
        """
입력한 **활동치 k**와 **진행 일수 days**를 기준으로,  
하루 활동 횟수 `n = 1 ~ 30` 전체에 대해 누적 활동치와 보너스를 계산합니다.

- 진행 일수: `days`
- 활동치: `k`
- 하루 활동 횟수: `n = 1 ~ 30`
- 누적 활동치: `P = days × k × n`
- 활동 보너스: `m(k)`
- 누적 보너스: `a(P)`
- 총 점수 모델: `650 + m(k) + a(P)`
""",
        unsafe_allow_html=True,
    )

    st.markdown("---")

    df = build_result_table(k=k, days=days)

    m_value = compute_m(k)
    n30_row = df.iloc[-1]

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("입력 활동치 k", f"{k:,}")

    with col2:
        st.metric("진행 일수", f"{days}일")

    with col3:
        st.metric("활동 보너스 m(k)", f"{m_value:,}")

    with col4:
        st.metric("n=30 기준 총점", f"{n30_row['모델 총점 650+m+a']:,}")

    st.markdown("---")

    st.subheader("1. 하루 횟수 1~30 전체 결과")
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.markdown("---")

    st.subheader("2. 하루 횟수별 보너스 변화")

    chart_df = df.set_index("하루 횟수 n")[
        [
            "누적 보너스 a(P)",
            "총 보너스 m+a",
            "모델 총점 650+m+a",
        ]
    ]

    st.line_chart(chart_df)

    st.markdown("---")

    st.subheader("3. 보너스 증가 발생 구간")

    increased_df = df[df["이전 n 대비 총점 증가"] > 0]

    if increased_df.empty:
        st.info("현재 입력값 기준으로 n=1~30 사이에서 추가 보너스 증가 구간이 없습니다.")
    else:
        st.dataframe(increased_df, use_container_width=True, hide_index=True)

    st.markdown(
        """
**메모**

- 이 계산기는 최적의 `k, n`을 추론하지 않습니다.
- 입력한 `k`와 `days`를 고정한 뒤, 하루 횟수 `n = 1 ~ 30` 전체 결과를 화면에 출력합니다.
- 점수 계산식은 `650 + m(k) + a(P)`입니다.
- CSV 다운로드 기능은 넣지 않았습니다.
""",
        unsafe_allow_html=True,
    )

    st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
