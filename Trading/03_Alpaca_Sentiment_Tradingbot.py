###Alpaca paper trading

import os
from datetime import datetime

from alpaca_trade_api import REST
from dotenv import load_dotenv

#Framework for backtesting
from lumibot.backtesting import YahooDataBacktesting

# Our broker
from lumibot.brokers import Alpaca

# Our trading bot
from lumibot.strategies.strategy import Strategy

# Deployment capability
from lumibot.traders import Trader
from timedelta import Timedelta

# Sentiment model
from Finbert_Utils import estimate_sentiment

load_dotenv()

API_KEY = os.getenv("ALPACA_API_KEY")
API_SECRET = os.getenv("ALPACA_API_SECRET")
BASE_URL = "https://paper-api.alpaca.markets"

ALPACA_CREDS = {
    "API_KEY": API_KEY,
    "API_SECRET": API_SECRET,
    "PAPER": True
}

class MLTrader(Strategy): 
    def initialize(self,
                   symbol:str="SPY",
                   cash_at_risk:float=.5): 
        self.symbol = symbol
        self.sleeptime = "24H" 
        self.last_trade = None 
        self.cash_at_risk = cash_at_risk
        self.api = REST(base_url=BASE_URL,
                        key_id=API_KEY,
                        secret_key=API_SECRET)

    def position_sizing(self): 
        cash = self.get_cash() 
        last_price = self.get_last_price(self.symbol)
        quantity = round(cash * self.cash_at_risk / last_price,0)
        return cash, last_price, quantity

    def get_dates(self): 
        today = self.get_datetime()
        three_days_prior = today - Timedelta(days=3)
        return today.strftime('%Y-%m-%d'), three_days_prior.strftime('%Y-%m-%d')

    def get_sentiment(self): 
        today, three_days_prior = self.get_dates()
        news = self.api.get_news(symbol=self.symbol, 
                                 start=three_days_prior, 
                                 end=today) 
        news = [ev.__dict__["_raw"]["headline"] for ev in news]
        probability, sentiment = estimate_sentiment(news)
        return probability, sentiment 

    def on_trading_iteration(self):
        cash, last_price, quantity = self.position_sizing() 
        probability, sentiment = self.get_sentiment()

        if cash > last_price: 
            if sentiment == "positive" and probability > .999: 
                # Remove all existing sells
                if self.last_trade == "sell": 
                    self.sell_all()
                # Place a buy order
                order = self.create_order(
                    self.symbol, 
                    quantity, 
                    "buy", 
                    type="bracket", 
                    take_profit_price=last_price*1.20, 
                    stop_loss_price=last_price*.95
                )
                self.submit_order(order) 
                self.last_trade = "buy"
            elif sentiment == "negative" and probability > .999:
                # Remove all existing buys 
                if self.last_trade == "buy": 
                    self.sell_all()
                # Place a sell order 
                order = self.create_order(
                    self.symbol, 
                    quantity, 
                    "sell", 
                    type="bracket", 
                    take_profit_price=last_price*.8, 
                    stop_loss_price=last_price*1.05
                )
                self.submit_order(order) 
                self.last_trade = "sell"

start_date = datetime(2023,10,1)
end_date = datetime(2024,1,31) 
broker = Alpaca(ALPACA_CREDS) 
strategy = MLTrader(name='mlstrat',
                    broker=broker, 
                    parameters={"symbol":"SPY", 
                                "cash_at_risk":.5})
strategy.backtest(
    YahooDataBacktesting, 
    start_date, 
    end_date, 
    parameters={"symbol":"SPY",
                "cash_at_risk":.5}
)
# trader = Trader()
# trader.add_strategy(strategy)
# trader.run_all()
# To go live, uncomment and remove the back testing


### run - python 03_Alpaca_Sentiment_Tradingbot.py