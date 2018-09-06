from market_simulator.models import DailySymbolData

import datetime


def get_num_trading_sessions(date_start, date_end, symbol, market_data_source):
    num_sessions = 0
    curr_date = date_end - datetime.timedelta(days=1)
    while curr_date >= date_start:
        if DailySymbolData.objects.filter(symbol=symbol,
                                          data_souce=market_data_source,
                                          date=curr_date).exists():
            num_sessions += 1
        curr_date = curr_date - datetime.timedelta(days=1)
    return num_sessions


class Indicators(object):

    def sma(self, data, window):
        if len(data) < window:
            return None
        return sum(data[-window:]) / float(window)

    def ema(self, data, window, position=None, previous_ema=None):
        if len(data) < 2 * window:
            raise ValueError("data is too short")
        c = 2.0 / (window + 1)
        current_ema = self.sma(data[-(window * 2):-window], window)
        for value in data[-window:]:
            current_ema = (c * value) + ((1 - c) * current_ema)
        return current_ema


class ApplyIndicators(object):

    def get_ema(self, symbol, data_source, date, window):
        all_dsds = []
        dsd = DailySymbolData.objects.filter(symbol__symbol_code=symbol,
                                             data_souce__market_data_source_code=data_source,
                                             date=date)
        if dsd.exists():
            dsd = dsd.first()
            all_dsds = dsd.get_all_dsds_for_last_x_days(window*2)
            if all_dsds:
                data_points = [some_dsd.close_price for some_dsd in all_dsds]
                indicators = Indicators()
                ema = indicators.ema(data_points, window)
                return ema
        return None

    def get_macd_ema(self, macd_line):
        indicators = Indicators()
        ema = indicators.ema(macd_line, 9)
        return ema
