import math
import quandl

from django.conf import settings

quandl.ApiConfig.api_key = settings.QUANDL_API_KEY


class QuandlDailyDataGenerator(object):

    key_to_highlight_map = {
        '{0}/{1} - Open': 'open',
        '{0}/{1} - High': 'high',
        '{0}/{1} - Low': 'low',
        '{0}/{1} - Close': 'close',
        '{0}/{1} - Total Trade Quantity': 'volume',
    }

    def generate_batch(self, symbols, index, input_date):
        self.symbols = symbols
        self.index = index
        self.input_date = input_date
        date_string = input_date.strftime('%Y-%m-%d')
        symbol_strs = [index.index_code + '/' + symbol.symbol_code for symbol in symbols if symbol.is_active]
        data = quandl.get(symbol_strs,
                          start_date=date_string,
                          end_date=date_string)
        data_points = self._get_data_point(data, index)
        return data_points

    def _get_data_point(self, data, index):
        print (data)
        data_points = {}
        if data.size:
            for symbol in self.symbols:
                data_points[symbol.symbol_code] = {}
                for key in self.key_to_highlight_map.keys():
                    data_points[symbol.symbol_code][self.key_to_highlight_map[key]] = data.iloc[0].get(
                        key.format(index.index_code, symbol.symbol_code),
                        None
                    )
                    if math.isnan(data_points[symbol.symbol_code][self.key_to_highlight_map[key]]):
                        data_points[symbol.symbol_code][self.key_to_highlight_map[key]] = None
        return data_points
