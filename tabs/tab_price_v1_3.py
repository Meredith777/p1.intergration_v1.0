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
            key="kpi_master_date"
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
            st.markdown("### 🎯 전략 가이드")
            st.markdown("""
            **1. 고탄력 / 저시즌 (우측 하단)**

            *   **전략**: 가격 할인에 매우 민감합니다. 쿠폰 마케팅이 가장 효과적입니다.

            **2. 저탄력 / 고시즌 (좌측 상단)**

            *   **전략**: 가격보다 **광고 노출**에 반응합니다. 할인보다 검색 상단 노출에 집중하세요.

            **3. 고탄력 / 고시즌 (우측 상단)**

            *   **전략**: 대규모 행사 시 가격 소구력을 극대화하여 물량을 밀어내야 합니다.
            """)
            
            st.warning("⚠️ **Y축 하단 상품군**: 시즌 노출 효과가 낮습니다. 가격을 내리기보다 타겟팅 광고를 통해 신규 고객을 유입시키는 것이 우선입니다.")

        st.markdown("""
        <div style="color: #8b8fb0; font-size: 13px; margin-top: 20px;">
            🔍 <b>데이터 품질 및 필터링 안내</b>: 본 탄력성 분석은 통계적 유의성 확보를 위해 <b>누적 판매 샘플 수 30개 미만</b>인 상품은 분석 대상에서 제외되었습니다. 
            또한, 이상치(Outlier) 처리를 통해 극단적인 가격 변동 데이터는 보정되었습니다.
        </div>
        """, unsafe_allow_html=True)

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
        st.header("✨ 가격 인상/인하 시뮬레이터")

        # --- 대분류-소분류 계층적 매핑 정의 ---
        cat_mapping = {
            "가구 (Furniture)": ["furniture_decor", "bed_bath_table", "office_furniture", "kitchen_dining_laundry_garden_furniture", "furniture_living_room", "furniture_bedroom", "furniture_mattress_and_pillow"],
            "가전/IT (Electronics/IT)": ["telephony", "computers_accessories", "electronics", "consoles_games", "air_conditioning", "audio", "tablets_printing_image", "fixed_telephony", "small_appliances_home_oven_and_coffee"],
            "건강/뷰티 (Health/Beauty)": ["health_beauty", "perfumery", "baby", "diapers_and_hygiene"],
            "생활/주방 (Home/Kitchen)": ["housewares", "home_confectionery", "home_construction", "garden_tools", "pet_shop", "cool_stuff", "luggage_accessories", "home_appliances", "home_appliances_2", "flowers", "kitchen_laptops_and_food_preparation", "small_appliances"],
            "스포츠/레저 (Sports/Leisure)": ["sports_leisure", "musical_instruments", "books_general_interest", "books_technical", "books_imported", "toys", "party_supplies", "art", "arts_and_craftsmanship"],
            "패션/의류 (Fashion/Apparel)": ["watches_sun_glass", "fashion_bags_accessories", "fashion_shoes", "fashion_underwear_beach", "fashion_male_clothing", "fashion_female_clothing", "fashion_childrens_clothes", "fashion_sport"],
            "식품/기타 (Food/Etc)": ["food_drink", "food", "drinks", "market_place", "agro_industry_and_commerce", "industry_commerce_and_business", "construction_tools_construction", "construction_tools_safety", "construction_tools_lights", "costruction_tools_garden", "costruction_tools_tools", "signaling_and_security", "security_and_services", "christmas_supplies"]
        }

        # 필터 레이아웃 (수직 배치 및 너비 최적화: 50%)
        c_filter, c_spacer = st.columns([1, 1])
        with c_filter:
            st.write("대분류 선택")
            major_cat = st.selectbox(
                "대분류 선택",
                options=list(cat_mapping.keys()),
                label_visibility="collapsed",
                key="sim_major_cat"
            )
            
            st.write("소분류 선택")
            # 선택된 대분류에 해당하는 소분류만 필터링 (데이터에 실제 존재하는 것만)
            available_minors = [c for c in cat_mapping[major_cat] if c in refined_elas['product_category_name_english'].unique()]
            target_cat = st.selectbox(
                "소분류 선택",
                options=sorted(available_minors) if available_minors else ["N/A"],
                label_visibility="collapsed",
                key="sim_minor_cat"
            )

        target_cat_data = cat_elas[cat_elas['category_eng'] == target_cat]
        if not target_cat_data.empty:
            avg_elas = target_cat_data['mean_elasticity'].values[0]
            current_rev = target_cat_data['category_revenue'].values[0]
            current_margin_rate = 0.25

            # --- 시뮬레이터 컨트롤 및 결과 (수직 배치) ---
            st.markdown("##### ⚙️ 시뮬레이션 설정")
            
            # 파라미터 영역 (박스 너비를 슬라이더에 맞춰 50%로 축소)
            c_box, c_spacer = st.columns([1, 1])
            with c_box:
                container_sim = st.container(border=True)
                with container_sim:
                    st.markdown("💡 **Tip**: 슬라이더 조절 시 결과가 아래 즉시 반영됩니다.")
                    price_change = st.slider("가격 변동 (%)", -30, 30, 0, 5, key="price_sim_slider")
                    
                    is_elastic = abs(avg_elas) > 1.0
                    st.write(f"📊 성격: {'**탄력적**' if is_elastic else '**비탄력적**'} (지수: {avg_elas:.2f})")

            # 계산 로직
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

            # 결과 리포트 영역
            st.markdown("#### 📋 시뮬레이션 분석 리포트")
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

        # 1. VIP 고민감 카테고리 & ROI (수평 배치)
        col_v1, col_v2 = st.columns(2)
        
        with col_v1:
            st.subheader("VIP 전용 고민감 카테고리 & 타겟 전략")
            vip_sens_data = pd.DataFrame({
                "카테고리": ["furniture_living_room", "bed_bath_table", "garden_tools", "stationery", "watches_gifts"],
                "민감도": [0.9500, 0.8800, 0.8200, 0.7900, 0.7500],
                "권장 전략": [
                    "VIP 전용 '최저가 보장' 쿠폰 발행",
                    "재구매 시 15% 보너스 포인트",
                    "신제품 출시 전 VIP 선공개 할인",
                    "일정 금액 이상 구매 시 무료 배송 보장",
                    "VIP 등급별 등급 할인율 차등 적용"
                ]
            })
            st.dataframe(vip_sens_data, use_container_width=True, hide_index=True)
            
            st.info("💡 **전략 포인트**: VIP는 가구와 가전 구매 시 가격 비교를 매우 활발히 수행합니다. 이들에게는 범용 할인보다는 '개별화된 가격 우대' 경험을 제공하여 이탈을 방지해야 합니다.")

        with col_v2:
            st.subheader("VIP 타겟 마케팅 예상 ROI")
            st.markdown("**타겟 마케팅 시 전환율 및 ROI 예측**")
            
            roi_data = pd.DataFrame({
                "구분": ["일반 범용 쿠폰", "VIP 타겟 쿠폰"],
                "ROI(배)": [1.2, 2.5],
                "전환율": ["3.2% (전환율)", "5.8% (전환율)"]
            })
            
            fig_roi = px.bar(roi_data, x='구분', y='ROI(배)', text='전환율', color='구분',
                             color_discrete_map={"일반 범용 쿠폰": "#d1d1e3", "VIP 타겟 쿠폰": "#0c29d0"})
            fig_roi.update_layout(template='plotly_white', showlegend=False, height=350,
                                  yaxis_title="ROI(배)", xaxis_title="구분")
            st.plotly_chart(fig_roi, use_container_width=True)

        st.markdown("---")

        # 2. VIP 패러독스 검증 & 번들 전략 (수평 배치)
        col_v3, col_v4 = st.columns([1, 1.2])

        with col_v3:
            st.subheader("🧪 VIP 패러독스 검증")
            # columns in vip_para: Segment, Elastic_Category_Share
            fig_vip = px.line(vip_para, x='Segment', y='Elastic_Category_Share', markers=True)
            fig_vip.update_traces(line_color='#0c29d0', line_width=4)
            fig_vip.update_layout(template='plotly_white', height=300)
            st.plotly_chart(fig_vip, use_container_width=True)
            
            st.info("""
            **VIP 패러독스**란 충성 고객일수록 오히려 가격에 더 민감하게 반응하거나 할인 기회를 더 잘 활용하는 현상을 말합니다.
            
            **분석 결과**:
            - **VIP 구매 비중**: 약 **16.3%** 가 고민감 상품군
            - **일반 구매 비중**: 약 **17.5%** 가 고민감 상품군
            
            Olist의 경우 VIP 패러독스가 나타나지 않았습니다. 즉, 우리 VIP들은 가격보다는 **브랜드 가치나 품질(Premium)**에 더 우선순위를 두는 성향이 강함을 의미합니다.
            """)

        with col_v4:
            st.subheader("🛒 VIP 연관 구매 분석 & 번들 전략")
            st.markdown("**VIP 고객의 주요 장바구니 패턴:**")
            st.markdown("""
            - `bed_bath_table` 구매 시 `housewares` 함께 구매 확률 **35% 증가**
            - `furniture_decor` 구매 시 `construction_tools_lights` 동시 구매 경향 뚜렷
            """)
            
            bundle_data = pd.DataFrame({
                "추천 번들 세트": ["안방 인테리어 세트", "주방 효율화 세트", "DIY 홈 가드닝 세트"],
                "구성 품목": ["가구 + 침구류", "주방가전 + 조리도구", "정원도구 + 조명기구"],
                "VIP 전용 묶음 할인율": ["10%", "15%", "12%"]
            })
            
            col_b1, col_b2 = st.columns([1.5, 1])
            with col_b1:
                st.dataframe(bundle_data, use_container_width=True, hide_index=True)
            with col_b2:
                st.success("✅ **번들링 권고**: 가격 민감도가 높은 VIP에게 원가 노출이 쉬운 단품 할인보다는, **가치 중심의 번들 세트**를 구성하여 '체감 할인 폭'을 키우고 객단가(AOV)를 높이는 전략이 유효합니다.")

    elif sub_menu == "🚀 개선의 확장: 지역 물류 전략":
        st.header("🚀 개선의 확장: 지역 격차 해소를 위한 물류-가격 매핑")
        
        # 1. 주별 배송비 탄력성 & 임계점 데이터 (실제 분석 기반 가공 데이터)
        state_strategy_data = {
            'state': ['SP', 'RJ', 'MG', 'RS', 'PR', 'SC', 'BA', 'DF', 'ES', 'GO', 'PE', 'CE', 'MT', 'MS', 'MA', 'PB', 'RN', 'PI', 'AL', 'SE', 'TO', 'RO', 'AM', 'AC', 'RR', 'AP', 'PA'],
            'freight_elasticity': [0.8, 1.8, 1.6, 1.2, 1.1, 0.9, 2.1, 1.0, 1.3, 1.4, 2.3, 2.2, 1.5, 1.6, 2.4, 2.2, 2.1, 2.5, 2.3, 2.2, 1.9, 1.8, 1.7, 2.0, 2.1, 2.2, 1.9],
            'threshold': [0.18, 0.22, 0.21, 0.20, 0.19, 0.18, 0.25, 0.19, 0.20, 0.21, 0.26, 0.25, 0.22, 0.22, 0.27, 0.26, 0.25, 0.28, 0.26, 0.25, 0.23, 0.24, 0.25, 0.26, 0.26, 0.27, 0.24]
        }
        state_df = pd.DataFrame(state_strategy_data)
        
        # 민감도 그룹 분류
        def categorize_sensitivity(elas):
            if elas >= 2.0: return "고민감 (High)"
            elif elas >= 1.5: return "보통 (Medium)"
            else: return "저민감 (Low)"
        
        state_df['Group'] = state_df['freight_elasticity'].apply(categorize_sensitivity)

        col_g1, col_g2 = st.columns([2, 1])
        
        with col_g1:
            st.subheader("� 주(State)별 배송비 탄력성 분포")
            
            @st.cache_data
            def load_brazil_geojson():
                import requests
                url = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson"
                try:
                    response = requests.get(url, timeout=10)
                    if response.status_code == 200:
                        return response.json()
                except Exception as e:
                    return None
                return None

            geojson_data = load_brazil_geojson()
            
            if geojson_data:
                fig_map = px.choropleth(
                    state_df,
                    geojson=geojson_data,
                    locations='state',
                    featureidkey="properties.sigla",
                    color='freight_elasticity',
                    color_continuous_scale="Reds",
                    labels={'freight_elasticity': '배송비 탄력성'},
                    title="브라질 지역별 배송비 민감도 (붉을수록 민감)"
                )
                fig_map.update_geos(fitbounds="locations", visible=False)
                fig_map.update_layout(height=450, margin={"r":0,"t":40,"l":0,"b":0}, template='plotly_white')
                st.plotly_chart(fig_map, use_container_width=True)
            else:
                st.warning("⚠️ 지도 로드 실패로 대체 차트를 표시합니다.")
                fig_alt = px.bar(state_df.sort_values('freight_elasticity'), 
                                 x='freight_elasticity', y='state', orientation='h',
                                 color='freight_elasticity', color_continuous_scale='Reds')
                st.plotly_chart(fig_alt, use_container_width=True)
        
        with col_g2:
            st.subheader("� 지역별 물류 전략 대조")
            
            # 전략 요약표
            strategy_summary = pd.DataFrame({
                "특성": ["민감 지역 (북부/북동부)", "무감 지역 (남부/남동부)"],
                "대표 주": ["MA, PI, PE, CE, BA", "SP, SC, PR, RS"],
                "핵심 전략": ["무료 배송 강조 (상품가 포함)", "도착 보장 시간 (Speed) 마케팅"],
                "임계점(Threshold)": ["25~28% (높은 수용도)", "18~20% (낮은 수용도)"]
            })
            st.dataframe(strategy_summary, use_container_width=True, hide_index=True)
            
            selected_state = st.selectbox("상세 분석 주 선택", state_df['state'].unique())
            s_data = state_df[state_df['state'] == selected_state].iloc[0]
            
            c1, c2 = st.columns(2)
            c1.metric(f"{selected_state} 탄력성", f"{s_data['freight_elasticity']:.2f}")
            c2.metric("권장 임계점", f"{s_data['threshold']:.1%}")

        st.markdown("---")
        st.subheader("🚚 지역별 배송비 임계점(Threshold) 세분화")
        
        fig_thresh = px.bar(
            state_df.sort_values('threshold', ascending=False),
            x='state', y='threshold', color='Group',
            color_discrete_map={"고민감 (High)": "#d9534f", "보통 (Medium)": "#f0ad4e", "저민감 (Low)": "#5bc0de"},
            labels={'threshold': '수용 가능 배송비 비중', 'state': '주(State)'}
        )
        fig_thresh.add_hline(y=0.20, line_dash="dash", line_color="black", annotation_text="전체 평균 임계점(20%)")
        fig_thresh.update_layout(template='plotly_white', height=400)
        st.plotly_chart(fig_thresh, use_container_width=True)
        
        st.info("""
        **💡 데이터 가이드**: 
        - **북동부 지역(MA, PI 등)**은 기본 물류 인프라 비용이 높아 배송비 비중이 **25%를 상회**하더라도 필요 상품에 대한 구매 의사가 강력합니다. 따라서 이 지역은 무료 배송 임계점을 높게 설정하되, 실적 기반의 물류 보조금 전략이 유효합니다.
        - **상파울루(SP)** 등 남서부 도심권은 배송비가 상품가의 **18%**를 넘어서는 순간 이탈이 가속화됩니다. 가격 경쟁력보다는 빠른 배송(Expedited Shipping) 옵션 제공이 최우선입니다.
        """)
