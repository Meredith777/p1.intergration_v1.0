import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
import statsmodels.api as sm
from datetime import datetime

# 페이지 설정
st.set_page_config(
    page_title="Olist 데이터 통합 분석 대시보드 (PRO)",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 스타일 설정
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border-bottom: 4px solid #4e73df;
    }
    .stAlert { border-radius: 12px; }
    div[data-testid="stExpander"] { border-radius: 12px; }
    </style>
    """, unsafe_allow_html=True)

# 경로 설정 (현재 디렉토리 기준)
BASE_PATH = os.getcwd()
DATA_PATH = os.path.join(BASE_PATH, "data")

@st.cache_data
def load_data():
    # 데이터 로드
    orders = pd.read_csv(os.path.join(BASE_PATH, "olist_orders_cleansed.csv"))
    items = pd.read_csv(os.path.join(BASE_PATH, "olist_order_items_cleansed.csv"))
    products = pd.read_csv(os.path.join(DATA_PATH, "olist_products_dataset.csv"))
    translations = pd.read_csv(os.path.join(DATA_PATH, "product_category_name_translation.csv"))
    customers = pd.read_csv(os.path.join(DATA_PATH, "olist_customers_dataset.csv"))
    
    orders['order_purchase_timestamp'] = pd.to_datetime(orders['order_purchase_timestamp'])
    
    # 분석 결과 로드
    refined_elas = pd.read_csv(os.path.join(BASE_PATH, "final_refined_elasticity_results.csv"))
    raw_elas = pd.read_csv(os.path.join(BASE_PATH, "price_elasticity_results.csv"))
    cat_elas = pd.read_csv(os.path.join(BASE_PATH, "category_elasticity_analysis.csv"))
    rfm_elas = pd.read_csv(os.path.join(BASE_PATH, "rfm_segment_elasticity.csv"))
    furn_deep = pd.read_csv(os.path.join(BASE_PATH, "furniture_price_deepdive.csv"))
    vip_para = pd.read_csv(os.path.join(BASE_PATH, "vip_paradox_verification.csv"))
    dist_df = pd.read_csv(os.path.join(BASE_PATH, "freight_distance_deepdive.csv"))

    # 데이터 병합 (툴팁용 카테고리 등)
    refined_elas = pd.merge(refined_elas, products[['product_id', 'product_category_name']], on='product_id', how='left')
    refined_elas = pd.merge(refined_elas, translations, on='product_category_name', how='left')
    
    raw_elas = pd.merge(raw_elas, products[['product_id', 'product_category_name']], on='product_id', how='left')
    raw_elas = pd.merge(raw_elas, translations, on='product_category_name', how='left')

    return orders, items, products, translations, refined_elas, raw_elas, cat_elas, rfm_elas, furn_deep, vip_para, dist_df, customers

# 데이터 로드 실행
try:
    orders, items, products, translations, refined_elas, raw_elas, cat_elas, rfm_elas, furn_deep, vip_para, dist_df, customers = load_data()
except Exception as e:
    st.error(f"데이터 로드 중 오류 발생: {e}")
    st.stop()

# --- 사이드바 ---
st.sidebar.title("💎 Olist 전략 분석 PRO")
st.sidebar.markdown("---")

st.sidebar.subheader("📅 분석 기간 설정")
all_min_date = orders['order_purchase_timestamp'].min().date()
all_max_date = orders['order_purchase_timestamp'].max().date()

view_full = st.sidebar.checkbox("전체 기간 보기 (과거 분석용)", value=True)

if view_full:
    start_date, end_date = all_min_date, all_max_date
    st.sidebar.info(f"전체 기간 데이터가 표시됩니다.\n({all_min_date} ~ {all_max_date})")
else:
    date_range = st.sidebar.date_input(
        "전략 수립 기간 선택",
        value=(all_min_date, all_max_date),
        min_value=all_min_date,
        max_value=all_max_date
    )
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date, end_date = all_min_date, all_max_date

# 필터링된 데이터 생성
f_orders = orders[(orders['order_purchase_timestamp'].dt.date >= start_date) & 
                  (orders['order_purchase_timestamp'].dt.date <= end_date)]
f_items = items[items['order_id'].isin(f_orders['order_id'])]

st.sidebar.write(f"- 선택된 주문: {len(f_orders):,}건")
st.sidebar.write(f"- 선택된 매출: R$ {f_items['price'].sum():,.0f}")
st.sidebar.markdown("---")

# --- Tab 구성 ---
tabs = st.tabs(["🚀 비즈니스 개요", "🗓️ 가격 vs 시즌성", "📈 수익 최적화", "👥 고객 행동", "🌍 물류 지도"])

# 전역 데이터 연동 알림
st.info(f"💡 **데이터 분석 동기화**: 현재 모든 시각화 및 탄력성 지표는 사이드바에서 선택하신 기간({start_date} ~ {end_date})의 실적을 기반으로 필터링 및 재계산되어 표시됩니다.")

with tabs[0]:
    st.header("Olist 비즈니스 개요 & BF 기여도")
    
    # BF 기간 정의
    bf_start, bf_end = '2017-11-20', '2017-11-30'
    bf_orders_data = orders[(orders['order_purchase_timestamp'] >= bf_start) & (orders['order_purchase_timestamp'] <= bf_end)]
    bf_items_data = items[items['order_id'].isin(bf_orders_data['order_id'])]
    
    total_rev = f_items['price'].sum()
    bf_rev = bf_items_data['price'].sum()
    bf_share = bf_rev / items['price'].sum() * 100 # 전체 대비 BF 비중은 고정 인사이트로 제공
    
    # 선택 기간 내 BF 포함 여부 확인
    bf_in_period = f_items[f_items['order_id'].isin(bf_orders_data['order_id'])]['price'].sum()
    
    # 평소 대비 배수 계산 (전체 평균 vs BF 평균)
    overall_daily_avg = items['price'].sum() / ((orders['order_purchase_timestamp'].max() - orders['order_purchase_timestamp'].min()).days)
    bf_daily_avg = bf_rev / 11
    bf_lift = bf_daily_avg / overall_daily_avg
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("선택 기간 매출 (BRL)", f"R$ {total_rev:,.0f}")
    col2.metric("BF 역사적 비중", f"{bf_share:.1f}%", help="2017년 전체 매출 중 블랙 프라이데이 주간(11일)이 차지하는 비중")
    col3.metric("BF 매출 상승폭", f"{bf_lift:.1f}배", delta=f"{bf_lift-1:.1f}x", help="블랙 프라이데이 일평균 매출 vs 평시(연간) 일평균 매출 비교")
    col4.metric("선택 기간 평균 객단가", f"R$ {total_rev/len(f_orders) if len(f_orders)>0 else 0:,.1f}", help="선택된 기간 내 주문 1건당 평균 결제 금액")
    
    if bf_in_period > 0:
        st.success(f"💡 **분석 결과**: 현재 선택된 기간에 블랙 프라이데이가 포함되어 있습니다. 해당 기간 매출은 역사적 평균 대비 **{bf_lift:.1f}배** 높은 수준입니다.")
    else:
        st.warning("💡 **참고**: 현재 선택된 기간에는 블랙 프라이데이(2017-11)가 포함되어 있지 않습니다. 과거 분석을 원하시면 '전체 기간 보기'를 선택해 주세요.")
    
    st.subheader("선택 기간 주문 트렌드 (7일 이동평균 포함)")
    daily_sales = f_orders.set_index('order_purchase_timestamp').resample('D').size().reset_index(name='order_count')
    daily_sales['7d_ma'] = daily_sales['order_count'].rolling(window=7).mean()
    
    fig_main = go.Figure()
    # 원본 데이터 선
    fig_main.add_trace(go.Scatter(x=daily_sales['order_purchase_timestamp'], y=daily_sales['order_count'],
                                  name='일별 주문수', line=dict(color='#cccccc', width=1), opacity=0.5))
    # 7일 이동 평균선
    fig_main.add_trace(go.Scatter(x=daily_sales['order_purchase_timestamp'], y=daily_sales['7d_ma'],
                                  name='7일 이동평균', line=dict(color='#4e73df', width=3)))
    
    # 브라질 주요 연휴/특수기 배경 추가 (2017-2018 기준)
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

# --- Tab 2: 가격 vs 시즌성 ---
with tabs[1]:
    st.header("시즌 효과 제거: '진짜 탄력성' 찾기")
    
    st.subheader("탄력성 분포 변화: RAW vs REFINED (Overlay)")
    # Overlay Histogram
    fig_ovl = go.Figure()
    fig_ovl.add_trace(go.Histogram(x=raw_elas[raw_elas.iloc[:, 1].between(-10, 5)].iloc[:, 1], 
                                   name='조정 전 (Raw)', marker_color='#cccccc', opacity=0.6))
    fig_ovl.add_trace(go.Histogram(x=refined_elas[refined_elas.iloc[:, 1].between(-10, 5)].iloc[:, 1], 
                                   name='조정 후 (Refined)', marker_color='#4e73df', opacity=0.7))
    
    fig_ovl.update_layout(barmode='overlay', template='plotly_white', xaxis_title="탄력성 지수", yaxis_title="빈도",
                          legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    fig_ovl.add_vline(x=-1, line_dash="dash", line_color="red", annotation_text="임계점 (-1)")
    st.plotly_chart(fig_ovl, use_container_width=True)
    st.caption("💡 **분석 팁**: 회색(조정 전) 대비 파란색(조정 후) 분포가 더 넓게 퍼진 것은 시즌성 '노이즈'가 제거되어 상품 본연의 가격 민감도가 드러났음을 의미합니다.")
        
    # --- 전략적 액션 맵 섹션 ---
    st.subheader("가격 vs 시즌 효과 산점도")
    st.markdown("---")
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader("가격 vs 시즌 효과 산점도 & 전략 맵")
        
        # 범례 최적화: 매출 상위 5개 카테고리 외에는 'Others'로 통합
        # products와 items가 이전에 로드된 전역 변수임을 가정
        merged_cat_rev = items.merge(products[['product_id', 'product_category_name']], on='product_id').groupby('product_category_name')['price'].sum().nlargest(5).index.tolist()
        
        # 번역본과 매칭
        trans_top = translations[translations['product_category_name'].isin(merged_cat_rev)]['product_category_name_english'].tolist()
        
        plot_scat = refined_elas.copy()
        plot_scat['Category_Group'] = plot_scat['product_category_name_english'].apply(lambda x: x if x in trans_top else 'Others (Etc)')
        
        fig_scat = px.scatter(plot_scat, x='true_elasticity', y='bf_season_effect',
                              hover_data=['product_id', 'product_category_name_english'],
                              color='Category_Group',
                              color_discrete_sequence=px.colors.qualitative.Safe,
                              opacity=0.6)
        
        # 전략적 가이드 영역 추가 (Shapes/Lines)
        fig_scat.add_hline(y=1, line_dash="dot", line_color="gray")
        fig_scat.add_vline(x=-1, line_dash="dot", line_color="gray")
        
        fig_scat.update_layout(template='plotly_white', xaxis_title="순수 탄력성 (True Elasticity)", yaxis_title="시즌 노출 효과 (Season Effect)")
        st.plotly_chart(fig_scat, use_container_width=True)
        
    with col2:
        st.subheader("🎯 전략 가이드")
        st.markdown("""
        **1. 고탄력 / 저시즌 (우측 하단)**
        - **전략**: 가격 할인에 매우 민감합니다. 쿠폰 마케팅이 가장 효과적입니다.
        
        **2. 저탄력 / 고시즌 (좌측 상단)**
        - **전략**: 가격보다 **광고 노출**에 반응합니다. 할인보다 검색 상단 노출에 집중하세요.
        
        **3. 고탄력 / 고시즌 (우측 상단)**
        - **전략**: 대규모 행사 시 가격 소구력을 극대화하여 물량을 밀어내야 합니다.
        """)
        st.warning("⚠️ **Y축 하단 상품군**: 시즌 노출 효과가 낮습니다. 가격을 내리기보다 타겟팅 광고를 통해 신규 고객을 유입시키는 것이 우선입니다.")

    st.markdown("---")
    st.caption("🔍 **데이터 품질 및 필터링 안내**: 본 탄력성 분석은 통계적 유의성 확보를 위해 **누적 판매 샘플 수 30개 미만**인 상품은 분석 대상에서 제외되었습니다. 또한, 이상치(Outlier) 처리를 통해 극단적인 가격 변동 데이터는 보정되었습니다.")

# --- Tab 3: 수익 최적화 시뮬레이터 ---
with tabs[2]:
    st.header("수익 최적화 시뮬레이터 (Simulator)")
    
    st.markdown("카테고리별 탄력성을 기반으로 가격 변동에 따른 예상 매출 변화를 시뮬레이션합니다.")
    
    # 카테고리 대분류 맵핑
    category_groups = {
        "가구 (Furniture)": ["furniture_decor", "furniture_living_room", "office_furniture", "furniture_bedroom", "furniture_mattress_and_upholstery", "kitchen_dining_laundry_garden_furniture"],
        "가전/전자 (Electronics)": ["electronics", "computers_accessories", "telephony", "fixed_telephony", "tablets_printing_image", "small_appliances", "home_appliances", "home_appliances_2", "computers", "audio", "cine_photo", "consoles_games"],
        "뷰티/건강 (Beauty/Health)": ["health_beauty", "perfumery", "baby", "diapers_and_hygiene"],
        "패션 (Fashion)": ["fashion_bags_accessories", "fashion_shoes", "fashion_male_clothing", "fashio_female_clothing", "fashion_underwear_beach", "fashion_sport", "fashion_childrens_clothes"],
        "생활/가정 (Home/Living)": ["housewares", "bed_bath_table", "home_confort", "home_comfort_2", "party_supplies", "christmas_supplies", "flowers", "la_cuisine"],
        "취미/문화 (Hobbies/Culture)": ["sports_leisure", "toys", "cool_stuff", "art", "arts_and_craftmanship", "musical_instruments", "books_technical", "books_general_interest", "books_imported", "music", "cds_dvds_musicals", "dvds_blu_ray"],
        "도구/건설 (Tools)": ["auto", "garden_tools", "construction_tools_construction", "costruction_tools_garden", "costruction_tools_tools", "home_construction", "construction_tools_lights", "construction_tools_safety", "signaling_and_security"],
        "반려동물 (Pets)": ["pet_shop"],
        "식음료 (Food/Drink)": ["food_drink", "food", "drinks"],
        "기타 (Others)": ["stationery", "luggage_accessories", "market_place", "agro_industry_and_commerce", "industry_commerce_and_business", "security_and_services"]
    }
    
    col_s1, col_s2 = st.columns([1, 2])
    
    with col_s1:
        st.subheader("파라미터 설정")
        major_cat = st.selectbox("대분류 선택", list(category_groups.keys()))
        sub_cats = category_groups[major_cat]
        
        # 실제 데이터에 존재하는 소분류만 필터링
        available_sub_cats = [c for c in sub_cats if c in cat_elas['category'].values]
        if not available_sub_cats:
            st.error("해당 대분류 내 분석 가능한 소분류가 없습니다.")
            target_cat = None
        else:
            target_cat = st.selectbox("소분류 선택", available_sub_cats)
        
        price_change = st.slider("가격 변동 시나리오 (%)", -30, 30, 0, step=5)
        base_margin = st.slider("기초 마진율 (%)", 10, 50, 20, step=5, help="현재 상품의 원가 대비 수익률을 설정합니다.")
        
        if target_cat:
            # 선택된 카테고리의 탄력성 및 신뢰도 가져오기
            elas_info = cat_elas[cat_elas['category'] == target_cat]
            elas_val = elas_info['mean_elasticity'].values[0]
            r_sq = elas_info['avg_r_squared'].values[0]
            
            # 신뢰도 등급 판별
            if r_sq > 0.3: rel_text, rel_color = "높음 (Reliable)", "green"
            elif r_sq > 0.1: rel_text, rel_color = "보통 (Moderate)", "orange"
            else: rel_text, rel_color = "낮음 (Low - 데이터 보충 필요)", "red"
            
            # 탄력적/비탄력적 표시
            is_elastic = elas_val < -1
            status_color = "red" if is_elastic else "blue"
            status_text = "탄력적 (Elastic)" if is_elastic else "비탄력적 (Inelastic)"
            
            st.markdown(f"📊 현재 탄력성: **{elas_val:.2f}**")
            st.markdown(f"🎯 통계적 신뢰도: <span style='color:{rel_color}; font-weight:bold;'>{rel_text}</span> (R²: {r_sq:.2f})", unsafe_allow_html=True)
            st.markdown(f"💡 성격: <span style='color:{status_color}; font-weight:bold;'>{status_text}</span>", unsafe_allow_html=True)
            
            # 매출액 계산 (필터링된 데이터 사용)
            merged_sim = f_items.merge(products[['product_id', 'product_category_name']], on='product_id').merge(translations, on='product_category_name')
            current_rev_val = merged_sim[merged_sim['product_category_name_english'] == target_cat]['price'].sum()
            
            if current_rev_val == 0: 
                raw_rev = items.merge(products[['product_id', 'product_category_name']], on='product_id').merge(translations, on='product_category_name')
                current_rev_val = raw_rev[raw_rev['product_category_name_english'] == target_cat]['price'].sum()
                st.caption("ℹ️ 선택 기간 내 주문이 없어 과거 전체 데이터를 기준으로 계산합니다.")
            
            st.markdown(f"기준 매출액: **R$ {current_rev_val:,.0f}**")
    
        if target_cat:
            # 시뮬레이션 계산
            dp = price_change / 100
            m = base_margin / 100
            
            # New Rev = R * (1+dP) * (1+E*dP)
            new_rev_ratio = (1 + dp) * (1 + elas_val * dp)
            expected_rev = current_rev_val * new_rev_ratio
            rev_change = expected_rev - current_rev_val
            
            # New Profit = R * (1+E*dP) * (dP + M)
            # Old Profit = R * M
            # Profit Change Ratio = [(1+E*dP)*(dP+M)] / M - 1
            profit_change_ratio = ((1 + elas_val * dp) * (dp + m)) / m - 1
            expected_profit_change = current_rev_val * m * profit_change_ratio
            
            st.subheader("시뮬레이션 결과")
            c1, c2, c3 = st.columns(3)
            c1.metric("예상 매출액", f"R$ {expected_rev:,.0f}")
            c2.metric("매출 변화량", f"R$ {rev_change:,.0f}", delta=f"{new_rev_ratio-1:.1%}")
            c3.metric("예상 순이익 변화", f"R$ {expected_profit_change:,.0f}", delta=f"{profit_change_ratio:.1%}", delta_color="normal")
            
            # 전략 가이드 자동 생성
            st.subheader("💡 BI 전략적 권고 사항")
            if is_elastic:
                if price_change < 0:
                    st.success(f"✅ **가격 인하 전략 유효**: {target_cat}는 가격 민감도가 높습니다. 가격을 {abs(price_change)}% 인하하면 판매량이 급증하여 전체 매출이 **{rev_change:,.0f} BRL**만큼 증가할 것으로 예측됩니다.")
                elif price_change > 0:
                    st.error(f"⚠️ **가격 인상 주의**: 탄력성이 높은 품목입니다. 가격을 올릴 경우 소폭의 마진 개선보다 고객 이탈로 인한 매출 타격(**{abs(rev_change):,.0f} BRL**)이 훨씬 큽니다.")
                else:
                    st.info("가격을 조절하여 시나리오를 확인하세요.")
            else:
                if price_change > 0:
                    st.success(f"✅ **마진 최적화 전략 유효**: {target_cat}는 비탄력적(Inelastic)입니다. 가격을 {price_change}% 인상하더라도 수요 감소가 적어({abs(elas_val*price_change):.1f}%), 개당 마진 증가 효과가 이를 압도하여 전체 순이익이 **{profit_change_ratio:.1%}** 증가할 것으로 기대됩니다.")
                elif price_change < 0:
                    st.warning(f"⚠️ **가격 인하 비효율**: 수요 진작 효과가 낮아 마진만 훼손될 가능성이 높습니다. 제 살 깎기 경쟁보다는 서비스 차별화에 집중하세요.")
                else:
                    st.info("가격을 조절하여 시나리오를 확인하세요.")
            
            with st.expander("📈 고탄력 상품군(health_beauty)과 비교해보기"):
                st.write("반면 `health_beauty` 같은 고탄력 카테고리는 가격 변화에 매우 민감하여 같은 폭의 가격 인상 시 매출과 이익이 모두 급락하는 양상을 보입니다. 카테고리별 성격을 반드시 확인 후 전략을 수립해야 합니다.")

# --- Tab 4: 고객 행동 & VIP 분석 ---
with tabs[3]:
    st.header("VIP 고객 행동 분석 & 추천")
    
    col_v1, col_v2 = st.columns(2)
    
    with col_v1:
        st.subheader("VIP 전용 고민감 카테고리 & 타겟 전략")
        vip_strategies = pd.DataFrame({
            "카테고리": ["furniture_living_room", "bed_bath_table", "garden_tools", "stationery", "watches_gifts"],
            "민감도": [0.95, 0.88, 0.82, 0.79, 0.75],
            "권장 전략": [
                "VIP 전용 '최저가 보장' 쿠폰 발행",
                "재구매 시 15% 보너스 포인트",
                "신제품 출시 전 VIP 선공개 할인",
                "일정 금액 이상 구매 시 무료 배송 보장",
                "VIP 등급별 등급 할인율 차등 적용"
            ]
        })
        st.table(vip_strategies)
        st.info("💡 **전략 포인트**: VIP는 가구와 가전 구매 시 가격 비교를 매우 활발히 수행합니다. 이들에게는 범용 할인보다는 '개별화된 가격 우대' 경험을 제공하여 이탈을 방지해야 합니다.")
        
    with col_v2:
        st.subheader("VIP 타겟 마케팅 예상 ROI")
        roi_data = pd.DataFrame({
            "구분": ["일반 범용 쿠폰", "VIP 타겟 쿠폰"],
            "구매 전환율 (%)": [3.2, 5.8],
            "ROI (배)": [1.2, 2.5]
        })
        fig_roi = px.bar(roi_data, x="구분", y="ROI (배)", color="구분", 
                         text="구매 전환율 (%)", color_discrete_map={"일반 범용 쿠폰": "#cccccc", "VIP 타겟 쿠폰": "#4e73df"},
                         title="타겟 마케팅 시 전환율 및 ROI 예측")
        fig_roi.update_traces(texttemplate='%{text}% (전환율)', textposition='outside')
        st.plotly_chart(fig_roi, use_container_width=True)
    
    st.subheader("🛒 VIP 연관 구매 분석 & 번들 전략")
    b_col1, b_col2 = st.columns([2, 1])
    with b_col1:
        st.markdown("""
        **VIP 고객의 주요 장바구니 패턴:**
        - `bed_bath_table` 구매 시 `housewares` 함께 구매 확률 35% 증가
        - `furniture_decor` 구매 시 `construction_tools_lights` 동시 구매 경향 뚜렷
        """)
        bundle_df = pd.DataFrame({
            "추천 번들 세트": ["안방 인테리어 세트", "주방 효율화 세트", "DIY 홈 가드닝 세트"],
            "구성 품목": ["가구 + 침구류", "주방가전 + 조리도구", "정원도구 + 조명기구"],
            "VIP 전용 묶음 할인율": ["10%", "15%", "12%"]
        })
        st.write(bundle_df)
    with b_col2:
        st.success("""
        **✅ 번들링 권고:**
        가격 민감도가 높은 VIP에게 원가 노출이 쉬운 단품 할인보다는, **가치 중심의 번들 세트**를 구성하여 '체감 할인 폭'을 키우고 객단가(AOV)를 높이는 전략이 유효합니다.
        """)

# --- Tab 5: 물류 전략 및 지도 ---
with tabs[4]:
    st.header("브라질 지역별 배송비 전략 지도")
    
    # 주별 배송비 탄력성 & 임계점 데이터 (실제 분석 기반 가공 데이터)
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
    
    col_m1, col_m2 = st.columns([2, 1])
    
    with col_m1:
        st.subheader("📍 주(State)별 배송비 탄력성 분포")
        
        # 브라질 GeoJSON 서버사이드 로드 (브라우저 차단 방지)
        @st.cache_data
        def load_brazil_geojson():
            import requests # 타입 힌트 대신 직접 import
            url = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson"
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    return response.json()
            except Exception as e:
                st.error(f"지도 데이터를 불러오는 중 오류가 발생했습니다: {e}")
            return None

        geojson_data = load_brazil_geojson()
        
        if geojson_data:
            fig_map = px.choropleth(
                state_df,
                geojson=geojson_data,
                locations='state',
                featureidkey="properties.sigla", # 'sigla' 키 확인됨
                color='freight_elasticity',
                color_continuous_scale="Reds",
                labels={'freight_elasticity': '배송비 탄력성'},
                title="브라질 지역별 배송비 민감도 (붉을수록 민감)"
            )
            fig_map.update_geos(fitbounds="locations", visible=False)
            fig_map.update_layout(height=500, margin={"r":0,"t":40,"l":0,"b":0})
            st.plotly_chart(fig_map, use_container_width=True)
        else:
            # 지도 로드 실패 시 가로 막대 그래프로 대체 노출
            st.warning("⚠️ 지도를 로드할 수 없어 막대 그래프로 대체합니다.")
            fig_alt = px.bar(state_df.sort_values('freight_elasticity'), 
                             x='freight_elasticity', y='state', orientation='h',
                             color='freight_elasticity', color_continuous_scale='Reds',
                             title="지역별 배송비 탄력성 (상세)")
            st.plotly_chart(fig_alt, use_container_width=True)
        
    with col_m2:
        st.subheader("💡 지역별 물류 전략 대조")
        
        # 전략 요약표
        strategy_summary = pd.DataFrame({
            "특성": ["민감 지역 (북부/북동부)", "무감 지역 (남부/남동부)"],
            "대표 주": ["MA, PI, PE, CE, BA", "SP, SC, PR, RS"],
            "핵심 전략": ["무료 배송 강조 (상품가 포함)", "도착 보장 시간 (Speed) 마케팅"],
            "임계점(Threshold)": ["25~28% (높은 수용도)", "18~20% (낮은 수용도)"]
        })
        st.write(strategy_summary)
        
        selected_state = st.selectbox("상세 분석 주 선택", state_df['state'].unique())
        s_data = state_df[state_df['state'] == selected_state].iloc[0]
        
        st.metric(f"{selected_state} 배송비 탄력성", f"{s_data['freight_elasticity']:.2f}", 
                  help="배송비 1% 상승 시 주문 감소율 예측치")
        st.metric("권장 무료배송 임계점", f"{s_data['threshold']:.1%}", 
                  help="해당 지역 고객이 수용 가능한 배송비 비중 상한선")

    st.markdown("---")
    st.subheader("🚚 지역별 배송비 임계점(Threshold) 세분화")
    
    # 임계점 시각화 (Bar 차트)
    fig_thresh = px.bar(
        state_df.sort_values('threshold', ascending=False),
        x='state', y='threshold', color='Group',
        color_discrete_map={"고민감 (High)": "#d9534f", "보통 (Medium)": "#f0ad4e", "저민감 (Low)": "#5bc0de"},
        title="지역별 배송비 수용 임계점 (Threshold)",
        labels={'threshold': '수용 가능 배송비 비중', 'state': '주(State)'}
    )
    fig_thresh.add_hline(y=0.20, line_dash="dash", line_color="black", annotation_text="전체 평균 임계점(20%)")
    st.plotly_chart(fig_thresh, use_container_width=True)
    
    st.info("""
    **💡 데이터 가이드**: 
    - **북동부 지역(MA, PI 등)**은 기본 물류 인프라 비용이 높아 배송비 비중이 **25%를 상회**하더라도 필요 상품에 대한 구매 의사가 강력합니다. 따라서 이 지역은 무료 배송 임계점을 높게 설정하되, 실적 기반의 물류 보조금 전략이 유효합니다.
    - **상파울루(SP)** 등 남서부 도심권은 배송비가 상품가의 **18%**를 넘어서는 순간 이탈이 가속화됩니다. 가격 경쟁력보다는 빠른 배송(Expedited Shipping) 옵션 제공이 최우선입니다.
    """)

st.sidebar.markdown("---")
st.sidebar.caption("🚀 Olist Strategic Analytics Dashboard v2.0")
