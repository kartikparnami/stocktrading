import datetime
import time

from django.core.management.base import BaseCommand, CommandError

from market_simulator.daily_data_generator.base import DailyDataGenerator
from market_simulator.models                    import Index, Symbol, MarketDataSource, DailySymbolData


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--date', type=str)
        parser.add_argument('--month', type=str)
        parser.add_argument('--year', type=str)
        parser.add_argument('--symbol', type=str)
        parser.add_argument('--index', type=str)
        parser.add_argument('--data_source', type=str)
        parser.add_argument('--batch_gen', type=str)

    def handle(self, *args, **options):
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

        if options['batch_gen'] == 'N':
            for symbol in symbols:
                # Check for date validity.
                print ('Starting symbol %s' % symbol)
                input_date_string = (str(options['date']) +
                                     '-' +
                                     str(options['month']) +
                                     '-' +
                                     str(options['year']))
                input_date = datetime.datetime.strptime(input_date_string, '%d-%m-%Y').date()
                curr_date = datetime.date.today()
                if input_date > curr_date:
                    raise CommandError('The date entered ' + str(input_date) + ' has not finished yet.')

                # Store data
                if not DailySymbolData.objects.filter(date=input_date,
                                                      symbol__symbol_code=symbol,
                                                      data_souce__market_data_source_code=data_source).exists():
                    time.sleep(15)
                    daily_data_generator = DailyDataGenerator(date=options['date'],
                                                              month=options['month'],
                                                              year=options['year'],
                                                              index=options['index'],
                                                              symbol=symbol,
                                                              data_source=options['data_source'],
                                                              read_from_api=True)
                    try:
                        daily_data_generator.generate()
                    except Exception as e1:
                        print ('Failed 1st time at symbol %s for date %s-%s-%s' % (symbol,
                                                                                   options['date'],
                                                                                   options['month'],
                                                                                   options['year']))
                        time.sleep(10)
                        try:
                            daily_data_generator.generate()
                        except Exception as e2:
                            print ('Failed 2nd time at symbol %s for date %s-%s-%s' % (symbol,
                                                                                       options['date'],
                                                                                       options['month'],
                                                                                       options['year']))
                            time.sleep(10)
                            try:
                                daily_data_generator.generate()
                            except Exception as e3:
                                print ('Failed 3rd time at symbol %s for date %s-%s-%s' % (symbol,
                                                                                           options['date'],
                                                                                           options['month'],
                                                                                           options['year']))
                                raise(e3)
        else:
            batch_size = int(options['batch_gen'])
            symbols = list(symbols)
            print (len(symbols))
            symbol_batches = [symbols[i:i + batch_size] for i in range(0, len(symbols), batch_size)]
            print (len(symbol_batches))
            for counter, batched_symbols in enumerate(symbol_batches):
                print ('Batch No. ' + str(counter), batched_symbols)
                daily_data_generator = DailyDataGenerator(date=options['date'],
                                                          month=options['month'],
                                                          year=options['year'],
                                                          index=options['index'],
                                                          symbol=batched_symbols,
                                                          data_source=options['data_source'],
                                                          read_from_api=True,
                                                          is_batch_generation_possible=True)
                daily_data_generator.generate_batch()
