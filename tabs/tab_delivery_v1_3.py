import streamlit as st
import pandas as pd
import os
import plotly.express as px


def render(base_dir, data_dir):
    """배송 분석 탭 렌더링"""

    # --- 0. UX 최적화: 커스텀 세그먼트 컨트롤 (Green Gradient Style) ---
    st.markdown("""
        <style>
            /* 버튼 기본 스타일 무력화 및 프리미엄 스타일 입히기 */
            div.stButton > button {
                border-radius: 12px !important;
                font-weight: 700 !important;
                transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
                padding: 10px 20px !important;
            }
            /* 활성 탭 (Primary) - 초록색 그라데이션 */
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


    st.markdown("---")

    # 데이터 경로 설정
    DELIVERY_DIR = os.path.join(base_dir, "draft", "delivery")
    DATA_DATA_DIR = os.path.join(DELIVERY_DIR, "data")
    VIZ_DIR = os.path.join(DELIVERY_DIR, "viz")

    # 데이터 로드 함수 (캐시 제거하여 실시간 반영 보장)
    def load_delivery_data(file_name):
        # 여러 경로 후보 시도
        candidates = [
            os.path.join(DATA_DATA_DIR, file_name),
            os.path.join(DELIVERY_DIR, "분석_결과", "데이터", file_name),
            os.path.join(base_dir, "draft", "delivery", "data", file_name)
        ]
        for path in candidates:
            if os.path.exists(path):
                try:
                    return pd.read_csv(path)
                except Exception as e:
                    st.error(f"Error reading {file_name}: {e}")
                    return None
        return None

    def find_image(file_name):
        candidates = [
            os.path.join(VIZ_DIR, file_name),
            os.path.join(DELIVERY_DIR, "분석_결과", "시각화", file_name),
        ]
        for path in candidates:
            if os.path.exists(path):
                return path
        return None

    # 내부 서브 메뉴 (Custom Button Tab Bar)
    tabs = [
        "📉 여정의 불편: 배송 지연 진단", 
        "💎 경험의 가치: 물류 체감 가치", 
        "🚀 성장의 개선: 재구매 최적화", 
        "📉 여정의 불편: 속도와 만족도", 
        "🚀 개선의 확장: 지역 물류 고도화"
    ]
    
    if "delivery_sub_menu" not in st.session_state:
        st.session_state["delivery_sub_menu"] = tabs[0]

    col_t1, col_t2, col_t3, col_t4, col_t5 = st.columns(5)
    tab_cols = [col_t1, col_t2, col_t3, col_t4, col_t5]
    
    for i, tab_name in enumerate(tabs):
        is_active = st.session_state["delivery_sub_menu"] == tab_name
        if tab_cols[i].button(
            tab_name, 
            key=f"del_tab_btn_{i}", 
            use_container_width=True,
            type="primary" if is_active else "secondary"
        ):
            st.session_state["delivery_sub_menu"] = tab_name
            st.rerun()

    del_sub_menu = st.session_state["delivery_sub_menu"]
    st.markdown("---")

    # 데이터 존재 여부 체크
    repurchase_sum = load_delivery_data('repurchase_analysis_summary.csv')
    speed_sum = load_delivery_data('delivery_speed_comparison_stats.csv')

    data_available = repurchase_sum is not None or speed_sum is not None

    if not data_available:
        st.warning("""
        ⚠️ **배송 분석 데이터가 아직 준비되지 않았습니다.**

        이 탭은 아래 파일들이 필요합니다:
        - `repurchase_analysis_summary.csv`
        - `delivery_speed_comparison_stats.csv`
        - `descriptive_stats_groups.csv`
        - `top_3_repurchase_categories.csv`
        - `state_repurchase_analysis.csv`
        - 시각화 이미지 (`.png`) 5개

        담당 멤버에게 데이터를 받은 후 `draft/delivery/` 폴더에 배치해주세요.
        """)
        st.info("💡 데이터가 준비되면 자동으로 대시보드가 활성화됩니다.")
        return

    if del_sub_menu == "📉 여정의 불편: 배송 지연 진단":
        st.header("📝 여정의 불편: 물류 단계의 심리적 불안 구간 (Fulfillment)")
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📌 분석 목적")
            st.write("""
            - Olist 데이터셋을 활용하여 **'저가 생필품'** 카테고리의 특성 파악
            - 배송비가 상품 가격에서 차지하는 비중과 재구매 사이의 관계 분석
            - 배송 속도 및 지역별 만족도의 상관관계 도출
            """)

        with col2:
            st.subheader("📂 분석 대상 (저가 생필품 그룹)")
            st.write("""
            - 건강/미용, 가정용품, 침구/욕실, 유아용품, 반려동물 용품 등
            - 실생활 밀착형 및 반복 구매 가능성이 높은 품목 위주 필터링
            """)

        st.subheader("📊 주요 KPI 요약")
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)

        if repurchase_sum is not None:
            avg_repurchase = repurchase_sum['재구매율'].mean() * 100
            kpi1.metric("평균 재구매율", f"{avg_repurchase:.2f}%")

        if speed_sum is not None:
            avg_speed = speed_sum['평균 배송 기간(일)'].mean()
            kpi2.metric("평균 배송 소요 기간", f"{avg_speed:.1f}일")

        kpi3.metric("가장 높은 재구매 주", "RO (5.32%)")
        kpi4.metric("재구매 1위 카테고리", "bed_bath_table")

    elif del_sub_menu == "💎 경험의 가치: 물류 체감 가치":
        st.header("💎 경험의 가치: 데이터로 증명된 물류 체감 가치")
        desc_sum = load_delivery_data('descriptive_stats_groups.csv')
        if desc_sum is not None:
            st.subheader("📊 그룹별 주요 지표 평균")
            st.dataframe(desc_sum.style.format({'price': '{:.1f}', 'freight_value': '{:.1f}', 'review_score': '{:.2f}'}))

            st.subheader("🖼️ 지표 비교 시각화")
            # Melt for easier plotting
            melted_stats = desc_sum.melt(id_vars='freight_ratio_group', value_vars=['price', 'freight_value'], 
                                        var_name='Metric', value_name='Value')
            fig_desc = px.bar(melted_stats, x='freight_ratio_group', y='Value', color='Metric', barmode='group',
                             title='배송비 비중 그룹별 가격 및 배송비 평균 비교',
                             color_discrete_sequence=['#0b134a', '#0c29d0'])
            st.plotly_chart(fig_desc, use_container_width=True)
        else:
            st.warning("📊 데이터 파일(descriptive_stats_groups.csv)이 없습니다.")

    elif del_sub_menu == "🚀 성장의 개선: 재구매 최적화":
        st.header("🚀 성장의 개선: 재구매 선순환을 위한 배송비 최적화")
        
        if repurchase_sum is not None:
            col1, col2 = st.columns([2, 1])
            with col1:
                fig = px.bar(repurchase_sum, x='배송비 비중 그룹', y='재구매율',
                             text=repurchase_sum['재구매율'].apply(lambda x: f'{x:.2%}'),
                             title='배송비 비중(20% 임계점)에 따른 재구매율 차이',
                             color='배송비 비중 그룹', color_discrete_sequence=['#0b134a', '#0c29d0'])
                fig.update_layout(yaxis_tickformat='.1%')
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.subheader("💡 발견된 인사이트")
                st.markdown("""
                - **배송비 저항선 포착**: 배송비 비중이 20%를 넘어서는 순간 재구매율이 급격히 하락하는 경향 확인.
                - **심리적 베리어**: '저가 생필품' 특성상 상품 가격 대비 배송비가 '아깝다'는 인식이 구매 결정 및 유지에 결정적 영향.
                - **개선 방향**: 묶음 배송 유도 혹은 일정 금액 이상 무료 배송 정책이 재구매 가시성을 높이는 핵심 전략임.
                """)
        else:
            st.warning("📊 데이터 파일(repurchase_analysis_summary.csv)이 없습니다.")

    elif del_sub_menu == "📉 여정의 불편: 속도와 만족도":
        st.header("📉 여정의 불편: 배송 속도와 고객 만족도의 상관관계")
        
        if speed_sum is not None:
            col_sp1, col_sp2 = st.columns([2, 1])
            with col_sp1:
                fig_speed = px.bar(speed_sum, x='배송비 비중 그룹', y='평균 배송 기간(일)',
                                  text=speed_sum['평균 배송 기간(일)'].apply(lambda x: f'{x:.1f}일'),
                                  title='배송비 부담 그룹별 실제 배송 소요 기간',
                                  color='배송비 비중 그룹', color_discrete_sequence=['#ff4b4b', '#ff9f9f'])
                st.plotly_chart(fig_speed, use_container_width=True)
            
            with col_sp2:
                st.write("📊 그룹별 배송 통계")
                st.dataframe(speed_sum)

            st.info("""
            💡 **반전의 결과**: 배송비 비중이 높은(High) 그룹이 오히려 평균적으로 더 느리게 배송되는 경향이 발견되었습니다. 
            이는 물류 인프라는 취약하나 거리가 멀어 배송비만 비싸게 책정된 '불편 지역'의 페인포인트를 시사합니다.
            """)
        else:
            st.warning("📊 데이터 파일(delivery_speed_comparison_stats.csv)이 없습니다.")

    elif del_sub_menu == "🚀 개선의 확장: 지역 물류 고도화":
        st.header("🚀 개선의 확장: 지역 격차 해소 및 카테고리별 물류 고도화")
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("🔝 재구매 TOP 카테고리")
            top_cat = load_delivery_data('top_3_repurchase_categories.csv')
            if top_cat is not None:
                fig_cat = px.bar(top_cat, x='카테고리', y='재구매 고객 수', 
                                 title='카테고리별 재구매 선호도',
                                 color_discrete_sequence=['#0c29d0'])
                st.plotly_chart(fig_cat, use_container_width=True)
                st.dataframe(top_cat)

        with col2:
            st.subheader("🗺️ 지역별 재구매 및 만족도")
            state_data = load_delivery_data('state_repurchase_analysis.csv')
            if state_data is not None:
                fig_state = px.scatter(state_data, x='재구매율', y='평균 리뷰 점수', text='주(State)',
                                      title='지역별 물류 성과 매트릭스 (재구매 vs 만족도)',
                                      size='재구매율', color='평균 리뷰 점수', color_continuous_scale='RdYlGn')
                st.plotly_chart(fig_state, use_container_width=True)
                st.dataframe(state_data.sort_values('재구매율', ascending=False).head(10))

    # 푸터
    st.markdown("---")
    st.caption("© 2026 Olist Customer Journey Analysis Project | 저가 생필품 배송비 분석")

