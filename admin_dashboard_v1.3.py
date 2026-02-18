import streamlit as st
import os

# --- Page Config (전체 앱에서 1번만 호출) ---
st.set_page_config(
    page_title="Olist Admin Dashboard",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Olist Blog 스타일 CSS ---
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
<style>
    /* ===== 전역 기본 스타일 (Olist Blog) ===== */
    html, body, [class*="st-"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    .main, [data-testid="stAppViewMain"] {
        background-color: #f3f3fc !important;
    }

    /* ===== 사이드바 (Olist Dark Blue) ===== */
    [data-testid="stSidebar"] {
        background: #0b134a;
        border-right: 1px solid #1a2266;
        min-width: 477px !important;
        max-width: 477px !important;
        width: 477px !important;
    }
    [data-testid="stSidebar"] * {
        color: #c8cce6 !important;
    }
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #ffffff !important;
    }
    [data-testid="stSidebar"] .stRadio label {
        font-size: 14px;
        font-weight: 500;
    }

    /* 사이드바 라디오 버튼 스타일 */
    [data-testid="stSidebar"] div[role="radiogroup"] > label {
        padding: 10px 16px;
        border-radius: 8px;
        margin-bottom: 2px;
        transition: all 0.2s ease;
        cursor: pointer;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] > label:hover {
        background-color: rgba(255, 255, 255, 0.1) !important;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) {
        background-color: rgba(255, 255, 255, 0.18) !important;
        border: 1px solid rgba(255, 255, 255, 0.25) !important;
        font-weight: 700 !important;
        box-shadow: none !important;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) span {
        color: #ffffff !important;
    }

    /* 사이드바 구분선 */
    [data-testid="stSidebar"] hr {
        border-color: rgba(255,255,255,0.1) !important;
    }

    /* 라디오 버튼 원형 아이콘 숨기기 (전역) */
    div[data-testid="stRadio"] div[role="radiogroup"] > label > div:first-child {
        display: none !important;
    }

    /* ===== 메트릭 카드 스타일 ===== */
    [data-testid="stMetricValue"] {
        font-size: 28px;
        font-weight: 800;
        color: #0b134a;
    }
    [data-testid="stMetricLabel"] {
        font-size: 14px;
        color: #696d8c;
        font-weight: 500;
    }
    div[data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid #e6eeff;
        border-radius: 12px;
        padding: 24px 20px;
        box-shadow: 0 1px 4px rgba(11, 19, 74, 0.06);
    }

    /* ===== 헤딩 스타일 (H1: 인사이트와 동일한 36px White) ===== */
    h1 {
        color: #ffffff !important;
        font-weight: 900 !important;
        font-size: 36px !important;
        letter-spacing: -1px;
        margin: 0 !important;
        padding: 0 !important;
    }
    h2 {
        color: #312f4f !important;
        font-weight: 700 !important;
        font-size: 28px !important;
        margin-bottom: 16px !important;
    }
    h3 {
        color: #50557c !important;
        font-weight: 600 !important;
        font-size: 20px !important;
    }
    p, li, label, div {
        font-size: 16px;
    }

    /* ===== 다크 헤더 섹션 (H1용) ===== */
    .header-container {
        background: linear-gradient(135deg, #0b134a 0%, #0c29d0 100%);
        padding: 30px 40px;
        border-radius: 16px;
        margin-bottom: 30px;
        box-shadow: 0 10px 30px rgba(11, 19, 74, 0.15);
        color: #ffffff;
    }

    /* ===== 탭 스타일 (Olist Blue 밑줄 탭) ===== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0px;
        border-bottom: 2px solid #d1d1e3;
        background: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        height: 48px;
        padding: 0 24px;
        background: transparent;
        border: none;
        border-radius: 0;
        color: #696d8c;
        font-weight: 500;
        font-size: 15px;
        white-space: nowrap;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: #0b134a;
    }
    .stTabs [aria-selected="true"] {
        color: #0c29d0 !important;
        font-weight: 700;
        border-bottom: 3px solid #0c29d0;
        background: transparent;
    }
    .stTabs [data-baseweb="tab-highlight"] {
        background-color: #0c29d0 !important;
    }

    /* ===== 본문 서브 메뉴 전용: 프리미엄 세그먼트 컨트롤 (Segmented Control) ===== */
    /* 사이드바가 아닌 모든 라디오 영역을 버튼 형태로 강제 */
    [data-testid="stAppViewMain"] div[data-testid="stRadio"] div[role="radiogroup"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: wrap !important;
        gap: 12px !important;
        background-color: #eff3f8 !important;
        padding: 12px !important;
        border-radius: 20px !important;
        border: 2px solid #e2e8f0 !important;
        margin: 25px 0 !important;
        width: 100% !important;
        box-shadow: inset 0 2px 5px rgba(0,0,0,0.04) !important;
    }

    [data-testid="stAppViewMain"] div[data-testid="stRadio"] div[role="radiogroup"] label {
        flex: 1 !important;
        min-width: 200px !important; /* 충분한 너비 확보 */
        background-color: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 12px !important;
        padding: 15px 20px !important;
        margin: 0 !important;
        cursor: pointer !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
        text-align: center !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05) !important;
    }

    [data-testid="stAppViewMain"] div[data-testid="stRadio"] div[role="radiogroup"] label:hover {
        background-color: #f8fafc !important;
        border-color: #0c29d0 !important;
        transform: translateY(-3px) !important;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1) !important;
    }

    /* 초강력 활성 상태 (Active State) */
    [data-testid="stAppViewMain"] div[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) {
        background-color: #0c29d0 !important;
        color: #ffffff !important;
        border-color: #0b134a !important;
        font-weight: 800 !important;
        box-shadow: 0 12px 20px -3px rgba(12, 41, 208, 0.4) !important;
        transform: scale(1.03) !important;
    }

    [data-testid="stAppViewMain"] div[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) p,
    [data-testid="stAppViewMain"] div[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) span {
        color: #ffffff !important;
        font-weight: 800 !important;
    }

    [data-testid="stAppViewMain"] div[data-testid="stRadio"] div[role="radiogroup"] label p {
        font-size: 15px !important;
        color: #1e293b !important;
        margin: 0 !important;
        font-weight: 700 !important;
    }

    /* 라디오 버튼 원형 아이콘 완전 제거 */
    div[data-testid="stRadio"] div[data-testid="stRadioButton"] {
        display: none !important;
    }
    div[data-testid="stRadio"] label > div:first-child {
        display: none !important;
    }

    /* ===== 데이터프레임 / 테이블 ===== */
    [data-testid="stDataFrame"] {
        background: #ffffff;
        border-radius: 12px;
        border: 1px solid #e6eeff;
        overflow: hidden;
    }

    /* ===== 버튼 스타일 (초록색 그라데이션 적용) ===== */
    /* Primary 버튼 (#FF4B4B 대체) */
    .main button[data-testid="stBaseButton-primary"] {
        background: linear-gradient(90deg, #9fc16e 0%, #94d8cf 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        box-shadow: 0 4px 10px rgba(159, 193, 110, 0.3) !important;
        padding: 8px 20px !important;
        transition: all 0.3s ease !important;
    }
    .main button[data-testid="stBaseButton-primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 15px rgba(159, 193, 110, 0.5) !important;
        opacity: 0.9 !important;
    }

    /* Secondary 버튼 (화이트/그레이 스타일) */
    .main button[data-testid="stBaseButton-secondary"] {
        background-color: #ffffff !important;
        color: #475569 !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        padding: 8px 20px !important;
        transition: all 0.2s ease !important;
    }
    .main button[data-testid="stBaseButton-secondary"]:hover {
        background-color: #f8fafc !important;
        border-color: #0c29d0 !important;
        color: #0c29d0 !important;
    }

    /* ===== Expander 스타일 (아이콘 겹침 방지) ===== */
    .streamlit-expanderHeader {
        background: #ffffff !important;
        border: 1px solid #d1d1e3 !important;
        border-radius: 12px !important;
        padding: 10px 15px !important;
        font-weight: 700 !important;
        color: #1e293b !important;
    }
    .streamlit-expanderHeader:hover {
        border-color: #9fc16e !important;
        background-color: #f8fafc !important;
    }
    /* 익스팬더 내부 아이콘 텍스트화 방지 */
    .streamlit-expanderHeader svg {
        fill: #9fc16e !important;
    }

    /* ===== 구분선 ===== */
    hr {
        border: none;
        border-top: 1px solid #d1d1e3;
        margin: 16px 0;
    }

    /* ===== 알림 배너 ===== */
    .stAlert {
        border-radius: 10px;
        border: none;
    }

    /* ===== Plotly 차트 컨테이너 ===== */
    [data-testid="stPlotlyChart"],
    .stPlotlyChart {
        background: #ffffff;
        border-radius: 12px;
        padding: 8px;
        border: 1px solid #e6eeff;
        box-shadow: 0 1px 4px rgba(11, 19, 74, 0.06);
    }

    /* ===== 스크롤바 ===== */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: #f3f3fc; }
    ::-webkit-scrollbar-thumb { background: #d1d1e3; border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: #9ea2c0; }

    /* ===== 셀러 탭 전용 카드 스타일 (전역화) ===== */
    .sub-card {
        padding: 16px 20px; border-radius: 12px;
        border-left: 6px solid #d1d1e3; margin: 6px 0;
        background: #ffffff;
        box-shadow: 0 1px 4px rgba(11, 19, 74, 0.06);
    }
    .sub-card.t1 { border-left-color: #0c29d0; background: #e6eeff; }
    .sub-card.t2 { border-left-color: #50557c; background: #f3f3fc; }
    .sub-card.t3 { border-left-color: #d1d1e3; background: #ffffff; }
    
    /* ===== 공통 강조 텍스트 ===== */
    .highlight {
        color: #0c29d0;
        font-weight: 700;
    }
    /* ===== 맥킨지(McKinsey) 스타일 리포트 전용 CSS ===== */
    .mck-header {
        background-color: #041E42;
        color: white;
        padding: 20px;
        border-radius: 4px;
        margin-bottom: 25px;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    .mck-headline {
        font-size: 24px;
        font-weight: 700;
        line-height: 1.3;
        margin-bottom: 5px;
    }
    .mck-sub-headline {
        font-size: 14px;
        font-weight: 300;
        opacity: 0.8;
    }
    .mck-section-title {
        color: #041E42;
        font-size: 20px;
        font-weight: 700;
        border-bottom: 3px solid #041E42;
        padding-bottom: 8px;
        margin-top: 40px;
        margin-bottom: 20px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .mck-insight-box {
        background-color: #f0f2f6;
        border-left: 6px solid #041E42;
        padding: 20px;
        margin: 15px 0;
        border-radius: 0 4px 4px 0;
    }
    .mck-action-item {
        background-color: #e6f0ff;
        border: 1px solid #cce0ff;
        padding: 15px;
        border-radius: 4px;
        margin-top: 10px;
    }
    .mck-label {
        font-weight: 700;
        color: #041E42;
        font-size: 13px;
        text-transform: uppercase;
        margin-bottom: 5px;
        display: block;
    }
    .mck-so-what {
        font-style: italic;
        color: #50557c;
        font-size: 14px;
        margin-top: 10px;
        padding-top: 10px;
        border-top: 1px dashed #d1d1e3;
    }
    /* ===== 고정 높이 메트릭 카드 (UI 통일용) ===== */
    .metric-card {
        background: white;
        padding: 15px 20px;
        border-radius: 12px;
        border: 1px solid #e6eeff;
        box-shadow: 0 1px 4px rgba(11, 19, 74, 0.06);
        height: 110px; /* 고정 높이 */
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        margin-bottom: 20px;
    }
    .metric-card .label {
        font-size: 13px;
        color: #666;
        font-weight: 500;
    }
    .metric-card .value {
        font-size: 22px;
        font-weight: 700;
        color: #041E42;
        margin: 4px 0;
    }
    .metric-card .delta {
        font-size: 12px;
        color: #10b981;
        background: #e6fffa;
        padding: 2px 8px;
        border-radius: 4px;
        width: fit-content;
        font-weight: 600;
    }
    .metric-card .delta-empty {
        height: 20px; /* 델타가 없을 때도 공간 차지 */
    }
</style>
""", unsafe_allow_html=True)


# --- 프로젝트 기본 경로 설정 ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data_commerce")

# --- 사이드바 네비게이션 ---
import base64

_logo_html = f'<img src="https://d3hw41hpah8tvx.cloudfront.net/images/logo_ecossistema_66f532e37b.svg" style="width: 235px; height: 47px; object-fit: contain;" />'

st.sidebar.markdown(f"""
<div style="text-align: center; padding: 24px 0 16px 0; border-bottom: 1px solid rgba(255,255,255,0.1); margin-bottom: 24px;">
    <div style="margin: 0 auto 16px; width: 235px;">
        {_logo_html}
    </div>
    <p style="font-size: 14px; color: #8b8fb0 !important; margin-top: 6px; font-weight: 400;">어드민 대시보드</p>
</div>
""", unsafe_allow_html=True)


# --- 세션 상태 초기화 및 네비게이션 처리 ---
PAGES = [
    "📉 고객 구매 여정 가시성 센터 (Journey Visibility)",
    "👀 탐색 및 발견 (Discovery)",
    "💳 구매 전환 (Decision)",
    "🚚 물류 및 경험 (Fulfillment)",
    "🏢 파트너십 가치 (Partnership)",
    "💎 로열티 및 개선 (Loyalty)"
]

if "main_menu" not in st.session_state:
    st.session_state["main_menu"] = PAGES[0]

# 현재 세션 상태에 기반하여 라디오 인덱스 계산
try:
    current_index = PAGES.index(st.session_state["main_menu"])
except ValueError:
    current_index = 0

# 라디오 위젯 (key를 사용하지 않고 index와 on_change 대신 리턴값 활용)
menu = st.sidebar.radio(
    "분석 영역",
    PAGES,
    index=current_index,
    label_visibility="collapsed"
)

# 메뉴 선택이 변경된 경우 세션 상태 업데이트 및 리런
if menu != st.session_state["main_menu"]:
    st.session_state["main_menu"] = menu
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style="padding: 14px 16px; background: rgba(12, 41, 208, 0.15); border-radius: 10px; border: 1px solid rgba(255,255,255,0.08);">
    <p style="font-size: 12px; margin: 0; color: #c8cce6 !important; line-height: 1.6;">
        <b style="color: #ffffff !important; font-weight: 700;">📂 데이터 소스</b><br>
        Olist Public Dataset<br>
        <span style="color: #8b8fb0 !important;">2016-09 ~ 2018-09</span>
    </p>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("")
st.sidebar.caption("© 2026 Olist Customer Journey Project")

# --- 상단 다크 헤더 섹션 (Breadcrumb + H1) ---
menu_name_clean = menu.split(' ', 1)[1] if ' ' in menu else menu

# --- 글로벌 뒤로가기 버튼 (KPI 탭 제외) ---
if menu != "📉 고객 구매 여정 가시성 센터 (Journey Visibility)":
    # 스타일 커스텀: 뒤로가기 버튼 전용
    st.markdown("""
        <style>
            div.stButton > button[key="global_back_to_kpi"] {
                background-color: #ffffff !important;
                color: #475569 !important;
                border: 1px dashed #cbd5e1 !important;
                border-radius: 8px !important;
                padding: 6px 16px !important;
                font-size: 13px !important;
                font-weight: 600 !important;
                margin-bottom: 10px !important;
                height: auto !important;
            }
            div.stButton > button[key="global_back_to_kpi"]:hover {
                border-color: #0c29d0 !important;
                color: #0c29d0 !important;
                background-color: #f8fafc !important;
            }
        </style>
    """, unsafe_allow_html=True)
    
    col_back, col_dummy = st.columns([1.2, 8.8])
    with col_back:
        if st.button("⇠ 뒤로 가기 (KPI 홈)", key="global_back_to_kpi", use_container_width=True):
            st.session_state["main_menu"] = "📉 고객 구매 여정 가시성 센터 (Journey Visibility)"
            st.rerun()

st.markdown(f"""
    <div class="header-container">
        <div>
            <p style="color: rgba(255,255,255,0.8); margin-bottom: 4px; font-size: 14px; font-weight: 500;">
                Olist Data Intelligence • <b>Journey Visibility Center</b>
            </p>
            <h1>{menu}</h1>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- 메뉴별 탭 렌더링 ---
if menu == "📉 고객 구매 여정 가시성 센터 (Journey Visibility)":
    from tabs.tab_total_kpi_v1_3 import render
    render(BASE_DIR, DATA_DIR)

elif menu == "👀 탐색 및 발견 (Discovery)":
    from tabs.tab_product_v1_3 import render
    render(BASE_DIR, DATA_DIR)

elif menu == "💳 구매 전환 (Decision)":
    from tabs.tab_price_v1_3 import render
    render(BASE_DIR, DATA_DIR)

elif menu == "🚚 물류 및 경험 (Fulfillment)":
    from tabs.tab_delivery_v1_3 import render
    render(BASE_DIR, DATA_DIR)

elif menu == "🏢 파트너십 가치 (Partnership)":
    from tabs.tab_seller_v1_3 import render
    render(BASE_DIR, DATA_DIR)

elif menu == "💎 로열티 및 개선 (Loyalty)":
    from tabs.tab_strategy_v1_3 import render
    render(BASE_DIR, DATA_DIR)

