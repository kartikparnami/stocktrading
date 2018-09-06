import datetime

from market_simulator.models  import DailySymbolData
from strategies.utils         import get_num_trading_sessions
from strategies.base_strategy import BaseStrategy


class ShootingStarChartStrategy(BaseStrategy):

    def is_candlestick_inverted_paper_umbrella(self, symbol_data):
        body_size = symbol_data.body_size()
        low_wick_size = symbol_data.low_wick_size()
        high_wick_size = symbol_data.high_wick_size()
        ohlc_size = symbol_data.ohlc_size()

        # High wick size check
        if high_wick_size >= (2 * body_size):
            self.confidence_metrics['high_wick_size'] = 1
        if (high_wick_size >= (1.8 * body_size)) and (high_wick_size < (2 * body_size)):
            self.confidence_metrics['high_wick_size'] = 0.7
        if (high_wick_size >= (1.5 * body_size)) and (high_wick_size < (1.8 * body_size)):
            self.confidence_metrics['high_wick_size'] = 0.3
        if high_wick_size < (1.5 * body_size):
            self.confidence_metrics['high_wick_size'] = 0
            return False

        # Low wick size check
        if low_wick_size <= (0.05 * ohlc_size):
            self.confidence_metrics['low_wick_size'] = 1
        if (low_wick_size <= (0.1 * ohlc_size)) and (low_wick_size > (0.05 * ohlc_size)):
            self.confidence_metrics['low_wick_size'] = 0.7
        if (low_wick_size <= (0.15 * ohlc_size)) and (low_wick_size > (0.1 * ohlc_size)):
            self.confidence_metrics['low_wick_size'] = 0.5
        if (low_wick_size <= (0.2 * ohlc_size)) and (low_wick_size > (0.15 * ohlc_size)):
            self.confidence_metrics['low_wick_size'] = 0.3
        if low_wick_size > (0.2 * ohlc_size):
            self.confidence_metrics['low_wick_size'] = 0
            return False

        # Body size check
        if body_size >= (0.25 * ohlc_size):
            self.confidence_metrics['body_size'] = 1
        if (body_size >= (0.15 * ohlc_size)) and (body_size < (0.2 * ohlc_size)):
            self.confidence_metrics['body_size'] = 0.7
        if (body_size >= (0.1 * ohlc_size)) and (body_size < (0.15 * ohlc_size)):
            self.confidence_metrics['body_size'] = 0.5
        if (body_size >= (0.075 * ohlc_size)) and (body_size < (0.1 * ohlc_size)):
            self.confidence_metrics['body_size'] = 0.3
        if body_size < (0.075 * ohlc_size):
            self.confidence_metrics['body_size'] = 0
            return False

        return True

    def populate_todays_trend_confidence(self, symbol_data):
        if symbol_data.is_bearish_body():
            self.confidence_metrics['body_trend'] = 1
        if symbol_data.is_bullish_body():
            self.confidence_metrics['body_trend'] = 0.3
        if symbol_data.is_flat_body():
            self.confidence_metrics['body_trend'] = 0.6
        self.extra_info['stoploss'] = symbol_data.high_price

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
            inverted_paper_umbrella_candle = self.is_candlestick_inverted_paper_umbrella(symbol_data)
            self.populate_todays_trend_confidence(symbol_data)
            day_difference = get_num_trading_sessions(date_start, date_end, symbol, market_data_source)
            if day_difference > 0:
                is_previously_upward = symbol_data.is_previously_upward_trend(
                    num_days=day_difference,
                    percent_upward=60
                )
            else:
                is_previously_upward = True
            if is_previously_upward and inverted_paper_umbrella_candle and self.is_symbol_data_tradeable(symbol_data):
                return (True, self.confidence_metrics, self.extra_info)
            else:
                return (False, self.confidence_metrics, self.extra_info)
        else:
            return (False, self.confidence_metrics, self.extra_info)
