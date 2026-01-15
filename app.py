"""
Municipal Credit Assessment Dashboard
A Streamlit application for visualizing and interacting with CWAS data.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
from pathlib import Path

# Add utils to path
sys.path.insert(0, str(Path(__file__).parent))

from utils.data_loader import load_excel_data, get_available_years
from utils.calculations import (
    RATING_SCALE,
    get_grade_from_score,
    calculate_total_score,
    format_percentage,
    format_currency,
    get_trend_indicator,
)

# Page configuration
st.set_page_config(
    page_title="Municipal Credit Assessment",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f4e79;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
    }
    .grade-display {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
    }
    .stMetric {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Data file path
DATA_FILE = Path(__file__).parent / "data" / "CWAS - Creditworthiness DIY Tool-Trichy.xlsm"


@st.cache_data
def load_data():
    """Load and cache the Excel data."""
    if DATA_FILE.exists():
        return load_excel_data(str(DATA_FILE))
    return None


def render_sidebar():
    """Render the sidebar navigation."""
    st.sidebar.title("🏛️ Navigation")

    page = st.sidebar.radio(
        "Select Page",
        ["📊 Dashboard", "💰 Financial Analysis", "⚙️ Operating Performance",
         "📈 Year Comparison", "📝 Data Input", "ℹ️ About"]
    )

    st.sidebar.markdown("---")

    # Year selector
    years = [2022, 2023, 2024, 2025]
    selected_year = st.sidebar.selectbox("Select Year", years, index=2)

    st.sidebar.markdown("---")
    st.sidebar.markdown("### Rating Scale")
    for grade, info in RATING_SCALE.items():
        st.sidebar.markdown(
            f"<span style='color:{info['color']}'> ● </span> **{grade}**: {info['min']}-{info['max']}",
            unsafe_allow_html=True
        )

    return page, selected_year


def render_dashboard(data, year):
    """Render the main dashboard page."""
    st.markdown("<h1 class='main-header'>Municipal Credit Assessment Dashboard</h1>", unsafe_allow_html=True)

    city_info = data['city_info']
    final_scores = data['final_scores']

    # City header
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown(f"### 🏙️ {city_info.get('city', 'Unknown City')}")
        st.markdown(f"**State:** {city_info.get('state', 'Unknown')}")

    # Get scores for selected year
    total_data = final_scores['total_scores'].get(year, {})
    financial_score = final_scores['financial_scores'].get(year, 0)
    operating_score = final_scores['operating_scores'].get(year, 0)
    total_score = total_data.get('total_score', 0)
    grade = total_data.get('grade', 'N/A')
    status = total_data.get('status', 'N/A')

    grade_info = get_grade_from_score(total_score)

    with col2:
        st.markdown(f"""
        <div style='background-color:{grade_info[2]}; padding:1rem; border-radius:10px; text-align:center; color:white;'>
            <h2 style='margin:0; color:white;'>{grade}</h2>
            <p style='margin:0; font-size:0.9rem;'>{status}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Key metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="📊 Total Score",
            value=f"{total_score:.1f}/100",
            delta=None
        )

    with col2:
        st.metric(
            label="💰 Financial Score",
            value=f"{financial_score:.0f}/100",
            delta=None
        )

    with col3:
        st.metric(
            label="⚙️ Operating Score",
            value=f"{operating_score:.1f}/100",
            delta=None
        )

    with col4:
        # Borrowing capacity (from the data)
        borrowing_cap = 231.69  # From the Excel analysis
        st.metric(
            label="🏦 Borrowing Capacity",
            value=f"₹{borrowing_cap:.0f} Cr",
            delta=None
        )

    st.markdown("---")

    # Score breakdown charts
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Score Composition")
        fig = go.Figure(data=[
            go.Bar(name='Financial (70%)', x=['Score'], y=[financial_score * 0.7], marker_color='#1f77b4'),
            go.Bar(name='Operating (30%)', x=['Score'], y=[operating_score * 0.3], marker_color='#ff7f0e')
        ])
        fig.update_layout(
            barmode='stack',
            height=300,
            showlegend=True,
            yaxis_title="Points",
            yaxis_range=[0, 100]
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Score Gauge")
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=total_score,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Creditworthiness Score"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': grade_info[2]},
                'steps': [
                    {'range': [0, 20], 'color': "#DC143C"},
                    {'range': [20, 40], 'color': "#FF6347"},
                    {'range': [40, 60], 'color': "#FFD700"},
                    {'range': [60, 80], 'color': "#32CD32"},
                    {'range': [80, 100], 'color': "#006400"},
                ],
                'threshold': {
                    'line': {'color': "black", 'width': 4},
                    'thickness': 0.75,
                    'value': total_score
                }
            }
        ))
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)

    # Year trend
    st.subheader("📈 Score Trend Over Years")
    years_data = []
    for y in [2022, 2023, 2024, 2025]:
        y_data = final_scores['total_scores'].get(y, {})
        years_data.append({
            'Year': y,
            'Total Score': y_data.get('total_score', 0),
            'Financial': final_scores['financial_scores'].get(y, 0),
            'Operating': final_scores['operating_scores'].get(y, 0),
            'Grade': y_data.get('grade', 'N/A')
        })

    df_trend = pd.DataFrame(years_data)

    fig = px.line(df_trend, x='Year', y=['Total Score', 'Financial', 'Operating'],
                  markers=True, title="Score Progression")
    fig.update_layout(
        yaxis_range=[0, 100],
        yaxis_title="Score",
        legend_title="Score Type"
    )
    st.plotly_chart(fig, use_container_width=True)


