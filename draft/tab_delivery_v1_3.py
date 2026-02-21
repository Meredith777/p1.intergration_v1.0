import streamlit as st
import pandas as pd
import os
import plotly.express as px


def render(base_dir, data_dir):
    """배송 분석 탭 렌더링"""

    # --- 0. UX 최적화: 디자인 시스템 및 스타일 (그린 그라데이션) ---
    st.markdown("""
        <style>
            /* 버튼 기본 스타일 초기화 및 프리미엄 스타일 적용 */
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

            /* 프리미엄 KPI 카드 스타일 */
            .kpi-container {
                display: flex;
                justify-content: space-between;
                gap: 15px;
                margin-bottom: 25px;
            }
            .kpi-card {
                flex: 1;
                background: linear-gradient(135deg, #ffffff 0%, #f0fdf4 100%);
                border-radius: 16px;
                padding: 20px;
                box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
                border: 1px solid #e0e7ff;
                transition: transform 0.2s ease-in-out;
            }
            .kpi-card:hover {
                transform: translateY(-5px);
                border-color: #9fc16e;
            }
            .kpi-label {
                font-size: 0.85rem;
                color: #64748b;
                font-weight: 600;
                margin-bottom: 8px;
            }
            .kpi-value {
                font-size: 1.8rem;
                font-weight: 800;
                color: #1e293b;
                line-height: 1.2;
                margin-bottom: 8px;
                background: -webkit-linear-gradient(90deg, #9fc16e, #94d8cf);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }
            .kpi-caption {
                font-size: 0.75rem;
                color: #94a3b8;
                line-height: 1.4;
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # 데이터 경로 설정 (유연한 경로 탐색)
    def load_delivery_data(file_name):
        candidates = [
            os.path.join(base_dir, "분석_결과", "데이터", file_name),
            os.path.join(data_dir, file_name) if data_dir else None,
            os.path.join(os.path.dirname(base_dir), "data", "olist_customer_journey_attention", "분석_결과", "데이터", file_name),
            os.path.join(base_dir, "draft", "delivery", "data", file_name)
        ]
        for path in candidates:
            if path and os.path.exists(path):
                try:
                    return pd.read_csv(path)
                except Exception as e:
                    st.error(f"파일 읽기 오류 ({file_name}): {e}")
                    return None
        return None

    # 내부 서브 메뉴 (커스텀 버튼 탭 바)
    tabs = [
        "📉 여정의 불편: 배송 지연 진단", 
        "💎 경험의 가치: 물류 체감 가치", 
        "🚀 성장의 개선: 재구매 최적화", 
        "� 속도와 만족도: 지연의 영향", 
        "�️ 개선의 확장: 지역 물류 고도화"
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

    # 공통 데이터 로드
    repurchase_sum = load_delivery_data('repurchase_analysis_summary.csv')
    speed_sum = load_delivery_data('delivery_speed_comparison_stats.csv')

    if del_sub_menu == "📉 여정의 불편: 배송 지연 진단":
        st.markdown("### 📑 여정의 불편: 물류 단계의 심리적 불안 구간 (Fulfillment)")
        
        st.info("""
        **분석 요약:** 본 분석은 Olist 데이터셋을 바탕으로 '저가 생필품' 카테고리의 물류 효율성을 진단했습니다. 
        특히 배송비 비중이 20%를 초과할 때 발생하는 재구매 저항선과 물류 소외 지역의 페인포인트를 중점적으로 다룹니다.
        """)

        st.markdown("#### 📊 주요 KPI 요약")
        
        # 카드 레이아웃 적용
        kpi_html = """
        <div class="kpi-container">
            <div class="kpi-card">
                <div class="kpi-label">평균 재구매율</div>
                <div class="kpi-value">5.10%</div>
                <div class="kpi-caption">지연에 따른 고객 이탈을 방어하는 핵심 심리적 저항선</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">평균 배송 소요</div>
                <div class="kpi-value">11.6일</div>
                <div class="kpi-caption">전체 배송망의 평균 속도로 최적화가 요구되는 기준점</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">최고 재구매 주</div>
                <div class="kpi-value">RO (5.32%)</div>
                <div class="kpi-caption">물류 시스템이 가장 효율적으로 작동하는 벤치마킹 지역</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">1위 카테고리</div>
                <div class="kpi-value">bed_bath_table</div>
                <div class="kpi-caption">생필품 중 배송 경험이 재구매로 가장 잘 연결되는 품목</div>
            </div>
        </div>
        """
        st.markdown(kpi_html, unsafe_allow_html=True)

        st.markdown("---")

        col_chart, col_insight = st.columns([2, 1])
        
        with col_chart:
            if repurchase_sum is not None:
                fig = px.bar(repurchase_sum, x='배송비 비중 그룹', y='재구매율',
                             text=repurchase_sum['재구매율'].apply(lambda x: f'{x:.2%}'),
                             title='배송비 비중(20% 임계점)에 따른 재구매율 차이',
                             color='배송비 비중 그룹', color_discrete_sequence=['#9fc16e', '#94d8cf'])
                fig.update_layout(yaxis_tickformat='.1%', xaxis_title="배송비 비중 그룹", yaxis_title="재구매율")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("데이터를 불러올 수 없습니다. 경로를 확인해주세요.")
                
        with col_insight:
            st.markdown("#### 🎯 전략 가이드: 물류 최적화 로드맵")
            
            # 섹션 1: 핵심 페인포인트 (🚨)
            st.error("""
            **🚨 핵심 페인포인트: '20%의 저항'**
            - **배송비 심리적 임계점**: 배송비 비중이 20%를 초과하는 순간 고객은 구매 확정 대신 이탈을 선택합니다.
            - **물류 소외 지역의 역설**: 고비용 지역(예: RO)은 배송비가 비쌈에도 불구하고 리드타임이 오히려 길어 만족도가 이중으로 하락합니다.
            """)
            
            # 섹션 2: 비즈니스 제언 (💡)
            st.info("""
            **💡 비즈니스 제언: 선제적 대응 전략**
            - **🎯 배송비 번들링 도입**: 상품 가격에 배송비를 일부 녹이거나, 일정 금액 이상 주문 시 '실질 비중'을 낮추는 넛지 전략이 필요합니다.
            - **🚀 물류 거점 고도화**: 재구매율이 높은 상위 주(RO, SP)를 중심으로 풀필먼트 센터를 전진 배치하여 리드타임을 획기적으로 단축해야 합니다.
            - **💎 프리미엄 배송 태깅**: 저가 상품이라도 배송 가능 일자를 명확히 노출하여 심리적 불안 구간을 해소하십시오.
            """)
            
            # 액션 버튼 유도 (옵션 스타일링)
            st.success("✅ **Next Step:** 상위 재구매 카테고리(Bed Bath Table)의 물류 노선을 우선 점검하십시오.")

    elif del_sub_menu == "💎 경험의 가치: 물류 체감 가치":
        st.header("💎 경험의 가치: 데이터로 증명된 물류 체감 가치")
        desc_sum = load_delivery_data('descriptive_stats_groups.csv')
        if desc_sum is not None:
            st.subheader("📊 그룹별 주요 지표 평균")
            st.dataframe(desc_sum.style.format({'price': '{:.1f}', 'freight_value': '{:.1f}', 'review_score': '{:.2f}'}))

            melted_stats = desc_sum.melt(id_vars='freight_ratio_group', value_vars=['price', 'freight_value'], 
                                        var_name='지표', value_name='값')
            fig_desc = px.bar(melted_stats, x='freight_ratio_group', y='값', color='지표', barmode='group',
                             title='배송비 비중 그룹별 가격 및 배송비 평균 비교',
                             color_discrete_sequence=['#0b134a', '#0c29d0'],
                             labels={'freight_ratio_group': '배송비 비중 그룹'})
            st.plotly_chart(fig_desc, use_container_width=True)
        else:
            st.warning("데이터를 불러올 수 없습니다.")

    elif del_sub_menu == "🚀 성장의 개선: 재구매 최적화":
        st.header("🚀 성장의 개선: 재구매 선순환을 위한 배송비 최적화")
        if repurchase_sum is not None:
            col1, col2 = st.columns([2, 1])
            with col1:
                fig = px.bar(repurchase_sum, x='배송비 비중 그룹', y='재구매율',
                             text=repurchase_sum['재구매율'].apply(lambda x: f'{x:.2%}'),
                             title='배송비 비중(20% 임계점)에 따른 재구매율 차이',
                             color='배송비 비중 그룹', color_discrete_sequence=['#0b134a', '#0c29d0'])
                fig.update_layout(yaxis_tickformat='.1%', xaxis_title="배송비 비중 그룹", yaxis_title="재구매율")
                st.plotly_chart(fig, use_container_width=True)
            with col2:
                st.subheader("💡 발견된 인사이트")
                st.markdown("- **배송비 저항선 포착**: 배송비 비중이 20%를 넘어서는 순간 재구매율이 급격히 하락하는 경향 확인.")
        else:
            st.warning("데이터를 불러올 수 없습니다.")

    elif del_sub_menu == "� 속도와 만족도: 지연의 영향":
        st.header("📉 여정의 불편: 배송 속도와 고객 만족도의 상관관계")
        if speed_sum is not None:
            col_sp1, col_sp2 = st.columns([2, 1])
            with col_sp1:
                fig_speed = px.bar(speed_sum, x='배송비 비중 그룹', y='평균 배송 기간(일)',
                                  text=speed_sum['평균 배송 기간(일)'].apply(lambda x: f'{x:.1f}일'),
                                  title='배송비 부담 그룹별 실제 배송 소요 기간',
                                  color='배송비 비중 그룹', color_discrete_sequence=['#ff4b4b', '#ff9f9f'])
                fig_speed.update_layout(xaxis_title="배송비 비중 그룹", yaxis_title="평균 배송 기간(일)")
                st.plotly_chart(fig_speed, use_container_width=True)
            with col_sp2:
                st.write("📊 그룹별 배송 통계")
                st.dataframe(speed_sum)
        else:
            st.warning("데이터를 불러올 수 없습니다.")

    elif del_sub_menu == "�️ 개선의 확장: 지역 물류 고도화":
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
                                      size='재구매율', color='평균 리뷰 점수', color_continuous_scale='RdYlGn',
                                      labels={'재구매율': '재구매율', '평균 리뷰 점수': '평균 만족도'})
                st.plotly_chart(fig_state, use_container_width=True)

    st.markdown("---")
    st.caption("© 2026 Olist Customer Journey Analysis Project | 저가 생필품 배송비 분석")
