import streamlit as st

# ---------------------
# 1. 계산기 1 (예: 단순 사칙연산)
# ---------------------
def calculator_one():
    st.subheader("계산기 1 : 사칙연산")

    a = st.number_input("첫 번째 숫자", value=0.0)
    b = st.number_input("두 번째 숫자", value=0.0)
    op = st.selectbox("연산자", ["+", "-", "*", "/"])

    if st.button("계산하기", key="calc1_button"):
        if op == "+":
            result = a + b
        elif op == "-":
            result = a - b
        elif op == "*":
            result = a * b
        else:
            result = a / b if b != 0 else "0으로 나눌 수 없습니다."

        st.success(f"결과: {result}")


# ---------------------
# 2. 계산기 2 (예: BMI 계산기)
# ---------------------
def calculator_two():
    st.subheader("계산기 2 : BMI 계산")

    height = st.number_input("키(cm)", value=170)
    weight = st.number_input("몸무게(kg)", value=65)

    if st.button("BMI 계산", key="calc2_button"):
        if height > 0:
            bmi = weight / ((height / 100) ** 2)
            st.success(f"BMI: {bmi:.2f}")
        else:
            st.error("키를 0보다 크게 입력해주세요.")


# ---------------------
# 3. 계산기 3 (예: 환율 계산기)
# ---------------------
def calculator_three():
    st.subheader("계산기 3 : 환율 계산")

    krw = st.number_input("원화 (KRW)", value=1000)
    rate = st.number_input("환율 (예: 1 USD = ? KRW)", value=1300.0)

    if st.button("달러로 바꾸기", key="calc3_button"):
        if rate > 0:
            usd = krw / rate
            st.success(f"약 {usd:.2f} USD")
        else:
            st.error("환율은 0보다 커야 합니다.")


# ---------------------
# 메인 앱
# ---------------------
def main():
    st.set_page_config(page_title="통합 계산기", layout="centered")
    st.title("통합 계산기 사이트")

    tab1, tab2, tab3 = st.tabs(["계산기 1", "계산기 2", "계산기 3"])

    with tab1:
        calculator_one()

    with tab2:
        calculator_two()

    with tab3:
        calculator_three()


if __name__ == "__main__":
    main()
