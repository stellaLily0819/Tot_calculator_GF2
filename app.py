import streamlit as st

# ---------------------
# 페이지 기본 설정
# ---------------------
st.set_page_config(
    page_title="통합 계산기",
    page_icon="🧮",
    layout="wide",
)

# ---------------------
# 커스텀 CSS
# ---------------------
st.markdown(
    """
    <style>
    /* 메인 배경 */
    .stApp {
        background: radial-gradient(circle at top left, #e0f2fe 0, #fdf2ff 35%, #ffffff 100%);
    }
    .block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 900px;
    }
    
    /* 헤더 텍스트 살짝 꾸미기 */
    .main-title {
    margin-top: 1rem;
    font-size: 2.2rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    margin-bottom: 0.3rem;
    }

    .main-subtitle {
        font-size: 0.95rem;
        color: #6b7280;
        margin-bottom: 1.2rem;
    }

    /* 계산기 카드 박스 */
    .calculator-card {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 20px;
        padding: 1.5rem 1.8rem;
        border: 1px solid rgba(148, 163, 184, 0.18);
        box-shadow: 0 18px 45px rgba(15, 23, 42, 0.10);
        backdrop-filter: blur(12px);
    }

    .calculator-title {
        font-size: 1.1rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
        display: flex;
        align-items: center;
        gap: 0.4rem;
    }

    .calculator-subtitle {
        font-size: 0.85rem;
        color: #6b7280;
        margin-bottom: 0.5rem;
    }

    /* 탭 스타일 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
    }

    .stTabs [data-baseweb="tab"] {
        padding: 0.6rem 0.9rem;
        border-radius: 999px;
        background-color: rgba(255, 255, 255, 0.7);
        border: 1px solid rgba(148, 163, 184, 0.4);
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #4f46e5, #ec4899);
        color: white !important;
        border: none;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------
# 계산기 1 (예시: 사칙연산)
# ---------------------
def calculator_one():
    st.markdown(
        """
        <div class="calculator-card">
            <div class="calculator-title">🧮 기본 계산기</div>
            <div class="calculator-subtitle">두 숫자를 입력하고 원하는 연산을 선택해 보세요.</div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        a = st.number_input("첫 번째 숫자", value=0.0, key="c1_a")
    with col2:
        b = st.number_input("두 번째 숫자", value=0.0, key="c1_b")

    op = st.segmented_control("연산자", ["+", "-", "×", "÷"], key="c1_op")

    calc_col1, calc_col2 = st.columns([1, 1.5])
    with calc_col1:
        calc_btn = st.button("결과 보기", key="calc1_button")
    with calc_col2:
        st.caption("Tip: 나눗셈에서 0으로 나누지 않도록 주의하세요!")

    if calc_btn:
        if op == "+":
            result = a + b
        elif op == "-":
            result = a - b
        elif op == "×":
            result = a * b
        else:
            result = "0으로 나눌 수 없습니다." if b == 0 else a / b

        st.markdown("---")
        st.metric(label="계산 결과", value=result)

    st.markdown("</div>", unsafe_allow_html=True)


# ---------------------
# 계산기 2 (예시: BMI)
# ---------------------
def calculator_two():
    st.markdown(
        """
        <div class="calculator-card">
            <div class="calculator-title">⚖️ BMI 계산기</div>
            <div class="calculator-subtitle">키와 몸무게로 간단하게 BMI를 계산해 보세요.</div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        height = st.number_input("키 (cm)", value=170, min_value=50, max_value=250, key="c2_h")
    with col2:
        weight = st.number_input("몸무게 (kg)", value=65.0, min_value=10.0, max_value=300.0, key="c2_w")

    if st.button("BMI 계산하기", key="calc2_button"):
        if height > 0:
            bmi = weight / ((height / 100) ** 2)

            if bmi < 18.5:
                status = "저체중"
            elif bmi < 23:
                status = "정상"
            elif bmi < 25:
                status = "과체중"
            else:
                status = "비만"

            st.markdown("---")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("BMI", f"{bmi:.2f}")
            with col2:
                st.metric("판정", status)
            st.caption("※ BMI는 참고용 지표이며, 정확한 건강 상태는 전문가 상담이 필요합니다.")
        else:
            st.error("키는 0보다 크게 입력해주세요.")

    st.markdown("</div>", unsafe_allow_html=True)


# ---------------------
# 계산기 3 (예시: 환율)
# ---------------------
def calculator_three():
    st.markdown(
        """
        <div class="calculator-card">
            <div class="calculator-title">💱 환율 계산기</div>
            <div class="calculator-subtitle">원화를 기준으로 달러로 환산해 보세요.</div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        krw = st.number_input("원화 (KRW)", value=10000, step=1000, key="c3_krw")
    with col2:
        rate = st.number_input("환율 (1 USD = ? KRW)", value=1300.0, min_value=1.0, key="c3_rate")

    if st.button("USD로 계산하기", key="calc3_button"):
        usd = krw / rate
        st.markdown("---")
        st.metric("달러 환산 값", f"{usd:.2f} USD")
        st.caption("실제 환율/수수료에 따라 실제 금액은 달라질 수 있습니다.")

    st.markdown("</div>", unsafe_allow_html=True)


# ---------------------
# 메인 앱
# ---------------------
def main():
    # 상단 헤더
    st.markdown(
        """
        <div>
            <div class="main-title">통합 계산기 대시보드</div>
            <div class="main-subtitle">
                하나의 화면에서 여러 계산기를 편하게 사용할 수 있는 올인원 도구입니다. <br/>
                상단 탭에서 원하는 계산기를 선택하세요.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 탭
    tab1, tab2, tab3 = st.tabs(["기본 계산기", "BMI 계산기", "환율 계산기"])

    with tab1:
        calculator_one()

    with tab2:
        calculator_two()

    with tab3:
        calculator_three()


if __name__ == "__main__":
    main()
