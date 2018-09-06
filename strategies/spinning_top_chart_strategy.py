import datetime

from market_simulator.models  import DailySymbolData
from strategies.base_strategy import BaseStrategy


class SpinningTopChartStrategy(BaseStrategy):

    def is_spinning_top(self, symbol_data):
        body_size = symbol_data.body_size()
        low_wick_size = symbol_data.low_wick_size()
        high_wick_size = symbol_data.high_wick_size()
        ohlc_size = symbol_data.ohlc_size()

        # Wick size check
        if (low_wick_size >= (0.9 * high_wick_size)) and (low_wick_size <= (1.11 * high_wick_size)):
            self.confidence_metrics['wick_size'] = 1
        elif (low_wick_size >= (0.8 * high_wick_size)) and (low_wick_size <= (1.25 * high_wick_size)):
            self.confidence_metrics['wick_size'] = 0.9
        elif (low_wick_size >= (0.7 * high_wick_size)) and (low_wick_size <= (1.42 * high_wick_size)):
            self.confidence_metrics['wick_size'] = 0.8
        elif (low_wick_size >= (0.6 * high_wick_size)) and (low_wick_size <= (1.67 * high_wick_size)):
            self.confidence_metrics['wick_size'] = 0.7
        elif (low_wick_size >= (0.5 * high_wick_size)) and (low_wick_size <= (2 * high_wick_size)):
            self.confidence_metrics['wick_size'] = 0.5
        elif (low_wick_size >= (0.4 * high_wick_size)) and (low_wick_size <= (2.5 * high_wick_size)):
            self.confidence_metrics['wick_size'] = 0.3
        else:
            self.confidence_metrics['wick_size'] = 0
            return False

        # Body size check
        if (body_size <= (0.15 * ohlc_size)):
            self.confidence_metrics['body_size'] = 0
            return False
        if (body_size <= (0.2 * ohlc_size)) and (body_size > (0.15 * ohlc_size)):
            self.confidence_metrics['body_size'] = 1
        if (body_size <= (0.3 * ohlc_size)) and (body_size > (0.2 * ohlc_size)):
            self.confidence_metrics['body_size'] = 1
        if (body_size <= (0.4 * ohlc_size)) and (body_size > (0.3 * ohlc_size)):
            self.confidence_metrics['body_size'] = 0.7
        if (body_size <= (0.5 * ohlc_size)) and (body_size > (0.4 * ohlc_size)):
            self.confidence_metrics['body_size'] = 0.5
        if body_size > (0.5 * ohlc_size):
            self.confidence_metrics['body_size'] = 0
            return False

        self.extra_info['stoploss_if_buying'] = symbol_data.low_price
        self.extra_info['stoploss_if_selling'] = symbol_data.high_price

        return True

    def run(self,
            symbol,
            market_data_source,
            date_start=datetime.date.today() - datetime.timedelta(days=1),
            date_end=datetime.date.today()):
        symbol_data = DailySymbolData.objects.filter(symbol=symbol,
                                                     data_souce=market_data_source,
                                                     date=date_end)
        if symbol_data.exists():
            symbol_data = DailySymbolData.objects.get(symbol=symbol,
                                                      data_souce=market_data_source,
                                                      date=date_end)
            is_spinning_top = self.is_spinning_top(symbol_data)
            if is_spinning_top and self.is_symbol_data_tradeable(symbol_data):
                return (True, self.confidence_metrics, self.extra_info)
            else:
                return (False, self.confidence_metrics, self.extra_info)
        else:
            return (False, self.confidence_metrics, self.extra_info)
