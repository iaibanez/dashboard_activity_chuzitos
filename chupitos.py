import streamlit as st
import plotly.express as px
import pandas as pd

# 1. Load the dataset
df = pd.read_csv("restaurante_baq_demanda_500_dias_2025_2026.csv")

# 2. Convert 'date' column to datetime objects
df['date'] = pd.to_datetime(df['date'])

# 3. Define product_columns, costs, and selling_prices
product_columns = ['Perros calientes', 'Pizza', 'Hamburguesa', 'Salchipapa', 'Chuzo Desgranado', 'Asados', 'Coca cola', 'Limonada', 'Cerveza']

costs = {
    'Perros calientes': 6000,
    'Pizza': 10000,
    'Hamburguesa': 17000,
    'Salchipapa': 12000,
    'Chuzo Desgranado': 9000,
    'Asados': 8000,
    'Coca_cola': 1500,
    'Limonada': 5000,
    'Cerveza': 1500
}

selling_prices = {
    'Perros calientes': 15000,
    'Pizza': 20000,
    'Hamburguesa': 25000,
    'Salchipapa': 17000,
    'Chuzo Desgranado': 15000,
    'Asados': 15000,
    'Coca cola': 6000,
    'Limonada': 10000,
    'Cerveza': 4000
}

# 4. Calculate profit for each product and total daily profit
for product in product_columns:
    df[f'{product}_ganancia'] = (selling_prices[product] - costs[product]) * df[product]
df['ganancia'] = df[[f'{product}_ganancia' for product in product_columns]].sum(axis=1)

# 5. Apply all holiday name adjustments
df['holiday_name'] = df['holiday_name'].str.replace('Corpus Christi', 'Carnavales')
df['holiday_name'] = df['holiday_name'].replace(['Jueves Santo', 'Viernes Santo', 'Todos los Santos'], 'Semana Santa')
df['holiday_name'] = df['holiday_name'].replace('Asunción', 'Carnavales')

# 6. Calculate total_demand
df['total_demand'] = df[product_columns].sum(axis=1)

# 7. Define weekday_order and convert 'weekday' column to categorical
weekday_order = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
df['weekday'] = pd.Categorical(df['weekday'], categories=weekday_order, ordered=True)

# 8. Calculate average_demand_per_weekday and melt for plotting
average_demand_per_weekday = df.groupby('weekday', observed=False)[product_columns].mean().reset_index()
average_demand_per_weekday_melted = average_demand_per_weekday.melt(id_vars='weekday', var_name='Product', value_name='Average Demand')

# 9. Calculate holiday_demand (excluding 'Ninguno')
holiday_demand = df[df['holiday_name'] != 'Ninguno'].groupby('holiday_name')['total_demand'].mean().reset_index()

# 10. Define specific_products
specific_products = ['Cerveza', 'Salchipapa']

# 11. Calculate holiday_product_demand and melt for plotting
holiday_product_demand = df[df['holiday_name'] != 'Ninguno'].groupby('holiday_name')[specific_products].mean().reset_index()
holiday_product_demand_melted = holiday_product_demand.melt(id_vars='holiday_name', var_name='Product', value_name='Average Demand')

# 12. Calculate overall_average_demand (not directly used in plots, but for completeness)
overall_average_demand = df[specific_products].mean()

# 13. Calculate daily costs for each product and melt for box plot
cost_columns = []
for product in product_columns:
    df[f'{product}_costo_diario'] = costs[product] * df[product]
    cost_columns.append(f'{product}_costo_diario') # Corrected: Removed extra '_costo'
df_costs_melted = df.melt(id_vars=['date'], value_vars=cost_columns, var_name='Product Cost', value_name='Daily Cost')
df_costs_melted['Product Cost'] = df_costs_melted['Product Cost'].map(product_columns)

# -------------------------
# DATA PREPARATION
# -------------------------

df_2025 = df[df['date'].dt.year == 2025].copy()
df_2025['month'] = df_2025['date'].dt.month

product_profit_columns = [f'{p}_ganancia' for p in product_columns]

monthly_aggregated_data_detailed = df_2025.groupby('month')[product_columns + product_profit_columns].sum().reset_index()

monthly_demand_melted = monthly_aggregated_data_detailed.melt(
    id_vars='month',
    value_vars=product_columns,
    var_name='Product',
    value_name='Demand'
)

monthly_profit_melted = monthly_aggregated_data_detailed.melt(
    id_vars='month',
    value_vars=product_profit_columns,
    var_name='Product_Profit_Col',
    value_name='Profit'
)

monthly_profit_melted['Product'] = monthly_profit_melted['Product_Profit_Col'].str.replace('_ganancia', '')

monthly_combined_melted = pd.merge(
    monthly_demand_melted,
    monthly_profit_melted[['month', 'Product', 'Profit']],
    on=['month', 'Product']
)

# -------------------------
# Page Configuration
# -------------------------
st.set_page_config(page_title="Restaurant Demand Dashboard", layout="wide")

# Logo
st.image("chuzitos-logo-ok.png", width=150)

st.title("Chuzitos Demand & Cost Analysis Dashboard")

st.markdown("""
This dashboard analyzes **500 days of demand data** from **The Best** international fast-food restaurant in the world.
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
    "📈 Monthly Performance",
    "📅 Weekly Demand",
    "🎉 Holiday Impact",
    "💰 Cost Analysis"
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
