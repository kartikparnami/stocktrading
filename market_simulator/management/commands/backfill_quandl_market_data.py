import datetime
import math
import quandl
import time

from django.core.management.base import BaseCommand, CommandError
from django.conf                 import settings

from market_simulator.models     import Index, Symbol, MarketDataSource, DailySymbolData

quandl.ApiConfig.api_key = settings.QUANDL_API_KEY


class Command(BaseCommand):

    key_to_highlight_map = {
        'Open': 'open',
        'High': 'high',
        'Low': 'low',
        'Close': 'close',
        'Total Trade Quantity': 'volume',
    }

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
            symbols = Symbol.objects.filter(index__index_code=index, is_active=True).values_list(
                'symbol_code',
                flat=True
            )
        else:
            symbols = [symbol]
        for symbol in symbols:
            # Process dates one by one
            data_points = {}
            symbol_str = index + '/' + symbol
            data = quandl.get(symbol_str)
            print (data.shape)
            for index, row in data.iterrows():
                data_points[index.date()] = {}
                for key in self.key_to_highlight_map.keys():
                    if key in row:
                        data_points[index.date()][self.key_to_highlight_map[key]] = row[
                            key
                        ] if not math.isnan(row[key]) else None
                    else:
                        data_points[index.date()][self.key_to_highlight_map[key]] = None
            for date in data_points.keys():
                if not DailySymbolData.objects.filter(
                    symbol=Symbol.objects.get(symbol_code=symbol),
                    date=date,
                    data_souce__market_data_source_code=data_source
                ).exists():
                    DailySymbolData.objects.create(
                        symbol=Symbol.objects.get(symbol_code=symbol),
                        start_price=data_points[date].get('open', None),
                        close_price=data_points[date].get('close', None),
                        high_price=data_points[date].get('high', None),
                        low_price=data_points[date].get('low', None),
                        volume=data_points[date].get('volume', None),
                        date=date,
                        high_time=None,
                        low_time=None,
                        data_souce=MarketDataSource.objects.get(market_data_source_code=data_source)
                    )
