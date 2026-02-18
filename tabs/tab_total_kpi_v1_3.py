import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os


@st.cache_data
def load_data(data_dir):
    """data_commerce 폴더에서 원시 데이터를 로드하고 병합합니다."""
    orders = pd.read_csv(os.path.join(data_dir, "olist_orders_dataset.csv"))
    items = pd.read_csv(os.path.join(data_dir, "olist_order_items_dataset.csv"))
    payments = pd.read_csv(os.path.join(data_dir, "olist_order_payments_dataset.csv"))
    reviews = pd.read_csv(os.path.join(data_dir, "olist_order_reviews_dataset.csv"))
    products = pd.read_csv(os.path.join(data_dir, "olist_products_dataset.csv"))
    customers = pd.read_csv(os.path.join(data_dir, "olist_customers_dataset.csv"))

    # 번역 파일 탐색 (여러 위치 시도)
    trans_path = None
    candidates = [
        os.path.join(data_dir, "product_category_name_translation.csv"),
        os.path.join(os.path.dirname(data_dir), "draft", "seller", "product_category_name_translation.csv"),
    ]
    for p in candidates:
        if os.path.exists(p):
            trans_path = p
            break

    if trans_path:
        category_trans = pd.read_csv(trans_path)
    else:
        category_trans = pd.DataFrame(columns=['product_category_name', 'product_category_name_english'])

    # 날짜 컬럼 변환
    date_cols = [
        'order_purchase_timestamp', 'order_approved_at',
        'order_delivered_carrier_date', 'order_delivered_customer_date',
        'order_estimated_delivery_date'
    ]
    for col in date_cols:
        if col in orders.columns:
            orders[col] = pd.to_datetime(orders[col], errors='coerce')

    # 데이터 병합
    df = orders.merge(items, on='order_id', how='left')
    df = df.merge(payments, on=['order_id'], how='left')
    df = df.merge(customers, on='customer_id', how='left')
    df = df.merge(products, on='product_id', how='left')
    df = df.merge(category_trans, on='product_category_name', how='left')

    df['category'] = df['product_category_name_english'].fillna(df['product_category_name'])

    # 배송 시간 계산
    df['delivery_time'] = (df['order_delivered_customer_date'] - df['order_purchase_timestamp']).dt.days
    df['estimated_delivery_time'] = (df['order_estimated_delivery_date'] - df['order_purchase_timestamp']).dt.days

    # 완료된 주문만
    df = df[df['order_status'] == 'delivered'].copy()

    return df