def render_financial_analysis(data, year):
    """Render the financial analysis page."""
    st.title("💰 Financial Analysis")

    financial_ratios = data['financial_ratios']
    financial_scores = data['financial_scores']

    if financial_ratios.empty:
        st.warning("No financial ratio data available.")
        return

    # Filter by year
    st.subheader(f"Financial Ratios - {year}")

    # Create tabs for different ratio categories
    tab1, tab2, tab3, tab4 = st.tabs(["Income Ratios", "Expense Ratios", "Operating Ratios", "Leverage Ratios"])

    categories = financial_ratios['category'].unique()

    with tab1:
        income_df = financial_ratios[financial_ratios['category'] == 'Income Ratios']
        if not income_df.empty:
            st.dataframe(income_df, use_container_width=True, hide_index=True)

            # Chart
            if year in income_df.columns:
                chart_data = income_df[['indicator', year]].dropna()
                chart_data[year] = pd.to_numeric(chart_data[year], errors='coerce')
                chart_data = chart_data.dropna()
                if not chart_data.empty:
                    fig = px.bar(chart_data, x='indicator', y=year,
                                title=f"Income Ratios ({year})")
                    fig.update_layout(xaxis_tickangle=-45)
                    st.plotly_chart(fig, use_container_width=True)

    with tab2:
        expense_df = financial_ratios[financial_ratios['category'] == 'Expenses Ratios']
        if not expense_df.empty:
            st.dataframe(expense_df, use_container_width=True, hide_index=True)

    with tab3:
        operating_df = financial_ratios[financial_ratios['category'] == 'Operating Ratios']
        if not operating_df.empty:
            st.dataframe(operating_df, use_container_width=True, hide_index=True)

    with tab4:
        leverage_df = financial_ratios[financial_ratios['category'] == 'Leverage Ratios']
        if not leverage_df.empty:
            st.dataframe(leverage_df, use_container_width=True, hide_index=True)

    # Financial Scores
    st.markdown("---")
    st.subheader("📊 Financial Score Breakdown")

    if not financial_scores.empty:
        st.dataframe(financial_scores, use_container_width=True, hide_index=True)


