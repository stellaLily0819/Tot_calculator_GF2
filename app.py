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


# =========================================================
# 핵심 계산식
# =========================================================
def compute_P(days: int, k: int, n: int) -> int:
    """
    누적 활동치 P.

    P = 650 + days × k × n + 10 × days
    """
    return 650 + days * k * n + 10 * days


def compute_total_score(days: int, k: int, n: int) -> tuple[int, int]:
    """
    총 점수 tot.

    tot = P + a(P)

    반환값:
    - total_score
    - P
    """
    P = compute_P(days=days, k=k, n=n)
    total_score = P + compute_a(P)
    return total_score, P


def find_best_k_for_n(target_total: int, days: int, n: int) -> dict:
    """
    특정 하루 활동횟수 n에 대해,
    입력 총점 target_total에 가장 가까운 단일 활동치 k를 탐색.

    a(P)가 계단식 보너스라서 단순 역산이 아니라 탐색이 필요함.
    total_score(k)는 k가 증가하면 감소하지 않는 단조 증가 함수이므로
    이진 탐색 후 주변 후보를 비교한다.
    """

    # 입력 총점이 기본 P보다 낮은 경우 k=0이 최선
    base_total, base_P = compute_total_score(days=days, k=0, n=n)

    if target_total <= base_total:
        best_k = 0
        best_total = base_total
        best_P = base_P
        best_a = compute_a(best_P)

        return {
            "하루 활동횟수 n": n,
            "최적화 단일 활동치 k": best_k,
            "누적 활동치 P": best_P,
            "누적 보너스 a(P)": best_a,
            "계산 총점 tot = P+a(P)": best_total,
            "입력 총점과 오차": best_total - target_total,
            "절대 오차": abs(best_total - target_total),
        }

    # 상한값 자동 확장
    low = 0
    high = 1

    while True:
        high_total, _ = compute_total_score(days=days, k=high, n=n)

        if high_total >= target_total:
            break

        high *= 2

        # 비정상적으로 커지는 경우 방어
        if high > 10_000_000:
            break

    # 이진 탐색
    while low <= high:
        mid = (low + high) // 2
        mid_total, _ = compute_total_score(days=days, k=mid, n=n)

        if mid_total < target_total:
            low = mid + 1
        else:
            high = mid - 1

    # 경계 주변 후보 비교
    candidates = set()

    for candidate_k in range(max(0, low - 5), low + 6):
        candidates.add(candidate_k)

    best = None

    for candidate_k in candidates:
        total_score, P = compute_total_score(days=days, k=candidate_k, n=n)
        bonus = compute_a(P)
        diff = total_score - target_total
        abs_diff = abs(diff)

        row = {
            "하루 활동횟수 n": n,
            "최적화 단일 활동치 k": candidate_k,
            "누적 활동치 P": P,
            "누적 보너스 a(P)": bonus,
            "계산 총점 tot = P+a(P)": total_score,
            "입력 총점과 오차": diff,
            "절대 오차": abs_diff,
        }

        if best is None:
            best = row
        else:
            if row["절대 오차"] < best["절대 오차"]:
                best = row
            elif row["절대 오차"] == best["절대 오차"]:
                # 오차가 같으면 더 낮은 k 우선
                if row["최적화 단일 활동치 k"] < best["최적화 단일 활동치 k"]:
                    best = row

    return best


def build_result_table(target_total: int, days: int) -> pd.DataFrame:
    """
    n = 1 ~ 30 전체에 대한 최적 k 추론 결과표.
    """
    rows = []

    for n in range(1, 31):
        rows.append(
            find_best_k_for_n(
                target_total=target_total,
                days=days,
                n=n,
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
                총 점수 tot와 진행 일수를 기준으로, 하루 활동횟수 1~30별 최적 단일 활동치 k를 추론합니다.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div class='calculator-card'>", unsafe_allow_html=True)

    st.markdown("### 📊 하루 활동횟수별 단일 활동치 k 추론")

    st.markdown(
        """
입력한 **총 점수 tot**와 **진행 일수 days**를 기준으로,  
하루 활동횟수 `n = 1 ~ 30` 각각에 대해 최적화된 단일 활동치 `k`를 계산합니다.

계산 기준:

`P = 650 + days × k × n + 10 × days`

`tot = P + a(P)`

여기서 `a(P)`는 기존 누적 활동치 P 구간에 따른 누적 보너스입니다.
""",
        unsafe_allow_html=True,
    )

    st.subheader("1. 입력값")

    col1, col2 = st.columns(2)

    with col1:
        target_total = st.number_input(
            "총 점수 tot",
            min_value=0,
            max_value=20_000_000,
            value=500_000,
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

    df = build_result_table(
        target_total=target_total,
        days=days,
    )

    best_row = df.loc[df["절대 오차"].idxmin()]

    st.subheader("2. 요약")

    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

    with metric_col1:
        st.metric("입력 총점 tot", f"{target_total:,}")

    with metric_col2:
        st.metric("진행 일수", f"{days}일")

    with metric_col3:
        st.metric("최소 오차", f"{int(best_row['절대 오차']):,}")

    with metric_col4:
        st.metric(
            "최소 오차 n",
            f"{int(best_row['하루 활동횟수 n'])}",
        )

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
        st.metric(
            "하루 활동횟수 n",
            f"{int(best_row['하루 활동횟수 n'])}",
        )

    with best_col2:
        st.metric(
            "최적화 단일 활동치 k",
            f"{int(best_row['최적화 단일 활동치 k']):,}",
        )

    with best_col3:
        st.metric(
            "누적 활동치 P",
            f"{int(best_row['누적 활동치 P']):,}",
        )

    with best_col4:
        st.metric(
            "누적 보너스 a(P)",
            f"{int(best_row['누적 보너스 a(P)']):,}",
        )

    st.markdown("---")

    st.subheader("5. 하루 활동횟수별 k 변화")

    chart_df = df.set_index("하루 활동횟수 n")[
        [
            "최적화 단일 활동치 k",
            "누적 보너스 a(P)",
            "절대 오차",
        ]
    ]

    st.line_chart(chart_df)

    st.markdown(
        """
**메모**

- 입력값은 `총 점수 tot`와 `진행 일수 days`입니다.
- `n = 1 ~ 30` 전체에 대해 최적화된 정수 `k`를 계산합니다.
- `P = 650 + days × k × n + 10 × days`입니다.
- `tot = P + a(P)`입니다.
- `a(P)`는 기존 P 구간별 누적 보너스를 그대로 사용합니다.
- CSV 다운로드 기능은 없습니다.
""",
        unsafe_allow_html=True,
    )

    st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
