# bot.py

import pandas as pd
import yfinance as yf
import numpy as np
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(
    filename='bot.log',
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

class AstroTraderBot:
    """
    AstroTraderBot is an advanced trading bot designed to execute multiple trading strategies
    across various markets, including Binance, Coinbase, Rithmic, and Tradovate.
    """

    def __init__(self, ticker, start_date, end_date):
        """
        Initializes the AstroTraderBot with a specific ticker and date range.

        :param ticker: The ticker symbol for the asset (e.g., 'AAPL', 'BTC-USD').
        :param start_date: The start date for historical data in 'YYYY-MM-DD' format.
        :param end_date: The end date for historical data in 'YYYY-MM-DD' format.
        """
        self.ticker = ticker
        self.start_date = start_date
        self.end_date = end_date
        self.data = None
        self.signals = None

        logging.info(f"Initialized AstroTraderBot for {self.ticker} from {self.start_date} to {self.end_date}")

    def fetch_data(self):
        """
        Fetches historical market data for the specified ticker and date range.

        :return: A pandas DataFrame containing historical OHLCV data.
        """
        try:
            self.data = yf.download(self.ticker, start=self.start_date, end=self.end_date)
            if self.data.empty:
                logging.warning(f"No data fetched for {self.ticker}. Check the ticker symbol and date range.")
            else:
                logging.info(f"Fetched data for {self.ticker}: {self.data.shape[0]} records")
        except Exception as e:
            logging.error(f"Error fetching data for {self.ticker}: {e}")
            raise

    def calculate_indicators(self):
        """
        Calculates technical indicators (SMA and RSI) and adds them to the DataFrame.
        """
        try:
            # Simple Moving Averages
            self.data['SMA_50'] = self.data['Close'].rolling(window=50).mean()
            self.data['SMA_200'] = self.data['Close'].rolling(window=200).mean()
            logging.info("Calculated SMA_50 and SMA_200 indicators")

            # Relative Strength Index
            self.data['RSI'] = self.calculate_rsi(periods=14)
            logging.info("Calculated RSI indicator")
        except Exception as e:
            logging.error(f"Error calculating indicators: {e}")
            raise

    def calculate_rsi(self, periods=14):
        """
        Calculates the Relative Strength Index (RSI) for the data.

        :param periods: The number of periods to use for RSI calculation.
        :return: A pandas Series containing RSI values.
        """
        try:
            delta = self.data['Close'].diff()
            gain = delta.where(delta > 0, 0).rolling(window=periods).mean()
            loss = -delta.where(delta < 0, 0).rolling(window=periods).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return rsi
        except Exception as e:
            logging.error(f"Error calculating RSI: {e}")
            raise

    def generate_signals(self):
        """
        Generates trading signals based on SMA crossover and RSI thresholds.

        :return: A pandas DataFrame containing trading signals.
        """
        try:
            self.signals = pd.DataFrame(index=self.data.index)
            self.signals['Signal'] = 0

            # SMA Crossover Strategy
            self.signals['SMA_Signal'] = 0
            self.signals['SMA_Signal'][self.data['SMA_50'] > self.data['SMA_200']] = 1
            self.signals['SMA_Signal'][self.data['SMA_50'] < self.data['SMA_200']] = -1

            # RSI Strategy
            self.signals['RSI_Signal'] = 0
            self.signals['RSI_Signal'][self.data['RSI'] > 70] = -1  # Overbought
            self.signals['RSI_Signal'][self.data['RSI'] < 30] = 1   # Oversold

            # Combine Signals
            self.signals['Signal'] = self.signals['SMA_Signal'] + self.signals['RSI_Signal']

            # Normalize Signals to ensure they are within -1, 0, 1
            self.signals['Signal'] = self.signals['Signal'].apply(lambda x: 1 if x > 0 else (-1 if x < 0 else 0))

            logging.info("Generated trading signals based on SMA and RSI strategies")
            return self.signals
        except Exception as e:
            logging.error(f"Error generating signals: {e}")
            raise

    def backtest_strategy(self):
        """
        Backtests the trading strategy against historical data.

        :return: A tuple containing cumulative strategy returns and cumulative market returns.
        """
        try:
            # Calculate returns
            self.data['Market_Return'] = self.data['Close'].pct_change()
            self.signals['Strategy_Return'] = self.signals['Signal'].shift(1) * self.data['Market_Return']
            self.signals['Cumulative_Strategy_Return'] = (1 + self.signals['Strategy_Return']).cumprod() - 1
            self.signals['Cumulative_Market_Return'] = (1 + self.data['Market_Return']).cumprod() - 1

            logging.info("Completed backtesting of the trading strategy")

            return self.signals['Cumulative_Strategy_Return'], self.signals['Cumulative_Market_Return']
        except Exception as e:
            logging.error(f"Error during backtesting: {e}")
            raise

    def plot_performance(self, strategy_returns, market_returns):
        """
        Plots the cumulative returns of the strategy versus the market.

        :param strategy_returns: Cumulative returns of the trading strategy.
        :param market_returns: Cumulative returns of the market.
        """
        try:
            import plotly.graph_objects as go

            fig = go.Figure()

            fig.add_trace(go.Scatter(
                x=strategy_returns.index,
                y=strategy_returns.values,
                mode='lines',
                name='Strategy Return'
            ))

            fig.add_trace(go.Scatter(
                x=market_returns.index,
                y=market_returns.values,
                mode='lines',
                name='Market Return'
            ))

            fig.update_layout(
                title=f"Cumulative Returns: {self.ticker}",
                xaxis_title="Date",
                yaxis_title="Cumulative Returns",
                hovermode="x unified"
            )

            fig.show()
            logging.info("Plotted performance graph")
        except Exception as e:
            logging.error(f"Error plotting performance: {e}")
            raise

    def execute_trades(self):
        """
        Executes trades based on the generated signals.
        Placeholder for integrating with broker APIs like Binance, Coinbase, Rithmic, and Tradovate.
        """
        try:
            # Placeholder: Implement API integration for real-time trading
            logging.info("Executing trades based on generated signals")
            pass
        except Exception as e:
            logging.error(f"Error executing trades: {e}")
            raise

if __name__ == "__main__":
    """
    Main execution block for testing the AstroTraderBot.
    """
    try:
        # Define parameters
        ticker = "AAPL"  # Example ticker
        start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')  # Past year
        end_date = datetime.now().strftime('%Y-%m-%d')  # Today

        # Initialize the bot
        bot = AstroTraderBot(ticker, start_date, end_date)

        # Fetch data
        bot.fetch_data()

        if bot.data is not None and not bot.data.empty:
            # Generate signals
            signals = bot.generate_signals()

            # Backtest strategy
            strategy_returns, market_returns = bot.backtest_strategy()

            # Plot performance (this will open in a web browser)
            bot.plot_performance(strategy_returns, market_returns)

            # Execute trades (placeholder)
            bot.execute_trades()

            # Display summary
            final_strategy_return = strategy_returns[-1] * 100
            final_market_return = market_returns[-1] * 100
            print(f"Cumulative Strategy Return: {final_strategy_return:.2f}%")
            print(f"Cumulative Market Return: {final_market_return:.2f}%")
        else:
            print(f"No data available for {ticker}. Please check the ticker symbol and date range.")
    except Exception as e:
        logging.critical(f"Critical error in main execution: {e}")
        print(f"An error occurred: {e}")