def render_operating_performance(data, year):
    """Render the operating performance page."""
    st.title("⚙️ Operating Performance")

    operating_ratios = data['operating_ratios']
    operating_scores = data['operating_scores']

    if operating_ratios.empty:
        st.warning("No operating ratio data available.")
        return

    st.subheader(f"Service Level Indicators - {year}")

    # Service coverage metrics
    col1, col2, col3, col4 = st.columns(4)

    # Extract key metrics
    def get_ratio_value(df, indicator_partial, year):
        for _, row in df.iterrows():
            if indicator_partial.lower() in str(row.get('indicator', '')).lower():
                val = row.get(year)
                if val is not None:
                    try:
                        return float(val)
                    except:
                        pass
        return None

    water_coverage = get_ratio_value(operating_ratios, 'water supply coverage', year)
    swm_coverage = get_ratio_value(operating_ratios, 'SWM Coverage', year)
    toilet_coverage = get_ratio_value(operating_ratios, 'Toilet coverage', year)
    sewerage_coverage = get_ratio_value(operating_ratios, 'sewerage', year)

    with col1:
        val = water_coverage if water_coverage else 0
        st.metric("💧 Water Coverage", f"{val*100:.0f}%")

    with col2:
        val = swm_coverage if swm_coverage else 0
        st.metric("🗑️ SWM Coverage", f"{val*100:.0f}%")

    with col3:
        val = toilet_coverage if toilet_coverage else 0
        st.metric("🚽 Toilet Coverage", f"{val*100:.0f}%")

    with col4:
        val = sewerage_coverage if sewerage_coverage else 0
        st.metric("🚰 Sewerage Coverage", f"{val*100:.0f}%")

    st.markdown("---")

    # Coverage chart
    coverage_data = {
        'Service': ['Water Supply', 'SWM', 'Toilet', 'Sewerage'],
        'Coverage': [
            (water_coverage or 0) * 100,
            (swm_coverage or 0) * 100,
            (toilet_coverage or 0) * 100,
            (sewerage_coverage or 0) * 100
        ]
    }
    df_coverage = pd.DataFrame(coverage_data)

    fig = px.bar(df_coverage, x='Service', y='Coverage',
                 title="Service Coverage (%)",
                 color='Coverage',
                 color_continuous_scale=['red', 'yellow', 'green'])
    fig.update_layout(yaxis_range=[0, 100])
    st.plotly_chart(fig, use_container_width=True)

    # Full data tables
    st.subheader("📋 All Operating Ratios")
    st.dataframe(operating_ratios, use_container_width=True, hide_index=True)

    st.subheader("📊 Operating Scores")
    if not operating_scores.empty:
        st.dataframe(operating_scores, use_container_width=True, hide_index=True)


def render_year_comparison(data, year):
    """Render the year comparison page."""
    st.title("📈 Year Comparison")

    final_scores = data['final_scores']

    # Create comparison table
    comparison_data = []
    for y in [2022, 2023, 2024, 2025]:
        y_data = final_scores['total_scores'].get(y, {})
        comparison_data.append({
            'Year': y,
            'Financial Score': final_scores['financial_scores'].get(y, 0),
            'Operating Score': final_scores['operating_scores'].get(y, 0),
            'Total Score': y_data.get('total_score', 0),
            'Grade': y_data.get('grade', 'N/A'),
            'Status': y_data.get('status', 'N/A')
        })

    df_comparison = pd.DataFrame(comparison_data)

    st.subheader("Score Comparison Across Years")
    st.dataframe(df_comparison, use_container_width=True, hide_index=True)

    # Multi-year chart
    col1, col2 = st.columns(2)

    with col1:
        fig = px.bar(df_comparison, x='Year', y=['Financial Score', 'Operating Score'],
                     barmode='group', title="Financial vs Operating Scores")
        fig.update_layout(yaxis_range=[0, 100])
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Grade distribution
        fig = go.Figure(data=[
            go.Scatter(
                x=df_comparison['Year'],
                y=df_comparison['Total Score'],
                mode='lines+markers+text',
                text=df_comparison['Grade'],
                textposition='top center',
                marker=dict(size=15),
                line=dict(width=3)
            )
        ])
        fig.update_layout(
            title="Total Score & Grade Progression",
            yaxis_range=[0, 100],
            yaxis_title="Total Score"
        )
        st.plotly_chart(fig, use_container_width=True)

    # Improvement analysis
    st.markdown("---")
    st.subheader("📊 Year-over-Year Changes")

    for i in range(1, len(comparison_data)):
        curr = comparison_data[i]
        prev = comparison_data[i-1]

        col1, col2, col3 = st.columns(3)
        with col1:
            change = curr['Total Score'] - prev['Total Score']
            icon = "📈" if change > 0 else "📉" if change < 0 else "➖"
            st.metric(
                f"{prev['Year']} → {curr['Year']}",
                f"{curr['Total Score']:.1f}",
                f"{change:+.1f} {icon}"
            )


