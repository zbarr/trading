#!/home/zbarr/trading/trading/bin/python

import math
import logging
from itertools import product
from alpaca_trade_api.rest import REST, TimeFrame, TimeFrameUnit

logger = logging.getLogger()
logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)

BASE_URL='https://paper-api.alpaca.markets'
KEY_ID='PKXK736QCHE6JS8AVF6Y'
SECRET_KEY='e2b3xYlhmtdk6SpD8sMdVEdMEiAoxzVlYLUS8pM7'

# class BackTester:
#     def __init__(self, start, end, symbol, strategy, interval):
#         self.start = start
#         self.end = end
#         self.symbol = symbol
#         self.strategy = strategy
#         self.interval = interval
    
#     def get_bars():


#     def run():



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
    
    def get_bars(self, symbol, start, end, interval):
        if interval >= 60:
            timeframe = TimeFrame(
                math.floor(interval / 60),
                TimeFrameUnit.Hour
            )
        else:
            timeframe = TimeFrame(
                interval,
                TimeFrameUnit.Minute
            )
        bars = self.alpaca.get_bars(
            symbol,
            timeframe,
            start,
            end
        )
        return bars.df
    
    def backtest(self, strategy, start, end, symbol, interval):
        bars = self.get_bars(symbol, start, end, interval)
        wins = list()
        losses = list()
        pnl = 0
        for time, bar in bars.iterrows():
            buy = strategy.process_bar(bar)
            if buy:
                diff = bar.close - bar.open
                pnl += diff
                if diff > 0:
                    wins.append(time)
                else:
                    losses.append(time)
        return wins, losses, pnl
    
    @staticmethod
    def gen_params(intervals, strat_params):
        param_list = [intervals] + strat_params
        all_params = product(*param_list)
        return list(all_params)


    def optimize(self, strat, start, end, symbol, intervals, all_strat_params):
        results = []
        param_set = self.gen_params(intervals, all_strat_params)
        for params in param_set:
            strat_params = params[1:]
            interval = params[0]
            print(f"Strat params: {strat_params}")
            strategy = strat(*strat_params)
            print(f"Interval: {interval}")
            w, l, pnl = self.backtest(strategy, start, end, symbol, params[0])
            print(len(w))
            print(len(l))
            print(pnl)
            print()
            results.append((w, l, pnl))
        return results


class MomentumLong:
    def __init__(self, greens):
        self.greens = greens
        self.streak = 0
    
    def process_bar(self, bar):
        if self.streak == self.greens:
            self.streak = 0
            return True
        else:
            if bar.close > bar.open:
                # print('green')
                self.streak += 1
            else:
                self.streak = 0
        

def test_momentum_long(start, end, symbol, intervals, greens):
    tm = TradeManager(
        BASE_URL,
        KEY_ID,
        SECRET_KEY
    )
    tm.get_account_status()
    # ml = MomentumLong(greens)
    # wins, losses, pnl = tm.backtest(ml, start, end, symbol, interval)
    # print(wins)
    # print(losses)
    # print(pnl)
    results = tm.optimize(
        MomentumLong,
        start,
        end,
        symbol,
        intervals,
        [greens]
    )

if __name__ == '__main__':
    test_momentum_long(
        '2022-05-02',
        '2022-08-19',
        'AMD',
        [1, 2, 3, 4, 5],
        [6, 7, 8]
    )