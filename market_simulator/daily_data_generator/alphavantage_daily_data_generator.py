import json
import requests

from django.conf import settings


class AlphavantageDailyDataGenerator(object):

    key_to_highlight_map = {
        '1. open': 'open',
        '2. high': 'high',
        '3. low': 'low',
        '4. close': 'close',
        '5. volume': 'volume',
    }
    DAILY_DATA_STRING = 'Time Series (Daily)'

    def generate(self, symbol, index, input_date, read_from_api):
        self.symbol = symbol
        self.index = index
        self.input_date = input_date
        if read_from_api:
            data = self._get_data_from_api(symbol, index)
        else:
            data = self._get_data_from_file(symbol, index)
        date_string = input_date.strftime('%Y-%m-%d')
        data_point = self._get_data_point(data, date_string)
        return data_point

    def _get_data_from_api(self, symbol, index):
        url = (settings.ALPHAVANTAGE_QUERY_URL +
               settings.ALPHAVANTAGE_TIME_SERIES_DAILY +
               '&symbol=' +
               index.index_code +
               ':' +
               symbol.symbol_code +
               '&apikey=' +
               settings.ALPHAVANTAGE_API_KEY +
               '&outputsize=full')
        r = requests.get(url)
        response = r.json()
        return response[self.DAILY_DATA_STRING]

    def _get_data_from_file(self, symbol, index):
        filename = index.index_code + '-' + symbol.symbol_code + '.stockdata'
        with open(filename, 'r') as f:
            data = json.load(f)
        return data[self.DAILY_DATA_STRING]

    def _get_data_point(self, data, date_string):
        data_object = None
        data_point = None
        for date in data.keys():
            if date == date_string:
                data_object = data[date]
        if data_object:
            data_point = {}
            for key in data_object.keys():
                if key in self.key_to_highlight_map.keys():
                    if float(data_object[key]) <= 0 and key != '5. volume':
                        print (
                            'WARN: Data point %s not found for symbol %s at index %s for date %s' % (
                                key,
                                self.symbol.symbol_code,
                                self.index.index_code,
                                str(self.input_date)
                            )
                        )
                    else:
                        data_point[self.key_to_highlight_map[key]] = data_object[key]
        return data_point

    def store_back_data_in_file(self, symbol, index):
        data = {}
        data[self.DAILY_DATA_STRING] = self._get_data_from_api(symbol, index)
        with open(index.index_code + '-' + symbol.symbol_code + '.stockdata', 'w') as f:
            json.dump(data, f)
