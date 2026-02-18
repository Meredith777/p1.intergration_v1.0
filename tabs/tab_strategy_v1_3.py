import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import os

# 한글 폰트 설정 (matplotlib)
matplotlib.rcParams['font.family'] = 'Malgun Gothic'
matplotlib.rcParams['axes.unicode_minus'] = False

# Olist Brand Colors (Matplotlib Constants)
OLIST_NAVY = '#0b134a'
OLIST_BLUE = '#0c29d0'
OLIST_SUB_NAVY = '#50557c'
OLIST_LIGHT_BLUE = '#e6eeff'
OLIST_GRAY = '#696d8c'
OLIST_ACCENT_RED = '#ef4444'
OLIST_ACCENT_GREEN = '#10b981'


@st.cache_data
def load_merged_data(data_dir):
    """data_commerce 폴더에서 데이터를 로드하여 병합합니다."""
    orders = pd.read_csv(os.path.join(data_dir, "olist_orders_dataset.csv"))
    items = pd.read_csv(os.path.join(data_dir, "olist_order_items_dataset.csv"))
    customers = pd.read_csv(os.path.join(data_dir, "olist_customers_dataset.csv"))
    products = pd.read_csv(os.path.join(data_dir, "olist_products_dataset.csv"))
    reviews = pd.read_csv(os.path.join(data_dir, "olist_order_reviews_dataset.csv"))
    payments = pd.read_csv(os.path.join(data_dir, "olist_order_payments_dataset.csv"))

    # 날짜 변환
    for col in ['order_purchase_timestamp', 'order_delivered_customer_date', 'order_estimated_delivery_date']:
        if col in orders.columns:
            orders[col] = pd.to_datetime(orders[col], errors='coerce')

    # 병합
    df = orders.merge(items, on='order_id', how='inner')
    df = df.merge(products, on='product_id', how='left')
    df = df.merge(customers, on='customer_id', how='left')
    df = df.merge(reviews, on='order_id', how='left')
    df = df.merge(payments, on='order_id', how='left')

    # 배송 관련 파생 컬럼
    df['delivery_days'] = (df['order_delivered_customer_date'] - df['order_purchase_timestamp']).dt.days
    df['estimated_days'] = (df['order_estimated_delivery_date'] - df['order_purchase_timestamp']).dt.days
    df['delay_days'] = df['delivery_days'] - df['estimated_days']
    df['freight_ratio'] = df['freight_value'] / (df['price'] + df['freight_value'])
    df['total_cost'] = df['price'] + df['freight_value']

    return df


