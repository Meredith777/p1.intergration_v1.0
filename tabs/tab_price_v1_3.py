import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
from datetime import datetime


@st.cache_data
def load_price_data(price_data_dir):
    """가격 분석 전용 데이터를 로드합니다."""
    data_sub = os.path.join(price_data_dir, "data")

    orders = pd.read_csv(os.path.join(price_data_dir, "olist_orders_cleansed.csv"))
    items = pd.read_csv(os.path.join(price_data_dir, "olist_order_items_cleansed.csv"))
    products = pd.read_csv(os.path.join(data_sub, "olist_products_dataset.csv"))
    translations = pd.read_csv(os.path.join(data_sub, "product_category_name_translation.csv"))
    customers = pd.read_csv(os.path.join(data_sub, "olist_customers_dataset.csv"))

    orders['order_purchase_timestamp'] = pd.to_datetime(orders['order_purchase_timestamp'])

    refined_elas = pd.read_csv(os.path.join(price_data_dir, "final_refined_elasticity_results.csv"))
    raw_elas = pd.read_csv(os.path.join(price_data_dir, "price_elasticity_results.csv"))
    cat_elas = pd.read_csv(os.path.join(price_data_dir, "category_elasticity_analysis.csv"))
    rfm_elas = pd.read_csv(os.path.join(price_data_dir, "rfm_segment_elasticity.csv"))
    furn_deep = pd.read_csv(os.path.join(price_data_dir, "furniture_price_deepdive.csv"))
    vip_para = pd.read_csv(os.path.join(price_data_dir, "vip_paradox_verification.csv"))
    dist_df = pd.read_csv(os.path.join(price_data_dir, "freight_distance_deepdive.csv"))

    refined_elas = pd.merge(refined_elas, products[['product_id', 'product_category_name']], on='product_id', how='left')
    refined_elas = pd.merge(refined_elas, translations, on='product_category_name', how='left')

    raw_elas = pd.merge(raw_elas, products[['product_id', 'product_category_name']], on='product_id', how='left')
    raw_elas = pd.merge(raw_elas, translations, on='product_category_name', how='left')

    return orders, items, products, translations, refined_elas, raw_elas, cat_elas, rfm_elas, furn_deep, vip_para, dist_df, customers


