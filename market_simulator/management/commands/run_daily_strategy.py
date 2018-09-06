import csv
import datetime

from django.core.management.base      import BaseCommand, CommandError

from strategies.models                import ChartStrategy
from market_simulator.models          import Index, Symbol, MarketDataSource
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

        input_date_string = (str(options['date']) +
                             '-' +
                             str(options['month']) +
                             '-' +
                             str(options['year']))
        input_date = datetime.datetime.strptime(input_date_string, '%d-%m-%Y').date()
        for strategy in strategies:
            strategy_satisfaction = {}
            strategy_satisfaction[strategy] = {}
            print ('Strategy under test: ', strategy)
            for counter, symbol in enumerate(symbols):
                print ('Symbol no: %s == %s' % (str(counter), symbol))
                tester = StrategyTester(input_date, strategy, symbol, data_source)
                strategy_data_points = tester.check_if_strategy_satisfied()
                if strategy_data_points:
                    for strategy_data in strategy_data_points:
                        print (strategy_data)
                        if strategy_data['symbol'] not in strategy_satisfaction[strategy]:
                            strategy_satisfaction[strategy][strategy_data['symbol']] = []
                        strategy_satisfaction[strategy][strategy_data['symbol']].append({
                            'days': strategy_data['days'],
                            'start_date': strategy_data['start_date'],
                            'end_date': strategy_data['end_date'],
                            'volume': strategy_data['volume'],
                            'avg_confidence': strategy_data['avg_confidence'],
                            'confidence_metrics': strategy_data['confidence_metrics'],
                            'extra_info': strategy_data['extra_info'],
                        })
            f = open(file_name + '-' + strategy + '.csv', 'w')
            csv_writer = csv.writer(f)
            csv_writer.writerow(['Strategy',
                                 'Symbol',
                                 'Num Days',
                                 'Volume',
                                 'Average Confidence',
                                 'Start Date',
                                 'End Date',
                                 'Confidence Metrics',
                                 'Extra Info'])
            for strategy in strategy_satisfaction:
                is_any_satisfaction = False
                for symbol in strategy_satisfaction[strategy]:
                    if len(strategy_satisfaction[strategy][symbol]):
                        is_any_satisfaction = True
                        for data_point in strategy_satisfaction[strategy][symbol]:
                            data = [strategy,
                                    symbol,
                                    data_point['days'],
                                    data_point['volume'],
                                    data_point['avg_confidence'],
                                    data_point['start_date'],
                                    data_point['end_date'],
                                    data_point['confidence_metrics'],
                                    data_point['extra_info']]
                            csv_writer.writerow(data)
                        csv_writer.writerow(['\n'])
                if is_any_satisfaction:
                    csv_writer.writerow(['\n'])
                    csv_writer.writerow(['\n'])
            f.close()
