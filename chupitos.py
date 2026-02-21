import streamlit as st
import plotly.express as px
import pandas as pd

# -------------------------
# Page Configuration
# -------------------------
st.set_page_config(page_title="Restaurant Demand Dashboard", layout="wide")

st.title("Restaurant Demand & Cost Analysis Dashboard")

st.markdown("""
This dashboard analyzes **500 days of demand data** from an international fast-food restaurant.
The objective is to:

- Identify **high-demand periods throughout the year**
- Detect **top-performing products**
- Support **raw material purchasing decisions**
- Improve **production cost planning and operational efficiency**
""")

# -------------------------
# Tabs
# -------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "Monthly Performance",
    "Weekly Demand",
    "Holiday Impact",
    "Cost Analysis"
])

# -------------------------
# TAB 1 – Monthly Demand & Profit
# -------------------------
with tab1:
    st.subheader("Monthly Product Demand & Profit (2025)")
    st.caption("Each bubble represents a product. Bubble size reflects total profit.")

    selected_month = st.slider(
        "Select Month (2025):",
        min_value=int(monthly_combined_melted['month'].min()),
        max_value=int(monthly_combined_melted['month'].max()),
        value=int(monthly_combined_melted['month'].min()),
        step=1
    )

    filtered_monthly_data = monthly_combined_melted[
        monthly_combined_melted['month'] == selected_month
    ]

    fig_monthly_scatter = px.scatter(
        filtered_monthly_data,
        x='Product',
        y='Demand',
        size='Profit',
        color='Product',
        title=f'Monthly Demand vs Profit – Month {selected_month} (2025)',
        labels={
            'Demand': 'Total Demand',
            'Profit': 'Total Profit (COP)'
        },
        hover_data={'Product': True, 'Demand': True, 'Profit': True}
    )

    fig_monthly_scatter.update_layout(hovermode="x unified")
    st.plotly_chart(fig_monthly_scatter, use_container_width=True)

# -------------------------
# TAB 2 – Weekly Demand
# -------------------------
with tab2:
    st.subheader("Average Demand by Weekday")
    st.caption("Helps identify peak operational days and optimize staffing and production.")

    fig_weekday = px.bar(
        average_demand_per_weekday_melted,
        x='weekday',
        y='Average Demand',
        color='Product',
        title='Average Product Demand per Weekday',
        labels={
            'weekday': 'Weekday',
            'Average Demand': 'Average Demand Quantity',
            'Product': 'Product'
        },
        barmode='group'
    )

    fig_weekday.update_layout(
        xaxis_title='Weekday',
        yaxis_title='Average Demand'
    )

    st.plotly_chart(fig_weekday, use_container_width=True)

# -------------------------
# TAB 3 – Holiday Impact
# -------------------------
with tab3:
    st.subheader("Holiday Demand Impact")
    st.caption("Evaluates demand changes for selected products during holidays.")

    fig_holiday = px.bar(
        holiday_product_demand_melted,
        x='holiday_name',
        y='Average Demand',
        color='Product',
        title='Average Demand During Holidays (Cerveza & Salchipapa)',
        labels={
            'holiday_name': 'Holiday',
            'Average Demand': 'Average Demand Quantity',
            'Product': 'Product'
        },
        barmode='group'
    )

    fig_holiday.update_layout(
        xaxis_title='Holiday',
        yaxis_title='Average Demand'
    )

    st.plotly_chart(fig_holiday, use_container_width=True)

# -------------------------
# TAB 4 – Cost Distribution
# -------------------------
with tab4:
    st.subheader("Daily Cost Distribution by Product")
    st.caption("Shows variability in daily production costs across products.")

    fig_boxplot = px.box(
        df_costs_melted,
        x='Product Cost',
        y='Daily Cost',
        color='Product Cost',
        title='Distribution of Daily Costs per Product',
        labels={
            'Product Cost': 'Product',
            'Daily Cost': 'Daily Cost (COP)'
        }
    )

    fig_boxplot.update_layout(
        xaxis_title='Product',
        yaxis_title='Daily Cost (COP)'
    )

    st.plotly_chart(fig_boxplot, use_container_width=True)