def render(base_dir, data_dir):
    """전체 KPI 탭 렌더링 - 통합 경영 대시보드 (Cross-Domain)"""

    try:
        df = load_data(data_dir)
    except Exception as e:
        st.error(f"데이터 로드 중 오류 발생: {e}")
        st.info("💡 `data_commerce/` 폴더에 Olist 데이터셋 CSV 파일들이 필요합니다.")
        return

    # --- 전용 CSS 주입 ---
    st.markdown("""
    <style>
        .section-header {
            font-size: 20px;
            font-weight: 700;
            color: #0b134a;
            margin: 30px 0 15px 0;
            padding-left: 10px;
            border-left: 5px solid #0c29d0;
        }
        .kpi-title-text {
            font-size: 14px;
            font-weight: 600;
            color: #50557c;
            margin-bottom: 4px;
        }
        .kpi-val-text {
            font-size: 24px;
            font-weight: 800;
            color: #0b134a;
            margin-bottom: 2px;
        }
        .kpi-desc-text {
            font-size: 12px;
            color: #8b8fb0;
            margin-bottom: 4px; /* 간격 축소 */
            line-height: 1.4;
            height: 34px;
            overflow: hidden;
        }
        /* 호버 인사이트 (Tooltip) - 훨씬 더 크게 조정 */
        .kpi-card-container {
            position: relative;
            cursor: pointer;
            padding: 5px;
            border-radius: 8px;
            transition: background 0.2s;
            height: 100px; /* 텍스트 영역 높이 축소 (110 -> 100) */
            display: flex;
            flex-direction: column;
            justify-content: flex-start;
        }
        .kpi-card-container:hover {
            background: #f8f9ff;
        }
        .kpi-tooltip {
            visibility: hidden;
            width: 580px; /* 텍스트가 거대해지므로 너비 대폭 확장 */
            background-color: #0b134a;
            color: #fff;
            text-align: left;
            border-radius: 15px;
            padding: 32px; /* 여백 극대화 */
            position: absolute;
            z-index: 9999;
            bottom: 115%;
            left: 50%;
            transform: translateX(-50%);
            opacity: 0;
            transition: opacity 0.3s, transform 0.3s;
            font-size: 36px !important; /* 인사이트 텍스트 파격적 확대 (2배 이상) */
            font-weight: 600;
            line-height: 1.3;
            box-shadow: 0 24px 64px rgba(0,0,0,0.4);
            border: 2px solid rgba(255,255,255,0.25);
        }
        .kpi-card-container:hover .kpi-tooltip {
            visibility: visible;
            opacity: 1;
            transform: translateX(-50%) translateY(-15px);
        }
        /* 기본 버튼 스타일 원복 */
        .main div.stButton > button,
        .main button[data-testid="stBaseButton-secondary"] {
            background-color: transparent !important;
            color: #ffffff !important;
            border: 1px solid #ffffff !important;
            padding: 4px 12px !important;
            font-size: 12px !important;
            font-weight: 500 !important;
            text-decoration: none !important;
            box-shadow: none !important;
            opacity: 0.1; /* 평상시 흐리게 */
            transition: all 0.3s ease !important;
        }
        /* 호버 시 선명하게 */
        .main div.stButton > button:hover,
        .main button[data-testid="stBaseButton-secondary"]:hover {
            color: #ffffff !important;
            background-color: rgba(255, 255, 255, 0.1) !important;
            opacity: 1 !important;
            border-color: #ffffff !important;
        }
        /* 비활성화된 버튼(GMV, 총주문)만 투명화하여 숨김 처리 */
        .main button[data-testid="stBaseButton-secondary"]:disabled {
            background-color: transparent !important;
            color: transparent !important;
            border-color: transparent !important;
            opacity: 0 !important;
            pointer-events: none !important;
            cursor: default !important;
        }
        /* 버튼 컨테이너 강제 고정 */
        div.stButton {
            height: 42px !important;
            min-height: 42px !important;
            max-height: 42px !important;
            margin: 0 !important;
            padding: 0 !important;
            display: flex !important;
            align-items: center !important;
            overflow: hidden !important;
        }
        div.stButton > button {
            margin: 0 !important;
        }
        /* 버튼이 없는 카드에 들어갈 대체 공간 (버튼 높이 42px 정확히 일치) */
        .kpi-button-placeholder {
            height: 42px !important;
            width: 100% !important;
            display: block !important;
            visibility: hidden !important; 
            margin: 0 !important;
            padding: 0 !important;
        }
        /* 메인 컨테이너 규격 강제 (사용자 요청: 456.75 * 372) */
        /* Streamlit 버전 차이를 대비하여 여러 선택자 병용 */
        div[data-testid="column"] div.stVerticalBlockBorderWrapper,
        div[data-testid="column"] div[data-testid="stVerticalBlockBorderWrapper"] {
            width: 456.75px !important;
            height: 372px !important;
            min-width: 456.75px !important;
            min-height: 372px !important;
            max-width: 456.75px !important;
            max-height: 372px !important;
            overflow: hidden !important;
            padding: 24px !important;
            margin: 0px !important;
            background-color: #ffffff !important;
            box-sizing: border-box !important;
            display: flex !important;
            flex-direction: column !important;
            justify-content: space-between !important; /* 요소 균등 배분 */
        }
        /* 개별 Plotly 차트 높이 미세 조정 (전체 높이 372에 맞춤) */
        div.stPlotlyChart, div[data-testid="stPlotlyChart"] {
            height: 160px !important;
            min-height: 160px !important;
            max-height: 160px !important;
            margin-top: 0px !important;
        }
    </style>
    """, unsafe_allow_html=True)

    # --- 내비게이션 헬퍼 함수 ---
    def nav_to(page_name):
        st.session_state["main_menu"] = page_name
        st.rerun()

    def kpi_card_header(title, value, desc, tooltip):
        st.markdown(f'''
            <div class="kpi-card-container">
                <div class="kpi-title-text">{title}</div>
                <div class="kpi-val-text">{value}</div>
                <div class="kpi-desc-text">{desc}</div>
                <span class="kpi-tooltip">
                    <strong style="color: #3b82f6; font-size: 22px; display: block; margin-bottom: 16px;">💡 핵심 통찰</strong>
                    {tooltip}
                </span>
            </div>
        ''', unsafe_allow_html=True)

    # --- 상단 필터 ---
    min_date = df['order_purchase_timestamp'].min().date()
    max_date = df['order_purchase_timestamp'].max().date()
    
    st.write("") # 간격 조절
    col_date, col_empty = st.columns([1, 2])
    with col_date:
        date_range = st.date_input("📅 분석 기간 설정", value=(min_date, max_date), key="kpi_master_date")

    if len(date_range) == 2:
        start_date, end_date = date_range
        mask = (df['order_purchase_timestamp'].dt.date >= start_date) & (df['order_purchase_timestamp'].dt.date <= end_date)
        df_filtered = df.loc[mask].copy()
    else:
        df_filtered = df.copy()

    # --- 1. 경영 실적 및 상품 전략 (Core & Product) ---
    st.markdown('<div class="section-header">📉 여정의 불편: 병목 구간 진단 (경영 및 제품)</div>', unsafe_allow_html=True)
    r1_c1, r1_c2, r1_c3, r1_c4 = st.columns(4)
    with r1_c1:
        with st.container(border=True):
            total_rev = df_filtered['payment_value'].sum()
            kpi_card_header("💰 총 매출액 (GMV)", f"R$ {total_rev:,.0f}", "전체 거래 규모 트렌드", "2017년 11월 블랙프라이데이에 역대 최대 매출을 기록했습니다.")
            # 버튼 영역 (상세보기 추가 - 비활성화로 숨김 처리)
            with st.container():
                st.button("상세보기 ➔", key="nav_gmv", type="secondary", disabled=True)
            df_filtered['month'] = df_filtered['order_purchase_timestamp'].dt.to_period('M').astype(str)
            m_s = df_filtered.groupby('month')['payment_value'].sum().reset_index()
            fig1 = px.area(m_s, x='month', y='payment_value', template='plotly_white', height=160)
            fig1.update_traces(line_color='#0c29d0', fillcolor='rgba(12, 41, 208, 0.1)')
            fig1.update_layout(margin=dict(l=5, r=5, t=5, b=25), xaxis_title=None, yaxis_title=None, xaxis=dict(showgrid=False, showticklabels=False), yaxis=dict(showgrid=False, showticklabels=False))
            st.plotly_chart(fig1, use_container_width=True, config={'displayModeBar': False})
    with r1_c2:
        with st.container(border=True):
            total_ord = df_filtered['order_id'].nunique()
            kpi_card_header("📦 총 주문 건수", f"{total_ord:,}건", "요일별 주문 및 구매 패턴", "금요일 오후 2시~4시 사이에 주문이 가장 집중되는 경향이 있습니다.")
            # 버튼 영역 (상세보기 추가 - 비활성화로 숨김 처리)
            with st.container():
                st.button("상세보기 ➔", key="nav_ord", type="secondary", disabled=True)
            day_m = {'Monday': '월', 'Tuesday': '화', 'Wednesday': '수', 'Thursday': '목', 'Friday': '금', 'Saturday': '토', 'Sunday': '일'}
            day_o = ['월', '화', '수', '목', '금', '토', '일']
            df_filtered['dow'] = df_filtered['order_purchase_timestamp'].dt.day_name().map(day_m)
            d_c = df_filtered.groupby('dow')['order_id'].nunique().reindex(day_o).reset_index()
            fig2 = px.bar(d_c, x='dow', y='order_id', template='plotly_white', height=160)
            fig2.update_traces(marker_color='#0c29d0')
            fig2.update_layout(margin=dict(l=10, r=10, t=5, b=30), xaxis_title=None, yaxis_title=None, xaxis=dict(showgrid=False, showticklabels=True, tickfont=dict(size=12, color='#50557c')), yaxis=dict(showgrid=False, showticklabels=False))
            st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})
    with r1_c3:
        with st.container(border=True):
            kpi_card_header("💎 수익 핵심 가격대", "200-500 BRL", "매출 기여도 30.1% 구간", "이 구간은 중고가 가전 및 사무용품 카테고리가 주도하고 있습니다.")
            # 버튼 영역 (Wrapper 제거, 순수 버튼만 랜더링)
            with st.container():
                if st.button("상세보기 ➔", key="nav_price", type="secondary"): nav_to("💳 구매 전환 (Decision)")
            price_bins = [0, 50, 100, 200, 500, 1000, 5000]
            price_labels = ['0-50', '50-100', '100-200', '200-500', '500-1k', '1k+']
            df_filtered['p_bin'] = pd.cut(df_filtered['price'], bins=price_bins, labels=price_labels)
            p_rev = df_filtered.groupby('p_bin', observed=False)['payment_value'].sum().reset_index()
            fig3 = px.bar(p_rev, x='p_bin', y='payment_value', template='plotly_white', height=160)
            fig3.update_traces(marker_color='#50557c')
            fig3.update_layout(margin=dict(l=10, r=10, t=5, b=35), xaxis_title=None, yaxis_title=None, xaxis=dict(showgrid=False, showticklabels=True, tickfont=dict(size=11, color='#50557c')), yaxis=dict(showgrid=False, showticklabels=False))
            st.plotly_chart(fig3, use_container_width=True, config={'displayModeBar': False})
    with r1_c4:
        with st.container(border=True):
            kpi_card_header("🚀 블랙 프라이데이", "11.4배 성장", "시즌 매출 폭발적 매출 증대", "BF 당일 1시간 매출이 평소 하루 매출보다 많아 전용 인프라가 필수적입니다.")
            # 버튼 영역
            with st.container():
                if st.button("상세보기 ➔", key="nav_bf", type="secondary"): nav_to("💳 구매 전환 (Decision)")
            bf_data = pd.DataFrame({'구분': ['평시', 'BF'], '매출': [1, 11.4]})
            fig4 = px.bar(bf_data, x='구분', y='매출', text_auto='.1f', template='plotly_white', height=160)
            fig4.update_traces(marker_color=['#d1d1e3', '#0c29d0'])
            fig4.update_layout(margin=dict(l=10, r=10, t=5, b=30), xaxis_title=None, yaxis_title=None, xaxis=dict(showticklabels=True, tickfont=dict(size=12, color='#50557c')), yaxis=dict(showgrid=False, showticklabels=False))
            st.plotly_chart(fig4, use_container_width=True, config={'displayModeBar': False})

    # --- 2. 물류 및 셀러 파트너 (Logistics & Seller) ---
    st.markdown('<div class="section-header">💎 경험의 가치: 구매 후 만족의 핵심 (물류 및 셀러)</div>', unsafe_allow_html=True)
    r2_c1, r2_c2, r2_c3, r2_c4 = st.columns(4)
    with r2_c1:
        with st.container(border=True):
            kpi_card_header("🔄 무료 배송 효과", "+5.3%p 상승", "저가 생필품 재구매율 증대", "무료 배송 제공 시 고객의 플랫폼 고착 효과(Retention)가 뚜렷하게 나타납니다.")
            with st.container():
                if st.button("상세보기 ➔", key="nav_free", type="secondary"): nav_to("🚚 물류 및 경험 (Fulfillment)")
            re_data = pd.DataFrame({'배송비': ['높음', '무료'], '재구매율': [3.1, 8.4]})
            fig5 = px.line(re_data, x='배송비', y='재구매율', markers=True, template='plotly_white', height=160)
            fig5.update_traces(line_color='#0c29d0', line_width=4)
            fig5.update_layout(margin=dict(l=20, r=20, t=5, b=30), xaxis_title=None, yaxis_title=None, xaxis=dict(showticklabels=True, tickfont=dict(size=12, color='#50557c')), yaxis=dict(showgrid=False, showticklabels=False))
            st.plotly_chart(fig5, use_container_width=True, config={'displayModeBar': False})
    with r2_c2:
        with st.container(border=True):
            avg_d = df_filtered['delivery_time'].mean()
            kpi_card_header("⏱️ 평균 배송 일수", f"{avg_d:.1f}일", "배송 지연 시 만족도 급감", "평균 배송 기간이 12일을 초과할 경우 불만족 리뷰 비율이 2.4배 증가합니다.")
            with st.container():
                if st.button("상세보기 ➔", key="nav_del", type="secondary"): nav_to("🚚 물류 및 경험 (Fulfillment)")
            fig6 = px.histogram(df_filtered[df_filtered['delivery_time']>=0], x='delivery_time', nbins=30, template='plotly_white', height=160)
            fig6.update_traces(marker_color='#50557c', opacity=0.8)
            fig6.update_layout(margin=dict(l=10, r=10, t=5, b=30), xaxis_title=None, yaxis_title=None, xaxis=dict(showgrid=False, showticklabels=True, tickfont=dict(size=12, color='#50557c')), yaxis=dict(showgrid=False, showticklabels=False))
            st.plotly_chart(fig6, use_container_width=True, config={'displayModeBar': False})
    with r2_c3:
        with st.container(border=True):
            total_sellers = df_filtered['seller_id'].nunique()
            kpi_card_header("🏪 활성 셀러 수", f"{total_sellers:,}개", "매출 발생 중인 파트너사", "전체 셀러의 약 15%가 플랫폼 거래액의 대부분을 발생시키고 있습니다.")
            with st.container():
                if st.button("상세보기 ➔", key="nav_sel", type="secondary"): nav_to("🏢 파트너십 가치 (Partnership)")
            s_rev = df_filtered.groupby('seller_id')['payment_value'].sum().sort_values(ascending=False).reset_index()
            s_rev['cumulative_rev'] = s_rev['payment_value'].cumsum() / s_rev['payment_value'].sum() * 100
            fig_s1 = px.line(s_rev.head(100), y='cumulative_rev', template='plotly_white', height=160)
            fig_s1.update_traces(line_color='#0c29d0', fill='tozeroy', fillcolor='rgba(12, 41, 208, 0.1)')
            fig_s1.update_layout(margin=dict(l=10, r=10, t=5, b=25), xaxis_title=None, yaxis_title=None, xaxis=dict(showgrid=False, showticklabels=False), yaxis=dict(showgrid=False, showticklabels=False))
            st.plotly_chart(fig_s1, use_container_width=True, config={'displayModeBar': False})
    with r2_c4:
        with st.container(border=True):
            kpi_card_header("📊 셀러 집중도", "Top 10%가 72%", "상위 셀러 매출 견인 구조", "핵심 셀러(Tier 1)의 이탈은 플랫폼 매출에 직접적인 리스크를 초래합니다.")
            with st.container():
                if st.button("상세보기 ➔", key="nav_conc", type="secondary"): nav_to("🏢 파트너십 가치 (Partnership)")
            tier_data = pd.DataFrame({'등급': ['T1', 'T2', 'T3'], '비중': [72, 20, 8]})
            fig_s2 = px.bar(tier_data, x='등급', y='비중', text_auto=True, template='plotly_white', height=160)
            fig_s2.update_traces(marker_color=['#0c29d0', '#50557c', '#d1d1e3'])
            fig_s2.update_layout(margin=dict(l=10, r=10, t=5, b=30), xaxis_title=None, yaxis_title=None, xaxis=dict(showticklabels=True, tickfont=dict(size=12, color='#50557c')), yaxis=dict(showgrid=False, showticklabels=False))
            st.plotly_chart(fig_s2, use_container_width=True, config={'displayModeBar': False})

    # --- 3. 핵심 전략 및 고객 통찰 (Strategic Insights) ---
    st.markdown('<div class="section-header">🚀 성장의 개선: 실행 가능한 전략 로드맵</div>', unsafe_allow_html=True)
    r3_c1, r3_c2, r3_c3, r3_c4 = st.columns(4)
    with r3_c1:
        with st.container(border=True):
            kpi_card_header("💎 VIP 매출 기여도", "35% 차지", "상위 10% 고객사 기여 비중", "VIP 고객군을 위한 전용 멤버십이나 배송 혜택 강화가 매출 성장의 핵심입니다.")
            with st.container():
                if st.button("상세보기 ➔", key="nav_vip", type="secondary"): nav_to("💎 로열티 및 개선 (Loyalty)")
            seg_data = pd.DataFrame({'그룹': ['기타', 'VIP'], '비중': [65, 35]})
            fig7 = px.pie(seg_data, values='비중', names='그룹', hole=0.6, color_discrete_sequence=['#e6eeff', '#0c29d0'], height=160)
            fig7.update_layout(margin=dict(l=0, r=0, t=0, b=0), showlegend=False)
            st.plotly_chart(fig7, use_container_width=True, config={'displayModeBar': False})
    with r3_c2:
        with st.container(border=True):
            kpi_card_header("🎟️ 바우처 효과", "12% 증가", "바우처 사용 시 객단가 상승", "바우처는 신규 유입보다는 기존 고객의 객단가(AOV)를 높이는 데 더 효과적입니다.")
            with st.container():
                if st.button("상세보기 ➔", key="nav_vouch", type="secondary"): nav_to("💎 로열티 및 개선 (Loyalty)")
            v_data = pd.DataFrame({'구분': ['일반', '바우처'], '객단가': [100, 112]})
            fig8 = px.bar(v_data, x='구분', y='객단가', template='plotly_white', height=160)
            fig8.update_traces(marker_color=['#d1d1e3', '#0c29d0'])
            fig8.update_layout(margin=dict(l=10, r=10, t=5, b=30), xaxis_title=None, yaxis_title=None, xaxis=dict(showticklabels=True, tickfont=dict(size=12, color='#50557c')), yaxis=dict(showgrid=False, showticklabels=False))
            st.plotly_chart(fig8, use_container_width=True, config={'displayModeBar': False})
    with r3_c3:
        with st.container(border=True):
            kpi_card_header("📉 지연 만족도 하락", "1.5점 급감", "2일 이상 지연 시 리뷰 하락", "배송 예정 기한보다 2일 이상 늦어지면 고객의 이탈 의향이 급격히 높아집니다.")
            with st.container():
                if st.button("상세보기 ➔", key="nav_sat", type="secondary"): nav_to("🚚 물류 및 경험 (Fulfillment)")
            delay_data = pd.DataFrame({'지연': ['정시', '지연'], '점수': [4.8, 3.3]})
            fig9 = px.bar(delay_data, x='지연', y='점수', template='plotly_white', height=160)
            fig9.update_traces(marker_color=['#0c29d0', '#ef4444'])
            fig9.update_layout(margin=dict(l=10, r=10, t=5, b=30), xaxis_title=None, yaxis_title=None, xaxis=dict(showticklabels=True, tickfont=dict(size=12, color='#50557c')), yaxis=dict(showgrid=False, showticklabels=False))
            st.plotly_chart(fig9, use_container_width=True, config={'displayModeBar': False})
    with r3_c4:
        with st.container(border=True):
            kpi_card_header("🗺️ 지역별 배송 격차", "최대 8.5일", "북동부 vs 남동부 성능 차이", "북동부(AM) 지역의 높은 물류 비용과 배송 기간은 플랫폼 확장의 장애물입니다.")
            with st.container():
                if st.button("상세보기 ➔", key="nav_geo", type="secondary"): nav_to("🚚 물류 및 경험 (Fulfillment)")
            geo_diff = pd.DataFrame({'지역': ['SP(남동)', 'AM(북부)'], '일수': [10.2, 18.7]})
            fig10 = px.bar(geo_diff, x='지역', y='일수', template='plotly_white', height=160)
            fig10.update_traces(marker_color=['#0c29d0', '#50557c'])
            fig10.update_layout(margin=dict(l=10, r=10, t=5, b=35), xaxis_title=None, yaxis_title=None, xaxis=dict(showticklabels=True, tickfont=dict(size=11, color='#50557c')), yaxis=dict(showgrid=False, showticklabels=False))
            st.plotly_chart(fig10, use_container_width=True, config={'displayModeBar': False})

    st.markdown("---")
    f1, f2, f3 = st.columns(3)
    f1.caption(f"📅 시작: {start_date}")
    f2.caption(f"📅 종료: {end_date}")
    f3.caption(f"업데이트: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}")
