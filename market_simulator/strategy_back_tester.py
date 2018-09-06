from market_simulator.models import MarketDataSource, Symbol, DailySymbolData
from strategies.models       import ChartStrategy

import datetime
import importlib
import time

class StrategyBackTester(object):

    def __init__(self,
                 strategy_code,
                 symbol_code,
                 market_data_source_code,
                 latest_date=datetime.date.today(),
                 earliest_date=datetime.datetime.strptime('30-12-1999', '%d-%m-%Y').date()):
        self.strategy_code = strategy_code
        self.strategy = ChartStrategy.objects.get(strategy_code=strategy_code)
        self.strategy_cls_module = importlib.import_module(
            'strategies.' +
            self.strategy_code +
            '_chart_strategy'
        )
        self.strategy_cls_generator = getattr(
            self.strategy_cls_module,
            self.strategy.source_class_prefix + 'ChartStrategy'
        )
        self.symbol = Symbol.objects.get(symbol_code=symbol_code)
        self.market_data_source = MarketDataSource.objects.get(
            market_data_source_code=market_data_source_code
        )
        self.latest_date = latest_date
        self.earliest_date = earliest_date

    def backtest(self):
        strategy_satisfaction_list = []
        strategy_cls = self.strategy_cls_generator()
        max_days_history = self.strategy.max_days_history
        curr_date = self.latest_date
        while curr_date > self.earliest_date:
            # print ('Curr_date: ', str(curr_date))
            dsd = DailySymbolData.objects.filter(symbol=self.symbol,
                                                 data_souce=self.market_data_source,
                                                 date=curr_date)
            if dsd.exists():
                dsd = dsd.first()
                print (str(dsd.date))
                for i in range(0, max_days_history + 1):
                    dsd_i_days_ago = dsd.get_dsd_x_days_back(i)
                    if dsd_i_days_ago:
                        start_date = dsd_i_days_ago.date
                        try:
                            is_strategy_satisfied, confidence_metrics, extra_info = strategy_cls.run(
                                self.symbol,
                                self.market_data_source,
                                start_date,
                                curr_date
                            )
                            if is_strategy_satisfied:
                                avg_confidence = sum(confidence_metrics.values()) / len(confidence_metrics.keys())
                                strategy_satisfaction_list.append((
                                    str(start_date),
                                    str(curr_date),
                                    avg_confidence,
                                    confidence_metrics
                                ))
                                print (
                                    'Days %s, from %s to %s. Strategy satisfied: %s. Avg Confidence %s. Confidence Metrics: %s, Extra info: %s' % (
                                        str(i),
                                        str(start_date),
                                        str(curr_date),
                                        str(is_strategy_satisfied),
                                        str(int(avg_confidence * 100)),
                                        str(confidence_metrics),
                                        str(extra_info))
                                )
                        except Exception as e:
                            print ('Exception %s for days %s, from %s to %s.' % (e,
                                                                                 i,
                                                                                 str(start_date),
                                                                                 str(curr_date)))
                            raise(e)
            curr_date = curr_date - datetime.timedelta(days=1)
        return strategy_satisfaction_list
