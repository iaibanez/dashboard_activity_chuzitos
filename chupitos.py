import streamlit as st
import plotly.express as px
import pandas as pd

# 1. Load the dataset
df = pd.read_csv("restaurante_baq_demanda_500_dias_2025_2026.csv")

# 2. Convert 'date' column to datetime objects
df['date'] = pd.to_datetime(df['date'])

# 3. Define product_columns, costs, and selling_prices
product_columns = ['Perros_calientes', 'Pizza', 'Hamburguesa', 'Salchipapa', 'Chuzo_Desgranado', 'Asados', 'Coca_cola', 'Limonada', 'Cerveza']

costs = {
    'Perros_calientes': 6000,
    'Pizza': 10000,
    'Hamburguesa': 17000,
    'Salchipapa': 12000,
    'Chuzo_Desgranado': 9000,
    'Asados': 8000,
    'Coca_cola': 1500,
    'Limonada': 5000,
    'Cerveza': 1500
}

selling_prices = {
    'Perros_calientes': 15000,
    'Pizza': 20000,
    'Hamburguesa': 25000,
    'Salchipapa': 17000,
    'Chuzo_Desgranado': 15000,
    'Asados': 15000,
    'Coca_cola': 6000,
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

# --- New Data Preparation for Monthly Scatter Plot (2025) ---
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

monthly_combined_melted = pd.merge(monthly_demand_melted, monthly_profit_melted[['month', 'Product', 'Profit']], on=['month', 'Product'])

# Streamlit App Title
st.title("Product Demand and Cost Analysis Dashboard")

# --- Plot 1: Monthly Product Demand and Profit Scatter Plot (2025) ---

selected_month = st.slider(
    "Select Month for Product Demand and Profit (2025):",
    min_value=int(monthly_combined_melted['month'].min()),
    max_value=int(monthly_combined_melted['month'].max()),
    value=int(monthly_combined_melted['month'].min()),
    step=1
)

filtered_monthly_data = monthly_combined_melted[monthly_combined_melted['month'] == selected_month]

fig_monthly_scatter = px.scatter(
    filtered_monthly_data,
    x='Product',
    y='Demand',
    size='Profit',
    color='Product',
    title=f'Monthly Product Demand and Profit for Month {selected_month} (2025)',
    labels={'Demand': 'Total Demand', 'Profit': 'Total Profit'},
    color_discrete_sequence=px.colors.qualitative.Plotly,
    hover_data={'Product': True, 'Demand': True, 'Profit': True, 'month': True}
)

fig_monthly_scatter.update_layout(hovermode="x unified")
st.plotly_chart(fig_monthly_scatter, width='stretch')

# --- End Plot 1 ---

# Plot 2: Bar plot of average product demand per weekday
fig_weekday = px.bar(
    average_demand_per_weekday_melted,
    x='weekday',
    y='Average Demand',
    color='Product',
    title='Average Product Demand per Weekday',
    labels={'weekday': 'Weekday', 'Average Demand': 'Average Demand Quantity', 'Product': 'Product Type'},
    barmode='group',
    color_discrete_sequence=px.colors.qualitative.Plotly
)
fig_weekday.update_layout(xaxis_title='Weekday', yaxis_title='Average Demand')
st.plotly_chart(fig_weekday, width='stretch')

# Plot 3: Bar plot of average demand for specific products per holiday
fig_holiday = px.bar(
    holiday_product_demand_melted,
    x='holiday_name',
    y='Average Demand',
    color='Product',
    title='Average Demand for Cerveza and Salchipapa per Holiday',
    labels={'holiday_name': 'Holiday Name', 'Average Demand': 'Average Demand Quantity', 'Product': 'Product Type'},
    barmode='group',
    color_discrete_sequence=px.colors.qualitative.Plotly
)
fig_holiday.update_layout(xaxis_title='Holiday Name', yaxis_title='Average Demand')
st.plotly_chart(fig_holiday, width='stretch')

# Plot 4: Box plot of daily product costs
fig_boxplot = px.box(df_costs_melted, x='Product Cost', y='Daily Cost',
                     color='Product Cost',
                     title='Distribution of Daily Costs per Product',
                     labels={'Product Cost': 'Product', 'Daily Cost': 'Daily Cost Value'},
                     color_discrete_sequence=px.colors.qualitative.Plotly)
fig_boxplot.update_layout(xaxis_title='Product', yaxis_title='Daily Cost')
st.plotly_chart(fig_boxplot, width='stretch')
