import datetime

from market_simulator.models  import DailySymbolData
from strategies.utils         import get_num_trading_sessions
from strategies.base_strategy import BaseStrategy


class BullishConcealingBabySwallowChartStrategy(BaseStrategy):

    def is_bearish_marubozu(self, symbol_data, conf_metric_str):
        body_size = symbol_data.body_size()
        ohlc_size = symbol_data.ohlc_size()

        # Body trend check
        if not symbol_data.is_bearish_body():
            return False

        # Body size check
        if (body_size <= (0.6 * ohlc_size)):
            self.confidence_metrics[conf_metric_str] = 0
            return False
        if (body_size <= (0.7 * ohlc_size)) and (body_size > (0.6 * ohlc_size)):
            self.confidence_metrics[conf_metric_str] = 0.2
        if (body_size <= (0.8 * ohlc_size)) and (body_size > (0.7 * ohlc_size)):
            self.confidence_metrics[conf_metric_str] = 0.6
        if (body_size <= (0.9 * ohlc_size)) and (body_size > (0.8 * ohlc_size)):
            self.confidence_metrics[conf_metric_str] = 0.8
        if (body_size <= (1.0 * ohlc_size)) and (body_size > (0.9 * ohlc_size)):
            self.confidence_metrics[conf_metric_str] = 1.0

        return True

    def is_concealed_body(self, symbol_data):
        body_size = symbol_data.body_size()
        ohlc_size = symbol_data.ohlc_size()

        previous_dsd = symbol_data.get_dsd_x_days_back(1)
        if not symbol_data.high_price > previous_dsd.close_price:
            return False
        else:
            self.confidence_metrics['last_high_greater_than_prev_low'] = 1

        two_day_prev_dsd = symbol_data.get_dsd_x_days_back(2)
        if symbol_data.high_price > two_day_prev_dsd.close_price:
            self.confidence_metrics['last_high_greater_than_prev_prev_low'] = 1

        if body_size > (0.7 * ohlc_size):
            self.confidence_metrics['last_body_size'] = 0
            return False
        elif body_size <= (0.7 * ohlc_size) and body_size > (0.5 * ohlc_size):
            self.confidence_metrics['last_body_size'] = 0.5
        elif body_size <= (0.5 * ohlc_size) and body_size > (0.2 * ohlc_size):
            self.confidence_metrics['last_body_size'] = 0
        elif body_size <= (0.2 * ohlc_size) and body_size > (0.1 * ohlc_size):
            self.confidence_metrics['last_body_size'] = 0.5
        else:
            self.confidence_metrics['last_body_size'] = 0
            return False

        return True

    def is_bullish_concealing_baby_swallow(self, symbol_data):
        # Check body three days ago
        symbol_three_days_ago = symbol_data.get_dsd_x_days_back(3)
        if not symbol_three_days_ago.is_bearish_body():
            self.confidence_metrics['third_last_body_trend'] = 0
            return False
        else:
            self.confidence_metrics['third_last_body_trend'] = 1

        if not self.is_bearish_marubozu(symbol_three_days_ago, 'third_last_body_size'):
            return False

        # Check body two days ago
        symbol_two_days_ago = symbol_data.get_dsd_x_days_back(2)
        if not symbol_two_days_ago.is_bearish_body():
            self.confidence_metrics['second_last_body_trend'] = 0
            return False
        else:
            self.confidence_metrics['second_last_body_trend'] = 1

        if not self.is_bearish_marubozu(symbol_two_days_ago, 'second_last_body_size'):
            return False

        # Check last body
        last_dsd = symbol_data.get_dsd_x_days_back(1)
        if not last_dsd.is_bearish_body():
            self.confidence_metrics['last_body_trend'] = 0
            return False
        else:
            self.confidence_metrics['last_body_trend'] = 1

        if not self.is_concealed_body(last_dsd):
            return False

        # Check current body
        if not symbol_data.is_bearish_body():
            self.confidence_metrics['curr_body_trend'] = 0
            return False
        else:
            self.confidence_metrics['curr_body_trend'] = 1

        if not (symbol_data.close_price < last_dsd.close_price and symbol_data.open_price > last_dsd.open_price):
            return False
        else:
            self.confidence_metrics['curr_body_engulfing'] = 1

        self.extra_info['stoploss'] = min(last_dsd.low_price, symbol_data.low_price)

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
            is_bullish_concealing_baby_swallow = self.is_bullish_concealing_baby_swallow(symbol_data)
            day_difference = get_num_trading_sessions(date_start, date_end, symbol, market_data_source)
            if day_difference > 0:
                is_previously_downward = symbol_two_days_ago.is_previously_downward_trend(
                    num_days=day_difference,
                    percent_downward=60
                )
            else:
                is_previously_downward = True
            if is_bullish_concealing_baby_swallow and is_previously_downward and self.is_symbol_data_tradeable(symbol_data):
                return (True, self.confidence_metrics, self.extra_info)
            else:
                return (False, self.confidence_metrics, self.extra_info)
        else:
            return (False, self.confidence_metrics, self.extra_info)
