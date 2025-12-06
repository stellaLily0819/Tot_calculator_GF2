import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# ---------------------
# 페이지 기본 설정
# ---------------------
st.set_page_config(
    page_title="통합 데미지 계산기",
    page_icon="🧮",
    layout="wide",
)

# ---------------------
# 커스텀 CSS (전부 문자열 안에 있음!) 
# ---------------------
st.markdown(
    """
    <style>
    /* 전체 배경 */
    .stApp {
        background: radial-gradient(circle at top left, #e0f2fe 0, #fdf2ff 35%, #ffffff 100%);
    }

    /* 내용 영역 여백 & 폭 */
    .block-container {
        padding-top: 4rem;   /* 🔽 제목 잘리지 않도록 위쪽 여백 */
        padding-bottom: 3rem;
        max-width: 1100px;
    }

    /* 상단 타이틀 영역 */
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        letter-spacing: -0.03em;
        margin-bottom: 0.3rem;
    }

    .main-subtitle {
        font-size: 0.95rem;
        color: #6b7280;
        margin-bottom: 1.4rem;
    }

    /* 계산기 카드 */
    .calculator-card {
        background: rgba(255, 255, 255, 0.92);
        border-radius: 20px;
        padding: 1.6rem 1.9rem;
        border: 1px solid rgba(148, 163, 184, 0.2);
        box-shadow: 0 18px 45px rgba(15, 23, 42, 0.10);
        backdrop-filter: blur(10px);
        margin-bottom: 1.5rem;
    }

    /* 탭 스타일 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 0.45rem 0.9rem;
        border-radius: 999px;
        background-color: rgba(255, 255, 255, 0.85);
        border: 1px solid rgba(148, 163, 184, 0.5);
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

# =========================================================
# 계산기 1 : 무기 효율 계산기
# =========================================================
def calculator_one():
    # ------- 내부 계산 함수 -------
    def compute_z(buff_x, buff_y, atk, E_def, def_coef, Weak_coef, sk_coef):
        numer = atk ** 2
        denomi = atk + E_def * (1 - def_coef * 0.01)
        return (
            (numer / denomi)
            * (1 + buff_x * 0.01)
            * (1 + Weak_coef * 0.1)
            * (sk_coef * 0.01)
            * (buff_y * 0.01)
        )

    st.markdown("<div class='calculator-card'>", unsafe_allow_html=True)

    st.markdown("### 🔧 무기 효율 계산기")
    st.caption("무기 A / B 옵션에 따른 최종 데미지와 효율 비교")

    # 사이드바 공통 변수
    st.sidebar.markdown(
        "<p style='text-align: center; font-size: 12px; color: gray;'>Made by Caleo01</p>",
        unsafe_allow_html=True
    )
    st.sidebar.markdown("---")
    st.sidebar.header("공통 변수 설정")
    E_def = st.sidebar.number_input("적 방어력", min_value=0.0, value=5000.0, max_value=20000.0, step=100.0, format="%.0f")
    atk_origin = st.sidebar.number_input("기초 공격력 (공% 제외 약 1600)", min_value=500.0, max_value=3000.0, value=1661.0, step=1.0, format="%.0f")
    atk_bonus = st.sidebar.number_input("기초 공격 보너스(%) (수정 X)", min_value=0.0, max_value=200.0, value=65.6, step=10.0, format="%.1f")
    def_coef = st.sidebar.number_input("방어 무시(%)", min_value=0.0, max_value=100.0, value=30.0, step=10.0, format="%.0f")
    Weak_coef = st.sidebar.number_input("약점 (개)", min_value=0.0, max_value=2.0, value=0.0, step=1.0, format="%.0f")
    sk_coef = st.sidebar.number_input("스킬 계수(%)", min_value=0.0, max_value=1500.0, value=100.0, step=10.0, format="%.0f")
    st.sidebar.markdown("---")
    buff_x = st.sidebar.number_input("피해 증가(%)", min_value=0.0, max_value=800.0, value=0.0, step=10.0, format="%.0f")
    buff_y = st.sidebar.number_input("치명 피해(%)", min_value=0.0, max_value=500.0, value=120.0, step=10.0, format="%.0f")

    # 직군
    st.subheader("인형 포지션")
    choice_doll = st.radio(
        "무기 옵션",
        options=["센티널", "뱅가드", "서포트", "불워크"],
        horizontal=True,
        key="Doll_option"
    )
    if choice_doll == "센티널":
        atk_per = 22.0
        ct_per = 0.0
    elif choice_doll == "뱅가드":
        atk_per = 17.0
        ct_per = 10.0
    elif choice_doll == "서포트":
        atk_per = 17.0
        ct_per = 0.0
    elif choice_doll == "불워크":
        atk_per = 0.0
        ct_per = 0.0
    st.markdown("---")

    # ----------------- 무기 A -----------------
    st.subheader("무기 A")

    col1, col2 = st.columns([2, 1])
    with col1:
        wep_atk_A_slider = st.slider("무기 공격력", 200.0, 390.0, 390.0, step=1.0, format="%.0f", key="wep_atk_A")
    with col2:
        wep_atk_A_input = st.number_input("직접 입력 (적용 값)", min_value=200.0, max_value=390.0, value=wep_atk_A_slider, step=1.0, format="%.0f", key="wep_atk_A_w")
    wep_atk_A = wep_atk_A_input

    wepA_ak = 0.0
    wepA_ct = 0.0
    choice_A = st.radio(
        "무기 옵션",
        options=["공격 보너스 15%", "치명타 피해 25%"],
        horizontal=True,
        key="weaponA_option"
    )
    if choice_A == "공격 보너스 15%":
        wepA_ak = 15.0
    elif choice_A == "치명타 피해 25%":
        wepA_ct = 25.0

    def_A = st.number_input("방어 무시(%)", min_value=0.0, max_value=20.0, value=0.0, step=10.0, format="%.0f", key="def_ignore_A")
    total_def_A = min(def_A + def_coef, 100.0)

    col1, col2 = st.columns([2, 1])
    with col1:
        dmg_A_slider = st.slider("무기 피증 계수 (합산)", 0.0, 100.0, 10.0, step=1.0, format="%.0f", key="dmg_buff_A")
    with col2:
        dmg_A_input = st.number_input("직접 입력 (적용 값)", min_value=0.0, max_value=100.0, value=dmg_A_slider, step=1.0, format="%.0f", key="dmg_buff_A_w")
    dmg_A = dmg_A_input

    st.write(f"관리실 공격력: {(atk_origin+wep_atk_A)*(1+(atk_bonus+atk_per+wepA_ak)*0.01):.0f}")

    st.markdown("---")

    # ----------------- 무기 B -----------------
    st.subheader("무기 B")

    col1, col2 = st.columns([2, 1])
    with col1:
        wep_atk_B_slider = st.slider("무기 공격력", 200.0, 390.0, 390.0, step=1.0, format="%.0f", key="wep_atk_B")
    with col2:
        wep_atk_B_input = st.number_input("직접 입력 (적용 값)", min_value=200.0, max_value=390.0, value=wep_atk_B_slider, step=1.0, format="%.0f", key="wep_atk_B_w")
    wep_atk_B = wep_atk_B_input

    wepB_ak = 0.0
    wepB_ct = 0.0
    choice_B = st.radio(
        "무기 옵션",
        options=["공격 보너스 15%", "치명타 피해 25%"],
        horizontal=True,
        key="weaponB_option"
    )
    if choice_B == "공격 보너스 15%":
        wepB_ak = 15.0
    elif choice_B == "치명타 피해 25%":
        wepB_ct = 25.0

    def_B = st.number_input("방어 무시(%)", min_value=0.0, max_value=20.0, value=0.0, step=10.0, format="%.0f", key="def_ignore_B")
    total_def_B = min(def_B + def_coef, 100.0)

    col1, col2 = st.columns([2, 1])
    with col1:
        dmg_B_slider = st.slider("무기 피증 계수 (합산)", 0.0, 100.0, 10.0, step=1.0, format="%.0f", key="dmg_buff_B")
    with col2:
        dmg_B_input = st.number_input("직접 입력 (적용 값)", min_value=0.0, max_value=100.0, value=dmg_B_slider, step=1.0, format="%.0f", key="dmg_buff_B_w")
    dmg_B = dmg_B_input

    st.write(f"관리실 공격력: {(atk_origin+wep_atk_B)*(1+(atk_bonus+atk_per+wepB_ak)*0.01):.0f}")

    st.markdown("---")

    # 결과 계산
    final_dmg_A = buff_x + dmg_A
    final_dmg_B = buff_x + dmg_B
    final_ct_A = buff_y + wepA_ct + ct_per
    final_ct_B = buff_y + wepB_ct + ct_per
    final_atk_A = (atk_origin+wep_atk_A)*(1+(atk_bonus+atk_per+wepA_ak)*0.01)
    final_atk_B = (atk_origin+wep_atk_B)*(1+(atk_bonus+atk_per+wepB_ak)*0.01)
    damage_A = compute_z(final_dmg_A, final_ct_A, final_atk_A, E_def, total_def_A, Weak_coef, sk_coef)
    damage_B = compute_z(final_dmg_B, final_ct_B, final_atk_B, E_def, total_def_B, Weak_coef, sk_coef)

    diff = damage_B - damage_A
    efficiency = (damage_B / damage_A - 1) * 100 if damage_A != 0 else 0

    if diff > 0:
        st.success(f"무기 B가 {diff:,.0f} 데미지만큼 강력하며, 효율은 {efficiency:.2f}% 더 좋습니다.")
    elif diff < 0:
        st.error(f"무기 A가 {-diff:,.0f} 데미지만큼 강력하며, 효율은 {-efficiency:.2f}% 더 좋습니다.")
    else:
        st.info("무기 A와 B의 최종 데미지가 동일합니다.")

    st.write("피증 변화만을 고려한 데미지 변화 (세로선 - 무기 포함 최종 데미지)")
    st.markdown(f"""
    **참고:**  
    - 파란 점선 = 무기 A 현재 공격력 ({final_atk_A:.0f})  
    - 빨간 점선 = 무기 B 현재 공격력 ({final_atk_B:.0f})  
    """)

    atk_range = np.linspace(0, 8000, 200)
    damage_curve_A = [
        compute_z(final_dmg_A, final_ct_A, atk, E_def, total_def_A, Weak_coef, sk_coef)
        for atk in atk_range
    ]
    damage_curve_B = [
        compute_z(final_dmg_B, final_ct_B, atk, E_def, total_def_B, Weak_coef, sk_coef)
        for atk in atk_range
    ]
    efficiency_curve = [(b/a - 1) * 100 if a != 0 else 0 for a, b in zip(damage_curve_A, damage_curve_B)]

    fig, ax1 = plt.subplots(figsize=(9, 6))

    ax1.plot(atk_range, damage_curve_A, label="Weapon A", color="blue")
    ax1.plot(atk_range, damage_curve_B, label="Weapon B", color="red")
    ax1.axvline(final_atk_A, color="blue", linestyle=":")
    ax1.axvline(final_atk_B, color="red", linestyle=":")
    ax1.set_xlabel("ATK")
    ax1.set_ylabel("Final Damage")
    ax1.legend(loc="upper left")
    ax1.grid(True)

    ax2 = ax1.twinx()
    ax2.plot(atk_range, efficiency_curve, label="Efficiency (B vs A, %)", color="green", linestyle="--")
    ax2.set_ylabel("Efficiency (%)")
    ax2.axhline(0, color="black", linestyle=":")
    ax2.legend(loc="upper right")

    st.pyplot(fig)

    st.markdown("</div>", unsafe_allow_html=True)


# =========================================================
# 계산기 2 : 실시간 데미지 계산 3D 그래프
# =========================================================
def calculator_two():
    # z 계산 함수
    def compute_z(x, y, atk, defense, w, skill, multiplier):
        numerator = atk ** 2
        denominator = atk + defense * (1 - w * 0.01)
        return (numerator / denominator) * (1 + x * 0.01) * multiplier * (skill * 0.01) * (y * 0.01)

    st.markdown("<div class='calculator-card'>", unsafe_allow_html=True)

    st.markdown("### 📈 실시간 데미지 계산 3D 그래프")
    st.markdown(
        """<p style='font-size: 12px; color: gray;'>
        Made by Caleo01 | Powered by Streamlit
        </p>""",
        unsafe_allow_html=True
    )

    st.latex(r'''\small
    z = \left( \frac{{\text{공격력}^2}}{{\text{공격력} + \text{적 방어력} \cdot (1 - 방깎)}} \right)
    \cdot (피증) \cdot (약점계수) \cdot (스킬계수) \cdot (치피)
    ''')

    multiplier = st.radio("약점 계수:", [1.0, 1.1, 1.2], index=0, horizontal=True)
    skill = st.slider("스킬 계수 %", 10, 800, 100, step=10)
    st.markdown("---")
    atk = st.slider("공격력", 0, 8000, 1000, step=10)
    defense = st.slider("적 방어력", 0, 7000, 1000, step=10)
    w = st.slider("방어감소 %", 0, 100, 50, step=10)
    x = st.slider("피해증가 %", 0, 500, 100, step=10)
    y = st.slider("치명피해 %", 0, 400, 100, step=10)

    z_val = compute_z(x, y, atk, defense, w, skill, multiplier)
    st.write(f"약점 계수 값: {multiplier}")
    st.write(f"스킬 계수 값: {skill}")
    st.markdown("---")
    st.markdown(f"### 실제 데미지 (z): `{z_val:.2f}`")

    x_vals = np.linspace(0, 400, 50)
    y_vals = np.linspace(0, 500, 50)
    X, Y = np.meshgrid(x_vals, y_vals)
    Z = compute_z(X, Y, atk, defense, w, skill, multiplier)

    fig = plt.figure(figsize=(10, 7))
    ax = fig.add_subplot(111, projection='3d')
    surf = ax.plot_surface(X, Y, Z, cmap='plasma', edgecolor='none', alpha=0.8)
    ax.scatter(x, y, z_val, color='red', s=50, label='Current')
    ax.set_xlabel('Dmg Increase (%)')
    ax.set_ylabel('Crit (%)')
    ax.set_zlabel('Actual Dmg')
    ax.set_title(f'3D Dmg Graph (atk={atk}, def={defense}, w={w}%)')
    ax.legend()

    st.pyplot(fig)

    st.markdown("</div>", unsafe_allow_html=True)


# =========================================================
# 계산기 3 : (추가용 자리)
# =========================================================
def calculator_three():
    st.markdown("<div class='calculator-card'>", unsafe_allow_html=True)
    st.markdown("### 🧪 계산기 3 (추가 예정)")
    st.info("여기에 3번 계산기 코드를 넣으면 됩니다.")
    st.markdown("</div>", unsafe_allow_html=True)


# =========================================================
# 메인 앱
# =========================================================
def main():
    st.markdown(
        """
        <div>
            <div class="main-title">통합 데미지 계산 대시보드</div>
            <div class="main-subtitle">
                무기 효율 비교, 실시간 데미지 3D 그래프 등 여러 계산기를 하나의 화면에서 사용하세요.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tab1, tab2, tab3 = st.tabs(["무기 효율 계산기", "3D 데미지 그래프", "계산기 3"])

    with tab1:
        calculator_one()
    with tab2:
        calculator_two()
    with tab3:
        calculator_three()


if __name__ == "__main__":
    main()
