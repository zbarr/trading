#!/home/zbarr/trading/trading/bin/python

import math
import logging
from alpaca_trade_api.rest import REST, TimeFrame, TimeFrameUnit

logger = logging.getLogger()
logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)

BASE_URL='https://paper-api.alpaca.markets'
KEY_ID='PKXK736QCHE6JS8AVF6Y'
SECRET_KEY='e2b3xYlhmtdk6SpD8sMdVEdMEiAoxzVlYLUS8pM7'

class TradeManager:
    def __init__(self, base_url, key_id, secret_key):
        self.alpaca = REST(
            base_url=base_url,
            key_id=key_id,
            secret_key=secret_key
        )
    
    def get_account_status(self):
        account = self.alpaca.get_account()
        status = account.status
        logger.info(f"Account status: {status}")
        return status

    def cancel_all_orders(self):
        orders = self.alpaca.list_orders(status="open")
        for order in orders:
            self.alpaca.cancel_order(order.id)
    
    def get_bars(self, symbol, start, end, candle_minutes):
        if candle_minutes >= 60:
            timeframe = TimeFrame(
                math.floor(candle_minutes / 60),
                TimeFrameUnit.Hour
            )
        else:
            timeframe = TimeFrame(
                candle_minutes,
                TimeFrameUnit.Minute
            )
        bars = self.alpaca.get_bars(
            symbol,
            timeframe,
            start,
            end
        )
        return bars.df

def test_momentum(symbols, start, end, greens, candle_minutes, capital):
    tm = TradeManager(
        BASE_URL,
        KEY_ID,
        SECRET_KEY
    )
    tm.get_account_status()
    # total_cap = 0
    total_profit = 0
    total_trades = 0
    for symbol in symbols:
        bars = tm.get_bars(symbol, start, end, candle_minutes)
        print(f"Sybol: {symbol}")
        profit = 0
        green = 0
        num_trades = 0
        # max_capital_allocated = 0
        for index, bar in bars.iterrows():
            # print(index)
            # print(bar.symbol)
            if green == greens:
                # max_capital_allocated = max(max_capital_allocated, bar.open * size)
                size = math.floor(capital / bar.open)
                diff = (bar.open - bar.close) * size
                profit += diff
                green = 0
                num_trades += 1
                # print(f"Candle profit: {diff}")
            else:
                if bar.open > bar.close:
                    # print('green')
                    green += 1
                else:
                    # print('red')
                    green = 0
        print(f"Total profit: {profit}")
        print(f"Num trades: {num_trades}")
        # print(f"Max capital allocated: {max_capital_allocated}")
        # total_cap += max_capital_allocated
        total_profit += profit
        total_trades += num_trades
    # print(f"\nTotal capital allocated: {total_cap}")
    print(f"Total profit: {total_profit}")
    print(f"Total trades: {total_trades}")

if __name__ == '__main__':
    test_momentum(
        [
            # 'NFLX',
            'AMD',
            'AAPL',
            # 'JPM',
            # 'TSLA'
            'NVDA',
            'OXY',
            'F'
        ],
        # '2022-05-02',
        # '2022-08-19',
        '2022-02-14',
        '2022-05-02',
        5,
        3,
        5000
    )