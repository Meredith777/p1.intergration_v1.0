# Olist E-commerce Customer Journey Dashboard

## Project Overview

This is an interactive **Streamlit Dashboard** designed to visualize and analyze the complete **Customer Journey** on the Olist e-commerce platform. The project focuses on key performance indicators (KPIs), product discovery, purchase decisions, fulfillment logistics, seller partnerships, and customer loyalty.

**Data Source:** Based on the actual Olist Public Dataset (2016-2018).

## Key Features

The dashboard is divided into 6 strategic tabs:

1.  **📉 Customer Journey Visibility Center (Total KPI)**
    -   Overview of GMV, Orders, Average Delivery Time, and Active Sellers.
    -   Visualize key bottlenecks in the customer journey.
    -   Interactive tooltips with actionable insights.

2.  **👀 Product Discovery (Discovery)**
    -   Analyze top-performing categories and products.
    -   Review sentiment analysis (Keyword WordClouds).

3.  **💳 Purchase Decision (Decision)**
    -   Price elasticity and conversion analysis.
    -   Impact of Black Friday promotions.

4.  **🚚 Fulfillment & Logistics (Fulfillment)**
    -   Delivery time vs. customer satisfaction correlation.
    -   Regional logistics performance (State-level analysis).

5.  **🏢 Seller Partnership (Partnership)**
    -   Seller Tier System (T1, T2, T3) and revenue concentration.
    -   Active seller retention metrics.

6.  **💎 Loyalty & Strategy (Loyalty)**
    -   VIP customer analysis and repurchase rates based on delivery speed.
    -   Strategic recommendations for growth.

## Tech Stack

-   **Python 3.8+**
-   **Streamlit** (Web Application Framework)
-   **Pandas** (Data Manipulation)
-   **Plotly** (Interactive Data Visualization)
-   **NumPy** (Numerical Computing)

## Installation & Setup

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/your-username/olist-dashboard.git
    cd olist-dashboard
    ```

2.  **Install Requirements**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Prepare Data**
    -   Download the **Olist Brazilian E-Commerce Public Dataset** from [Kaggle](https://www.kaggle.com/olistbr/brazilian-ecommerce).
    -   Place all CSV files (e.g., `olist_orders_dataset.csv`, `olist_products_dataset.csv`) inside the `data_commerce/` directory in the project root.
    -   _(Optional)_ Translation files for product categories should be placed in `data_commerce/` as `product_category_name_translation.csv`.

4.  **Run the Application**
    ```bash
    streamlit run admin_dashboard_v1.3.py
    ```

## Project Structure

```
├── admin_dashboard_v1.3.py  # Main Application Entry Point
├── tabs/                    # Individual Dashboard Tabs (Modules)
│   ├── tab_total_kpi_v1_3.py   # KPI Dashboard Logic
│   ├── tab_product_v1_3.py     # Product Analysis Logic
│   ├── tab_price_v1_3.py       # Price Analysis Logic
│   ├── tab_delivery_v1_3.py    # Delivery Analysis Logic
│   ├── tab_seller_v1_3.py      # Seller Analysis Logic
│   └── tab_strategy_v1_3.py    # Strategy Analysis Logic
├── assets/                  # Images and static assets
├── data_commerce/           # Data Directory (git-ignored)
├── requirements.txt         # Dependency List
└── README.md                # Project Documentation
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](https://choosealicense.com/licenses/mit/)
