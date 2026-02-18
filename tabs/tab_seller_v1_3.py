import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import plotly.express as px
import plotly.graph_objects as go
import os


# ====== 데이터 로드 함수 ======
@st.cache_data
def load_agg_data(seller_dir):
    path = os.path.join(seller_dir, "output", "cash_flow", "seller_cash_flow_detailed.csv")
    if os.path.exists(path): return pd.read_csv(path)
    return None

@st.cache_data
def load_transaction_data(seller_dir):
    path = os.path.join(seller_dir, "output", "cash_flow", "seller_transaction_details.csv")
    if os.path.exists(path): return pd.read_csv(path)
    return None

@st.cache_data
def load_tier_data(seller_dir):
    path = os.path.join(seller_dir, "output", "seller_tiers", "all_sellers_metrics.csv")
    if os.path.exists(path): return pd.read_csv(path)
    return None

@st.cache_data
def load_risk_data(seller_dir):
    path = os.path.join(seller_dir, "output", "risk", "sales_surge_risk.csv")
    if os.path.exists(path): return pd.read_csv(path)
    return None

@st.cache_data
def load_risk_all_data(seller_dir):
    path = os.path.join(seller_dir, "output", "risk", "sales_surge_all.csv")
    if os.path.exists(path): return pd.read_csv(path)
    return None

@st.cache_data
def load_market_cat_data(seller_dir):
    path = os.path.join(seller_dir, "output", "risk", "market_category_trends.csv")
    if os.path.exists(path): return pd.read_csv(path)
    return None

@st.cache_data
def load_category_translation(seller_dir):
    path = os.path.join(seller_dir, "product_category_name_translation.csv")
    if os.path.exists(path):
        try: return pd.read_csv(path)
        except: pass
    return None

@st.cache_data
def load_forecast_data(seller_dir):
    path = os.path.join(seller_dir, "output", "risk", "daily_sales_series.csv")
    if os.path.exists(path): return pd.read_csv(path)
    return None

@st.cache_data
def load_scm_data(seller_dir):
    path = os.path.join(seller_dir, "output", "scm", "seller_lead_time_analysis.csv")
    if os.path.exists(path): return pd.read_csv(path)
    return None

@st.cache_data
def load_route_data(seller_dir):
    path = os.path.join(seller_dir, "output", "scm", "route_lead_time_stats.csv")
    if os.path.exists(path): return pd.read_csv(path)
    return None

@st.cache_data
def load_geo_data(seller_dir):
    path = os.path.join(seller_dir, "output", "risk", "seller_geo_stats.csv")
    if os.path.exists(path): return pd.read_csv(path)
    return None

@st.cache_data
def load_sku_data(seller_dir):
    path = os.path.join(seller_dir, "output", "risk", "seller_sku_stats.csv")
    if os.path.exists(path): return pd.read_csv(path)
    return None

@st.cache_data
def load_raw_commerce_data(data_dir):
    """Load raw data for dynamic SKU analysis."""
    try:
        _items = pd.read_csv(os.path.join(data_dir, 'olist_order_items_dataset.csv'))
        _orders = pd.read_csv(os.path.join(data_dir, 'olist_orders_dataset.csv'))
        _products = pd.read_csv(os.path.join(data_dir, 'olist_products_dataset.csv'))
        _trans = pd.read_csv(os.path.join(data_dir, 'product_category_name_translation.csv'))

        _orders['order_purchase_timestamp'] = pd.to_datetime(_orders['order_purchase_timestamp'], errors='coerce')
        _orders['order_delivered_carrier_date'] = pd.to_datetime(_orders['order_delivered_carrier_date'], errors='coerce')
        _orders['order_delivered_customer_date'] = pd.to_datetime(_orders['order_delivered_customer_date'], errors='coerce')

        df = _items.merge(_orders, on='order_id', how='left')
        df = df.merge(_products[['product_id', 'product_category_name']], on='product_id', how='left')
        df = df.merge(_trans, on='product_category_name', how='left')
        df.rename(columns={'product_category_name_english': 'category_eng'}, inplace=True)
        return df
    except Exception:
        return None


