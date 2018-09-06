from market_simulator.models import MarketDataSource, Symbol, DailySymbolData
from strategies.models       import ChartStrategy

import importlib


class StrategyTester(object):

    def __init__(self, date, strategy_code, symbol_code, market_data_source_code):
        self.strategy_code = strategy_code
        self.date = date
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
        self.market_data_source = MarketDataSource.objects.get(
            market_data_source_code=market_data_source_code
        )
        self.symbol = Symbol.objects.get(symbol_code=symbol_code)

    def check_if_strategy_satisfied(self):
        strategy_cls = self.strategy_cls_generator()
        max_days_history = self.strategy.max_days_history
        strategy_satisfacion_list = []
        for i in range(0, max_days_history + 1):
            dsd = DailySymbolData.objects.filter(symbol=self.symbol,
                                                 data_souce=self.market_data_source,
                                                 date=self.date)
            if dsd.exists():
                dsd = dsd.first()
                dsd_i_days_ago = dsd.get_dsd_x_days_back(i)
                if dsd_i_days_ago:
                    start_date = dsd_i_days_ago.date
                    try:
                        is_strategy_satisfied, confidence_metrics, extra_info = strategy_cls.run(
                            self.symbol,
                            self.market_data_source,
                            start_date,
                            self.date
                        )
                        if is_strategy_satisfied:
                            avg_confidence = sum(confidence_metrics.values()) / len(confidence_metrics.keys())
                            strategy_satisfacion_list.append({
                                'strategy': self.strategy.full_name,
                                'symbol': self.symbol.symbol_code,
                                'days': str(i),
                                'start_date': str(start_date),
                                'end_date': str(self.date),
                                'volume': str(dsd.volume),
                                'avg_confidence': str(int(avg_confidence * 100)),
                                'confidence_metrics': str(confidence_metrics),
                                'extra_info': str(extra_info),
                            })
                            print (
                                ('Strategy %s has been satisfied for symbol %s for %s continuous days' +
                                 ' (from %s to %s with last volume %s). \n\nAvg Confidence %s\nConfidence' +
                                 ' Metrics: %s\nExtra info: %s\n\n' +
                                 '=====================================\n=====================================') % (
                                    self.strategy.full_name,
                                    self.symbol.symbol_code,
                                    str(i),
                                    str(start_date),
                                    str(self.date),
                                    str(dsd.volume),
                                    str(int(avg_confidence * 100)),
                                    str(confidence_metrics),
                                    str(extra_info))
                            )
                    except Exception as e:
                        print ('Exception %s for days %s, from %s to %s.' % (e,
                                                                             i,
                                                                             str(start_date),
                                                                             str(self.date)))
        return strategy_satisfacion_list
