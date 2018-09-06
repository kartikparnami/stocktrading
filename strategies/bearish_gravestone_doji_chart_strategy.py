import datetime

from market_simulator.models  import DailySymbolData
from strategies.utils         import get_num_trading_sessions
from strategies.base_strategy import BaseStrategy


class BearishGravestoneDojiChartStrategy(BaseStrategy):

    def is_bearish_gravestone_doji(self, symbol_data):
        body_size = symbol_data.body_size()
        low_wick_size = symbol_data.low_wick_size()
        ohlc_size = symbol_data.ohlc_size()

        # Wick size check
        if (low_wick_size < (0.02 * ohlc_size)):
            self.confidence_metrics['low_wick_size'] = 1
        elif (low_wick_size >= (0.02 * ohlc_size)) and (low_wick_size < (0.04 * ohlc_size)):
            self.confidence_metrics['low_wick_size'] = 0.9
        elif (low_wick_size >= (0.04 * ohlc_size)) and (low_wick_size < (0.06 * ohlc_size)):
            self.confidence_metrics['low_wick_size'] = 0.8
        elif (low_wick_size >= (0.06 * ohlc_size)) and (low_wick_size < (0.09 * ohlc_size)):
            self.confidence_metrics['low_wick_size'] = 0.7
        elif (low_wick_size >= (0.09 * ohlc_size)) and (low_wick_size < (0.12 * ohlc_size)):
            self.confidence_metrics['low_wick_size'] = 0.5
        elif (low_wick_size >= (0.12 * ohlc_size)) and (low_wick_size < (0.15 * ohlc_size)):
            self.confidence_metrics['low_wick_size'] = 0.3
        else:
            self.confidence_metrics['low_wick_size'] = 0
            return False

        # Body size check
        if (body_size < (0.02 * ohlc_size)):
            self.confidence_metrics['body_size'] = 1
        elif (body_size >= (0.02 * ohlc_size)) and (body_size < (0.04 * ohlc_size)):
            self.confidence_metrics['body_size'] = 0.9
        elif (body_size >= (0.04 * ohlc_size)) and (body_size < (0.06 * ohlc_size)):
            self.confidence_metrics['body_size'] = 0.8
        elif (body_size >= (0.06 * ohlc_size)) and (body_size < (0.09 * ohlc_size)):
            self.confidence_metrics['body_size'] = 0.7
        elif (body_size >= (0.09 * ohlc_size)) and (body_size < (0.12 * ohlc_size)):
            self.confidence_metrics['body_size'] = 0.5
        elif (body_size >= (0.12 * ohlc_size)) and (body_size < (0.15 * ohlc_size)):
            self.confidence_metrics['body_size'] = 0.3
        else:
            self.confidence_metrics['body_size'] = 0
            return False

        self.extra_info['stoploss'] = symbol_data.high_price

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
            is_bearish_gravestone_doji = self.is_bearish_gravestone_doji(symbol_data)
            day_difference = get_num_trading_sessions(date_start, date_end, symbol, market_data_source)
            if day_difference > 0:
                is_previously_upward = symbol_data.is_previously_upward_trend(
                    num_days=day_difference,
                    percent_upward=60
                )
            else:
                is_previously_upward = True
            if is_bearish_gravestone_doji and is_previously_upward and self.is_symbol_data_tradeable(symbol_data):
                return (True, self.confidence_metrics, self.extra_info)
            else:
                return (False, self.confidence_metrics, self.extra_info)
        else:
            return (False, self.confidence_metrics, self.extra_info)
