import datetime

from market_simulator.models  import DailySymbolData
from strategies.utils         import get_num_trading_sessions
from strategies.base_strategy import BaseStrategy


class MorningStarChartStrategy(BaseStrategy):

    def is_doji(self, symbol_data):
        body_size = symbol_data.body_size()
        low_wick_size = symbol_data.low_wick_size()
        high_wick_size = symbol_data.high_wick_size()
        ohlc_size = symbol_data.ohlc_size()
        metrics = {}

        # Wick size check
        if (low_wick_size >= (0.9 * high_wick_size)) and (low_wick_size <= (1.11 * high_wick_size)):
            metrics['doji_wick_size'] = 1
        elif (low_wick_size >= (0.8 * high_wick_size)) and (low_wick_size <= (1.25 * high_wick_size)):
            metrics['doji_wick_size'] = 0.9
        elif (low_wick_size >= (0.7 * high_wick_size)) and (low_wick_size <= (1.42 * high_wick_size)):
            metrics['doji_wick_size'] = 0.8
        elif (low_wick_size >= (0.6 * high_wick_size)) and (low_wick_size <= (1.67 * high_wick_size)):
            metrics['doji_wick_size'] = 0.7
        elif (low_wick_size >= (0.5 * high_wick_size)) and (low_wick_size <= (2 * high_wick_size)):
            metrics['doji_wick_size'] = 0.5
        elif (low_wick_size >= (0.4 * high_wick_size)) and (low_wick_size <= (2.5 * high_wick_size)):
            metrics['doji_wick_size'] = 0.3
        else:
            metrics['doji_wick_size'] = 0
            return False

        # Body size check
        if (body_size <= (0.02 * ohlc_size)):
            metrics['doji_body_size'] = 1
        if (body_size <= (0.05 * ohlc_size)) and (body_size > (0.02 * ohlc_size)):
            metrics['doji_body_size'] = 1
        if (body_size <= (0.075 * ohlc_size)) and (body_size > (0.05 * ohlc_size)):
            metrics['doji_body_size'] = 0.8
        if (body_size <= (0.1 * ohlc_size)) and (body_size > (0.075 * ohlc_size)):
            metrics['doji_body_size'] = 0.6
        if (body_size <= (0.125 * ohlc_size)) and (body_size > (0.1 * ohlc_size)):
            metrics['doji_body_size'] = 0.4
        if (body_size <= (0.15 * ohlc_size)) and (body_size > (0.125 * ohlc_size)):
            metrics['doji_body_size'] = 0.2
        if body_size > (0.15 * ohlc_size):
            metrics['doji_body_size'] = 0
            return False

        self.confidence_metrics.update(metrics)
        return True

    def is_spinning_top(self, symbol_data):
        body_size = symbol_data.body_size()
        low_wick_size = symbol_data.low_wick_size()
        high_wick_size = symbol_data.high_wick_size()
        ohlc_size = symbol_data.ohlc_size()
        metrics = {}

        # Wick size check
        if (low_wick_size >= (0.9 * high_wick_size)) and (low_wick_size <= (1.11 * high_wick_size)):
            metrics['spinning_top_wick_size'] = 1
        elif (low_wick_size >= (0.8 * high_wick_size)) and (low_wick_size <= (1.25 * high_wick_size)):
            metrics['spinning_top_wick_size'] = 0.9
        elif (low_wick_size >= (0.7 * high_wick_size)) and (low_wick_size <= (1.42 * high_wick_size)):
            metrics['spinning_top_wick_size'] = 0.8
        elif (low_wick_size >= (0.6 * high_wick_size)) and (low_wick_size <= (1.67 * high_wick_size)):
            metrics['spinning_top_wick_size'] = 0.7
        elif (low_wick_size >= (0.5 * high_wick_size)) and (low_wick_size <= (2 * high_wick_size)):
            metrics['spinning_top_wick_size'] = 0.5
        elif (low_wick_size >= (0.4 * high_wick_size)) and (low_wick_size <= (2.5 * high_wick_size)):
            metrics['spinning_top_wick_size'] = 0.3
        else:
            metrics['spinning_top_wick_size'] = 0
            return False

        # Body size check
        if (body_size <= (0.15 * ohlc_size)):
            metrics['spinning_top_body_size'] = 0
            return False
        if (body_size <= (0.2 * ohlc_size)) and (body_size > (0.15 * ohlc_size)):
            metrics['spinning_top_body_size'] = 1
        if (body_size <= (0.3 * ohlc_size)) and (body_size > (0.2 * ohlc_size)):
            metrics['spinning_top_body_size'] = 1
        if (body_size <= (0.4 * ohlc_size)) and (body_size > (0.3 * ohlc_size)):
            metrics['spinning_top_body_size'] = 0.7
        if (body_size <= (0.5 * ohlc_size)) and (body_size > (0.4 * ohlc_size)):
            metrics['spinning_top_body_size'] = 0.5
        if body_size > (0.5 * ohlc_size):
            metrics['spinning_top_body_size'] = 0
            return False

        self.confidence_metrics.update(metrics)
        return True

    def is_morning_star(self, symbol_data):
        # Check body two days ago
        symbol_two_days_ago = symbol_data.get_dsd_x_days_back(2)
        if not symbol_two_days_ago.is_bearish_body():
            self.confidence_metrics['second_last_body'] = 0
            return False
        else:
            self.confidence_metrics['second_last_body'] = 1

        # Check last body
        last_dsd = symbol_data.get_dsd_x_days_back(1)
        if self.is_doji(last_dsd) and last_dsd.is_gap_down_opening():
            self.confidence_metrics['last_body'] = 1
        elif self.is_spinning_top(last_dsd) and last_dsd.is_gap_down_opening():
            self.confidence_metrics['last_body'] = 1
        else:
            self.confidence_metrics['last_body'] = 0
            return False

        # Check if current body is bullish
        if symbol_data.is_bullish_body() and symbol_data.is_gap_up_opening():
            self.confidence_metrics['current_body_trend'] = 1
        else:
            self.confidence_metrics['current_body_trend'] = 0
            return False

        if symbol_data.close_price > symbol_two_days_ago.start_price:
            self.confidence_metrics['current_body_price'] = 1
        else:
            self.confidence_metrics['current_body_price'] = 0
            return False

        self.extra_info['stoploss'] = min(symbol_two_days_ago.low_price, last_dsd.low_price, symbol_data.low_price)

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
            symbol_two_days_ago = symbol_data.get_dsd_x_days_back(2)
            is_morning_star = self.is_morning_star(symbol_data)
            day_difference = get_num_trading_sessions(date_start, date_end, symbol, market_data_source)
            if day_difference > 0:
                is_previously_downward = symbol_two_days_ago.is_previously_downward_trend(
                    num_days=day_difference,
                    percent_downward=60
                )
            else:
                is_previously_downward = True
            if is_morning_star and is_previously_downward and self.is_symbol_data_tradeable(symbol_data):
                return (True, self.confidence_metrics, self.extra_info)
            else:
                return (False, self.confidence_metrics, self.extra_info)
        else:
            return (False, self.confidence_metrics, self.extra_info)
