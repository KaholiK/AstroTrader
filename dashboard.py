import streamlit as st
import openai
from dotenv import load_dotenv
import os
import pandas as pd
import yfinance as yf
import plotly.express as px
import datetime

# Load environment variables from .env file
load_dotenv()

# Set OpenAI API key from Streamlit Secrets
openai.api_key = st.secrets["CHATGPT_API_KEY"]

# Set Streamlit page configuration
st.set_page_config(page_title="AstroTrader Dashboard", layout="wide")

# Sidebar Configuration
st.sidebar.title("AstroTrader")
st.sidebar.markdown("### Control Panel")

# Select Trading Strategy
strategy = st.sidebar.selectbox(
    "Select Trading Strategy",
    ("Scalping", "Momentum Trading", "Arbitrage", "Trend Following", "Mean Reversion")
)

# Select Market
market = st.sidebar.selectbox(
    "Select Market",
    ("Binance", "Coinbase", "Rithmic", "Tradovate")
)

# Date Range Selection
st.sidebar.markdown("### Date Range")
start_date = st.sidebar.date_input("Start Date", datetime.date(2023, 1, 1))
end_date = st.sidebar.date_input("End Date", datetime.date.today())

# Main Dashboard
st.title("AstroTrader Dashboard")
st.markdown("""
**AstroTrader** is an advanced, multi-strategy trading bot designed to operate across various markets, including Binance, Coinbase, Rithmic, and Tradovate. Leveraging machine learning and AI capabilities, AstroTrader executes trades in real-time, ensuring optimal performance and profitability.
""")

# Features Section
st.header("🚀 Features")
features = [
    "Multiple Trading Strategies: Scalping, Momentum Trading, Arbitrage, Trend Following, Mean Reversion, and more.",
    "Multi-Market Support: Binance, Coinbase, Rithmic, Tradovate.",
    "AI & Machine Learning: Predictive analytics, sentiment analysis, and model training.",
    "Comprehensive Monitoring: Real-time dashboards with Grafana integration and email alerts.",
    "Secure Operations: Encryption of API keys, secure storage, and access controls.",
    "User-Friendly Interface: Streamlit dashboard with an integrated chat interface powered by ChatGPT.",
    "Backtesting Capabilities: Test strategies against historical data using Backtrader."
]
for feature in features:
    st.markdown(f"- {feature}")

# Market Data Visualization
st.header("📈 Market Data")
if market == "Binance":
    ticker = st.text_input("Enter Binance Ticker Symbol (e.g., BTC-USD):", "BTC-USD")
elif market == "Coinbase":
    ticker = st.text_input("Enter Coinbase Ticker Symbol (e.g., ETH-USD):", "ETH-USD")
elif market == "Rithmic":
    ticker = st.text_input("Enter Rithmic Ticker Symbol:", "AAPL")
elif market == "Tradovate":
    ticker = st.text_input("Enter Tradovate Ticker Symbol:", "GOOGL")

# Fetch Data
def fetch_data(ticker, start, end):
    data = yf.download(ticker, start=start, end=end)
    return data

data_load_state = st.text("Loading data...")
data = fetch_data(ticker, start_date, end_date)
data_load_state.text("Loading data...done!")

if not data.empty:
    st.subheader(f"Price Chart for {ticker}")
    fig = px.line(data, x=data.index, y='Close', title=f"{ticker} Closing Prices")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.error("No data available for the selected ticker and date range.")

# Chat Interface
st.header("💬 Chat with AstroTrader")
user_input = st.text_input("You:", "")
if st.button("Send"):
    if user_input:
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are AstroTrader, an advanced trading bot."},
                    {"role": "user", "content": user_input}
                ]
            )
            bot_response = response.choices[0].message['content']
            st.text_area("AstroTrader:", value=bot_response, height=200)
        except Exception as e:
            st.error(f"Error: {e}")