# ====== 메인 렌더 함수 ======
def render(base_dir, data_dir):
    """셀러 운영 분석 탭 렌더링"""

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

    SELLER_DIR = os.path.join(base_dir, "draft", "seller")


    # === 데이터 로드 및 전처리에 필요한 설정 ===
    df_agg = load_agg_data(SELLER_DIR)
    df_tier = load_tier_data(SELLER_DIR)
    cat_trans = load_category_translation(SELLER_DIR)

    if df_agg is None or df_tier is None:
        st.error("⚠️ 셀러 데이터를 로드할 수 없습니다.")
        return

    # Tier & Risk mapping for formatting
    tier_map = dict(zip(df_tier['seller_id'], df_tier['tier']))
    df_risks_data = load_risk_data(SELLER_DIR)
    risk_list = df_risks_data['seller_id'].unique().tolist() if df_risks_data is not None else []

    def format_seller(s_id):
        labels = []
        if s_id in tier_map:
            t = str(tier_map[s_id])
            if 'Tier 1' in t: labels.append("💎 T1")
        if s_id in risk_list: labels.append("🚨 Risk")
        return f"{s_id[:12]} ({', '.join(labels)})" if labels else s_id[:15]

    # === 통합 싱글 로우 헤더 (Simplified Widgets) ===
    col_search, col_select = st.columns([1, 1])

    # 검색 영역 (좌측 1/2)
    with col_search:
        st.markdown('<p style="font-size:13px; font-weight:700; color:#50557c; margin-bottom:8px; display:flex; align-items:center;"><span style="margin-right:8px;">🔍</span> 셀러 ID 검색</p>', unsafe_allow_html=True)
        seller_search = st.text_input("셀러 검색", "", key="seller_search_input", placeholder="ID 입력 시 아래 목록이 필터링됩니다...", label_visibility="collapsed")

    # 선택 영역 (우측 1/2)
    with col_select:
        available_sellers = sorted(df_agg['seller_id'].unique().tolist())
        if seller_search:
            available_sellers = [s for s in available_sellers if seller_search.lower() in s.lower()]
        
        st.markdown('<p style="font-size:13px; font-weight:700; color:#50557c; margin-bottom:8px; display:flex; align-items:center;"><span style="margin-right:8px;">🎯</span> 분석 대상 셀러 선택</p>', unsafe_allow_html=True)
        if available_sellers:
            sel = st.selectbox("셀러 선택", available_sellers, format_func=format_seller, key="seller_select", label_visibility="collapsed")
        else:
            st.selectbox("셀러 선택", ["일치하는 셀러가 없습니다"], disabled=True, label_visibility="collapsed")
            sel = None

    selected_seller = sel if sel != "일치하는 셀러가 없습니다" and sel is not None else None
    st.markdown("<div style='margin-bottom: 25px;'></div>", unsafe_allow_html=True)

    # === 서브 메뉴 네비게이션 (Custom Button Tab Bar) ===
    tabs = [
        "📉 여정의 불편: 운영 리스크 진단", 
        "💎 경험의 가치: 정산 및 유동성", 
        "🚀 성장의 개선: 재고 및 판매 기회", 
        "🚀 개선의 확장: AI 물류 지능화"
    ]
    
    if "seller_sub_menu" not in st.session_state:
        st.session_state["seller_sub_menu"] = tabs[0]

    col_t1, col_t2, col_t3, col_t4 = st.columns(4)
    tab_cols = [col_t1, col_t2, col_t3, col_t4]
    
    for i, tab_name in enumerate(tabs):
        is_active = st.session_state["seller_sub_menu"] == tab_name
        if tab_cols[i].button(
            tab_name, 
            key=f"seller_tab_btn_{i}", 
            use_container_width=True,
            type="primary" if is_active else "secondary"
        ):
            st.session_state["seller_sub_menu"] = tab_name
            st.rerun()

    sub_menu = st.session_state["seller_sub_menu"]

    # --- 서브 메뉴 콘텐츠 기반 조건부 렌더링 ---
    if sub_menu == "📉 여정의 불편: 운영 리스크 진단":
        _render_risk_tab(SELLER_DIR, data_dir, selected_seller, df_agg, df_tier)

    # --- Tab: Cash Flow Cycle ---
    elif sub_menu == "💎 경험의 가치: 정산 및 유동성":
        st.header("💎 경험의 가치: 파트너 정산 및 자금 유동성 분석")
        st.markdown("할부 결제로 인한 **명목 매출(GMV)**과 **실제 현금 유입(Realized Cash)** 간의 시차(Gap)를 분석합니다.")

        st.caption(f"Currently Analyzing: **{selected_seller}**")
        st.divider()

        # Promotion Banner for Tier 1 Sellers
        if df_tier is not None:
            current_tier_info = df_tier[df_tier['seller_id'] == selected_seller]
            if not current_tier_info.empty:
                tier_str = str(current_tier_info['tier'].iloc[0])
                if str(tier_str).startswith("Tier 1"):
                    st.markdown("""
                    <div style="background: linear-gradient(100deg, #1e3a8a 0%, #3b82f6 100%); padding: 20px; border-radius: 12px; border: 1px solid #60a5fa; margin-bottom: 25px; box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4);">
                        <div style="display: flex; align-items: start;">
                            <div style="font-size: 30px; margin-right: 15px;">💎</div>
                            <div>
                                <h3 style="color: #ffffff !important; margin: 0 0 8px 0; font-weight: 700;">선입금 프로모션대상 (Premium Benefit)</h3>
                                <p style="color: #dbeafe; font-size: 16px; margin: 0; line-height: 1.6;">
                                    귀하는 <strong>Tier 1 최상위 파트너</strong>이십니다. <br>
                                    할부 결제로 묶인 자금을 기다리지 마세요. <strong>'실제 현금 선입금'</strong> 서비스를 통해 즉각적인 유동성을 확보하실 수 있습니다.
                                </p>
                                <div style="margin-top: 12px;">
                                    <span style="background-color: rgba(255,255,255,0.2); color: #ffffff; padding: 4px 10px; border-radius: 6px; font-size: 13px;">✨ 이탈 방지 특별 케어 프로그램</span>
                                </div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

        # Monthly Cash Flow Cycle
        st.subheader("📉 월별 현금 흐름 사이클 (Monthly Overview)")

        data = df_agg[df_agg['seller_id'] == selected_seller].copy()
        data['month'] = pd.to_datetime(data['month'])
        data['nominal_gmv'] = pd.to_numeric(data['nominal_gmv'], errors='coerce').fillna(0)
        data['realized_cash'] = pd.to_numeric(data['realized_cash'], errors='coerce').fillna(0)
        data = data.sort_values('month').set_index('month')

        total_gmv = data['nominal_gmv'].sum()
        total_cash = data['realized_cash'].sum()
        deferred_gap = total_gmv - total_cash

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("총 명목 매출 (GMV)", f"R$ {total_gmv:,.2f}")
        col2.metric("총 현금 유입액", f"R$ {total_cash:,.2f}")
        col3.metric("총 유입 지연금 (Gap)", f"R$ {deferred_gap:,.2f}", delta_color="off" if deferred_gap > 0 else "normal")
        col4.metric("현금 회수율", f"{(total_cash / total_gmv * 100) if total_gmv > 0 else 0:.1f}%")

        st.markdown("###### 📊 GMV vs Realized Cash 추이")
        chart_data_line = data.reset_index()
        chart_data_line_melted = chart_data_line.melt('month', value_vars=['nominal_gmv', 'realized_cash'], var_name='Type', value_name='Amount')
        chart_data_line_melted['Type'] = chart_data_line_melted['Type'].replace({'nominal_gmv': '명목 매출', 'realized_cash': '실제 현금'})
        base_line = alt.Chart(chart_data_line_melted).mark_line().encode(
            x=alt.X('month', title='월', axis=alt.Axis(format='%Y-%m', labelAngle=-45)),
            y=alt.Y('Amount', title='금액 (BRL)'),
            color=alt.Color('Type', title='구분', scale=alt.Scale(domain=['명목 매출', '실제 현금'], range=['#3b82f6', '#10b981'])),
            tooltip=['month', 'Type', 'Amount']
        ).properties(height=350)
        st.altair_chart(base_line, use_container_width=True)

        st.divider()

        # Monthly Net Cash Flow
        st.subheader("📆 월별 순 현금 흐름 (Monthly Net Cash Flow)")
        st.info("💡 **가정**: 주문 시점에 매출액의 **70%가 선지출(비용)**된다고 가정하여, 실제 현금 흐름(입금-출금)을 **월 단위**로 시뮬레이션합니다.")

        df_trans = load_transaction_data(SELLER_DIR)
        if df_trans is not None:
            sel_trans = df_trans[df_trans['seller_id'] == selected_seller].copy()

            if not sel_trans.empty:
                sel_trans['order_approved_at'] = pd.to_datetime(sel_trans['order_approved_at'], errors='coerce')
                sel_trans = sel_trans.dropna(subset=['order_approved_at'])

                flow_rows = []
                cost_ratio = 0.70

                for _, row in sel_trans.iterrows():
                    p_val = row['payment_value']
                    inst = int(row['payment_installments'])
                    if inst <= 0: inst = 1
                    base_date = row['order_approved_at']

                    flow_rows.append({'date': base_date, 'amount': -1 * p_val * cost_ratio, 'type': 'Outflow'})

                    if row['payment_type'] == 'credit_card':
                        unit_val = p_val / inst
                        for i in range(1, inst + 1):
                            deposit_dt = base_date + pd.Timedelta(days=30*i)
                            flow_rows.append({'date': deposit_dt, 'amount': unit_val, 'type': 'Inflow'})
                    else:
                        deposit_dt = base_date + pd.Timedelta(days=3)
                        flow_rows.append({'date': deposit_dt, 'amount': p_val, 'type': 'Inflow'})

                if flow_rows:
                    df_flow = pd.DataFrame(flow_rows)
                    df_flow['date'] = pd.to_datetime(df_flow['date'])

                    df_monthly = df_flow.set_index('date').resample('MS')['amount'].sum().reset_index()

                    monthly_chart = alt.Chart(df_monthly).mark_bar().encode(
                        x=alt.X('date:T', title='월 (Month)', axis=alt.Axis(format='%Y-%m')),
                        y=alt.Y('amount:Q', title='순 현금 흐름 (BRL)'),
                        color=alt.condition(
                            alt.datum.amount > 0,
                            alt.value('#10b981'),
                            alt.value('#ef4444')
                        ),
                        tooltip=[
                            alt.Tooltip('date', format='%Y-%m', title='월'),
                            alt.Tooltip('amount', format=',.2f', title='순 증감액')
                        ]
                    ).properties(height=300).interactive()

                    st.altair_chart(monthly_chart, use_container_width=True)
                else:
                    st.warning("유효한 결제 내역이 없습니다.")
            else:
                st.warning("상세 거래 내역이 없습니다.")
        else:
            st.warning("상세 데이터 파일을 찾을 수 없습니다.")

    elif sub_menu == "🚀 성장의 개선: 재고 및 판매 기회":
        _render_turnover_tab(SELLER_DIR, data_dir, selected_seller)

    elif sub_menu == "🚀 개선의 확장: AI 물류 지능화":
        _render_scm_tab(SELLER_DIR, data_dir, selected_seller, df_tier)


def _render_turnover_tab(SELLER_DIR, data_dir, selected_seller):
    """고회전/급판매 분석 탭"""
    st.header("🚀 성장의 개선: 재고 리스크 및 판매 골든타임 분석")
    st.markdown("**재고 소진 위험(Stockout Risk)**이 높은 '급판매(Sales Surge)' 구간을 탐지하여 최적의 발주 시점을 제시합니다.")

    df_risk = load_risk_data(SELLER_DIR)
    df_all = load_risk_all_data(SELLER_DIR)
    df_market = load_market_cat_data(SELLER_DIR)

    if df_risk is not None and df_all is not None:
        st.subheader(f"분석 대상: {selected_seller}")

        risk_sellers = df_risk['seller_id'].unique().tolist()
        if selected_seller in risk_sellers:
            st.error(f"🚨 **위기 감지(Risk Detected)**: 최근 급판매 혹은 재고 소진 위험이 높은 셀러입니다.")
        else:
            st.success("✅ 정상 (Normal Trend): 특이 사항 없음")

        with st.expander("💡 재고 위험도(Z-Score) 산출 원리 및 기준 상세 안내"):
            st.markdown("**1. 산출 공식**: Z = (현재 - 평균) / 표준편차")

        st.divider()
        st.subheader("📈 판매 트렌드 확인 (카테고리별/전체)")

        seller_all = df_all[df_all['seller_id'] == selected_seller].copy()
        raw_cats = seller_all['category_eng'].unique().tolist()
        display_cats = []
        if 'ALL_CATEGORIES' in raw_cats:
            display_cats.append('ALL_CATEGORIES')
            for c in sorted(raw_cats):
                if c != 'ALL_CATEGORIES': display_cats.append(c)
        else:
            display_cats = sorted(raw_cats)

        selected_cat = st.selectbox("분석 대상 선택", display_cats, index=0, key="tab2_cat")

        chart_data = seller_all[seller_all['category_eng'] == selected_cat].sort_values('month').copy()
        chart_data['month_dt'] = pd.to_datetime(chart_data['month'])

        max_y = chart_data['sales_count'].max()
        if 'moving_avg_30d' in chart_data.columns:
            max_y = max(max_y, chart_data['moving_avg_30d'].max())
        if df_market is not None:
            market_data_temp = df_market[df_market['category_eng'] == selected_cat]
            if not market_data_temp.empty:
                max_y = max(max_y, market_data_temp['market_avg_sales'].max())

        y_domain = [0, max_y * 1.10]

        line = alt.Chart(chart_data).mark_line(point=True, color='#3b82f6').encode(
            x=alt.X('month_dt:T', title='월'),
            y=alt.Y('sales_count:Q', title='판매량', scale=alt.Scale(domain=y_domain)),
            tooltip=['month', 'sales_count', 'z_score']
        )
        ma_line = alt.Chart(chart_data).mark_line(strokeDash=[5,5], color='#60a5fa', opacity=0.7).encode(
            x='month_dt:T', y='moving_avg_30d:Q'
        )
        layers = [line, ma_line]

        if 'z_score' in chart_data.columns:
            points = alt.Chart(chart_data[chart_data['z_score'] > 2.0]).mark_circle(color='red', size=100).encode(
                x='month_dt:T', y='sales_count:Q', tooltip=['month', 'sales_count', 'z_score', 'risk_level']
            )
            layers.append(points)

        st.altair_chart(alt.layer(*layers).properties(height=500).interactive(), use_container_width=True)
        st.caption("🔵 내 판매량 | 🔵-- 30일 이동평균 | 🔴 위험 지점")

        st.divider()

        # Practical Insights
        st.subheader("📉 시장 변동성 요인 분석 (Seasonality & Event Impact)")
        st.markdown("시장 전체 트렌드와 비교하여 **구매 골든타임**을 파악하고 마케팅 전략을 수립하세요.")

        raw_data = load_raw_commerce_data(data_dir)
        if raw_data is not None:
            cat_raw = raw_data if selected_cat == 'ALL_CATEGORIES' else raw_data[raw_data['category_eng'] == selected_cat]

            if not cat_raw.empty:
                col_d1, col_d2 = st.columns(2)
                with col_d1:
                    st.markdown("##### 📅 요일별 구매 패턴 (Weekly Pattern)")
                    cat_raw_copy = cat_raw.copy()
                    cat_raw_copy['day_name'] = cat_raw_copy['order_purchase_timestamp'].dt.day_name()
                    order_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                    dow_counts = cat_raw_copy['day_name'].value_counts().reindex(order_days).reset_index()
                    dow_counts.columns = ['Day', 'Orders']

                    c_dow = alt.Chart(dow_counts).mark_bar().encode(
                        x=alt.X('Day', sort=order_days, title=None, axis=alt.Axis(labelAngle=-45)),
                        y=alt.Y('Orders', title=None),
                        color=alt.condition(alt.datum.Orders == dow_counts['Orders'].max(), alt.value('#3b82f6'), alt.value('#cbd5e1'))
                    ).properties(height=220)
                    st.altair_chart(c_dow, use_container_width=True)
                    max_day_idx = dow_counts['Orders'].argmax()
                    max_day = dow_counts.iloc[max_day_idx]['Day']
                    st.info(f"💡 **{max_day}**에 주문이 가장 집중됩니다.")

                with col_d2:
                    st.markdown("##### ⏰ 시간대별 골든 타임")
                    cat_raw_copy2 = cat_raw.copy()
                    cat_raw_copy2['hour'] = cat_raw_copy2['order_purchase_timestamp'].dt.hour
                    hour_counts = cat_raw_copy2.groupby('hour')['order_id'].count().reset_index(name='Orders')

                    c_hour = alt.Chart(hour_counts).mark_area(
                        line={'color':'#8b5cf6'},
                        color=alt.Gradient(gradient='linear', stops=[
                            alt.GradientStop(color='#8b5cf6', offset=0),
                            alt.GradientStop(color='white', offset=1)
                        ])
                    ).encode(
                        x=alt.X('hour', title='시간'), y='Orders'
                    ).properties(height=220)
                    max_h_row = hour_counts.loc[hour_counts['Orders'].idxmax()]
                    rule = alt.Chart(pd.DataFrame([max_h_row])).mark_rule(color='red').encode(x='hour')
                    st.altair_chart(c_hour + rule, use_container_width=True)
                    st.info(f"💡 **{int(max_h_row['hour'])}시** 전후로 트래픽이 급증합니다.")
    else:
        st.warning("재고 위험 분석 데이터를 찾을 수 없습니다.")
        st.info(f"📂 필요 경로: `{SELLER_DIR}/output/risk/`")



def _render_risk_tab(SELLER_DIR, data_dir, selected_seller, df_agg, df_tier):
    """종합 운영 리스크 분석 탭"""
    st.header("📉 여정의 불편: 셀러 운영 건전성 및 리스크 진단")

    df_sku = load_sku_data(SELLER_DIR)
    if df_sku is not None:
        sel_op = selected_seller
        st.caption(f"Currently Analyzing: **{sel_op}**")

        # Seller Profile & Risk Summary (7 Key Metrics)
        st.markdown("##### 📋 실무 인사이트 요약")

        # 1. Tier Info
        tier_val = "-"
        if df_tier is not None:
            t_row = df_tier[df_tier['seller_id'] == sel_op]
            if not t_row.empty: tier_val = t_row['tier'].iloc[0]

        # 2. Total Orders & Review Score & Top Category
        total_orders = 0
        avg_review = 0.0
        top_cat = "-"

        sku_subset = df_sku[df_sku['seller_id'] == sel_op]
        if not sku_subset.empty:
            total_orders = sku_subset['sku_sales_count'].sum()
            if total_orders > 0:
                avg_review = (sku_subset['sku_avg_review_score'] * sku_subset['sku_sales_count']).sum() / total_orders
            else:
                avg_review = sku_subset['sku_avg_review_score'].mean()
            top_cat = sku_subset.groupby('category_eng')['sku_sales_count'].sum().idxmax()

        # 3. Monthly Avg Orders
        monthly_avg = 0
        if df_agg is not None:
            agg_subset = df_agg[df_agg['seller_id'] == sel_op]
            if not agg_subset.empty:
                months_count = agg_subset['month'].nunique()
                if months_count > 0:
                    monthly_avg = total_orders / months_count

        # 4. Avg Handling & Delivery Time
        avg_handling = 0.0
        avg_delivery = 0.0
        delta_val = None
        top_state = "-"

        try:
            if os.path.exists(data_dir):
                _items = pd.read_csv(os.path.join(data_dir, 'olist_order_items_dataset.csv'))
                _orders = pd.read_csv(os.path.join(data_dir, 'olist_orders_dataset.csv'))

                sel_items = _items[_items['seller_id'] == sel_op]
                sel_raw_direct = sel_items.merge(_orders, on='order_id', how='left')

                if not sel_raw_direct.empty:
                    sel_raw_direct['p'] = pd.to_datetime(sel_raw_direct['order_purchase_timestamp'])
                    sel_raw_direct['c'] = pd.to_datetime(sel_raw_direct['order_delivered_carrier_date'])
                    sel_raw_direct['d'] = pd.to_datetime(sel_raw_direct['order_delivered_customer_date'])

                    avg_handling = ((sel_raw_direct['c'] - sel_raw_direct['p']).dt.total_seconds() / 86400).mean()
                    avg_delivery = ((sel_raw_direct['d'] - sel_raw_direct['p']).dt.total_seconds() / 86400).mean()

            # Benchmark (Tier 1)
            raw_df_profile = load_raw_commerce_data(data_dir)
            if raw_df_profile is not None and df_tier is not None:
                tier1_ids = df_tier[df_tier['tier'].astype(str).str.contains('Tier 1', na=False)]['seller_id'].unique()
                if len(tier1_ids) > 0:
                    t1_raw = raw_df_profile[raw_df_profile['seller_id'].isin(tier1_ids)]
                    if not t1_raw.empty:
                        t1_d_days = (t1_raw['order_delivered_customer_date'] - t1_raw['order_purchase_timestamp']).dt.total_seconds() / (24*3600)
                        tier1_avg = t1_d_days.mean()
                        if pd.notna(tier1_avg) and pd.notna(avg_delivery):
                            diff = avg_delivery - tier1_avg
                            delta_val = f"{diff:+.1f}일 (vs Tier 1)"
        except Exception as e:
            st.error(f"Time Calc Error: {e}")

        # 5. Top State from Geo Data
        df_geo_tmp = load_geo_data(SELLER_DIR)
        if df_geo_tmp is not None:
            g_rows = df_geo_tmp[df_geo_tmp['seller_id'] == sel_op]
            if not g_rows.empty:
                top_rec = g_rows.sort_values('order_count', ascending=False).iloc[0]
                top_state = f"{top_rec['customer_state']}"

        # Display Metrics
        m1, m2, m3, m4, m5, m6, m7, m8 = st.columns(8)
        m1.metric("판매자 등급", tier_val)
        m2.metric("총 주문 건수", f"{int(total_orders):,}건")
        m3.metric("월 평균 주문", f"{int(monthly_avg):,}건")
        m4.metric("고객 만족도", f"{avg_review:.1f}")
        m5.metric("평균 출고 시간", f"{avg_handling:.1f}일")
        m6.metric("다빈도 배송지", top_state)
        m7.metric("평균 배송 시간", f"{avg_delivery:.1f}일", delta=delta_val, delta_color="inverse")
        m8.metric("주력 카테고리", top_cat)

        st.divider()
        st.subheader("🔍 카테고리 내 SKU별 성과")
        sku_filtered = df_sku[df_sku['seller_id'] == sel_op].copy()

        my_cats = sku_filtered['category_eng'].unique().tolist()
        my_cats = ['ALL_CATEGORIES'] + sorted(my_cats)
        sel_cat_op = st.selectbox("카테고리 선택", my_cats, key='tab3_cat')

        if sel_cat_op != 'ALL_CATEGORIES':
            sku_filtered = sku_filtered[sku_filtered['category_eng'] == sel_cat_op]

        if not sku_filtered.empty:
            top_skus = sku_filtered.sort_values('sku_sales_count', ascending=False).head(10)
            st.dataframe(
                top_skus[['product_id', 'sku_sales_count', 'sku_share_in_cat', 'sku_avg_review_score', 'sku_avg_price']]
                .style
                .format({
                    'sku_share_in_cat': '{:.2f}',
                    'sku_avg_review_score': '{:.2f}',
                    'sku_avg_price': '{:.2f}'
                })
                .background_gradient(subset=['sku_sales_count']),
                use_container_width=True
            )

        st.divider()
        st.subheader("가격 포지셔닝 분석 (Price Positioning)")

        target_cat_pp = sel_cat_op
        if target_cat_pp == 'ALL_CATEGORIES':
            if not sku_filtered.empty:
                top_c_s = sku_filtered.groupby('category_eng')['sku_sales_count'].sum().sort_values(ascending=False)
                if not top_c_s.empty:
                    target_cat_pp = top_c_s.index[0]
                    st.info(f"💡 전체 카테고리 대신, 귀하의 주력 카테고리인 **'{target_cat_pp}'**를 기준으로 분석합니다.")

        if target_cat_pp != 'ALL_CATEGORIES':
            st.caption(f"Analyzing Category: **{target_cat_pp}**")

            raw_df = load_raw_commerce_data(data_dir)
            if raw_df is not None:
                cat_items = raw_df[raw_df['category_eng'] == target_cat_pp]
                if not cat_items.empty:
                    p95 = cat_items['price'].quantile(0.95)
                    market_prices = cat_items[cat_items['price'] <= p95]
                    hist_chart = alt.Chart(market_prices).mark_bar(color='#e2e8f0').encode(
                        x=alt.X('price:Q', bin=alt.Bin(maxbins=50), title='가격대 (BRL)'),
                        y=alt.Y('count()', title='상품 수')
                    )

                    my_skus_pp = df_sku[(df_sku['seller_id'] == sel_op) & (df_sku['category_eng'] == target_cat_pp)]
                    my_avg = my_skus_pp['sku_avg_price'].mean()

                    if pd.notna(my_avg):
                        my_rule = alt.Chart(pd.DataFrame({'x': [my_avg]})).mark_rule(color='blue', size=3).encode(
                            x='x:Q', tooltip=[alt.Tooltip('x', format='.1f', title='내 평균 가격')]
                        )
                        my_text = alt.Chart(pd.DataFrame({'x': [my_avg], 'label': ['  내 가격']})).mark_text(
                            align='left', dx=5, color='blue', fontWeight='bold'
                        ).encode(x='x:Q', text='label')

                        mkt_avg = market_prices['price'].mean()
                        mkt_rule = alt.Chart(pd.DataFrame({'x': [mkt_avg]})).mark_rule(color='red', strokeDash=[4,4]).encode(x='x:Q')

                        st.altair_chart((hist_chart + my_rule + my_text + mkt_rule).properties(height=300), use_container_width=True)

                        diff_pct = ((my_avg - mkt_avg) / mkt_avg) * 100
                        if diff_pct > 20:
                            st.success(f"📈 내 상품은 시장 평균({mkt_avg:.0f})보다 **{diff_pct:.1f}% 더 비싼 프리미엄 라인**입니다.")
                        elif diff_pct < -20:
                            st.warning(f"📉 내 상품은 시장 평균({mkt_avg:.0f})보다 **{abs(diff_pct):.1f}% 저렴한 가성비 라인**입니다.")
                        else:
                            st.info(f"⚖️ 내 상품은 시장 평균({mkt_avg:.0f})과 유사한 **적정 가격대**입니다.")
                    else:
                        st.warning("해당 카테고리에 내 상품 가격 정보가 없습니다.")
                else:
                    st.warning("시장 비교 데이터가 부족합니다.")
        else:
            st.info("분석할 카테고리 데이터가 없습니다.")

        st.divider()
        st.subheader("🗺️ 지역별 고객 분포 및 물류 효율 (Geo Distribution)")

        df_geo = load_geo_data(SELLER_DIR)
        if df_geo is not None:
            seller_geo = df_geo[df_geo['seller_id'] == sel_op].copy()

            if not seller_geo.empty:
                seller_geo['order_count'] = pd.to_numeric(seller_geo['order_count'], errors='coerce').fillna(0)
                seller_geo['avg_lead_time'] = pd.to_numeric(seller_geo['avg_lead_time'], errors='coerce').fillna(0)

                total_orders_all = seller_geo['order_count'].sum()
                if total_orders_all > 0:
                    overall_avg_lead = (seller_geo['avg_lead_time'] * seller_geo['order_count']).sum() / total_orders_all
                else:
                    overall_avg_lead = 0.0

                col_map, col_stat = st.columns([2, 1])

                with col_map:
                    st.markdown("##### 📍 주문 밀집도 및 배송 지연 지역 시각화")
                    st.info(f"🚚 **전체 평균 배송 리드타임: {overall_avg_lead:.1f}일**")

                    max_orders = seller_geo['order_count'].max()
                    if max_orders == 0: max_orders = 1
                    sizes = 8 + (seller_geo['order_count'] / max_orders) * 25

                    fig = go.Figure(go.Scattermapbox(
                        lat=seller_geo["lat"],
                        lon=seller_geo["lng"],
                        mode='markers',
                        marker=go.scattermapbox.Marker(
                            size=sizes,
                            color=seller_geo["avg_lead_time"],
                            colorscale="RdYlGn_r",
                            cmin=0, cmax=20,
                            showscale=True,
                            colorbar=dict(title="일수(Days)")
                        ),
                        text=seller_geo.apply(lambda x: f"<b>{x['customer_state']}</b><br>주문: {x['order_count']}건<br>배송: {x['avg_lead_time']:.1f}일", axis=1),
                        hoverinfo='text'
                    ))

                    fig.update_layout(
                        mapbox_style="carto-positron",
                        mapbox_zoom=3,
                        mapbox_center={"lat": -14.2, "lon": -51.9},
                        height=500,
                        margin={"r":0,"t":0,"l":0,"b":0}
                    )
                    st.plotly_chart(fig, use_container_width=True)

                with col_stat:
                    st.markdown("###### 📊 지역별 점유율 & 리드타임 비교")
                    st.caption(f"전체 평균: **{overall_avg_lead:.1f}일**")

                    market_df = df_geo.copy()
                    market_df['avg_lead_time'] = pd.to_numeric(market_df['avg_lead_time'], errors='coerce')
                    market_avgs = market_df.groupby('customer_state')['avg_lead_time'].mean()

                    state_summary = seller_geo.groupby('customer_state').agg({
                        'order_count': 'sum',
                        'avg_lead_time': 'mean'
                    }).reset_index()

                    state_summary['market_avg'] = state_summary['customer_state'].map(market_avgs)

                    total_orders_geo = state_summary['order_count'].sum()
                    state_summary['Share'] = (state_summary['order_count'] / total_orders_geo) * 100
                    state_summary = state_summary.sort_values('order_count', ascending=False).head(10)

                    disp_df = state_summary[['customer_state', 'order_count', 'Share', 'avg_lead_time', 'market_avg']].copy()
                    disp_df.columns = ['지역', '주문수', '점유율', '내 리드타임', '전체 리드타임']

                    def highlight_risk(s):
                        is_risk = False
                        my_lead = s['내 리드타임']
                        mkt_lead = s['전체 리드타임']
                        if pd.notnull(mkt_lead) and mkt_lead > 0:
                            if my_lead >= mkt_lead * 2.5:
                                is_risk = True
                        return ['background-color: #fee2e2; color: #b91c1c' if is_risk else '' for _ in s]

                    st.dataframe(
                        disp_df.style
                        .format({
                            '점유율': '{:.1f}%',
                            '내 리드타임': '{:.1f}일',
                            '전체 리드타임': '{:.1f}일'
                        })
                        .background_gradient(subset=['주문수'], cmap='Blues')
                        .apply(highlight_risk, axis=1),
                        use_container_width=True,
                        hide_index=True
                    )

                    risk_rows = state_summary[state_summary['avg_lead_time'] >= state_summary['market_avg'] * 2.5]
                    if not risk_rows.empty:
                        bad_state = risk_rows.iloc[0]['customer_state']
                        bad_my = risk_rows.iloc[0]['avg_lead_time']
                        bad_mkt = risk_rows.iloc[0]['market_avg']
                        st.error(f"🚨 **배송 지연 경고**: {bad_state} (내 배송 {bad_my:.1f}일 vs 전체 {bad_mkt:.1f}일) - 2.5배 이상 느림")
                    elif not state_summary.empty:
                        top_s = state_summary.iloc[0]
                        st.info(f"🏆 점유율 1위: **{top_s['customer_state']}** ({top_s['Share']:.1f}%)")
            else:
                st.warning("지역별 판매 데이터가 없습니다.")
        else:
            st.warning("데이터 로드 실패")
    else:
        st.warning("SKU 데이터를 로드할 수 없습니다.")


def _render_scm_tab(SELLER_DIR, data_dir, selected_seller, df_tier):
    """AI 재고 관리 및 SCM 최적화 탭"""
    # 1. Access Check
    has_access = False
    if df_tier is not None:
        t_info = df_tier[df_tier['seller_id'] == selected_seller]
        if not t_info.empty:
            tier_s = str(t_info['tier'].iloc[0])
            if 'Tier 1' in tier_s or 'Tier 2' in tier_s:
                has_access = True

    col_h1, col_h2 = st.columns([3, 1])
    with col_h1:
        st.header("🚀 개선의 확장: AI 기반 물류 지능화 (AI SCM & Forecasting)")
        st.markdown("""
        <span style='background-color:#dbeafe; color:#1e40af; padding: 4px 8px; border-radius: 4px; font-weight:bold; font-size:12px;'>Tier 1 & 2 전용 기능</span>
        &nbsp; **수요 예측(Forecasting)**과 **물류 리스크(Lead Time)**를 통합 분석하여 가시성 높은 재고 관리 솔루션을 제공합니다.
        """, unsafe_allow_html=True)

    with col_h2:
        st.empty()

    st.divider()

    if not has_access:
        st.error("🔒 **접근 권한이 없습니다.**")
        st.markdown("""
        ### 🚫 Premium Feature Locked
        이 기능은 **Tier 1 (최상위)** 및 **Tier 2 (우수)** 파트너 전용입니다.

        **제공 기능:**
        - 📈 **AI 수요 예측**: 향후 30일 판매량 예측 및 발주 추천
        - 🚚 **SCM 최적화**: 배송 리스크 분석 및 안전재고 자동 산출
        - 🗺️ **루트 시뮬레이터**: 지역별 최적 물류 경로 분석

        티어 승급을 통해 비즈니스 효율을 극대화하세요!
        """)
        return

    df_forecast = load_forecast_data(SELLER_DIR)

    sel_f = selected_seller
    if df_forecast is not None:
        st.caption(f"Currently Analyzing: **{sel_f}**")
    else:
        st.error("예측 데이터 파일이 없어 셀러 목록을 불러올 수 없습니다.")

    st.subheader("1️⃣ AI 수요 예측 및 발주 추천")
    if sel_f and df_forecast is not None:
        seller_data = df_forecast[df_forecast['seller_id'] == sel_f]

        if not seller_data.empty:
            cats_f = seller_data['category_eng'].dropna().unique().tolist()
            cats_f = [c for c in cats_f if str(c).lower() != 'unknown']

            if cats_f:
                cat_f = st.selectbox("카테고리 선택", cats_f, key='tab4_cat_forecast')
                ts_data = seller_data[seller_data['category_eng'] == cat_f].copy()
                ts_data['date'] = pd.to_datetime(ts_data['date'])

                if not ts_data.empty and len(ts_data) >= 7:
                    full_idx = pd.date_range(start=ts_data['date'].min(), end=ts_data['date'].max(), freq='D')
                    ts_daily = ts_data.set_index('date').reindex(full_idx).fillna({'daily_sales_count': 0}).reset_index().rename(columns={'index': 'date'})
                    ts_daily['days'] = (ts_daily['date'] - ts_daily['date'].min()).dt.days

                    std_err = 0
                    if len(ts_daily) >= 30:
                        try:
                            z = np.polyfit(ts_daily['days'], ts_daily['daily_sales_count'], 1)
                            p = np.poly1d(z)
                            hist_pred = p(ts_daily['days'])
                            residuals = ts_daily['daily_sales_count'] - hist_pred
                            std_err = np.std(residuals)
                            future_days = np.arange(ts_daily['days'].max() + 1, ts_daily['days'].max() + 31)
                            future_val_list = p(future_days)
                            future_forecast = [max(0, val) for val in future_val_list]
                        except:
                            avg_sales = ts_daily['daily_sales_count'].mean()
                            std_err = ts_daily['daily_sales_count'].std()
                            future_forecast = [avg_sales] * 30
                    else:
                        avg_sales = ts_daily['daily_sales_count'].mean()
                        std_err = ts_daily['daily_sales_count'].std()
                        future_forecast = [avg_sales] * 30

                    margin = 1.96 * std_err if std_err > 0 else 0
                    future_upper = [f + margin for f in future_forecast]
                    future_lower = [max(0, f - margin) for f in future_forecast]

                    forecast_val = sum(future_forecast)

                    future_dates = pd.date_range(start=ts_daily['date'].max() + pd.Timedelta(days=1), periods=30, freq='D')
                    df_future = pd.DataFrame({
                        'date': future_dates,
                        'value': future_forecast,
                        'type': 'Forecast',
                        'lower': future_lower,
                        'upper': future_upper
                    })

                    df_hist = ts_daily[['date', 'daily_sales_count']].rename(columns={'daily_sales_count': 'value'})
                    df_hist['type'] = 'History'

                    chart_df = pd.concat([df_hist, df_future], ignore_index=True)

                    line = alt.Chart(chart_df).mark_line().encode(
                        x=alt.X('date:T', title='날짜'),
                        y=alt.Y('value:Q', title='판매량'),
                        color=alt.Color('type:N', scale=alt.Scale(domain=['History', 'Forecast'], range=['#1e3a8a', '#ea580c']), legend=alt.Legend(title="구분")),
                        strokeDash=alt.condition(alt.datum.type == 'Forecast', alt.value([5, 5]), alt.value([0]))
                    )

                    band = alt.Chart(df_future).mark_area(opacity=0.2, color='#ea580c').encode(
                        x='date:T',
                        y=alt.Y('lower:Q', title=''),
                        y2='upper:Q'
                    )

                    final_chart = (band + line).properties(height=300)

                    st.altair_chart(final_chart, use_container_width=True)
                    st.metric("향후 30일 예상 수요", f"{int(forecast_val):,}개")

                    if len(ts_daily) < 30:
                        st.caption("ℹ️ 과거 데이터가 부족하여(30일 미만) **평균 기반 예측**을 제공합니다.")
                else:
                    st.warning(f"⚠️ 선택하신 카테고리('{cat_f}')의 데이터가 부족하여(7일 미만) 예측할 수 없습니다.")
            else:
                st.warning("⚠️ 예측 가능한 카테고리가 없습니다.")
        else:
            st.warning(f"⚠️ 선택하신 셀러 **'{sel_f}'**의 시계열 판매 데이터(Sales Series)가 존재하지 않습니다.")
    else:
        st.warning("📉 예측 데이터를 로드할 수 없습니다.")

    st.divider()
    st.subheader("2️⃣ 배송 리스크 및 안전재고 최적화")

    scm_path = os.path.join(SELLER_DIR, "output", "scm", "seller_lead_time_analysis.csv")
    route_path = os.path.join(SELLER_DIR, "output", "scm", "route_lead_time_stats.csv")

    if sel_f and os.path.exists(scm_path) and os.path.exists(route_path) and df_forecast is not None:
        df_scm = pd.read_csv(scm_path)
        my_scm = df_scm[df_scm['seller_id'] == sel_f].copy()
        seller_data_local = df_forecast[df_forecast['seller_id'] == sel_f]

        if not my_scm.empty:
            # Pre-calculate AI Forecast for ALL categories
            cat_forecasts = []
            for c_name in my_scm['category_eng'].unique():
                c_ts = seller_data_local[seller_data_local['category_eng'] == c_name].copy()
                if not c_ts.empty and len(c_ts) >= 7:
                    c_ts['date'] = pd.to_datetime(c_ts['date'])
                    f_idx = pd.date_range(start=c_ts['date'].min(), end=c_ts['date'].max(), freq='D')
                    c_daily = c_ts.set_index('date').reindex(f_idx).fillna({'daily_sales_count': 0}).reset_index().rename(columns={'index': 'date'})
                    c_daily['days'] = (c_daily['date'] - c_daily['date'].min()).dt.days
                    try:
                        if len(c_daily) >= 30:
                            z_c = np.polyfit(c_daily['days'], c_daily['daily_sales_count'], 1)
                            p_c = np.poly1d(z_c)
                            f_days = np.arange(c_daily['days'].max() + 1, c_daily['days'].max() + 31)
                            f_val = sum([max(0, v) for v in p_c(f_days)])
                        else:
                            f_val = c_daily['daily_sales_count'].mean() * 30
                    except:
                        f_val = c_daily['daily_sales_count'].mean() * 30
                else:
                    f_val = 0
                cat_forecasts.append({'category_eng': c_name, 'ai_forecast_30d': np.ceil(f_val)})

            df_cat_f = pd.DataFrame(cat_forecasts)
            my_scm = my_scm.merge(df_cat_f, on='category_eng', how='left')

            # Safety Stock
            avg_sales_hist = seller_data_local.groupby('category_eng')['daily_sales_count'].mean().reset_index()
            avg_sales_hist.columns = ['category_eng', 'hist_daily_avg']
            my_scm = my_scm.merge(avg_sales_hist, on='category_eng', how='left')
            my_scm['hist_daily_avg'] = my_scm['hist_daily_avg'].fillna(0)

            my_scm['safety_stock_qty'] = np.ceil(my_scm['ai_safety_stock_days'] * my_scm['hist_daily_avg'])
            my_scm['total_rec_stock'] = my_scm['ai_forecast_30d'] + my_scm['safety_stock_qty']
            my_scm['risk_ratio'] = (my_scm['safety_stock_qty'] / my_scm['total_rec_stock'] * 100).fillna(0)

            def get_status(row):
                if row['std_lead_time'] > 2.0 or row['efficiency_gap'] > 2.0: return "🔴 위험 (불안정)"
                elif row['std_lead_time'] > 1.2 or row['efficiency_gap'] > 1.0: return "🟡 주의 (변동성)"
                return "🟢 최적 (안정)"
            my_scm['status'] = my_scm.apply(get_status, axis=1)

            # Bridge UI
            if 'cat_f' in dir() and cat_f in my_scm['category_eng'].values:
                cat_row = my_scm[my_scm['category_eng'] == cat_f]
                if not cat_row.empty:
                    st.success(f"✅ **'{cat_f}'** 분석 결과: AI가 예측한 수요(**{int(cat_row['ai_forecast_30d'].iloc[0])}개**)에 물류 불안정성 대비 안전재고(**{int(cat_row['safety_stock_qty'].iloc[0])}개**)를 더해 최종 **{int(cat_row['total_rec_stock'].iloc[0])}개**의 보유를 권장합니다.")

            st.dataframe(
                my_scm[['status', 'category_eng', 'ai_forecast_30d', 'safety_stock_qty', 'total_rec_stock', 'risk_ratio', 'avg_actual_lead_time', 'std_lead_time']],
                column_config={
                    "status": "상태",
                    "category_eng": "카테고리",
                    "ai_forecast_30d": st.column_config.NumberColumn(
                        "AI 예상 수요(30일)",
                        help="📈 Step 1의 AI 트렌드 분석에 따른 향후 30일간의 순수 판매 예측량 (Base)",
                        format="%d 개"
                    ),
                    "safety_stock_qty": st.column_config.NumberColumn(
                        "안전재고(버퍼)",
                        help="🛡️ 배송 변동성 리스트를 방어하기 위해 확보해야 할 추가 수량 (Buffer)",
                        format="%d 개"
                    ),
                    "total_rec_stock": st.column_config.NumberColumn(
                        "최종 발주 목표",
                        help="✨ (예상 수요) + (안전재고). 품절 방지를 위한 최종 타겟 보유량",
                        format="%d 개"
                    ),
                    "risk_ratio": st.column_config.ProgressColumn(
                        "재고 리스크 비중(%)",
                        help="📊 전체 재고 중 배송 리스크 때문에 들고 있는 재고의 비율.",
                        format="%.1f%%",
                        min_value=0, max_value=100
                    ),
                    "avg_actual_lead_time": "평균 리드타임(일)",
                    "std_lead_time": "변동성(표준편차)"
                },
                use_container_width=True,
                hide_index=True
            )

            with st.expander("💡 SCM 최적화 가이드 (상세 도움말)", expanded=False):
                st.markdown("""
                ### 📋 지표 상세 설명
                1. **평균 리드타임**: 주문 시점부터 고객이 물건을 받을 때까지의 총 소요 시간입니다.
                2. **배송 변동성 (표준편차)**: 배송 기간이 얼마나 들쭉날쭉한지를 나타냅니다.
                   - **1.2일 미만**: 안정 (안전재고 최적화 가능)
                   - **1.2일 ~ 2.0일**: 주의 (변동성 발생, 버퍼 확보 필요)
                   - **2.0일 초과**: 위험 (출고 및 배송 프로세스 긴급 점검 권장)
                3. **안전재고(개)**: 배송 지연 리스크를 방지하기 위해 추가로 보유해야 하는 재고량입니다.
                4. **권장 보유량**: `(30일 판매 예측량) + (안전재고)` 입니다. 이 수치만큼 재고를 유지하는 것이 서비스 수준 유지와 재고 비용 최적화의 균형점입니다.

                ---
                ### 🚀 SCM 개선 전략
                - **위험 상태**: 배송 변동성이 큽니다. 출고 프로세스를 점검하거나, 물류 거점을 변동성이 낮은 지역으로 분산하는 것을 고려하세요.
                - **효율성 Gap**: 업계 평균(또는 티어 평균) 대비 내 배송 속도가 얼마나 느린지 보여줍니다.
                """)
        else:
            st.warning("SCM 분석 데이터가 없습니다.")
    else:
        st.warning("📉 SCM 데이터를 로드할 수 없습니다.")
