import datetime
import time

from django.core.management.base import BaseCommand, CommandError

from market_simulator.daily_data_generator.base import DailyDataGenerator
from market_simulator.models                    import Index, Symbol, MarketDataSource


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--start_date', type=str)
        parser.add_argument('--start_month', type=str)
        parser.add_argument('--start_year', type=str)
        parser.add_argument('--symbol', type=str)
        parser.add_argument('--index', type=str)
        parser.add_argument('--data_source', type=str)

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
            symbols = Symbol.objects.filter(index__index_code=index).values_list(
                'symbol_code',
                flat=True
            )
        else:
            symbols = [symbol]
        for symbol in symbols:
            # Process dates one by one
            time.sleep(5)
            try:
                print ('Processing symbol %s' % symbol)
                is_first_date = True
                input_date_string = (str(options['start_date']) +
                                     '-' +
                                     str(options['start_month']) +
                                     '-' +
                                     str(options['start_year']))
                input_date = datetime.datetime.strptime(input_date_string, '%d-%m-%Y').date()
                while input_date < datetime.date.today():
                    print ('Processing date... ' + input_date.strftime('%d-%m-%Y'))
                    daily_data_generator = DailyDataGenerator(date=input_date.strftime('%d'),
                                                              month=input_date.strftime('%m'),
                                                              year=input_date.strftime('%Y'),
                                                              index=index,
                                                              symbol=symbol,
                                                              data_source=data_source,
                                                              read_from_api=False)
                    # Store data in file.
                    if is_first_date:
                        daily_data_generator.store_back_data_in_file()
                        is_first_date = False
                    daily_data_generator.generate()
                    input_date = input_date + datetime.timedelta(days=1)
            except Exception as e:
                print ('\n\n\n===============================================')
                print ('Exception %s encountered for symbol %s' % (e, symbol))
                print ('===============================================\n\n\n')
