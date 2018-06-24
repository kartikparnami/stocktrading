import datetime

from django.core.management.base import BaseCommand, CommandError

from market_simulator.daily_data_generator.base import DailyDataGenerator
from market_simulator.models                    import Index, Symbol, MarketDataSource


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--date', type=str)
        parser.add_argument('--month', type=str)
        parser.add_argument('--year', type=str)
        parser.add_argument('--symbol', type=str)
        parser.add_argument('--index', type=str)
        parser.add_argument('--data_source', type=str)

    def handle(self, *args, **options):
        # Check for symbol, index and data source validity
        index = options['index']
        if not Index.objects.filter(index_code=index).count() == 1:
            raise CommandError('Index "%s" does not exist or exists more than once.' % index)
        symbol = options['symbol']
        if not Symbol.objects.filter(symbol_code=symbol).count() == 1:
            raise CommandError('Symbol "%s" does not exist or exists more than once.' % symbol)
        data_source = options['data_source']
        if not MarketDataSource.objects.filter(market_data_source_code=data_source).count() == 1:
            raise CommandError(
                'Market data source "%s" does not exist or exists more than once.' % data_source
            )

        # Check for date validity.
        input_date_string = str(options['date']) + '-' + str(options['month']) + '-' + str(options['year'])
        input_date = datetime.datetime.strptime(input_date_string, '%d-%m-%Y').date()
        curr_date = datetime.date.today()
        if input_date > curr_date:
            raise CommandError('The date entered ' + str(input_date) + ' has not finished yet.')

        # Store data
        daily_data_generator = DailyDataGenerator(date=options['date'],
                                                  month=options['month'],
                                                  year=options['year'],
                                                  index=options['index'],
                                                  symbol=options['symbol'],
                                                  data_source=options['data_source'],
                                                  read_from_api=True)
        daily_data_generator.generate()
