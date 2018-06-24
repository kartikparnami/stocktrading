import datetime
import importlib

from market_simulator.models import Index, MarketDataSource, Symbol, DailySymbolData


class DailyDataGenerator(object):

    def __init__(self, date, month, year, index, symbol, data_source, read_from_api):
        self.data_source = MarketDataSource.objects.get(market_data_source_code=data_source)
        daily_data_generator_module = importlib.import_module(
            'market_simulator.daily_data_generator.' +
            self.data_source.source_class_prefix.lower() +
            '_daily_data_generator'
        )
        self.generator_class = getattr(daily_data_generator_module,
                                       self.data_source.source_class_prefix + 'DailyDataGenerator')
        self.symbol = Symbol.objects.get(symbol_code=symbol)
        self.index = Index.objects.get(index_code=index)
        input_date_string = str(date) + '-' + str(month) + '-' + str(year)
        self.input_date = datetime.datetime.strptime(input_date_string, '%d-%m-%Y').date()
        self.read_from_api = read_from_api

    def generate(self):
        if not DailySymbolData.objects.filter(
            symbol=self.symbol,
            date=self.input_date,
            data_souce=self.data_source
        ).exists():
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

    def _extract_from_data(self, data_point, data_key):
        return data_point.get(data_key, None)

    def store_back_data_in_file(self):
        self.generator_class().store_back_data_in_file(self.symbol,
                                                       self.index)
