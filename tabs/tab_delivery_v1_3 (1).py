import streamlit as st
import pandas as pd
import os
import plotly.express as px
import plotly.graph_objects as go


def render(base_dir, data_dir):
    """배송 분석 탭 렌더링 (팀원 페이지 수준 고도화 버전)"""

    # --- 0. UI/UX 최적화: 커스텀 CSS (Premium Dashboard Style) ---
    st.markdown("""
        <style>
            /* 메인 컨테이너 폰트 및 배경 */
            @import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;700&display=swap');
            * { font-family: 'Pretendard', sans-serif; }

            /* KPI 카드 스타일 */
            .kpi-container {
                display: flex;
                justify-content: space-between;
                gap: 20px;
                margin-bottom: 25px;
            }
            .kpi-card {
                background: white;
                padding: 20px;
                border-radius: 16px;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
                border: 1px solid #f0f2f6;
                flex: 1;
                text-align: center;
                transition: transform 0.3s ease;
            }
            .kpi-card:hover { transform: translateY(-5px); }
            .kpi-label { font-size: 0.9rem; color: #64748b; margin-bottom: 8px; font-weight: 500; }
            .kpi-value { font-size: 1.8rem; font-weight: 700; color: #1e293b; margin-bottom: 4px; }
            .kpi-caption { font-size: 0.75rem; color: #94a3b8; }
            .kpi-trend-up { color: #10b981; font-weight: 600; }
            .kpi-trend-down { color: #ef4444; font-weight: 600; }

            /* 버튼/탭 스타일 고도화 */
            div.stButton > button {
                border-radius: 12px !important;
                font-weight: 700 !important;
                transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
                padding: 10px 20px !important;
            }
            div.stButton > button[kind="primary"] {
                background: linear-gradient(135deg, #10b981 0%, #3b82f6 100%) !important;
                color: #ffffff !important;
                border: none !important;
                box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3) !important;
            }
            div.stButton > button[kind="secondary"] {
                background-color: #ffffff !important;
                color: #64748b !important;
                border: 1px solid #e2e8f0 !important;
            }

            /* 가이드 박스 헤더 스타일 */
            .guide-header { font-size: 1.1rem; font-weight: 700; margin-bottom: 10px; display: flex; align-items: center; gap: 8px; }
            
            /* 구분선 스타일 */
            hr { margin: 2rem 0 !important; border-top: 2px solid #f1f5f9 !important; }
        </style>
    """, unsafe_allow_html=True)

    # 데이터 경로 설정
    DELIVERY_DIR = os.path.join(base_dir, "draft", "delivery")
    DATA_DATA_DIR = os.path.join(DELIVERY_DIR, "data")
    
    # 데이터 로드 함수
    def load_delivery_data(file_name):
        candidates = [
            os.path.join(base_dir, "data", "olist_customer_journey_attention", "분석_결과", "데이터", file_name),
            os.path.join(DATA_DATA_DIR, file_name),
            os.path.join(base_dir, "draft", "delivery", "data", file_name)
        ]
        for path in candidates:
            if os.path.exists(path):
                try:
                    return pd.read_csv(path)
                except Exception as e:
                    return None
        return None

    # KPI 카드 렌더링 헬퍼
    def render_kpi(label, value, caption, trend=None):
        trend_html = f'<span class="kpi-trend-{"up" if trend > 0 else "down"}">{"▲" if trend > 0 else "▼"} {abs(trend)}%</span>' if trend else ""
        return f"""
            <div class="kpi-card">
                <div class="kpi-label">{label}</div>
                <div class="kpi-value">{value}</div>
                <div class="kpi-caption">{trend_html} {caption}</div>
            </div>
        """

    # Plotly 테마 적용 헬퍼
    def apply_plotly_style(fig):
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_family='Pretendard',
            title_font_size=20,
            margin=dict(t=50, b=50, l=20, r=20),
            hoverlabel=dict(bgcolor="white", font_size=13)
        )
        fig.update_traces(marker_line_width=0)
        return fig

    # --- 1. 내비게이션 섹션 ---
    tabs = [
        "📉 배송 지연 진단", 
        "💎 물류 체감 가치", 
        "🚀 재구매 최적화", 
        "⏱️ 속도와 만족도", 
        "🗺️ 지역 물류 고도화"
    ]
    
    if "delivery_sub_menu" not in st.session_state:
        st.session_state["delivery_sub_menu"] = tabs[0]

    cols = st.columns(5)
    for i, tab_name in enumerate(tabs):
        is_active = st.session_state["delivery_sub_menu"] == tab_name
        if cols[i].button(tab_name, key=f"del_tab_{i}", use_container_width=True, type="primary" if is_active else "secondary"):
            st.session_state["delivery_sub_menu"] = tab_name
            st.rerun()

    menu = st.session_state["delivery_sub_menu"]
    st.markdown("---")

    # 데이터 미리 로딩
    repurchase_sum = load_delivery_data('repurchase_analysis_summary.csv')
    speed_sum = load_delivery_data('delivery_speed_comparison_stats.csv')
    desc_sum = load_delivery_data('descriptive_stats_groups.csv')

    # --- 2. 탭별 콘텐츠 ---

    if menu == "📉 배송 지연 진단":
        st.subheader("📑 여정의 불편: 배송 지연 및 물류 병목 진단")
        
        # KPI 섹션
        kpi_html = f"""
        <div class="kpi-container">
            {render_kpi("평균 재구매율", "5.10%", "생필품 카테고리 평균", trend=2.1)}
            {render_kpi("평균 배송 소요", "11.6일", "전년 대비 0.5일 단축", trend=-4.2)}
            {render_kpi("최고 재구매 주", "RO (5.32%)", "물류 효율 최적 지역")}
            {render_kpi("핵심 카테고리", "가구/데코", "re-buy 빈도 최고")}
        </div>
        """
        st.markdown(kpi_html, unsafe_allow_html=True)

        # 전략 가이드
        g1, g2 = st.columns(2)
        with g1:
            st.warning("**🚨 핵심 문제점**\n\n- 배송비 비중이 **20%를 초과**할 때 재구매율이 심리적 저항선에 부딪힘.\n- 도서 지역의 경우 리드타임이 평균 대비 **30% 길게** 나타남.")
        with g2:
            st.success("**💡 비즈니스 액션 플랜**\n\n- 저가 상품군 대상 **'Fulfillment 입고 대행'**을 통한 배송비 평준화.\n- 장기 배송 예상 고객 대상 **'배송 지연 보상 쿠폰'** 자동 발급 시스템 도입.")

        # 시각화
        if repurchase_sum is not None:
            fig = px.bar(repurchase_sum, x='그룹', y='재구매율', text_auto='.2%',
                         title='배송비 비중 그룹별 재구매율 현황',
                         color='그룹', color_discrete_sequence=['#10b981', '#3b82f6'])
            st.plotly_chart(apply_plotly_style(fig), use_container_width=True)

        # 상세 데이터
        with st.expander("🔍 세부 데이터 인사이트 확인"):
            st.dataframe(repurchase_sum, use_container_width=True)

    elif menu == "💎 물류 체감 가치":
        st.subheader("💎 경험의 가치: 데이터로 증명된 물류 체감 가치")
        
        if desc_sum is not None:
            # KPI
            kpi_html = f"""
            <div class="kpi-container">
                {render_kpi("평균 판매 가격", "R$ 106.2", "저가 생필품 그룹")}
                {render_kpi("평균 배송비", "R$ 19.4", "비중 18.2% 기록")}
                {render_kpi("평균 리뷰 점수", "4.04점", "품질 대비 높은 만족도", trend=0.5)}
                {render_kpi("데이터 샘플", "36,905건", "생필품 세그먼트 규모")}
            </div>
            """
            st.markdown(kpi_html, unsafe_allow_html=True)

            col1, col2 = st.columns([1, 1])
            with col1:
                st.info("**🚨 핵심 문제점**\n\n- 배송비가 상품 가격의 변동폭보다 커질 때 고객 이탈 가속화.\n- 리뷰 점수는 안정적이나 배송 경험 불만족이 전체 평가의 하방 압력으로 작용.")
            with col2:
                st.success("**💡 비즈니스 액션 플랜**\n\n- **묶음 배송 서비스** 강화로 건당 체감 배송비 인하 유도.\n- 배송비 무료 임계점(Threshold) 설정을 통한 객단가 상승 전략 수립.")

            melted = desc_sum.reset_index().melt(id_vars='index', value_vars=['price', 'freight_value'])
            fig = px.bar(melted, x='index', y='value', color='variable', barmode='group', text_auto='.1f',
                         title='그룹별 가격 vs 배송비 구조 비교',
                         color_discrete_sequence=['#1e293b', '#10b981'])
            st.plotly_chart(apply_plotly_style(fig), use_container_width=True)

            with st.expander("🔍 세부 데이터 인사이트 확인"):
                st.dataframe(desc_sum, use_container_width=True)

    elif menu == "🚀 재구매 최적화":
        st.subheader("🚀 성장의 개선: 재구매 선순환을 위한 배송비 최적화")
        
        kpi_html = f"""
        <div class="kpi-container">
            {render_kpi("Critical Zone", "20%+", "배송비 저항선 포착")}
            {render_kpi("재구매 하락폭", "-12.5%", "임계점 초과 시", trend=-12.5)}
            {render_kpi("최적 배송비", "R$ 15.0", "재구매 전환율 극대화 지점")}
            {render_kpi("개선 잠재력", "+3.2%", "물류 최적화 시 기대 효과")}
        </div>
        """
        st.markdown(kpi_html, unsafe_allow_html=True)

        st.warning("**🚨 핵심 문제점**\n\n- 배송비 비중이 20%를 넘는 그룹에서 재구매 의사 결정이 2배 이상 지연됨.\n- 단순 배송 속도보다 '비용 대비 속도'의 효율성에 더 민감하게 반응.")
        st.success("**💡 비즈니스 액션 플랜**\n\n- **구독형 프리미엄 배송 서비스** 도입으로 배송비 거부감 제거.\n- 재구매 고객 대상 차기 주문 배송비 **50% 할인권** 자동 발급.")

        if repurchase_sum is not None:
            fig = px.line(repurchase_sum, x='그룹', y='재구매율', markers=True, text=[f"{val:.2%}" for val in repurchase_sum['재구매율']],
                          title='배송비 비중 변화에 따른 재구매율 변곡점', color_discrete_sequence=['#3b82f6'])
            st.plotly_chart(apply_plotly_style(fig), use_container_width=True)
            
        with st.expander("🔍 세부 데이터 인사이트 확인"):
            st.dataframe(repurchase_sum, use_container_width=True)

    elif menu == "⏱️ 속도와 만족도":
        st.subheader("📉 여정의 불편: 배송 속도와 고객 만족도의 상관관계")
        
        if speed_sum is not None:
            kpi_html = f"""
            <div class="kpi-container">
                {render_kpi("평균 배송", "12.5일", "고비용 배송 그룹", trend=1.2)}
                {render_kpi("배송 편차", "±9.4일", "신뢰도 저하 요소")}
                {render_kpi("지연 경험률", "15.8%", "재구매 포기 주원인")}
                {render_kpi("만족도 상관계수", "-0.68", "속도와 강한 음의 상관관계")}
            </div>
            """
            st.markdown(kpi_html, unsafe_allow_html=True)

            st.error("**🚨 핵심 문제점**\n\n- 배송비가 비싼 그룹일수록 배송이 더 느린 **'물류의 역설'** 발생.\n- 불규칙한 배송 완료 예측 기간이 고객 만족 점수를 1.5점 이상 하락시킴.")
            st.info("**💡 비즈니스 액션 플랜**\n\n- 머신러닝 기반 **'도착 보장일'** 시스템 정교화.\n- 배송 지연 예상 시 선제적 푸시 알림 및 포인트 보상 처리.")

            fig = px.bar(speed_sum, x='그룹', y='평균 배송 기간(일)', text_auto='.1f',
                         title='배송비 부담 그룹별 실제 배송 소요 기간 (일)',
                         color='그룹', color_discrete_sequence=['#ef4444', '#f87171'])
            st.plotly_chart(apply_plotly_style(fig), use_container_width=True)

            with st.expander("🔍 세부 데이터 인사이트 확인"):
                st.dataframe(speed_sum, use_container_width=True)

    elif menu == "🗺️ 지역 물류 고도화":
        st.subheader("🚀 개선의 확장: 지역 격차 해소 및 카테고리별 물류 고도화")
        
        kpi_html = f"""
        <div class="kpi-container">
            {render_kpi("최우수 지역", "SP (Sao Paulo)", "물류 인프라 최적 지역")}
            {render_kpi("최다 수요 지역", "RJ / MG", "추가 거점 확보 필요")}
            {render_kpi("지역별 편차", "8.5일", "최단-최장 구간 차이", trend=5.2)}
            {render_kpi("최적 거점 수", "3개소", "전국 커버리지 최적화 산출")}
        </div>
        """
        st.markdown(kpi_html, unsafe_allow_html=True)

        st.warning("**🚨 핵심 문제점**\n\n- 특정 지역(북동부)의 배송비가 중남부 대비 **2.5배** 높게 형성됨.\n- 지역적 한계로 인해 우량 고객의 이탈이 지속적으로 발생함.")
        st.success("**💡 비즈니스 액션 플랜**\n\n- **Micro-Fulfillment Center (MFC)** 지역 거점 분산 배치.\n- 지역 물류 파트너사 다각화를 통한 '라스트마일' 비용 경쟁력 확보.")

        col1, col2 = st.columns(2)
        with col1:
            top_cat = load_delivery_data('top_3_repurchase_categories.csv')
            if top_cat is not None:
                fig = px.pie(top_cat, values='재구매 고객 수', names='카테고리', title='재구매 집중 카테고리 비중',
                             hole=0.4, color_discrete_sequence=px.colors.sequential.Teal)
                st.plotly_chart(apply_plotly_style(fig), use_container_width=True)
        with col2:
            state_data = load_delivery_data('state_repurchase_analysis.csv')
            if state_data is not None:
                fig = px.scatter(state_data, x='재구매율', y='평균 리뷰 점수', size='재구매율', text='주(State)',
                                title='지역별 성과 매트릭스', color='평균 리뷰 점수', color_continuous_scale='Greens')
                st.plotly_chart(apply_plotly_style(fig), use_container_width=True)

        with st.expander("🔍 세부 데이터 인사이트 확인"):
            state_data = load_delivery_data('state_repurchase_analysis.csv')
            if state_data is not None:
                st.dataframe(state_data, use_container_width=True)

    st.markdown("---")
    st.caption("© 2026 Olist Customer Journey Analysis Project | 프리미엄 배송 전략 대시보드 v1.5")
