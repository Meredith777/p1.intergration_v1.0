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

    st.markdown("---")

    # 데이터 경로 설정
    DELIVERY_DIR = os.path.join(base_dir, "draft", "delivery")
    DATA_DATA_DIR = os.path.join(DELIVERY_DIR, "data")
    VIZ_DIR = os.path.join(DELIVERY_DIR, "viz")

    # 데이터 로드 함수
    def load_delivery_data(file_name):
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

    # 데이터 로드
    repurchase_sum = load_delivery_data('repurchase_analysis_summary.csv')
    speed_sum = load_delivery_data('delivery_speed_comparison_stats.csv')

    if del_sub_menu == "📉 여정의 불편: 배송 지연 진단":
        # 1. 메인 타이틀
        st.markdown("### 📑 여정의 불편: 물류 단계의 심리적 불안 구간 (Fulfillment)")
        
        # 2. 요약 배경 박스
        st.info("""
        **분석 요약:** 본 분석은 Olist 데이터셋을 바탕으로 '저가 생필품' 카테고리의 물류 효율성을 진단했습니다. 
        특히 배송비 비중이 20%를 초과할 때 발생하는 재구매 저항선과 물류 소외 지역의 페인포인트를 중점적으로 다룹니다.
        """)

        # 3. 주요 KPI 요약 (고정 수치 반영)
        st.markdown("#### 📊 주요 KPI 요약")
        kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
        with kpi_col1:
            st.metric("평균 재구매율", "5.10%")
        with kpi_col2:
            st.metric("평균 배송 소요", "11.6일")
        with kpi_col3:
            st.metric("최고 재구매 주", "RO (5.32%)")
        with kpi_col4:
            st.metric("1위 카테고리", "bed_bath_table")

        st.markdown("---")

        # 4. 차트와 인사이트 2:1 배치
        col_chart, col_insight = st.columns([2, 1])
        
        with col_chart:
            if repurchase_sum is not None:
                fig = px.bar(repurchase_sum, x='배송비 비중 그룹', y='재구매율',
                             text=repurchase_sum['재구매율'].apply(lambda x: f'{x:.2%}'),
                             title='배송비 비중(20% 임계점)에 따른 재구매율 차이',
                             color='배송비 비중 그룹', color_discrete_sequence=['#9fc16e', '#94d8cf'])
                fig.update_layout(yaxis_tickformat='.1%')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("그래프 출력을 위한 데이터가 없습니다.")
                
        with col_insight:
            st.markdown("#### 💡 발견된 인사이트")
            st.write("- **배송비 저항선 포착**: 비중이 20%를 넘어서면 재구매율이 급락함.")
            st.write("- **심리적 베리어**: 저가 상품일수록 배송비에 대한 심리적 거부감이 큼.")
            st.write("- **물류 역설**: 배송비 비중이 높은 그룹이 오히려 배송은 더 느림(12.4일).")

    elif del_sub_menu == "💎 경험의 가치: 물류 체감 가치":
        st.header("💎 경험의 가치: 데이터로 증명된 물류 체감 가치")
        desc_sum = load_delivery_data('descriptive_stats_groups.csv')
        if desc_sum is not None:
            st.subheader("📊 그룹별 주요 지표 평균")
            st.dataframe(desc_sum.style.format({'price': '{:.1f}', 'freight_value': '{:.1f}', 'review_score': '{:.2f}'}))

            melted_stats = desc_sum.melt(id_vars='freight_ratio_group', value_vars=['price', 'freight_value'], 
                                        var_name='Metric', value_name='Value')
            fig_desc = px.bar(melted_stats, x='freight_ratio_group', y='Value', color='Metric', barmode='group',
                             title='배송비 비중 그룹별 가격 및 배송비 평균 비교',
                             color_discrete_sequence=['#0b134a', '#0c29d0'])
            st.plotly_chart(fig_desc, use_container_width=True)

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
                st.markdown("- **배송비 저항선 포착**: 배송비 비중이 20%를 넘어서는 순간 재구매율이 급격히 하락하는 경향 확인.")

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

        with col2:
            st.subheader("🗺️ 지역별 재구매 및 만족도")
            state_data = load_delivery_data('state_repurchase_analysis.csv')
            if state_data is not None:
                fig_state = px.scatter(state_data, x='재구매율', y='평균 리뷰 점수', text='주(State)',
                                      title='지역별 물류 성과 매트릭스 (재구매 vs 만족도)',
                                      size='재구매율', color='평균 리뷰 점수', color_continuous_scale='RdYlGn')
                st.plotly_chart(fig_state, use_container_width=True)

    st.markdown("---")
    st.caption("© 2026 Olist Customer Journey Analysis Project | 저가 생필품 배송비 분석")