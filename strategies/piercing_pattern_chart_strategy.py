import datetime

from market_simulator.models  import DailySymbolData
from strategies.utils         import get_num_trading_sessions
from strategies.base_strategy import BaseStrategy


class PiercingPatternChartStrategy(BaseStrategy):

    def is_piercing_pattern(self, symbol_data):
        # Check last body
        last_dsd = symbol_data.get_dsd_x_days_back(1)
        if not last_dsd.is_bearish_body():
            self.confidence_metrics['last_body'] = 0
            return False
        else:
            self.confidence_metrics['last_body'] = 1

        # Check if current body is bullish
        if not symbol_data.is_bullish_body():
            self.confidence_metrics['current_body_trend'] = 0
            return False
        else:
            self.confidence_metrics['current_body_trend'] = 1

        self.extra_info['stoploss'] = min(last_dsd.low_price, symbol_data.low_price)

        # Upper engulfing
        check_price = last_dsd.high_price - symbol_data.start_price
        if ((last_dsd.high_price <= symbol_data.close_price) and
            (check_price >= (0.5 * (last_dsd.ohlc_size()))) and
            (check_price < (0.7 * (last_dsd.ohlc_size())))):
            self.confidence_metrics['piercing'] = 0.6
            return True

        if ((last_dsd.high_price <= symbol_data.close_price) and
            (check_price >= (0.7 * (last_dsd.ohlc_size()))) and
            (check_price < (0.9 * (last_dsd.ohlc_size())))):
            self.confidence_metrics['piercing'] = 0.8
            return True

        if ((last_dsd.high_price <= symbol_data.close_price) and
            (check_price >= (0.9 * (last_dsd.ohlc_size()))) and
            (check_price < (1.0 * (last_dsd.ohlc_size())))):
            self.confidence_metrics['piercing'] = 1
            return True

        check_price = last_dsd.start_price - symbol_data.start_price
        if ((last_dsd.start_price <= symbol_data.close_price) and
            (check_price >= (0.5 * (last_dsd.body_size()))) and
            (check_price < (0.7 * (last_dsd.body_size())))):
            self.confidence_metrics['piercing'] = 0.6
            return True

        if ((last_dsd.start_price <= symbol_data.close_price) and
            (check_price >= (0.7 * (last_dsd.body_size()))) and
            (check_price < (0.9 * (last_dsd.body_size())))):
            self.confidence_metrics['piercing'] = 0.8
            return True

        if ((last_dsd.start_price <= symbol_data.close_price) and
            (check_price >= (0.9 * (last_dsd.body_size()))) and
            (check_price < (1.0 * (last_dsd.body_size())))):
            self.confidence_metrics['piercing'] = 1
            return True

        # Lower engulfing
        check_price = symbol_data.close_price - last_dsd.low_price
        if ((last_dsd.low_price >= symbol_data.start_price) and
            (check_price >= (0.5 * (last_dsd.ohlc_size()))) and
            (check_price < (0.7 * (last_dsd.ohlc_size())))):
            self.confidence_metrics['piercing'] = 0.6
            return True

        if ((last_dsd.low_price >= symbol_data.start_price) and
            (check_price >= (0.7 * (last_dsd.ohlc_size()))) and
            (check_price < (0.9 * (last_dsd.ohlc_size())))):
            self.confidence_metrics['piercing'] = 0.8
            return True

        if ((last_dsd.low_price >= symbol_data.start_price) and
            (check_price >= (0.9 * (last_dsd.ohlc_size()))) and
            (check_price < (1.0 * (last_dsd.ohlc_size())))):
            self.confidence_metrics['piercing'] = 1
            return True

        check_price = symbol_data.close_price - last_dsd.close_price
        if ((last_dsd.close_price >= symbol_data.start_price) and
            (check_price >= (0.5 * (last_dsd.body_size()))) and
            (check_price < (0.7 * (last_dsd.body_size())))):
            self.confidence_metrics['piercing'] = 0.6
            return True

        if ((last_dsd.close_price >= symbol_data.start_price) and
            (check_price >= (0.7 * (last_dsd.body_size()))) and
            (check_price < (0.9 * (last_dsd.body_size())))):
            self.confidence_metrics['piercing'] = 0.8
            return True

        if ((last_dsd.close_price >= symbol_data.start_price) and
            (check_price >= (0.9 * (last_dsd.body_size()))) and
            (check_price < (1.0 * (last_dsd.body_size())))):
            self.confidence_metrics['piercing'] = 1
            return True

        self.confidence_metrics['piercing'] = 0
        return False

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
            is_piercing_pattern = self.is_piercing_pattern(symbol_data)
            day_difference = get_num_trading_sessions(date_start, date_end, symbol, market_data_source)
            if day_difference > 0:
                is_previously_downward = symbol_data.is_previously_downward_trend(
                    num_days=day_difference,
                    percent_downward=60
                )
            else:
                is_previously_downward = True
            if is_piercing_pattern and is_previously_downward and self.is_symbol_data_tradeable(symbol_data):
                return (True, self.confidence_metrics, self.extra_info)
            else:
                return (False, self.confidence_metrics, self.extra_info)
        else:
            return (False, self.confidence_metrics, self.extra_info)
