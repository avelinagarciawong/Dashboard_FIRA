import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(
    page_title="FIRA Financial Dashboard",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(
    """
    <style>
    .main {
        background-color: #0E1117;
    }

    .title-style {
        font-size: 40px;
        font-weight: bold;
        color: #00E5A8;
    }

    .subtitle-style {
        font-size: 18px;
        color: #B0B0B0;
    }

    .metric-card {
        background-color: #161B22;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #30363D;
        text-align: center;
    }

    .sidebar .sidebar-content {
        background-color: #161B22;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# HEADER
st.markdown('<div class="title-style">💸 FIRA (Financial Insight & Resource Assistant) Smart Financial Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle-style">CC26-PSU056 — Financial Insight & Risk Analysis Dashboard</div>', unsafe_allow_html=True)
st.markdown("---")

# LOAD DATA
@st.cache_data

def load_data():
    df = pd.read_csv("smart_spending_dataset.csv")
    df['record_date'] = pd.to_datetime(df['record_date'])
    df['age_group'] = pd.cut(
        df['age'],
        bins=[18,25,35,45,55,70],
        labels=['18-25','26-35','36-45','46-55','56-70']
    )

    return df

df = load_data()


# SIDEBAR FILTERS
st.sidebar.title("⚙️ Dashboard Filters")

# DATE FILTER
min_date = df['record_date'].min()
max_date = df['record_date'].max()

selected_date = st.sidebar.date_input(
    "Select Date Range",
    [min_date, max_date],
    min_value=min_date,
    max_value=max_date
)

# REGION FILTER
regions = st.sidebar.multiselect(
    "Select Region",
    options=df['region'].unique(),
    default=df['region'].unique()
)

# LOAN FILTER
loan_filter = st.sidebar.multiselect(
    "Loan Type",
    options=df['loan_type'].dropna().unique(),
    default=df['loan_type'].dropna().unique()
)

# SPENDING CATEGORY FILTER
spending_filter = st.sidebar.multiselect(
    "Spending Category",
    options=df['spending_category'].unique(),
    default=df['spending_category'].unique()
)


# FILTER DATAFRAME
filtered_df = df[
    (df['record_date'] >= pd.to_datetime(selected_date[0])) &
    (df['record_date'] <= pd.to_datetime(selected_date[1])) &
    (df['region'].isin(regions)) &
    (df['loan_type'].isin(loan_filter)) &
    (df['spending_category'].isin(spending_filter))
]

# KPI SECTION
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="👥 Total Users",
        value=f"{filtered_df.shape[0]:,}"
    )

with col2:
    st.metric(
        label="💵 Avg Income",
        value=f"${filtered_df['monthly_income_usd'].mean():,.2f}"
    )

with col3:
    st.metric(
        label="💳 Avg Credit Score",
        value=f"{filtered_df['credit_score'].mean():.0f}"
    )

with col4:
    st.metric(
        label="🏦 Avg EMI",
        value=f"${filtered_df['monthly_emi_usd'].mean():,.2f}"
    )

st.markdown("---")


# QUESTION 1
st.subheader("1️⃣ Loan Type Analysis & Monthly EMI Impact")

loan_count = filtered_df['loan_type'].value_counts().reset_index()
loan_count.columns = ['loan_type', 'count']

loan_analysis = filtered_df.groupby('loan_type')['monthly_emi_usd'].mean().reset_index()

colA, colB = st.columns(2)
with colA:
    fig1 = px.bar(
        loan_count,
        x='loan_type',
        y='count',
        color='loan_type',
        title='Most Common Loan Types',
        text_auto=True
    )

    fig1.update_layout(
        xaxis_title='Loan Type',
        yaxis_title='Total Users',
        height=500
    )

    st.plotly_chart(fig1, use_container_width=True)

with colB:
    fig2 = px.bar(
        loan_analysis,
        x='loan_type',
        y='monthly_emi_usd',
        color='loan_type',
        title='Average Monthly EMI by Loan Type',
        text_auto='.2f'
    )

    fig2.update_layout(
        xaxis_title='Loan Type',
        yaxis_title='Average EMI (USD)',
        height=500
    )

    st.plotly_chart(fig2, use_container_width=True)


# QUESTION 2
st.subheader("2️⃣ Age Group with Highest Monthly Expenses")

age_expense = filtered_df.groupby('age_group')['monthly_expenses_usd'].mean().reset_index()

fig3 = px.bar(
    age_expense,
    x='age_group',
    y='monthly_expenses_usd',
    color='monthly_expenses_usd',
    title='Average Monthly Expenses by Age Group',
    text_auto='.2f'
)

fig3.update_layout(
    xaxis_title='Age Group',
    yaxis_title='Average Expenses (USD)',
    height=500
)

st.plotly_chart(fig3, use_container_width=True)


# QUESTION 3
st.subheader("3️⃣ Region with Best Average Credit Score")

region_credit = filtered_df.groupby('region')['credit_score'].mean().reset_index()

fig4 = px.bar(
    region_credit,
    x='region',
    y='credit_score',
    color='credit_score',
    title='Average Credit Score by Region',
    text_auto='.0f'
)

fig4.update_layout(
    xaxis_title='Region',
    yaxis_title='Average Credit Score',
    height=500
)

st.plotly_chart(fig4, use_container_width=True)

st.markdown("---")
st.header("📊 Advanced Financial Analytics")

# Scatter Plot
colX, colY = st.columns(2)

with colX:
    scatter_fig = px.scatter(
        filtered_df,
        x='monthly_income_usd',
        y='monthly_expenses_usd',
        color='spending_category',
        size='credit_score',
        hover_data=['loan_type', 'region'],
        title='Income vs Expenses Analysis'
    )

    scatter_fig.update_layout(height=550)

    st.plotly_chart(scatter_fig, use_container_width=True)

with colY:
    pie_fig = px.pie(
        filtered_df,
        names='spending_category',
        title='Spending Category Distribution'
    )

    pie_fig.update_layout(height=550)

    st.plotly_chart(pie_fig, use_container_width=True)


# TREND ANALYSIS
st.subheader("📈 Financial Trend Analysis")

trend_df = filtered_df.groupby('record_date').agg({
    'monthly_income_usd':'mean',
    'monthly_expenses_usd':'mean',
    'credit_score':'mean'
}).reset_index()

fig5 = make_subplots(specs=[[{"secondary_y": True}]])

fig5.add_trace(
    go.Scatter(
        x=trend_df['record_date'],
        y=trend_df['monthly_income_usd'],
        name='Average Income'
    ),
    secondary_y=False,
)

fig5.add_trace(
    go.Scatter(
        x=trend_df['record_date'],
        y=trend_df['monthly_expenses_usd'],
        name='Average Expenses'
    ),
    secondary_y=False,
)

fig5.add_trace(
    go.Scatter(
        x=trend_df['record_date'],
        y=trend_df['credit_score'],
        name='Average Credit Score'
    ),
    secondary_y=True,
)

fig5.update_layout(
    title='Financial Trends Over Time',
    height=600
)

fig5.update_xaxes(title_text='Date')
fig5.update_yaxes(title_text='Income / Expenses (USD)', secondary_y=False)
fig5.update_yaxes(title_text='Credit Score', secondary_y=True)

st.plotly_chart(fig5, use_container_width=True)


# RAW DATA VIEWER
st.markdown("---")
st.subheader("🗂️ Dataset Preview")

st.dataframe(filtered_df, use_container_width=True)


# DOWNLOAD BUTTON
csv = filtered_df.to_csv(index=False).encode('utf-8')

st.download_button(
    label="⬇️ Download Filtered Dataset",
    data=csv,
    file_name='filtered_fira_dataset.csv',
    mime='text/csv'
)


# FOOTER
st.markdown("---")
st.markdown(
    """
    <center>
    <h4>FIRA — Financial Intelligence & Risk Analysis</h4>
    <p>Developed by Team CC26-PSU056</p>
    </center>
    """,
    unsafe_allow_html=True
)