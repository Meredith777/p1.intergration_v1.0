import streamlit as st
import pandas as pd
import os
from PIL import Image


def render(base_dir, data_dir):
    """상품 분석 탭 렌더링"""

    # --- 0. UX 최적화: 커스텀 세그먼트 컨트롤 (Fail-safe 스타일) ---
    st.markdown("""
        <style>
            /* 커스텀 버튼 탭 바 컨테이너 */
            .custom-tab-container {
                display: flex;
                gap: 12px;
                padding: 12px;
                background-color: #f1f5f9;
                border-radius: 20px;
                border: 2px solid #e2e8f0;
                margin: 20px 0 30px 0;
            }
            /* 기본 버튼 스타일 무력화 및 커스텀 스타일 입히기 */
            div.stButton > button {
                border-radius: 12px !important;
                font-weight: 700 !important;
                transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
                padding: 10px 20px !important;
            }
            /* 활성 탭 (Primary) */
            div.stButton > button[kind="primary"] {
                background: linear-gradient(90deg, #9fc16e 0%, #94d8cf 100%) !important;
                color: #ffffff !important;
                border: none !important;
                box-shadow: 0 4px 12px rgba(159, 193, 110, 0.4) !important;
            }
            /* 비활성 탭 (Secondary) */
            div.stButton > button[kind="secondary"] {
                background-color: #ffffff !important;
                color: #64748b !important;
                border: 1px solid #e2e8f0 !important;
            }
            div.stButton > button[kind="secondary"]:hover {
                border-color: #9fc16e !important;
                color: #9fc16e !important;
                background-color: #f8fafc !important;
            }
        </style>
    """, unsafe_allow_html=True)

    # --- 상단 내비게이션 (뒤로 가기) ---


    st.markdown("<br>", unsafe_allow_html=True)

    # 내부 서브메뉴 데이터 및 상태 관리
    tabs = [
        "📉 여정의 불편: 탐색 단계 병목 진단", 
        "💎 경험의 가치: 카테고리별 핵심 가치", 
        "💳 구매 전환: 최적 가격대 식별", 
        "🚀 성장의 개선: 전환 최적화 가이드"
    ]
    
    if "product_sub_menu" not in st.session_state:
        st.session_state["product_sub_menu"] = tabs[0]

    # 세그먼트 컨트롤 시뮬레이션 (Columns + Buttons)
    # 이것은 CSS 캐시 문제와 무관하게 100% 확실하게 버튼 형태로 렌더링됩니다.
    col_t1, col_t2, col_t3, col_t4 = st.columns(4)
    tab_cols = [col_t1, col_t2, col_t3, col_t4]
    
    for i, tab_name in enumerate(tabs):
        is_active = st.session_state["product_sub_menu"] == tab_name
        if tab_cols[i].button(
            tab_name, 
            key=f"tab_btn_{i}", 
            use_container_width=True,
            type="primary" if is_active else "secondary"
        ):
            st.session_state["product_sub_menu"] = tab_name
            st.rerun()

    sub_menu = st.session_state["product_sub_menu"]
    st.markdown("---")

    # 이미지 경로 설정
    IMAGE_DIR = os.path.join(base_dir, "draft", "product", "images")



    # --- 1. 홈 / 분석 개요 ---
    if sub_menu == "📉 여정의 불편: 탐색 단계 병목 진단":
        st.header("📝 여정의 불편: 탐색 단계 병목 진단 (Summary)")
        st.success("""
        본 분석은 브라질 최대 이커머스 Olist의 데이터를 바탕으로 **카테고리별 성과, 가격 전략, 제품 정보 품질**의 상관관계를 심층 분석했습니다.
        특히 매출을 견인하는 핵심 가격대(200-500 BRL)와 물량을 확보하는 주력 카테고리를 식별하여 향후 비즈니스 성장을 위한 구체적인 전략 방향을 제시합니다.
        """)

        st.header("💎 경험의 가치: 제품 정보의 신뢰도 영향 (Background)")
        st.markdown("""
        이커머스 시장의 경쟁이 심화됨에 따라 데이터 기반의 **제품 전략 최적화**가 필수적입니다.
        단순히 많이 파는 것을 넘어, 어떤 가격대에서 수익성이 극대화되는지, 배송비와 제품 정보(사진, 설명)가 실제 구매 전환에 어떤 영향을 미치는지 파악하여 플랫폼 운영 효율을 높이고자 분석을 수행했습니다.
        """)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("""
                <div class="metric-card">
                    <div class="label">데이터 개수</div>
                    <div class="value">100k+</div>
                    <div class="delta">↑ Orders</div>
                </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown("""
                <div class="metric-card">
                    <div class="label">분석 기간</div>
                    <div class="value">2년</div>
                    <div class="delta">↑ 2016-2018</div>
                </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown("""
                <div class="metric-card">
                    <div class="label">최종 업데이트</div>
                    <div class="value">2026-02-14</div>
                    <div class="delta-empty"></div>
                </div>
            """, unsafe_allow_html=True)

        st.header("🚀 성장의 개선: 전환율 극대화 로드맵")
        st.markdown("""
        1. **제품 특성 영향도:** 이름 길이, 설명 길이, 사진 개수가 구매 및 만족도에 미치는 영향 분석.
        2. **가격 전략:** 최적의 판매 가격대 도출 및 매출-수량 분포 확인.
        3. **카테고리 성과:** 주력 카테고리의 매출 효율성(단가) 및 성장 추세 분석.
        """)

        st.header("🏁 결론 (Conclusion)")
        st.info("""
        - **가격 전략:** '200-500 BRL' 구간은 전체 매출의 30%를 차지하는 핵심 수익원이므로 해당 가격대 상품의 강화가 필요합니다.
        - **운영 최적화:** 제품 정보(사진 2~4장, 이름 40~60자)의 품질을 표준화할 때 구매 전환율이 가장 높게 나타납니다.
        - **성장 동력:** `bed_bath_table`과 같은 고물량 카테고리와 `watches_gifts`와 같은 고효율 카테고리의 전략적 배분을 통해 전체 매출 성장을 도모해야 합니다.
        """)

    # --- 2. 상위 카테고리 성과 ---
    elif sub_menu == "💎 경험의 가치: 카테고리별 핵심 가치":
        st.header("💎 경험의 가치: 카테고리별 수익 기여도 분석")
        st.subheader("2-1. 상위 10개 카테고리 성과 (매출, 수량, 효율성)")

        img_path_v3 = os.path.join(IMAGE_DIR, "top_products", "top10_revenue_quantity_v3.png")
        if os.path.exists(img_path_v3):
            st.image(img_path_v3, caption="Top 10 Category Performance", use_container_width=True)
        else:
            st.warning("📷 이미지 파일이 없습니다: `images/top_products/top10_revenue_quantity_v3.png`")

        st.markdown("#### 상위 10개 카테고리 상세 데이터")
        data_top10 = {
            "카테고리": ["bed_bath_table", "health_beauty", "computers_accessories", "furniture_decor", "watches_gifts", "sports_leisure", "housewares", "auto", "garden_tools", "telephony"],
            "총 매출액(BRL)": [1744000, 1662960, 1599480, 1443960, 1430550, 1400220, 1097900, 855096, 840722, 487190],
            "매출 비중": ["8.5%", "8.1%", "7.8%", "7.1%", "7.0%", "6.9%", "5.4%", "4.2%", "4.1%", "2.4%"],
            "판매 수량": [11988, 10032, 8150, 8832, 6213, 9004, 7380, 4400, 4590, 4726],
            "개당 평균가(BRL)": [145.5, 165.8, 196.3, 163.5, 230.3, 155.5, 148.8, 194.3, 183.2, 103.1]
        }
        st.table(pd.DataFrame(data_top10))

        st.markdown("""
        #### 💡 상위 10개 카테고리 주요 인사이트
        - **수익성 및 효율성 분석:** 상위 10개 카테고리 중 `watches_gifts`(230.3 BRL)와 `computers_accessories`(196.3 BRL)가 개당 평균 판매가가 가장 높아, 판매 수량 대비 높은 매출 효율성을 보입니다.
        - **물량 중심 카테고리:** `bed_bath_table`은 매출 순위 1위(매출 비중 8.5%)이며 동시에 가장 많은 판매 수량(11,988건)을 기록하고 있어, 서비스 성장을 견인하는 핵심 볼륨 엔진 역할을 하고 있습니다.
        - **상관관계 확인:** 매출 규모와 판매 단가는 정비례하지 않으며, 단가가 낮은 `telephony`(103.1 BRL)와 같은 카테고리는 많은 수량 판매를 통해 매출 상위권을 유지하고 있습니다.
        - **시즌성 추이:** 2017년 하반기(특히 11월)부터 모든 카테고리에서 판매량이 급증하며, 이는 대규모 프로모션(블랙 프라이데이 등)이 전 카테고리의 성장을 이끌고 있음을 시사합니다.
        """)

        st.subheader("2-2. 상위 5개 카테고리 심층 분석 (Deep Dive)")
        col1, col2 = st.columns(2)
        with col1:
            img_q = os.path.join(IMAGE_DIR, "top5_deepdive", "top5_quantity_trend.png")
            if os.path.exists(img_q):
                st.image(img_q, caption="수량 추이")
            else:
                st.warning("📷 이미지 파일 없음: `top5_quantity_trend.png`")
        with col2:
            img_a = os.path.join(IMAGE_DIR, "top5_deepdive", "top5_amount_trend.png")
            if os.path.exists(img_a):
                st.image(img_a, caption="금액 추이")
            else:
                st.warning("📷 이미지 파일 없음: `top5_amount_trend.png`")

        img_e = os.path.join(IMAGE_DIR, "top5_deepdive", "top5_efficiency_comparison.png")
        if os.path.exists(img_e):
            st.image(img_e, caption="효율성 비교", use_container_width=True)
        else:
            st.warning("📷 이미지 파일 없음: `top5_efficiency_comparison.png`")

        st.markdown("""
        #### 💡 상위 5개 카테고리 심층 인사이트
        - **효율성 1위:** 단위당 판매 금액이 가장 높은 카테고리는 `computers_accessories` 입니다.
        - **판매량 1위:** 가장 많은 누적 판매량을 기록한 카테고리는 `bed_bath_table` 입니다.
        - **성장 추세:** 모든 상위 카테고리가 연말(11월) 쇼핑 시즌에 급격한 매출 상승을 공통적으로 보이고 있습니다.
        """)

    # --- 3. 가격대별 분포 분석 ---
    elif sub_menu == "💳 구매 전환: 최적 가격대 식별":
        st.header("💳 구매 전환: 최적 가격대 식별")
        st.markdown("**가설:** 어떤 가격대의 제품이 비즈니스에 핵심적인 기여를 하고 있는가?")

        img_dist = os.path.join(IMAGE_DIR, "price_distribution_v2.png")
        if os.path.exists(img_dist):
            st.image(img_dist, caption="Price Range Distribution", use_container_width=True)
        else:
            st.warning("📷 이미지 파일 없음: `price_distribution_v2.png`")

        st.markdown("#### 가격 구간별 기여도")
        data_price = {
            "가격 구간 (BRL)": ["0-50", "50-100", "100-200", "200-500", "500-1,000", "1,000-5,000", "5,000+"],
            "판매 수량": [22028, 32778, 36434, 20891, 4413, 1736, 21],
            "총 매출액(BRL)": [728776, 2416040, 5201510, 6144950, 3019240, 2710850, 195480],
            "매출 비중": ["3.6%", "11.8%", "25.5%", "30.1%", "14.8%", "13.3%", "1.0%"]
        }
        st.dataframe(pd.DataFrame(data_price), use_container_width=True)

        st.markdown("""
        #### 💡 가격대별 분포 주요 인사이트
        - **매출 핵심 구간 (Core Revenue):** **200-500 BRL** 구간이 전체 매출의 약 **30.1%**를 차지하며 가장 높은 수익 기여도를 보입니다.
        - **물량 핵심 구간 (High Volume):** **100-200 BRL** 구간(36,434건)과 **50-100 BRL** 구간(32,778건)에서 가장 활발한 거래가 일어납니다.
        - **고가권의 영향력 (High-End):** 500 BRL 이상의 고가 상품군은 전체 판매 수량의 약 **5%**에 불과하지만, 전체 매출의 약 **29%**를 차지합니다.
        - **결론:** 안정적인 물량 확보를 위해서는 **100BRL 내외**의 상품군 관리가 중요하며, 매출 성장을 위해서는 **200-500 BRL** 가격대의 제품 경쟁력을 강화하는 전략이 유효합니다.
        """)

    # --- 4. 제품 특성 및 인사이트 ---
    elif sub_menu == "🚀 성장의 개선: 전환 최적화 가이드":
        st.header("🚀 성장의 개선: 전환 최적화 가이드")

        img_attr = os.path.join(IMAGE_DIR, "h345_product_attributes.png")
        if os.path.exists(img_attr):
            st.image(img_attr, caption="Product Attributes Analysis", use_container_width=True)
        else:
            st.warning("📷 이미지 파일 없음: `h345_product_attributes.png`")

        st.info("""
        - **이름 길이:** 40~60자 사이의 제품이 가장 많이 판매됨.
        - **설명 길이:** 약 1,000자 내외에서 충분한 정보 전달 시 판매 효과 극대화.
        - **사진 개수:** 2~3장의 사진을 보유한 제품의 판매 빈도가 가장 높음.
        """)
