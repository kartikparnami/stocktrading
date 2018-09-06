import datetime

from django.core.management.base import BaseCommand, CommandError

from market_simulator.models     import Index, Symbol, MarketDataSource, DailySymbolData
from strategies.utils            import Indicators


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--start_date', type=str)
        parser.add_argument('--start_month', type=str)
        parser.add_argument('--start_year', type=str)
        parser.add_argument('--symbol', type=str)
        parser.add_argument('--index', type=str)
        parser.add_argument('--window', type=str)
        parser.add_argument('--data_source', type=str)

    def handle(self, *args, **options):
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

        window = int(options['window'])
        input_date_string = (str(options['start_date']) +
                             '-' +
                             str(options['start_month']) +
                             '-' +
                             str(options['start_year']))
        input_date = datetime.datetime.strptime(input_date_string, '%d-%m-%Y').date()

        for symbol in symbols:
            all_dsds = []
            last_date = datetime.date.today()
            while last_date > input_date:
                dsd = DailySymbolData.objects.filter(symbol__symbol_code=symbol,
                                                     data_souce__market_data_source_code=data_source,
                                                     date=last_date)
                if dsd.exists():
                    dsd = dsd.first()
                    if not all_dsds:
                        all_dsds = dsd.get_all_dsds_for_last_x_days(window*2)
                    else:
                        del all_dsds[-1]
                        next_dsd = all_dsds[0].get_dsd_x_days_back(1)
                        if next_dsd:
                            all_dsds = [next_dsd] + all_dsds
                    if all_dsds:
                        data_points = [some_dsd.close_price for some_dsd in all_dsds]
                        indicators = Indicators()
                        ema = indicators.ema(data_points, window)
                        print (dsd.date, ema)
                last_date = last_date - datetime.timedelta(days=1)
