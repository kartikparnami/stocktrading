"""
Generic market data store.

Inherit and implement the abstract methods for specifc api.
"""
import datetime
import pytz

from influxdb import InfluxDBClient
from settings import settings


class MarketDataStore(object):
    """Main class for market data storage to influx."""

    def __init__(self, objects, local_pytz=pytz.utc):
        """Constructor method."""
        self.client = InfluxDBClient(settings.INFLUX_SERVER,
                                     settings.INFLUX_PORT,
                                     settings.INFLUX_USERNAME,
                                     settings.INFLUX_PASSWORD,
                                     settings.INFLUX_DB)
        self.local_pytz = local_pytz
        for obj in objects:
            metric = [{
                'measurement': self.get_measurement(obj),
                'tags': self.get_tags(obj),
                'time': self.get_time(obj),
                'fields': self.get_fields(obj)
            }]
            self.client.write_points(metric)

    def get_measurement(self, obj):
        """
        Return a measurement name string.

        Abstract method, can be overriden
        """
        return 'market_data'

    def get_tags(self, obj):
        """
        Return a dictionary with tags.

        Abstract method, can be overriden
        """
        tags = {
            'country': '',
            'index': '',
            'symbol': '',
            'highlight': ''
        }
        return tags

    def get_time(self, obj):
        """
        Return timezone aware date preferably.

        Abstract method, can be overriden
        """
        return datetime.datetime.now(self.local_pytz)

    def get_fields(self, obj):
        """
        Return a dictionary of fields.

        Abstract method, can be overriden
        """
        fields = {
            'price': 0
        }
        return fields
