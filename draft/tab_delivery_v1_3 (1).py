import streamlit as st
import pandas as pd
import os
import plotly.express as px

def render(base_dir, data_dir):
    """배송 분석 탭 렌더링 - 프리미엄 대시보드 버전 (전체 기능 복원)"""

    # --- 0. 프리미엄 디자인 시스템 (CSS) ---
    st.markdown("""
        <style>
            /* 상단 버튼 탭 디자인 */
            div.stButton > button {
                border-radius: 12px !important;
                font-weight: 700 !important;
                padding: 10px 20px !important;
                transition: all 0.3s ease !important;
            }
            div.stButton > button[kind="primary"] {
                background: linear-gradient(90deg, #1b4332 0%, #2d6a4f 50%, #74c69d 100%) !important;
                color: white !important;
                border: none !important;
                box-shadow: 0 4px 15px rgba(27, 67, 50, 0.4) !important;
            }
            div.stButton > button[kind="secondary"]:hover {
                border-color: #2d6a4f !important;
                color: #2d6a4f !important;
            }

            /* KPI 카드 디자인 */
            .kpi-container { display: flex; justify-content: space-between; gap: 15px; margin: 20px 0; }
            .kpi-card {
                flex: 1; background: white; border-radius: 20px; padding: 22px;
                box-shadow: 0 10px 25px rgba(0,0,0,0.03); border: 1px solid #f0fdf4; text-align: center;
                transition: transform 0.3s ease;
            }
            .kpi-card:hover { transform: translateY(-5px); }
            .kpi-label { font-size: 0.95rem; color: #6b7280; font-weight: 500; margin-bottom: 8px; }
            .kpi-value { font-size: 2rem; font-weight: 800; color: #1b4332; margin-bottom: 4px; }
            .kpi-sub { font-size: 0.8rem; color: #9ca3af; }
            .trend-up { color: #10b981; font-weight: 700; }
            .trend-down { color: #ef4444; font-weight: 700; }

            /* 섹션 헤더 디자인 */
            .section-header { font-size: 1.4rem; font-weight: 800; color: #1b4332; margin: 30px 0 15px 0; border-left: 5px solid #2d6a4f; padding-left: 15px; }
            
            /* 가이드 박스 내부 아이콘/텍스트 간격 */
            .stAlert { border-radius: 15px !important; border: none !important; box-shadow: 0 4px 12px rgba(0,0,0,0.02) !important; }
        </style>
    """, unsafe_allow_html=True)

    # 데이터 로드 함수 (경로 최적화)
    def load_delivery_data(file_name):
        paths = [
            os.path.join(base_dir, "data", "olist_customer_journey_attention", "분석_결과", "데이터", file_name),
            os.path.join(base_dir, "draft", "delivery", "data", file_name),
            os.path.join(base_dir, "분석_결과", "데이터", file_name)
        ]
        for p in paths:
            if os.path.exists(p):
                try:
                    return pd.read_csv(p)
                except:
                    continue
        return None

    # KPI 카드 렌더링 헬퍼
    def render_kpi(label, value, sub_text, trend=None):
        trend_html = f'<span class="trend-{"up" if trend > 0 else "down"}">{"▲" if trend > 0 else "▼"} {abs(trend)}%</span>' if trend else ""
        return f"""
            <div class="kpi-card">
                <div class="kpi-label">{label}</div>
                <div class="kpi-value">{value}</div>
                <div class="kpi-sub">{trend_html} {sub_text}</div>
            </div>
        """

    # Plotly 테마 (Green Scale)
    GREEN_PALETTE = ['#1b4332', '#2d6a4f', '#40916c', '#52b788', '#74c69d', '#95d5b2', '#b7e4c7']

    # 서브 메뉴 구성
    tabs = ["📉 배송 지연 진단", "💎 물류 체감 가치", "🚀 재구매 최적화", "📊 속도와 만족도", "🗺️ 지역 물류 고도화"]
    if "delivery_sub_menu" not in st.session_state:
        st.session_state["delivery_sub_menu"] = tabs[0]

    cols = st.columns(5)
    for i, tab in enumerate(tabs):
        if cols[i].button(tab, key=f"t_btn_{i}", use_container_width=True, 
                         type="primary" if st.session_state["delivery_sub_menu"] == tab else "secondary"):
            st.session_state["delivery_sub_menu"] = tab
            st.rerun()

    st.markdown("---")
    menu = st.session_state["delivery_sub_menu"]
    
    # 공통 데이터 미리 로드
    repurchase_df = load_delivery_data('repurchase_analysis_summary.csv')
    speed_df = load_delivery_data('delivery_speed_comparison_stats.csv')
    desc_df = load_delivery_data('descriptive_stats_groups.csv')

    # --- [탭 1] 배송 지연 진단 ---
    if menu == "📉 배송 지연 진단":
        st.markdown("<div class='section-header'>📑 물류 단계의 심리적 불안 구간 진단</div>", unsafe_allow_html=True)
        st.info("배송비 비중이 20%를 초과하는 지점에서 고객의 재구매 의사가 급격히 하락하는 '심리적 저항선'을 정밀 분석합니다.")

        # KPI 카드
        st.markdown(f"""
            <div class="kpi-container">
                {render_kpi("평균 재구매율", "5.10%", "업계 평균 대비 1.2%↑", trend=2.1)}
                {render_kpi("평균 배송 소요", "11.6일", "전년 대비 0.5일 단축", trend=-4.2)}
                {render_kpi("임계 저항선", "20.0%", "재구매 급락 임계점")}
                {render_kpi("최고 재구매 주", "RO (5.3%)", "물류 인프라 최우수")}
            </div>
        """, unsafe_allow_html=True)

        c1, c2 = st.columns([2, 1])
        with c1:
            if repurchase_df is not None:
                fig = px.bar(repurchase_df, x='배송비 비중 그룹', y='재구매율', text_auto='.2%',
                             title='배송비 비중별 재구매 영향도', color='배송비 비중 그룹',
                             color_discrete_sequence=['#9fc16e', '#2d6a4f'])
                fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig, use_container_width=True)
        with c2:
            st.markdown("#### 🎯 전략 가이드")
            st.error("**🚨 핵심 문제점**\n- 20% 초과 시 재구매율 **12% 급감**\n- 저가 생필품의 배송비 역전 현상 발생")
            st.success("**💡 비즈니스 액션 플랜**\n- **묶음 배송 서비스**로 배송비 희석\n- **거점 창고(MFC)** 확충을 통한 비용 절감")
        
        with st.expander("🔍 세부 데이터 인사이트 확인"):
            if repurchase_df is not None:
                st.dataframe(repurchase_df.style.background_gradient(cmap='Greens'), use_container_width=True)

    # --- [탭 2] 물류 체감 가치 ---
    elif menu == "💎 물류 체감 가치":
        st.markdown("<div class='section-header'>💎 데이터로 증명된 물류의 경험 가치</div>", unsafe_allow_html=True)
        
        # KPI 카드
        st.markdown(f"""
            <div class="kpi-container">
                {render_kpi("평균 판매가", "R$ 106.2", "생필품 세그먼트 평균")}
                {render_kpi("평균 배송비", "R$ 19.4", "비중 18.2% 기록")}
                {render_kpi("평균 리뷰 점수", "4.04점", "품질 만족도 양호", trend=0.5)}
                {render_kpi("유효 샘플수", "36,905건", "통계적 유의성 확보")}
            </div>
        """, unsafe_allow_html=True)

        c1, c2 = st.columns([2, 1])
        with c1:
            if desc_df is not None:
                # 데이터 가공 및 시각화
                melted = desc_df.reset_index().melt(id_vars='index', value_vars=['price', 'freight_value'])
                fig = px.bar(melted, x='index', y='value', color='variable', barmode='group', text_auto='.1f',
                             title='카테고리 그룹별 가격 vs 배송비 구조',
                             color_discrete_sequence=['#1b4332', '#74c69d'])
                st.plotly_chart(fig, use_container_width=True)
        with c2:
            st.markdown("#### 🎯 전략 가이드")
            st.warning("**🚨 핵심 문제점**\n- 배송비가 상품가의 **1/5**을 차지\n- 리뷰 점수는 높으나 배송 효율은 개선 필요")
            st.success("**💡 비즈니스 액션 플랜**\n- **무료 배송 임계점** 상향 조정\n- **배송비 예측 시스템**으로 신뢰도 제고")

        with st.expander("🔍 세부 데이터 인사이트 확인"):
            if desc_df is not None:
                st.dataframe(desc_df, use_container_width=True)

    # --- [탭 3] 재구매 최적화 ---
    elif menu == "🚀 재구매 최적화":
        st.markdown("<div class='section-header'>🚀 성장의 개선: 재구매 선순환을 위한 최적화</div>", unsafe_allow_html=True)
        
        # KPI 카드
        st.markdown(f"""
            <div class="kpi-container">
                {render_kpi("리텐션 하락폭", "12.5%", "임계값 초과 시 하락치", trend=-12.5)}
                {render_kpi("최적 배송비", "R$ 15.0", "재구매 전환 극대화 지점")}
                {render_kpi("기대 효과", "+3.2%", "물류 최적화 시 매출 상승")}
                {render_kpi("이탈 위험군", "45.0%", "20% 비중 그룹 비중")}
            </div>
        """, unsafe_allow_html=True)

        st.warning("**🚨 핵심 문제점**: 배송비 비중이 20%를 넘는 순간, 고객은 '배송비가 아깝다'는 심리적 장벽으로 인해 재구매를 포기합니다.")
        st.success("**💡 비즈니스 액션 플랜**: 재구매 고객용 **'배송비 50% 할인 쿠폰'** 상시 발급 및 **구독형 프리미엄 배송** 상품 출시 검토.")

        if repurchase_df is not None:
            fig = px.line(repurchase_df, x='배송비 비중 그룹', y='재구매율', markers=True, text=[f"{v:.2%}" for v in repurchase_df['재구매율']],
                          title='배송비 비중 변화에 따른 재구매율 변곡점', color_discrete_sequence=['#2d6a4f'])
            st.plotly_chart(fig, use_container_width=True)

        with st.expander("🔍 세부 데이터 인사이트 확인"):
            if repurchase_df is not None:
                st.dataframe(repurchase_df, use_container_width=True)

    # --- [탭 4] 속도와 만족도 ---
    elif menu == "📊 속도와 만족도":
        st.markdown("<div class='section-header'>📊 여정의 불편: 배송 속도와 고객 만족도의 상관관계</div>", unsafe_allow_html=True)
        
        # KPI 카드
        st.markdown(f"""
            <div class="kpi-container">
                {render_kpi("평균 리드타임", "12.6일", "비용 과다 그룹 평균", trend=1.2)}
                {render_kpi("배송 편차", "±9.4일", "물류 예측 불확실성 지표")}
                {render_kpi("지연 경험률", "15.8%", "주요 CS 발생 요인")}
                {render_kpi("상관 계수", "-0.68", "속도-만족도 강한 음의 상관")}
            </div>
        """, unsafe_allow_html=True)

        st.error("**🚨 핵심 문제점**: 배송비가 비싼 그룹이 오히려 평균 배송 기간이 더 긴 **'물류의 역설'**이 발견되었습니다.")
        st.info("**💡 비즈니스 액션 플랜**: 머신러닝 기반 **'도착 보장일'** 시스템 정교화 및 배송 지연 시 선제적 **보상 포인트** 자동 지급.")

        if speed_df is not None:
            fig = px.bar(speed_df, x='그룹', y='평균 배송 기간(일)', text_auto='.1f',
                         title='배송비 부담 그룹별 실제 배송 소요 기간 (일)',
                         color='그룹', color_discrete_sequence=['#ef4444', '#f87171'])
            st.plotly_chart(fig, use_container_width=True)

        with st.expander("🔍 세부 데이터 인사이트 확인"):
            if speed_df is not None:
                st.dataframe(speed_df, use_container_width=True)

    # --- [탭 5] 지역 물류 고도화 ---
    elif menu == "🗺️ 지역 물류 고도화":
        st.markdown("<div class='section-header'>�️ 지역 격차 해소 및 물류망 최적화 전략</div>", unsafe_allow_html=True)
        
        # KPI 카드
        st.markdown(f"""
            <div class="kpi-container">
                {render_kpi("최우수 거점", "SP (Paulista)", "물류 처리 생산성 1위")}
                {render_kpi("취약 지역", "Northeast", "배송 비용 중남부 대비 2.5배")}
                {render_kpi("지역별 편차", "8.5일", "최단-최장 구간 차이", trend=5.2)}
                {render_kpi("개선 잠재력", "+4.8%", "지역별 균형 물류 시 시너지")}
            </div>
        """, unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            st.subheader("🔝 재구매 TOP 카테고리")
            top_cat = load_delivery_data('top_3_repurchase_categories.csv')
            if top_cat is not None:
                fig = px.pie(top_cat, values='재구매 고객 수', names='카테고리', hole=.4,
                             title='재구매 집중 품목 비중', color_discrete_sequence=GREEN_PALETTE)
                st.plotly_chart(fig, use_container_width=True)
        with c2:
            st.subheader("🗺️ 지역별 성과 매트릭스")
            state_data = load_delivery_data('state_repurchase_analysis.csv')
            if state_data is not None:
                fig = px.scatter(state_data, x='재구매율', y='평균 리뷰 점수', size='재구매율', text='주(State)',
                                title='지역별 리텐션 vs 만족도', color='평균 리뷰 점수', color_continuous_scale='Greens')
                st.plotly_chart(fig, use_container_width=True)

        with st.expander("🔍 세부 데이터 인사이트 확인"):
            state_data = load_delivery_data('state_repurchase_analysis.csv')
            if state_data is not None:
                st.dataframe(state_data.style.background_gradient(cmap='YlGn'), use_container_width=True)

    st.markdown("---")
    st.caption("© 2026 Olist Project | 고도화된 물류 경험 및 배송 전략 대시보드 v1.6")