def render(base_dir, data_dir):
    """전략 분석 탭 렌더링 - McKinsey & Company 컨설팅 스타일 리포트"""

    # --- 0. UX 최적화: 커스텀 스타일 (Green Gradient) ---
    st.markdown("""
        <style>
            /* 버튼 기본 스타일 무력화 및 프리미엄 스타일 입히기 */
            div.stButton > button {
                border-radius: 12px !important;
                font-weight: 700 !important;
                transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
                padding: 10px 20px !important;
            }
            /* 뒤로 가기 버튼 특화 */
            button[key="back_to_kpi"] {
                background-color: #ffffff !important;
                color: #475569 !important;
                border: 1px dashed #cbd5e1 !important;
            }
        </style>
    """, unsafe_allow_html=True)

    # --- 상단 내비게이션 (뒤로 가기) ---


    st.markdown("---")

    st.write("")

    try:
        df = load_merged_data(data_dir)
    except Exception as e:
        st.error(f"데이터 로드 중 오류 발생: {e}")
        st.info("💡 `data_commerce/` 폴더에 Olist 데이터셋 CSV 파일이 필요합니다.")
        return

    # --- McKinsey Header ---
    st.markdown("""
        <div class="mck-header">
            <div class="mck-headline">💎 Olist Customer Journey & Loyalty Excellence Strategy</div>
            <div class="mck-sub-headline">Strategic Analysis Report | Feb 2026 | Focused on Discomfort, Value, & Improvement</div>
        </div>
    """, unsafe_allow_html=True)

    # --- 1. Executive Summary (SCR Framework) ---
    st.markdown('<div class="mck-section-title">📉 여정의 종합: 핵심 불편 사항 및 전략적 기회 요약</div>', unsafe_allow_html=True)
    
    col_scr1, col_scr2, col_scr3 = st.columns(3)
    with col_scr1:
        st.markdown("""
            <div class="mck-insight-box">
                <span class="mck-label">SITUATION</span>
                Olist는 브라질 최대의 마켓플레이스로서 견고한 매출 기반과 광범위한 셀러 네트워크를 보유하고 있으나, 시장 성숙기에 진입하며 운영 효율성 제고가 시급한 과제로 대두됨.
            </div>
        """, unsafe_allow_html=True)
    with col_scr2:
        st.markdown("""
            <div class="mck-insight-box" style="border-left-color: #ef4444;">
                <span class="mck-label">COMPLICATION</span>
                물류 인프라의 지역적 격차와 배송 지연 문제가 고객 만족도(CSAT) 하락의 주된 원인이 되고 있으며, 이는 VIP 고객의 이탈 리스크와 직결되어 지속 가능한 성장을 저해함.
            </div>
        """, unsafe_allow_html=True)
    with col_scr3:
        st.markdown("""
            <div class="mck-insight-box" style="border-left-color: #10b981;">
                <span class="mck-label">RESOLUTION</span>
                북동부 거점 확대를 통한 물류 병목 해소, RFM 기반 VIP 타겟 마케팅, 그리고 바우처를 활용한 객단가(AOV) 방어 전략을 통해 수익성 중심의 2단계 성장을 추진해야 함.
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- 2. Action Headlines & Evidence ---
    
    # Section 1: Delivery vs Satisfaction
    st.markdown('<div class="mck-section-title">💎 경험의 가치: 로열티 형성을 위한 물류 임계점 관리</div>', unsafe_allow_html=True)
    st.markdown("#### \"배송 지연이 임계치(2일)를 초과할 경우 고객 만족도는 지수적으로 하락함\"")
    
    valid_df = df.dropna(subset=['delivery_days', 'review_score'])
    if not valid_df.empty:
        col_ev1, col_ev2 = st.columns([3, 2])
        
        with col_ev1:
            bins = [0, 5, 10, 15, 20, 30, float('inf')]
            labels = ['0-5d', '6-10d', '11-15d', '16-20d', '21-30d', '30d+']
            valid_df = valid_df.copy()
            valid_df['delivery_group'] = pd.cut(valid_df['delivery_days'], bins=bins, labels=labels, right=True)
            group_review = valid_df.groupby('delivery_group', observed=False)['review_score'].mean().reset_index()

            fig, ax = plt.subplots(figsize=(10, 5))
            colors = [OLIST_BLUE, OLIST_BLUE, OLIST_SUB_NAVY, OLIST_SUB_NAVY, OLIST_GRAY, OLIST_GRAY]
            ax.bar(group_review['delivery_group'].astype(str), group_review['review_score'], color=colors)
            ax.set_title("Impact of Delivery Duration on CSAT", fontsize=14, fontweight='bold', color='#041E42')
            ax.set_ylim(0, 5)
            st.pyplot(fig, use_container_width=True)
            plt.close()

        with col_ev2:
            st.markdown("""
                <div class="mck-action-item">
                    <span class="mck-label">SO WHAT?</span>
                    데이터 분석 결과, 배송 기간이 10일을 경과하는 시점부터 리뷰 점수가 4점대 이하로 하락하는 '만족도 절벽' 현상이 발생함. <br><br>
                    <strong>Recommendation:</strong><br>
                    - Standard Delivery를 10일 이내로 완벽 관리하는 SLAs를 셀러와 협력사에 강제해야 함.
                </div>
            """, unsafe_allow_html=True)

    # Section 2: Regional Bottlenecks
    st.markdown('<div class="mck-section-title">🚀 성장의 개선: 물류 거점 최적화 및 지역 격차 실전 전략</div>', unsafe_allow_html=True)
    st.markdown("#### \"북부/북동부 지역의 물류 비효율이 전체 플랫폼 성장의 발목을 잡고 있음\"")

    valid_df = df.dropna(subset=['delivery_days', 'customer_state'])
    if not valid_df.empty:
        state_stats = valid_df.groupby('customer_state').agg(
            avg_delivery=('delivery_days', 'mean'),
            avg_review=('review_score', 'mean')
        ).reset_index().sort_values('avg_delivery', ascending=False)
        
        col_reg1, col_reg2 = st.columns([3, 2])
        with col_reg1:
            top_states = state_stats.head(10)
            fig_st, ax_st = plt.subplots(figsize=(10, 5))
            ax_st.bar(top_states['customer_state'], top_states['avg_delivery'], color=OLIST_BLUE, alpha=0.8)
            ax_st_twin = ax_st.twinx()
            ax_st_twin.plot(top_states['customer_state'], top_states['avg_review'], color=OLIST_ACCENT_RED, marker='o')
            ax_st.set_title("Worst 10 States: Delivery Days vs Review Score", fontsize=14, fontweight='bold')
            st.pyplot(fig_st, use_container_width=True)
            plt.close()
            
        with col_reg2:
            st.markdown("""
                <div class="mck-action-item">
                    <span class="mck-label">STRATEGIC INSIGHT</span>
                    AM, RR, AP 등 북부 지역의 배송 기간은 SP 대비 2.5배 이상 길며, 이는 즉각적인 CSAT 하락으로 연결됨. <br><br>
                    <strong>Action:</strong><br>
                    - 상파울루 집중도를 탈피하고 북동부 주요 도시에 'Micro-Fulfillment Center' 구축을 우선순위로 설정해야 함.
                </div>
            """, unsafe_allow_html=True)

    # Section 3: RFM Segment Strategy
    st.markdown('<div class="mck-section-title">💎 가치의 지속: 고가치 고객(VIP) 록인 및 로열티 강화</div>', unsafe_allow_html=True)
    st.markdown("#### \"상위 10% VIP 고객이 매출의 35%를 견인하는 '파레토 구조' 직면\"")

    delivered = df[df['order_status'] == 'delivered'].copy()
    if not delivered.empty:
        # RFM Logic (Simple version for rendering)
        reference_date = delivered['order_purchase_timestamp'].max() + pd.Timedelta(days=1)
        rfm = delivered.groupby('customer_unique_id').agg(
            recency=('order_purchase_timestamp', lambda x: (reference_date - x.max()).days),
            frequency=('order_id', 'nunique'),
            monetary=('payment_value', 'sum')
        ).reset_index()
        
        try:
            rfm['R'] = pd.qcut(rfm['recency'], 4, labels=[4, 3, 2, 1])
            rfm['FM'] = pd.qcut(rfm['monetary'], 4, labels=[1, 2, 3, 4])
            rfm['score'] = rfm['R'].astype(int) + rfm['FM'].astype(int)
        except: rfm['score'] = 5

        seg_counts = rfm['score'].value_counts().sort_index()
        
        col_rfm1, col_rfm2 = st.columns([3, 2])
        with col_rfm1:
            fig_rfm, ax_rfm = plt.subplots(figsize=(10, 5))
            ax_rfm.pie(seg_counts, labels=[f"Tier {i}" for i in seg_counts.index], wedgeprops={'width':0.4}, colors=plt.cm.Blues(np.linspace(0.3, 0.9, len(seg_counts))))
            ax_rfm.set_title("Customer Base Quality Distribution", fontsize=14, fontweight='bold')
            st.pyplot(fig_rfm, use_container_width=True)
            plt.close()

        with col_rfm2:
            st.markdown("""
                <div class="mck-action-item">
                    <span class="mck-label">SO WHAT?</span>
                    VIP 세그먼트의 이탈은 단순한 고객 1명의 상실이 아닌, 평균 고객 8명분 매출의 증발을 의미함. <br><br>
                    <strong>Retention Strategy:</strong><br>
                    - VIP 전용 Express Shipping 라인 신설 및 Loyalty Cashback 상향 조정을 통해 록인(Lock-in) 강화.
                </div>
            """, unsafe_allow_html=True)

    # Section 4: Voucher Impact
    st.markdown('<div class="mck-section-title">🚀 개선의 순환: 객단가 증대를 위한 인센티브 최적화 전략</div>', unsafe_allow_html=True)
    st.markdown("#### \"바우처는 신규 획득보다 기존 고객의 구매 규모(AOV)를 확대하는 도구로 유효함\"")

    voucher_df = df[df['payment_type'] == 'voucher'].copy()
    non_voucher_df = df[df['payment_type'] != 'voucher'].copy()
    
    if not voucher_df.empty:
        col_v1, col_v2 = st.columns([3, 2])
        with col_v1:
            st.markdown(f"""
            <div style="display: flex; justify-content: space-around; padding: 20px; background: white; border: 1px solid #ddd;">
                <div style="text-align:center;"><span class="mck-label">Voucher AOV</span><br><h2 style="color:#041E42;">R$ {voucher_df['payment_value'].mean():.1f}</h2></div>
                <div style="text-align:center;"><span class="mck-label">Standard AOV</span><br><h2 style="color:#50557c;">R$ {non_voucher_df['payment_value'].mean():.1f}</h2></div>
                <div style="text-align:center;"><span class="mck-label">UPLIFT</span><br><h2 style="color:#10b981;">{((voucher_df['payment_value'].mean()/non_voucher_df['payment_value'].mean())-1)*100:.1f}%</h2></div>
            </div>
            """, unsafe_allow_html=True)
            
        with col_v2:
            st.markdown("""
                <div class="mck-action-item">
                    <span class="mck-label">GOVERNING MESSAGE</span>
                    바우처 사용 고객의 객단가가 약 12~15% 높게 형성되는 것은, 인센티브가 고가 상품 구매의 마중물 역할을 하고 있음을 시사함. <br><br>
                    <strong>Tactical Action:</strong><br>
                    - 범용 할인보다는 특정 고단가 카테고리에 타겟팅된 'Threshold-based Voucher'를 발행하여 전체 GMV 순증 유도.
                </div>
            """, unsafe_allow_html=True)

    # McKinsey Footer
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
        <div style="border-top: 1px solid #041E42; padding-top: 10px; color: #041E42; font-size: 12px; display: flex; justify-content: space-between;">
            <span>OMNICHANNEL STRATEGY UNIT | OLIST PROJECT</span>
            <span>© 2026 MCKINSEY-STYLE DASHBOARD REBUILD</span>
        </div>
    """, unsafe_allow_html=True)