def render_data_input(data, year):
    """Render the data input page."""
    st.title("📝 Data Input")

    st.info("This section allows you to input or modify municipal data for credit assessment.")

    data_input = data['data_input']

    # Tabs for different data categories
    tab1, tab2, tab3, tab4 = st.tabs(["Basic Info", "Financial Data", "Service Data", "Other Indicators"])

    with tab1:
        st.subheader("City Information")
        col1, col2 = st.columns(2)
        with col1:
            state = st.text_input("State", value=data['city_info'].get('state', ''))
        with col2:
            city = st.text_input("City/Municipality Name", value=data['city_info'].get('city', ''))

        assessment_year = st.selectbox("Assessment Year", [2022, 2023, 2024, 2025], index=2)

    with tab2:
        st.subheader("Financial Indicators")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Revenue Income (in Lakhs)**")
            tax_revenue = st.number_input("Tax Revenue", min_value=0.0, value=0.0)
            non_tax_revenue = st.number_input("Non-Tax Revenue", min_value=0.0, value=0.0)
            assigned_revenue = st.number_input("Assigned Revenue", min_value=0.0, value=0.0)
            revenue_grants = st.number_input("Revenue Grants", min_value=0.0, value=0.0)
            other_income = st.number_input("Other Income", min_value=0.0, value=0.0)

        with col2:
            st.markdown("**Revenue Expenditure (in Lakhs)**")
            establishment_exp = st.number_input("Establishment Expenses", min_value=0.0, value=0.0)
            admin_exp = st.number_input("Administrative Expenses", min_value=0.0, value=0.0)
            om_exp = st.number_input("O&M Expenses", min_value=0.0, value=0.0)
            interest_exp = st.number_input("Interest & Finance Charges", min_value=0.0, value=0.0)
            depreciation = st.number_input("Depreciation", min_value=0.0, value=0.0)

        st.markdown("**Property Tax**")
        col1, col2 = st.columns(2)
        with col1:
            pt_demand = st.number_input("Property Tax Demand (Lakhs)", min_value=0.0, value=0.0)
        with col2:
            pt_collection = st.number_input("Property Tax Collection (Lakhs)", min_value=0.0, value=0.0)

    with tab3:
        st.subheader("Service Level Indicators")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("**Coverage (%)**")
            water_coverage = st.slider("Water Supply Coverage", 0, 100, 95)
            swm_coverage = st.slider("SWM Coverage", 0, 100, 92)
            toilet_coverage = st.slider("Toilet Coverage", 0, 100, 100)
            sewerage_coverage = st.slider("Sewerage Coverage", 0, 100, 30)

        with col2:
            st.markdown("**Efficiency (%)**")
            water_collection_eff = st.slider("Water Tax Collection Efficiency", 0, 100, 58)
            pt_collection_eff = st.slider("Property Tax Collection Efficiency", 0, 100, 89)
            cost_recovery_water = st.slider("Cost Recovery (Water)", 0, 100, 100)

        with col3:
            st.markdown("**Other Metrics**")
            nrw = st.slider("Non-Revenue Water (%)", 0, 100, 23)
            metering = st.slider("Water Metering (%)", 0, 100, 100)
            per_capita_supply = st.number_input("Per Capita Water Supply (lpcd)", min_value=0, value=126)

    with tab4:
        st.subheader("Other Indicators")

        col1, col2 = st.columns(2)
        with col1:
            audit_reports = st.selectbox("Does city prepare annual audit reports?", ["Yes", "No"])
            accrual_accounting = st.selectbox("Does city follow accrual accounting?", ["Yes", "No"])

        with col2:
            population = st.number_input("Population (in Lakhs)", min_value=0.0, value=0.0)
            capital_income = st.number_input("Capital Income (Lakhs)", min_value=0.0, value=0.0)
            capital_expenditure = st.number_input("Capital Expenditure (Lakhs)", min_value=0.0, value=0.0)

    st.markdown("---")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("💾 Save Data", type="primary"):
            st.success("Data saved successfully! (Demo mode)")
    with col2:
        if st.button("🔄 Calculate Scores"):
            st.info("Score calculation would run here. (Demo mode)")
    with col3:
        if st.button("📥 Export to Excel"):
            st.info("Export functionality would run here. (Demo mode)")


