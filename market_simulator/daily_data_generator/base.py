import datetime
import importlib

from market_simulator.models import Index, MarketDataSource, Symbol, DailySymbolData


class DailyDataGenerator(object):

    def __init__(self, date, month, year, index, symbol, data_source, read_from_api, is_batch_generation_possible=False):
        self.data_source = MarketDataSource.objects.get(market_data_source_code=data_source)
        daily_data_generator_module = importlib.import_module(
            'market_simulator.daily_data_generator.' +
            self.data_source.source_class_prefix.lower() +
            '_daily_data_generator'
        )
        self.generator_class = getattr(daily_data_generator_module,
                                       self.data_source.source_class_prefix + 'DailyDataGenerator')
        if not is_batch_generation_possible:
            self.symbol = Symbol.objects.get(symbol_code=symbol)
        else:
            self.symbol = Symbol.objects.filter(symbol_code__in=symbol)
        self.index = Index.objects.get(index_code=index)
        input_date_string = str(date) + '-' + str(month) + '-' + str(year)
        self.input_date = datetime.datetime.strptime(input_date_string, '%d-%m-%Y').date()
        self.read_from_api = read_from_api
        self.is_batch_generation_possible = is_batch_generation_possible

    def generate(self):
        if not DailySymbolData.objects.filter(
            symbol=self.symbol,
            date=self.input_date,
            data_souce=self.data_source
        ).exists() and self.symbol.is_active:
            data_point = self.generator_class().generate(self.symbol,
                                                         self.index,
                                                         self.input_date,
                                                         read_from_api=self.read_from_api)
            if data_point:
                DailySymbolData.objects.create(
                    symbol=self.symbol,
                    start_price=self._extract_from_data(data_point, 'open'),
                    close_price=self._extract_from_data(data_point, 'close'),
                    high_price=self._extract_from_data(data_point, 'high'),
                    low_price=self._extract_from_data(data_point, 'low'),
                    volume=self._extract_from_data(data_point, 'volume'),
                    date=self.input_date,
                    high_time=self._extract_from_data(data_point, 'high_time'),
                    low_time=self._extract_from_data(data_point, 'low_time'),
                    data_souce=self.data_source
                )

    def is_any_symbol_not_fetched(self, symbols):
        is_any_symbol_not_fetched = False
        for symbol in symbols:
            if not DailySymbolData.objects.filter(
                symbol=symbol,
                date=self.input_date,
                data_souce=self.data_source
            ).exists():
                is_any_symbol_not_fetched = True
        return is_any_symbol_not_fetched

    def generate_batch(self):
        is_any_symbol_not_fetched = self.is_any_symbol_not_fetched(self.symbol)
        if is_any_symbol_not_fetched:
            data_points = self.generator_class().generate_batch(self.symbol,
                                                                self.index,
                                                                self.input_date)
            for symbol in data_points.keys():
                if not DailySymbolData.objects.filter(
                    symbol=Symbol.objects.get(symbol_code=symbol),
                    date=self.input_date,
                    data_souce=self.data_source
                ).exists():
                    DailySymbolData.objects.create(
                        symbol=Symbol.objects.get(symbol_code=symbol),
                        start_price=self._extract_from_data(data_points[symbol], 'open'),
                        close_price=self._extract_from_data(data_points[symbol], 'close'),
                        high_price=self._extract_from_data(data_points[symbol], 'high'),
                        low_price=self._extract_from_data(data_points[symbol], 'low'),
                        volume=self._extract_from_data(data_points[symbol], 'volume'),
                        date=self.input_date,
                        high_time=self._extract_from_data(data_points[symbol], 'high_time'),
                        low_time=self._extract_from_data(data_points[symbol], 'low_time'),
                        data_souce=self.data_source
                    )

    def _extract_from_data(self, data_point, data_key):
        try:
            return float(data_point.get(data_key, None))
        except (ValueError, TypeError):
            print ('--==--==--==--==--==--==--==--==--==--==--==--')
            print (data_point, data_key)
            print ('--==--==--==--==--==--==--==--==--==--==--==--')
            return None

    def store_back_data_in_file(self):
        if self.symbol.is_active:
            self.generator_class().store_back_data_in_file(self.symbol,
                                                           self.index)
