import csv
import datetime

from django.core.management.base import BaseCommand, CommandError

from strategies.models                import ChartStrategy
from market_simulator.models          import Index, Symbol, MarketDataSource, DailySymbolData
from market_simulator.strategy_tester import StrategyTester


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--date', type=str)
        parser.add_argument('--month', type=str)
        parser.add_argument('--year', type=str)
        parser.add_argument('--strategy', type=str)
        parser.add_argument('--symbol', type=str)
        parser.add_argument('--index', type=str)
        parser.add_argument('--data_source', type=str)
        parser.add_argument('--file_name', type=str)

    def handle(self, *args, **options):
        file_name = options['file_name']

        # Check for symbol, index and data source validity
        index = options['index']
        if not Index.objects.filter(index_code=index).count() == 1:
            raise CommandError('Index "%s" does not exist or exists more than once.' % index)

        data_source = options['data_source']
        if not MarketDataSource.objects.filter(market_data_source_code=data_source).count() == 1:
            raise CommandError(
                'Market data source "%s" does not exist or exists more than once.' % data_source
            )

        run_for_all_symbols = False
        symbol = options['symbol']
        if symbol:
            if not Symbol.objects.filter(symbol_code=symbol).count() == 1:
                raise CommandError('Symbol "%s" does not exist or exists more than once.' % symbol)
        else:
            run_for_all_symbols = True
            print ('Running for all symbols in index {0} from market data source {1}'.format(
                index,
                data_source
            ))

        if run_for_all_symbols:
            symbols = Symbol.objects.filter(index__index_code=index, is_active=True).values_list(
                'symbol_code',
                flat=True
            )
        else:
            symbols = [symbol]

        run_for_all_strategies = False
        strategy = options['strategy']
        if strategy:
            if not ChartStrategy.objects.filter(strategy_code=strategy).count() == 1:
                raise CommandError('Strategy "%s" does not exist or exists more than once.' % strategy)
        else:
            run_for_all_strategies = True
            print ('Running all strategies...')

        if run_for_all_strategies:
            strategies = ChartStrategy.objects.filter(is_active=True).values_list(
                'strategy_code',
                flat=True
            )
        else:
            strategies = [strategy]

        strategy_satisfacion_list = []
        input_date_string = (str(options['date']) +
                             '-' +
                             str(options['month']) +
                             '-' +
                             str(options['year']))
        input_date = datetime.datetime.strptime(input_date_string, '%d-%m-%Y').date()
        for counter, symbol in enumerate(symbols):
            print ('Symbol no: %s == %s' % (str(counter), symbol))
            print (symbol, data_source, input_date)
            dsd = DailySymbolData.objects.filter(symbol__symbol_code=symbol,
                                                 data_souce__market_data_source_code=data_source,
                                                 date=input_date)
            if dsd.exists():
                dsd = dsd.first()
                prev_date = dsd.get_dsd_x_days_back(1)
                for strategy in strategies:
                    strategy_obj = ChartStrategy.objects.get(strategy_code=strategy)
                    tester = StrategyTester(prev_date, strategy, symbol, data_source)
                    curr_strategy_satisfaction_list = tester.check_if_strategy_satisfied()
                    if len(curr_strategy_satisfaction_list):
                        if strategy_obj.expected_stock_direction == 'bullish' and dsd.is_bullish_body():
                            strategy_satisfacion_list.extend(curr_strategy_satisfaction_list)
                        elif strategy_obj.expected_stock_direction == 'bearish' and dsd.is_bearish_body():
                            strategy_satisfacion_list.extend(curr_strategy_satisfaction_list)
                        elif strategy_obj.expected_stock_direction == 'uncertain':
                            strategy_satisfacion_list.extend(curr_strategy_satisfaction_list)
                    strategy_satisfacion_list.append(['\n'])
                strategy_satisfacion_list.append(['\n'])
                strategy_satisfacion_list.append(['\n'])
                strategy_satisfacion_list.append(['\n'])
        f = open(file_name + '.csv', 'w')
        csv_writer = csv.writer(f)
        csv_writer.writerows(strategy_satisfacion_list)
        f.close()
