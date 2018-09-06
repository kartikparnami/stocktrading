import datetime


class BaseStrategy(object):

    def __init__(self):
        self.confidence_metrics = dict()
        self.extra_info = dict()
        pass

    def run(self,
            symbol,
            market_source,
            date_start=datetime.datetime.now() - datetime.timedelta(days=1),
            date_end=datetime.date.today()):
        pass

    def is_symbol_data_tradeable(self, symbol_data):
        mid_point = (symbol_data.low_price + symbol_data.high_price) / 2
        if mid_point:
            total_range = (symbol_data.high_price - symbol_data.low_price)
            if (total_range > (0.1 * mid_point)) or (total_range < (0.01 * mid_point)):
                return False
            else:
                return True
        else:
            return False

    def success():
        pass