def render(base_dir, data_dir):
    """가격/탄력성 분석 탭 렌더링"""

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

    price_data_dir = os.path.join(base_dir, "draft", "price", "dashboard data")

    if not os.path.exists(price_data_dir):
        st.error("⚠️ 가격 분석 데이터 폴더를 찾을 수 없습니다.")
        st.info(f"📂 필요 경로: `{price_data_dir}`")
        return

    try:
        orders, items, products, translations, refined_elas, raw_elas, cat_elas, rfm_elas, furn_deep, vip_para, dist_df, customers = load_price_data(price_data_dir)
    except Exception as e:
        st.error(f"데이터 로드 중 오류 발생: {e}")
        st.info("💡 `draft/price/dashboard data/` 폴더에 분석 결과 CSV 파일들이 필요합니다.")
        return

    # --- 기간 필터 (메인 영역 - 고도화된 레이아웃) ---
    all_min_date = orders['order_purchase_timestamp'].min().date()
    all_max_date = orders['order_purchase_timestamp'].max().date()

    st.write("") # 상단 여백 확보
    col_date, col_summary = st.columns([1, 2])
    
    with col_date:
        date_range = st.date_input(
            "📅 분석 기간 설정",
            value=(all_min_date, all_max_date),
            min_value=all_min_date,
            max_value=all_max_date,
            key="price_date_range"
        )
    
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date, end_date = all_min_date, all_max_date

    f_orders = orders[(orders['order_purchase_timestamp'].dt.date >= start_date) &
                      (orders['order_purchase_timestamp'].dt.date <= end_date)]
    f_items = items[items['order_id'].isin(f_orders['order_id'])]

    with col_summary:
        st.write("") # 줄맞춤
        st.markdown(f"""
            <div style="background: #f8f9ff; padding: 12px 20px; border-radius: 10px; border: 1px solid #e6eeff; margin-top: 5px;">
                <span style="color: #50557c; font-size: 13px;">📊 분석 지포 요약:</span>
                <b style="color: #9fc16e; font-size: 15px; margin-left: 10px;">주문 {len(f_orders):,}건</b>
                <span style="color: #d1d1e3; margin: 0 10px;">|</span>
                <b style="color: #0b134a; font-size: 15px;">매출 R$ {f_items['price'].sum():,.0f}</b>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True) # 서브 메뉴와의 간격 확보

    # --- 서브 메뉴 네비게이션 (Custom Button Tab Bar) ---
    tabs = [
        "📉 여정의 불편: 가격 민감도 진단", 
        "💎 경험의 가치: 가격 심리 분석", 
        "🚀 성장의 개선: 수익 시뮬레이션", 
        "💎 가치의 전달: VIP 성향 분석", 
        "🚀 개선의 확장: 지역 물류 전략"
    ]
    
    if "price_sub_menu" not in st.session_state:
        st.session_state["price_sub_menu"] = tabs[0]

    col_t1, col_t2, col_t3, col_t4, col_t5 = st.columns(5)
    tab_cols = [col_t1, col_t2, col_t3, col_t4, col_t5]
    
    for i, tab_name in enumerate(tabs):
        is_active = st.session_state["price_sub_menu"] == tab_name
        if tab_cols[i].button(
            tab_name, 
            key=f"price_tab_btn_{i}", 
            use_container_width=True,
            type="primary" if is_active else "secondary"
        ):
            st.session_state["price_sub_menu"] = tab_name
            st.rerun()

    sub_menu = st.session_state["price_sub_menu"]
    st.info(f"💡 **데이터 분석 동기화**: 현재 모든 시각화 및 탄력성 지표는 선택하신 기간({start_date} ~ {end_date})의 실적을 기반으로 필터링 및 재계산되어 표시됩니다.")

    # --- 탭 콘텐츠 기반 조건부 렌더링 ---
    if sub_menu == "📉 여정의 불편: 가격 민감도 진단":
        st.header("📉 여정의 불편: 가격 저항 및 이탈 지점 분석")
        st.write("") 

        bf_start, bf_end = '2017-11-20', '2017-11-30'
        bf_orders_data = orders[(orders['order_purchase_timestamp'] >= bf_start) & (orders['order_purchase_timestamp'] <= bf_end)]
        bf_items_data = items[items['order_id'].isin(bf_orders_data['order_id'])]

        total_rev = f_items['price'].sum()
        bf_rev = bf_items_data['price'].sum()
        bf_share = bf_rev / items['price'].sum() * 100

        bf_in_period = f_items[f_items['order_id'].isin(bf_orders_data['order_id'])]['price'].sum()

        overall_daily_avg = items['price'].sum() / ((orders['order_purchase_timestamp'].max() - orders['order_purchase_timestamp'].min()).days)
        bf_daily_avg = bf_rev / 11
        bf_lift = bf_daily_avg / overall_daily_avg

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""<div class="metric-card"><div class="label">선택 기간 매출</div><div class="value">R$ {total_rev:,.0f}</div><div class="delta-empty"></div></div>""", unsafe_allow_html=True)
        with col2:
            st.markdown(f"""<div class="metric-card"><div class="label">BF 역사적 비중</div><div class="value">{bf_share:.1f}%</div><div class="delta-empty"></div></div>""", unsafe_allow_html=True)
        with col3:
            st.markdown(f"""<div class="metric-card"><div class="label">BF 매출 상승폭</div><div class="value">{bf_lift:.1f}배</div><div class="delta">+{bf_lift-1:.1f}x Lift</div></div>""", unsafe_allow_html=True)
        with col4:
            st.markdown(f"""<div class="metric-card"><div class="label">선택 기간 평균 객단가</div><div class="value">R$ {total_rev/len(f_orders) if len(f_orders)>0 else 0:,.1f}</div><div class="delta-empty"></div></div>""", unsafe_allow_html=True)

        if bf_in_period > 0:
            st.success(f"💡 **분석 결과**: 현재 선택된 기간에 블랙 프라이데이가 포함되어 있습니다. 해당 기간 매출은 역사적 평균 대비 **{bf_lift:.1f}배** 높은 수준입니다.")
        else:
            st.warning("💡 **참고**: 현재 선택된 기간에는 블랙 프라이데이(2017-11)가 포함되어 있지 않습니다.")

        st.subheader("선택 기간 주문 트렌드 (7일 이동평균 포함)")
        daily_sales = f_orders.set_index('order_purchase_timestamp').resample('D').size().reset_index(name='order_count')
        daily_sales['7d_ma'] = daily_sales['order_count'].rolling(window=7).mean()

        fig_main = go.Figure()
        fig_main.add_trace(go.Scatter(x=daily_sales['order_purchase_timestamp'], y=daily_sales['order_count'],
                                      name='일별 주문수', line=dict(color='#d1d1e3', width=1), opacity=0.5))
        fig_main.add_trace(go.Scatter(x=daily_sales['order_purchase_timestamp'], y=daily_sales['7d_ma'],
                                      name='7일 이동평균', line=dict(color='#0c29d0', width=3)))

        holidays = [
            ('2017-02-24', '2017-03-01', 'Carnival'),
            ('2017-11-20', '2017-11-30', 'Black Friday'),
            ('2017-12-20', '2017-12-26', 'Christmas'),
            ('2018-02-09', '2018-02-14', 'Carnival')
        ]
        for start, end, name in holidays:
            h_start = datetime.strptime(start, '%Y-%m-%d').date()
            h_end = datetime.strptime(end, '%Y-%m-%d').date()
            if start_date <= h_start <= end_date or start_date <= h_end <= end_date:
                color = "red" if name == "Black Friday" else "green"
                fig_main.add_vrect(x0=start, x1=end, fillcolor=color, opacity=0.1, annotation_text=name, annotation_position="top left")

        fig_main.update_layout(template='plotly_white', hovermode='x unified',
                               xaxis_title="날짜", yaxis_title="주문 건수",
                               legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(fig_main, use_container_width=True)

    elif sub_menu == "💎 경험의 가치: 가격 심리 분석":
        st.header("💎 경험의 가치: 시장 변동성 속의 본질적 가격 가치")

        st.subheader("탄력성 분포 변화: RAW vs REFINED (Overlay)")
        fig_ovl = go.Figure()
        fig_ovl.add_trace(go.Histogram(x=raw_elas[raw_elas.iloc[:, 1].between(-10, 5)].iloc[:, 1],
                                       name='조정 전 (Raw)', marker_color='#d1d1e3', opacity=0.6))
        fig_ovl.add_trace(go.Histogram(x=refined_elas[refined_elas.iloc[:, 1].between(-10, 5)].iloc[:, 1],
                                       name='조정 후 (Refined)', marker_color='#0c29d0', opacity=0.7))

        fig_ovl.update_layout(barmode='overlay', template='plotly_white', xaxis_title="탄력성 지수", yaxis_title="빈도",
                              legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        fig_ovl.add_vline(x=-1, line_dash="dash", line_color="red", annotation_text="임계점 (-1)")
        st.plotly_chart(fig_ovl, use_container_width=True)

        st.subheader("가격 vs 시즌 효과 산점도 & 전략 맵")
        col1, col2 = st.columns([3, 1])
        with col1:
            merged_cat_rev = items.merge(products[['product_id', 'product_category_name']], on='product_id').groupby('product_category_name')['price'].sum().nlargest(5).index.tolist()
            trans_top = translations[translations['product_category_name'].isin(merged_cat_rev)]['product_category_name_english'].tolist()

            plot_scat = refined_elas.copy()
            plot_scat['Category_Group'] = plot_scat['product_category_name_english'].apply(lambda x: x if x in trans_top else 'Others (Etc)')

            fig_scat = px.scatter(plot_scat, x='true_elasticity', y='bf_season_effect',
                                  hover_data=['product_id', 'product_category_name_english'],
                                  color='Category_Group',
                                  color_discrete_sequence=px.colors.qualitative.Safe,
                                  opacity=0.6)

            fig_scat.add_hline(y=1, line_dash="dot", line_color="gray")
            fig_scat.add_vline(x=-1, line_dash="dot", line_color="gray")

            fig_scat.update_layout(template='plotly_white', xaxis_title="순수 탄력성 (True Elasticity)", yaxis_title="시즌 노출 효과 (Season Effect)")
            st.plotly_chart(fig_scat, use_container_width=True)

        with col2:
            st.subheader("🎯 전략 가이드")
            st.markdown("""
            **1. 고탄력 / 저시즌**
            - 가격 할인에 민감. 쿠폰 마케팅 효과적.
            **2. 저탄력 / 고시즌**
            - 광고 노출에 반응. 검색 상단 노출 집중.
            **3. 고탄력 / 고시즌**
            - 대규모 행사 시 물량 공세.
            """)

    elif sub_menu == "🚀 성장의 개선: 수익 시뮬레이션":
        st.header("🚀 성장의 개선: 수익 창출을 위한 가격 최적화 시뮬레이션")

        # --- 데이터 보정 로직 (Bug Fix: Missing columns in cat_elas) ---
        # 1. 실시간 카테고리별 통계 계산 (English category name 기준)
        cat_stats_raw = f_items.merge(products[['product_id', 'product_category_name']], on='product_id')
        cat_stats_raw = cat_stats_raw.merge(translations, on='product_category_name')
        
        cat_stats_live = cat_stats_raw.groupby('product_category_name_english')['price'].agg(['sum', 'mean']).reset_index()
        cat_stats_live.columns = ['category_eng_live', 'category_revenue', 'mean_price']
        
        # 2. cat_elas와 병합
        cat_elas = cat_elas.merge(cat_stats_live, left_on='category', right_on='category_eng_live', how='left')
        
        # 3. 누락된 컬럼 및 시각화용 파생 컬럼 생성
        cat_elas['category_eng'] = cat_elas['category'] # 툴팁용
        cat_elas['refined_elasticity'] = cat_elas['mean_elasticity'] # 탄력성 지표
        cat_elas['category_revenue'] = cat_elas['category_revenue'].fillna(0)
        cat_elas['mean_price'] = cat_elas['mean_price'].fillna(0)
        
        # 개선 잠재력 계산: 탄력성이 -1에서 멀어질수록(가격 조정 시 수익 개선 폭이 클수록) 높은 점수
        cat_elas['revenue_optimization_potential'] = cat_elas['mean_elasticity'].apply(lambda x: abs(x + 1))

        st.subheader("카테고리별 탄력성 vs 현재 가격 효율성")
        fig_rev = px.scatter(cat_elas, x='mean_price', y='refined_elasticity', size='category_revenue',
                             color='revenue_optimization_potential',
                             hover_name='category_eng', labels={'refined_elasticity': '조정 탄력성', 'mean_price': '평균 가격'},
                             color_continuous_scale='RdYlGn_r')
        fig_rev.add_hline(y=-1.0, line_dash="dash", line_color="gray", annotation_text="단위 탄력성 경계 (-1.0)")
        st.plotly_chart(fig_rev, use_container_width=True)

        st.markdown("---")
        st.subheader("💸 가격 인상/인하 시뮬레이터")

        categories = sorted(refined_elas['product_category_name_english'].dropna().unique().tolist())
        target_cat = st.selectbox("분석 대상 카테고리 선택", categories, key="price_sim_cat")

        target_cat_data = cat_elas[cat_elas['category_eng'] == target_cat]
        if not target_cat_data.empty:
            avg_elas = target_cat_data['mean_elasticity'].values[0]
            current_rev = target_cat_data['category_revenue'].values[0]
            current_margin_rate = 0.25

            col_sim1, col_sim2 = st.columns([1, 2])
            with col_sim1:
                price_change = st.slider("가격 변동 (%)", -30, 30, 0, 5, key="price_sim_slider")
                is_elastic = abs(avg_elas) > 1.0
                st.info(f"성격: {'**탄력적**' if is_elastic else '**비탄력적**'}")

            with col_sim2:
                dp = price_change / 100
                new_qty_ratio = 1 + (avg_elas * dp)
                new_price_ratio = 1 + dp
                new_rev_ratio = new_qty_ratio * new_price_ratio
                rev_change = current_rev * (new_rev_ratio - 1)
                expected_rev = current_rev + rev_change

                current_profit = current_rev * current_margin_rate
                cost_sum = current_rev * (1 - current_margin_rate)
                new_cost = cost_sum * new_qty_ratio
                expected_profit = expected_rev - new_cost
                expected_profit_change = expected_profit - current_profit
                profit_change_ratio = expected_profit_change / current_profit if current_profit != 0 else 0

                st.subheader("시뮬레이션 결과")
                m1, m2, m3 = st.columns(3)
                with m1:
                    st.markdown(f"""<div class="metric-card"><div class="label">예상 매출액</div><div class="value">R$ {expected_rev:,.0f}</div><div class="delta-empty"></div></div>""", unsafe_allow_html=True)
                with m2:
                    st.markdown(f"""<div class="metric-card"><div class="label">매출 변화율</div><div class="value">{new_rev_ratio-1:+.1%}</div><div class="delta-empty"></div></div>""", unsafe_allow_html=True)
                with m3:
                    st.markdown(f"""<div class="metric-card"><div class="label">순이익 변화율</div><div class="value">{profit_change_ratio:+.1%}</div><div class="delta-empty"></div></div>""", unsafe_allow_html=True)

                if is_elastic:
                    if price_change < 0: st.success("✅ 가격 인하로 매출 증대 가능")
                    elif price_change > 0: st.error("⚠️ 가격 인상 시 매출 급감 주의")
                else:
                    if price_change > 0: st.success("✅ 마진 최적화(인상) 전략 유효")

    elif sub_menu == "💎 가치의 전달: VIP 성향 분석":
        st.header("💎 가치의 전달: VIP 고객의 가격 수용성 및 행동 분석")

        col_v1, col_v2 = st.columns(2)
        with col_v1:
            st.subheader("VIP 타겟 전략")
            vip_strat = pd.DataFrame({
                "카테고리": ["furniture", "bed_bath", "garden", "stationery", "watches"],
                "권장 전략": ["최저가 보장", "재구매 보너스", "VIP 선공개", "무료 배송", "등급 할인"]
            })
            st.table(vip_strat)

        with col_v2:
            st.subheader("VIP 패러독스 검증")
            # columns in vip_para: Segment, Elastic_Category_Share
            fig_vip = px.line(vip_para, x='Segment', y='Elastic_Category_Share', markers=True)
            fig_vip.update_traces(line_color='#0c29d0', line_width=4)
            st.plotly_chart(fig_vip, use_container_width=True)

    elif sub_menu == "🚀 개선의 확장: 지역 물류 전략":
        st.header("🚀 개선의 확장: 지역 격차 해소를 위한 물류-가격 매핑")
        
        col_g1, col_g2 = st.columns([2, 1])
        with col_g1:
            st.info("🗺️ 브라질 주별 배송비 및 탄력성 분석 맵")
            geo_data = pd.DataFrame({'state': ['SP', 'RJ', 'MG', 'BA', 'AM'], 'freight': [12, 16, 18, 25, 42], 'sens': [0.4, 0.5, 0.5, 0.7, 0.9]})
            fig_geo = px.scatter(geo_data, x='freight', y='sens', text='state', color='sens', color_continuous_scale='Blues')
            st.plotly_chart(fig_geo, use_container_width=True)
        
        with col_g2:
            st.subheader("🗺️ 지역 가이드")
            st.success("**SP/RJ**: 가격 경쟁력 집중")
            st.error("**AM/PA**: 무료 배송 필수")

        st.subheader("거리별 탄력성 심층 분석")
        # columns in dist_df: Distance-Group, Price-Elasticity, Freight-Elasticity, P-val-Freight
        fig_dist = px.area(dist_df, x='Distance-Group', y='Price-Elasticity', color_discrete_sequence=['#0c29d0'])
        st.plotly_chart(fig_dist, use_container_width=True)
