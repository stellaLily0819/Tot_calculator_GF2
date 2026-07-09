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
# 누적 보너스 a(P)
# =========================================================
def compute_a(P: int) -> int:
    """
    누적 활동치 P에 따른 누적 보너스 a(P).
    기존 P 구간 그대로 사용.
    """
    bonus_table = [
        ([1200, 2400, 3600], 40),
        ([6000, 12000, 20000, 32000, 48000], 100),
        ([60000, 80000, 96000, 120000], 160),
        ([168000, 240000, 320000, 440000], 2000),
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
            if P >= threshold:
                bonus += value

    return bonus


# =========================================================
# 기본 계산식
# =========================================================
def compute_P(days: int, k: int, n: int) -> int:
    """
    누적 활동치 P.

    P = 650 + days × k × n + 10 × days
    """
    return 650 + days * k * n + 10 * days


def compute_tot(days: int, k: int, n: int) -> tuple[int, int, int]:
    """
    총 점수 tot.

    tot = P + a(P)

    반환:
    - tot
    - P
    - a(P)
    """
    P = compute_P(days=days, k=k, n=n)
    bonus = compute_a(P)
    total = P + bonus

    return total, P, bonus


# =========================================================
# n별 최적 k 탐색
# =========================================================
def find_best_k_for_n(
    target_tot: int,
    days: int,
    n: int,
    k_min: int = 0,
    k_max: int = 100,
) -> dict:
    """
    특정 n에 대해 target_tot에 가장 가까운 k를 찾는다.

    k는 0~100 정수 범위에서만 탐색한다.
    """

    best_row = None

    for k in range(k_min, k_max + 1):
        calculated_tot, P, bonus = compute_tot(
            days=days,
            k=k,
            n=n,
        )

        diff = calculated_tot - target_tot
        abs_diff = abs(diff)

        row = {
            "하루 활동횟수 n": n,
            "추론 단일 활동치 k": k,
            "누적 활동치 P": P,
            "누적 보너스 a(P)": bonus,
            "계산 tot = P+a(P)": calculated_tot,
            "입력 tot": target_tot,
            "오차 = 계산tot-입력tot": diff,
            "절대 오차": abs_diff,
        }

        if best_row is None:
            best_row = row
        else:
            if abs_diff < best_row["절대 오차"]:
                best_row = row
            elif abs_diff == best_row["절대 오차"]:
                # 오차가 같으면 더 낮은 k 선택
                if k < best_row["추론 단일 활동치 k"]:
                    best_row = row

    return best_row


def build_result_table(target_tot: int, days: int) -> pd.DataFrame:
    """
    n = 1~30 전체에 대해 최적 k를 추론한다.
    """
    rows = []

    for n in range(1, 31):
        rows.append(
            find_best_k_for_n(
                target_tot=target_tot,
                days=days,
                n=n,
                k_min=0,
                k_max=100,
            )
        )

    df = pd.DataFrame(rows)

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
                입력한 총 점수 tot에 가장 가까운 단일 활동치 k를 하루 활동횟수 1~30별로 추론합니다.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div class='calculator-card'>", unsafe_allow_html=True)

    st.markdown("### 📊 하루 활동횟수별 k 추론")

    st.markdown(
        """
입력값은 **총 점수 tot**와 **진행 일수 days**입니다.

코드는 하루 활동횟수 `n = 1 ~ 30`을 전부 계산하고,  
각 `n`마다 입력한 `tot`에 가장 가까운 단일 활동치 `k`를 찾습니다.

계산식:

`P = 650 + days × k × n + 10 × days`

`tot = P + a(P)`

제약 조건:

`0 ≤ k ≤ 100`
""",
        unsafe_allow_html=True,
    )

    st.subheader("1. 입력값")

    col1, col2 = st.columns(2)

    with col1:
        target_tot = st.number_input(
            "총 점수 tot",
            min_value=0,
            max_value=20_000_000,
            value=3000,
            step=10,
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

    df = build_result_table(
        target_tot=target_tot,
        days=days,
    )

    best_row = df.loc[df["절대 오차"].idxmin()]

    st.subheader("2. 전체 최적 조합")

    col_a, col_b, col_c, col_d = st.columns(4)

    with col_a:
        st.metric("입력 tot", f"{target_tot:,}")

    with col_b:
        st.metric("최적 n", f"{int(best_row['하루 활동횟수 n'])}")

    with col_c:
        st.metric("추론 k", f"{int(best_row['추론 단일 활동치 k'])}")

    with col_d:
        st.metric("계산 tot", f"{int(best_row['계산 tot = P+a(P)']):,}")

    st.markdown(
        f"""
**전체 최적 결과**

- 입력 tot: `{target_tot:,}`
- 진행 일수: `{days}`일
- 최적 하루 활동횟수 n: `{int(best_row['하루 활동횟수 n'])}`
- 추론 단일 활동치 k: `{int(best_row['추론 단일 활동치 k'])}`
- 누적 활동치 P: `{int(best_row['누적 활동치 P']):,}`
- 누적 보너스 a(P): `{int(best_row['누적 보너스 a(P)']):,}`
- 계산 tot: `{int(best_row['계산 tot = P+a(P)']):,}`
- 오차: `{int(best_row['오차 = 계산tot-입력tot']):,}`
"""
    )

    st.markdown("---")

    st.subheader("3. 하루 활동횟수 1~30별 추론 결과")

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("---")

    st.subheader("4. 입력 tot에 가까운 순서")

    sorted_df = df.sort_values("절대 오차", ascending=True)

    st.dataframe(
        sorted_df,
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("---")

    st.subheader("5. 도달 가능 여부")

    exact_df = df[df["절대 오차"] == 0]

    if exact_df.empty:
        st.warning(
            "입력한 tot와 정확히 일치하는 조합은 없습니다. "
            "위 표에서 절대 오차가 가장 작은 조합을 사용하세요."
        )
    else:
        st.success("입력한 tot와 정확히 일치하는 조합이 있습니다.")
        st.dataframe(
            exact_df,
            use_container_width=True,
            hide_index=True,
        )

    st.markdown(
        """
**메모**

- 이 코드는 `n`별로 tot를 임의 계산하는 코드가 아닙니다.
- 입력한 `tot`에 가장 가까워지는 `k`를 `n=1~30` 각각에 대해 찾습니다.
- 출력되는 `계산 tot`는 `P + a(P)`입니다.
- `계산 tot`가 입력 tot와 가까울수록 좋은 추론 결과입니다.
- `k`는 0~100 정수 범위에서만 탐색합니다.
- CSV 다운로드 기능은 없습니다.
""",
        unsafe_allow_html=True,
    )

    st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
