import alpaca_trade_api as tradeapi
import logging
import os
from dotenv import load_dotenv
import pandas as pd
import numpy as np
import yfinance as yf
import ccxt  # For cryptocurrency exchanges

# Configure Logging
logging.basicConfig(
    filename='astrotader_bot.log',
    level=logging.INFO,
    format='%(asctime)s:%(levelname)s:%(message)s'
)

# Load environment variables
load_dotenv()

# Retrieve Alpaca API Keys
ALPACA_API_KEY = os.getenv("ALPACA_API_KEY")
ALPACA_API_SECRET = os.getenv("ALPACA_API_SECRET")
ALPACA_BASE_URL = 'https://paper-api.alpaca.markets'

# Initialize Alpaca Client
alpaca = tradeapi.REST(
    ALPACA_API_KEY,
    ALPACA_API_SECRET,
    ALPACA_BASE_URL,
    api_version='v2'
)

class AstroTraderBot:
    def __init__(self, ticker, strategy):
        self.ticker = ticker
        self.strategy = strategy
        self.data = None
        self.position = 0  # 1 for long, -1 for short, 0 for no position

    def fetch_historical_data(self, period='1y', interval='1d'):
        try:
            logging.info(f"Fetching historical data for {self.ticker}")
            self.data = yf.download(self.ticker, period=period, interval=interval)
            logging.info("Historical data fetched successfully.")
        except Exception as e:
            logging.error(f"Error fetching historical data: {e}")

    def calculate_indicators(self):
        if self.data is None:
            logging.error("No data to calculate indicators.")
            return

        logging.info("Calculating technical indicators.")
        self.data['SMA_50'] = self.data['Close'].rolling(window=50).mean()
        self.data['SMA_200'] = self.data['Close'].rolling(window=200).mean()
        self.data['RSI'] = self.calculate_rsi()
        logging.info("Technical indicators calculated.")

    def calculate_rsi(self, periods=14):
        delta = self.data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=periods).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=periods).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def generate_signals(self):
        if self.data is None:
            logging.error("No data to generate signals.")
            return

        logging.info("Generating trading signals based on strategy.")
        if self.strategy.lower() == 'sma_crossover':
            self.data['Signal'] = 0
            self.data.loc[self.data['SMA_50'] > self.data['SMA_200'], 'Signal'] = 1
            self.data.loc[self.data['SMA_50'] < self.data['SMA_200'], 'Signal'] = -1
        elif self.strategy.lower() == 'rsi_strategy':
            self.data['Signal'] = 0
            self.data.loc[self.data['RSI'] < 30, 'Signal'] = 1
            self.data.loc[self.data['RSI'] > 70, 'Signal'] = -1
        else:
            logging.error(f"Unsupported strategy: {self.strategy}")
            raise ValueError(f"Unsupported strategy: {self.strategy}")
        
        logging.info("Trading signals generated.")

    def backtest_strategy(self):
        if self.data is None or 'Signal' not in self.data.columns:
            logging.error("No signals to backtest.")
            return

        logging.info("Starting backtest.")
        self.data['Daily_Return'] = self.data['Close'].pct_change()
        self.data['Strategy_Return'] = self.data['Daily_Return'] * self.data['Signal'].shift(1)
        self.data['Cumulative_Market_Return'] = (1 + self.data['Daily_Return']).cumprod() - 1
        self.data['Cumulative_Strategy_Return'] = (1 + self.data['Strategy_Return']).cumprod() - 1
        logging.info("Backtest completed.")

        return self.data[['Cumulative_Market_Return', 'Cumulative_Strategy_Return']]

    def execute_trade(self, side, qty):
        try:
            order = alpaca.submit_order(
                symbol=self.ticker,
                qty=qty,
                side=side,
                type='market',
                time_in_force='gtc'
            )
            logging.info(f"{side.capitalize()} order placed: {order}")
            return order
        except Exception as e:
            logging.error(f"Error placing {side} order: {e}")
            return None

    def run(self):
        logging.info("AstroTrader Bot is starting.")
        self.fetch_historical_data()
        self.calculate_indicators()
        self.generate_signals()
        # Example: Backtest the strategy
        backtest_results = self.backtest_strategy()
        if backtest_results is not None:
            logging.info(backtest_results.tail())
        logging.info("AstroTrader Bot run completed.")

if __name__ == "__main__":
    # Example usage
    ticker = "AAPL"  # Example stock ticker
    strategy = "sma_crossover"  # Options: sma_crossover, rsi_strategy

    bot = AstroTraderBot(ticker, strategy)
    bot.run()
