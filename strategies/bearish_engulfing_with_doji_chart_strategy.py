import datetime

from market_simulator.models  import DailySymbolData
from strategies.utils         import get_num_trading_sessions
from strategies.base_strategy import BaseStrategy


class BearishEngulfingWithDojiChartStrategy(BaseStrategy):

    def is_bearish_engulfing(self, symbol_data):
        # Check last body is bullish
        last_dsd = symbol_data.get_dsd_x_days_back(1)
        if not last_dsd.is_bullish_body():
            self.confidence_metrics['last_body'] = 0
            return False
        else:
            self.confidence_metrics['last_body'] = 1

        # Check if current body is bearish
        if not symbol_data.is_bearish_body():
            self.confidence_metrics['current_body_trend'] = 0
            return False
        else:
            self.confidence_metrics['current_body_trend'] = 1

        if (last_dsd.high_price <= symbol_data.start_price) and (last_dsd.low_price >= symbol_data.close_price):
            self.confidence_metrics['engulfing'] = 1
        else:
            # Check if current body is engulfing
            if (last_dsd.close_price <= symbol_data.start_price) and (last_dsd.start_price >= symbol_data.close_price):
                self.confidence_metrics['engulfing'] = 0.8
            else:
                self.confidence_metrics['engulfing'] = 0
                return False

        self.extra_info['stoploss'] = max(last_dsd.high_price, symbol_data.high_price)

        return True

    def is_doji(self, symbol_data):
        body_size = symbol_data.body_size()
        low_wick_size = symbol_data.low_wick_size()
        high_wick_size = symbol_data.high_wick_size()
        ohlc_size = symbol_data.ohlc_size()

        # Wick size check
        if (low_wick_size >= (0.9 * high_wick_size)) and (low_wick_size <= (1.11 * high_wick_size)):
            self.confidence_metrics['doji_wick_size'] = 1
        elif (low_wick_size >= (0.8 * high_wick_size)) and (low_wick_size <= (1.25 * high_wick_size)):
            self.confidence_metrics['doji_wick_size'] = 0.9
        elif (low_wick_size >= (0.7 * high_wick_size)) and (low_wick_size <= (1.42 * high_wick_size)):
            self.confidence_metrics['doji_wick_size'] = 0.8
        elif (low_wick_size >= (0.6 * high_wick_size)) and (low_wick_size <= (1.67 * high_wick_size)):
            self.confidence_metrics['doji_wick_size'] = 0.7
        elif (low_wick_size >= (0.5 * high_wick_size)) and (low_wick_size <= (2 * high_wick_size)):
            self.confidence_metrics['doji_wick_size'] = 0.5
        elif (low_wick_size >= (0.4 * high_wick_size)) and (low_wick_size <= (2.5 * high_wick_size)):
            self.confidence_metrics['doji_wick_size'] = 0.3
        else:
            self.confidence_metrics['doji_wick_size'] = 0
            return False

        # Body size check
        if (body_size <= (0.02 * ohlc_size)):
            self.confidence_metrics['doji_body_size'] = 1
        if (body_size <= (0.05 * ohlc_size)) and (body_size > (0.02 * ohlc_size)):
            self.confidence_metrics['doji_body_size'] = 1
        if (body_size <= (0.075 * ohlc_size)) and (body_size > (0.05 * ohlc_size)):
            self.confidence_metrics['doji_body_size'] = 0.8
        if (body_size <= (0.1 * ohlc_size)) and (body_size > (0.075 * ohlc_size)):
            self.confidence_metrics['doji_body_size'] = 0.6
        if (body_size <= (0.125 * ohlc_size)) and (body_size > (0.1 * ohlc_size)):
            self.confidence_metrics['doji_body_size'] = 0.4
        if (body_size <= (0.15 * ohlc_size)) and (body_size > (0.125 * ohlc_size)):
            self.confidence_metrics['doji_body_size'] = 0.2
        if body_size > (0.15 * ohlc_size):
            self.confidence_metrics['doji_body_size'] = 0
            return False

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
            is_last_day_bearish_engulfing = self.is_bearish_engulfing(
                symbol_data.get_dsd_x_days_back(1)
            )
            is_current_day_doji = self.is_doji(symbol_data)
            day_difference = get_num_trading_sessions(date_start, date_end, symbol, market_data_source)
            if day_difference > 0:
                is_previously_upward = symbol_data.is_previously_upward_trend(
                    num_days=day_difference,
                    percent_upward=60
                )
            else:
                is_previously_upward = True
            if is_last_day_bearish_engulfing and is_current_day_doji and is_previously_upward and self.is_symbol_data_tradeable(symbol_data):
                return (True, self.confidence_metrics, self.extra_info)
            else:
                return (False, self.confidence_metrics, self.extra_info)
        else:
            return (False, self.confidence_metrics, self.extra_info)
