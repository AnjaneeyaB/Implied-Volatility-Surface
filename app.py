# app.py
import streamlit as st
import pandas as pd
from datetime import date

from utils import impliedVolatilitySurface  # your existing function

st.set_page_config(
    page_title="Implied Volatility Surface",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.sidebar.title("Model Parameters")

# Numeric inputs
risk_free_rate = st.sidebar.number_input(
    "Risk-free rate",
    min_value=0.0,
    max_value=1.0,
    value=0.05,
    step=0.005,
    format="%.4f"
)

dividend_yield = st.sidebar.number_input(
    "Dividend yield",
    min_value=0.0,
    max_value=1.0,
    value=0.03,
    step=0.005,
    format="%.4f"
)

st.sidebar.divider()
st.sidebar.subheader("Date Range for selecting Options from Option Chain")

MIN_DATE = date(2019, 1, 4)
MAX_DATE = date(2025, 1, 17)

start_date = st.sidebar.date_input(
    "Start date",
    value=date(2022, 10, 1),
    min_value=MIN_DATE,
    max_value=MAX_DATE
)

end_date = st.sidebar.date_input(
    "End date",
    value=date(2022, 12, 31),
    min_value=MIN_DATE,
    max_value=MAX_DATE
)

# Validation
dates_valid = start_date <= end_date
if not dates_valid:
    st.sidebar.error("Start date must be earlier than or equal to end date.")

st.title("Implied Volatility Surface")
st.write("Generated using AAPL Option Chain from 2019-01-04 - 2025-01-17")

# Convert to pandas.Timestamp and plot
if dates_valid:
    with st.spinner("Generating implied volatility surface..."):
        fig = impliedVolatilitySurface(
            start_date=pd.Timestamp(start_date),
            end_date=pd.Timestamp(end_date),
            risk_free_rate=risk_free_rate,
            dividend_yield=dividend_yield
        )

    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Please correct the date range to generate the surface.")