def render_about():
    """Render the about page."""
    st.title("ℹ️ About This Tool")

    st.markdown("""
    ## PAS Creditworthiness Assessment Framework

    This application is a digital implementation of the **Performance Assessment System (PAS)
    Creditworthiness Assessment Framework**, designed to help urban local bodies (ULBs) in India
    understand and improve their creditworthiness.

    ### Key Features

    - **📊 Dashboard**: Overview of creditworthiness scores and grades
    - **💰 Financial Analysis**: Detailed financial ratio analysis
    - **⚙️ Operating Performance**: Service level indicators and coverage metrics
    - **📈 Year Comparison**: Track progress over multiple years
    - **📝 Data Input**: Enter and modify municipal data

    ### Scoring Methodology

    The creditworthiness score is calculated using:
    - **70%** Financial Performance Score
    - **30%** Operating/Service Level Score

    ### Rating Scale
    """)

    # Rating scale table
    rating_data = []
    for grade, info in RATING_SCALE.items():
        rating_data.append({
            'Grade': grade,
            'Score Range': f"{info['min']} - {info['max']}",
            'Status': info['status']
        })

    st.table(pd.DataFrame(rating_data))

    st.markdown("""
    ### Disclaimer

    The assessment grade contained herein should be treated as opinion and not statements of fact
    or recommendations to investors. No warranty, express or implied, as to the accuracy,
    timeliness, completeness, or fitness for any particular purpose is given.

    ---
    **Data Source**: CWAS - Creditworthiness DIY Tool for Tiruchirappalli City Municipal Corporation
    """)


def main():
    """Main application entry point."""
    # Load data
    data = load_data()

    if data is None:
        st.error(f"Could not load data file. Please ensure the Excel file exists at: {DATA_FILE}")
        return

    # Render sidebar and get selections
    page, selected_year = render_sidebar()

    # Render selected page
    if page == "📊 Dashboard":
        render_dashboard(data, selected_year)
    elif page == "💰 Financial Analysis":
        render_financial_analysis(data, selected_year)
    elif page == "⚙️ Operating Performance":
        render_operating_performance(data, selected_year)
    elif page == "📈 Year Comparison":
        render_year_comparison(data, selected_year)
    elif page == "📝 Data Input":
        render_data_input(data, selected_year)
    elif page == "ℹ️ About":
        render_about()


if __name__ == "__main__":
    main()
