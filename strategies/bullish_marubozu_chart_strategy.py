import datetime

from market_simulator.models  import DailySymbolData
from strategies.base_strategy import BaseStrategy


class BullishMarubozuChartStrategy(BaseStrategy):

    def is_bullish_marubozu(self, symbol_data):
        body_size = symbol_data.body_size()
        ohlc_size = symbol_data.ohlc_size()

        # Body trend check
        if not symbol_data.is_bullish_body():
            return False

        # Body size check
        if (body_size <= (0.6 * ohlc_size)):
            self.confidence_metrics['body_size'] = 0
            return False
        if (body_size <= (0.7 * ohlc_size)) and (body_size > (0.6 * ohlc_size)):
            self.confidence_metrics['body_size'] = 0.2
        if (body_size <= (0.8 * ohlc_size)) and (body_size > (0.7 * ohlc_size)):
            self.confidence_metrics['body_size'] = 0.6
        if (body_size <= (0.9 * ohlc_size)) and (body_size > (0.8 * ohlc_size)):
            self.confidence_metrics['body_size'] = 0.8
        if (body_size <= (1.0 * ohlc_size)) and (body_size > (0.9 * ohlc_size)):
            self.confidence_metrics['body_size'] = 1.0

        self.extra_info['stoploss'] = symbol_data.low_price

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
            is_bullish_marubozu = self.is_bullish_marubozu(symbol_data)
            if is_bullish_marubozu and self.is_symbol_data_tradeable(symbol_data):
                return (True, self.confidence_metrics, self.extra_info)
            else:
                return (False, self.confidence_metrics, self.extra_info)
        else:
            return (False, self.confidence_metrics, self.extra_info)
