import datetime

from django.db import models

from market_simulator.exceptions import NotEnoughDataForTrend

SYMBOL_SECTOR_CHOICES = (
    ('cmpsoft', 'Computers - Software'),
    ('finhouse', 'Finance - Housing'),
    ('refinery', 'Refineries'),
    ('pvtbank', 'Banks - Private Sector'),
    ('perscare', 'Personal Care'),
    ('cigret', 'Cigarettes'),
    ('autocar', 'Auto - Cars & Jeeps'),
    ('pubbank', 'Banks - Public Sector'),
    ('oil', 'Oil Drilling & Exploration'),
    ('infra', 'Infrastructure - General'),
    ('mine', 'Mining & Minerals'),
    ('telecom', 'Telecommunication - Services'),
    ('pharma', 'Pharmaceuticals'),
    ('leasehire', 'Finance - Leasing & Hire Purchase'),
    ('powergen', 'Power - Generation & Distribution'),
    ('metalnf', 'Metals - Non Ferrous'),
    ('paintvar', 'Paints & Varnishes'),
    ('cement', 'Cement - Major'),
    ('fininvest', 'Finance - Investments'),
    ('foodproc', 'Food Processing'),
    ('misc', 'Miscellaneous'),
    ('retail', 'Retail'),
    ('autolc', 'Auto - LCVS & HCVS'),
    ('autotwo', 'Auto - 2 Wheelers & 3 Wheelers'),
    ('steellar', 'Steel - Large'),
    ('diverse', 'Diversified'),
    ('autoanc', 'Auto Ancillaries'),
    ('fingen', 'Finance - General'),
    ('mediaent', 'Media & Entertainment'),
    ('chem', 'Chemicals'),
    ('telecomin', 'Telecommunications - Infrastructure'),
    ('alum', 'Aluminium'),
    ('brew', 'Breweries & Distillaries'),
    ('trans', 'Transport & Logistics'),
    ('constcont', 'Construction & Contracting - Real Estate'),
    ('electric', 'Electric Equipment'),
    ('tyres', 'Tyres'),
    ('textiles', 'Textiles - Readymade Apparels'),
    ('steeltub', 'Steel - Tubes & Pipes'),
    ('trading', 'Trading'),
    ('products', 'Products & Building Materials'),
    ('fertilisers', 'Fertilisers'),
    ('textilesco', 'Textiles - Spinning - Cotton Blended'),
    ('drycells', 'Dry Cells'),
    ('hosiery', 'Hosiery & Knitwear'),
    ('paper', 'Paper'),
    ('lubricants', 'Lubricants'),
    ('finterm', 'Finance - Term Lending Institutions'),
    ('castings', 'Castings & Forgings'),
    ('hotels', 'Hotels'),
    ('textilesman', 'Textiles - Manmade'),
    ('diamonds', 'Diamond Cutting & Jewellery & Precious Metals'),
    ('telecomequip', 'Telecommunications - Equipment'),
    ('electgraph', 'Electrodes & Graphite'),
    ('bearings', 'Bearings'),
    ('enggheavy', 'Engineering - Heavy'),
    ('steelgp', 'Steel - GP & GC Sheets'),
    ('dyespigments', 'Dyes & Pigments'),
    ('cementmini', 'Cement - Mini'),
    ('packaging', 'Packaging'),
    ('steelmed', 'Steel - Medium & Small'),
    ('cables', 'Cables - Power & Others'),
    ('textileswoolen', 'Textiles - Woolen & Worsted'),
    ('powertrans', 'Power - Transmission & Equipment'),
    ('printing', 'Printing & Stationary'),
    ('steelpig', 'Steel - Pig Iron'),
    ('sugar', 'Sugar'),
    ('vanspatioil', 'Vanaspati & Oils'),
    ('pumps', 'Pumps'),
    ('steelsponge', 'Steel - Sponge Iron'),
    ('petrochemicals', 'Petrochemicals'),
    ('consumergoods', 'Consumer Goods - Electronic'),
    ('engines', 'Engines'),
    ('consumergoodswhite', 'Consumer Goods - White Goods'),
    ('pesticides', 'Pesticides & Agro Chemicals'),
    ('ceramics', 'Ceramics & Granite'),
    ('leather', 'Leather Products'),
    ('detergents', 'Detergents'),
    ('engineering', 'Engineering'),
    ('cmphard', 'Computers - Hardware'),
    ('plantationstea', 'Plantations - Tea & Coffee'),
    ('hospitals', 'Hospitals & Medical Services'),
    ('shipping', 'Shipping'),
    ('plastics', 'Plastics'),
    ('aquaculture', 'Aquaculture'),
    ('couriers', 'Couriers'),
)


# Create your models here.
class Country(models.Model):
    country_code = models.CharField(max_length=100, unique=True)
    full_name    = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.full_name + '(' + self.country_code + ')'


class Index(models.Model):
    index_code = models.CharField(max_length=100, unique=True)
    full_name  = models.CharField(max_length=255, null=True, blank=True)
    country    = models.ForeignKey(Country, on_delete=models.DO_NOTHING, null=True, blank=True)
    timezone   = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return (self.index_code +
                '(' +
                self.country.country_code +
                '-' +
                self.country.full_name +
                ')')


class Symbol(models.Model):
    symbol_code = models.CharField(max_length=100, null=True, blank=True)
    full_name   = models.CharField(max_length=255, null=True, blank=True)
    sector      = models.CharField(max_length=100, choices=SYMBOL_SECTOR_CHOICES)
    is_active   = models.BooleanField(default=True)
    index       = models.ForeignKey(Index, on_delete=models.DO_NOTHING, null=True, blank=True)

    class Meta:
        unique_together = ('symbol_code', 'index')

    def __str__(self):
        return self.full_name + '(' + self.symbol_code + '-' + self.index.index_code + ')'


class MarketDataSource(models.Model):
    market_data_source_code = models.CharField(max_length=100, null=True, blank=True)
    full_name               = models.CharField(max_length=255, null=True, blank=True)
    source_class_prefix     = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.full_name + '(' + self.market_data_source_code + '-' + self.source_class_prefix + ')'


class DailySymbolData(models.Model):
    symbol      = models.ForeignKey(Symbol, on_delete=models.DO_NOTHING)
    start_price = models.FloatField(default=0, null=True)
    close_price = models.FloatField(default=0, null=True)
    high_price  = models.FloatField(default=0, null=True)
    low_price   = models.FloatField(default=0, null=True)
    volume      = models.IntegerField(default=0, null=True)
    date        = models.DateField(null=True, blank=True)
    high_time   = models.DateTimeField(null=True, blank=True)
    low_time    = models.DateTimeField(null=True, blank=True)
    data_souce  = models.ForeignKey(MarketDataSource, on_delete=models.DO_NOTHING, null=True, blank=True)

    def __str__(self):
        return self.symbol.symbol_code + '(' + str(self.date) + ')'

    def is_bearish_body(self):
        return self.close_price < self.start_price

    def is_bullish_body(self):
        return self.close_price > self.start_price

    def is_flat_body(self):
        return self.close_price == self.start_price

    def check_enough_data_for_trend(self, num_days=3):
        # Just a check to see in case something goes crazy where we
        # dont have enough data for previous num_days days.
        check_date = self.date - datetime.timedelta(days=num_days * 7)
        num_objs = DailySymbolData.objects.filter(symbol=self.symbol,
                                                  data_souce=self.data_souce,
                                                  date__gte=check_date).count()
        if num_objs < num_days:
            raise NotEnoughDataForTrend

    def get_data_for_trend(self, num_days=3):
        all_objs = []
        curr_date = self.date
        while len(all_objs) < num_days:
            data_obj = DailySymbolData.objects.filter(symbol=self.symbol,
                                                      data_souce=self.data_souce,
                                                      date=curr_date)
            if data_obj.exists():
                all_objs.append(data_obj)
            curr_date = curr_date - datetime.timedelta(days=1)
        return all_objs

    def is_currently_downward_trend(self, num_days=3, percent_downward=100):
        bearish_count = 0
        bullish_count = 0
        total_count = 0
        self.check_enough_data_for_trend(num_days=num_days)
        all_objs = self.get_data_for_trend(num_days=num_days)
        for data_obj in reversed(all_objs):
            if data_obj.first().is_bearish_body():
                bearish_count += 1
            elif data_obj.first().is_bullish_body():
                bullish_count += 1
            total_count += 1
        if ((bearish_count * 100) / total_count) >= percent_downward:
            return True
        else:
            return False

    def is_currently_upward_trend(self, num_days=3, percent_upward=100):
        bearish_count = 0
        bullish_count = 0
        total_count = 0
        self.check_enough_data_for_trend(num_days=num_days)
        all_objs = self.get_data_for_trend(num_days=num_days)
        for data_obj in reversed(all_objs):
            if data_obj.first().is_bearish_body():
                bearish_count += 1
            elif data_obj.first().is_bullish_body():
                bullish_count += 1
            total_count += 1
        if ((bullish_count * 100) / total_count) >= percent_upward:
            return True
        else:
            return False

    def is_previously_downward_trend(self, num_days=3, percent_downward=100):
        bearish_count = 0
        bullish_count = 0
        total_count = 0
        self.check_enough_data_for_trend(num_days=num_days + 1)
        all_objs = self.get_data_for_trend(num_days=num_days + 1)
        for data_obj in reversed(all_objs[1:]):
            if data_obj.first().is_bearish_body():
                bearish_count += 1
            elif data_obj.first().is_bullish_body():
                bullish_count += 1
            total_count += 1
        last_obj = all_objs[-1].first()
        if ((last_obj.close_price > self.close_price) and (((bearish_count * 100) / total_count) >= percent_downward)):
            return True
        else:
            return False

    def is_previously_upward_trend(self, num_days=3, percent_upward=100):
        bearish_count = 0
        bullish_count = 0
        total_count = 0
        self.check_enough_data_for_trend(num_days=num_days + 1)
        all_objs = self.get_data_for_trend(num_days=num_days + 1)
        for data_obj in reversed(all_objs[1:]):
            if data_obj.first().is_bearish_body():
                bearish_count += 1
            elif data_obj.first().is_bullish_body():
                bullish_count += 1
            total_count += 1
        last_obj = all_objs[-1].first()
        if ((last_obj.close_price < self.close_price) and (((bullish_count * 100) / total_count) >= percent_upward)):
            return True
        else:
            return False

    def high_wick_size(self):
        return min(self.high_price - self.close_price,
                   self.high_price - self.start_price)

    def low_wick_size(self):
        return min(self.close_price - self.low_price,
                   self.start_price - self.low_price)

    def body_size(self):
        return abs(self.start_price - self.close_price)

    def ohlc_size(self):
        return abs(self.high_price - self.low_price)

    def get_dsd_x_days_back(self, x):
        if x == 0:
            return self
        curr_date = self.date
        last_check_date = curr_date - datetime.timedelta(days=x * 7)
        days_back = 1
        while days_back <= x and curr_date > last_check_date:
            curr_date = curr_date - datetime.timedelta(days=1)
            if DailySymbolData.objects.filter(symbol=self.symbol,
                                              data_souce=self.data_souce,
                                              date=curr_date).exists():
                days_back += 1
                if days_back == x + 1:
                    return DailySymbolData.objects.get(symbol=self.symbol,
                                                       data_souce=self.data_souce,
                                                       date=curr_date)
        return None

    def get_dsd_x_days_forward(self, x):
        if x == 0:
            return self
        curr_date = self.date
        last_check_date = curr_date + datetime.timedelta(days=x * 7)
        days_forward = 1
        while days_forward <= x and curr_date < last_check_date:
            curr_date = curr_date + datetime.timedelta(days=1)
            if DailySymbolData.objects.filter(symbol=self.symbol,
                                              data_souce=self.data_souce,
                                              date=curr_date).exists():
                days_forward += 1
                if days_forward == x + 1:
                    return DailySymbolData.objects.get(symbol=self.symbol,
                                                       data_souce=self.data_souce,
                                                       date=curr_date)
        return None

    def is_gap_up_opening(self):
        last_obj = self.get_dsd_x_days_back(1)
        if self.start_price > last_obj.close_price:
            return True
        else:
            return False

    def is_gap_down_opening(self):
        last_obj = self.get_dsd_x_days_back(1)
        if self.start_price < last_obj.close_price:
            return True
        else:
            return False

    def get_all_dsds_for_last_x_days(self, x):
        all_dsds = [self, ]
        if x == 0:
            return all_dsds
        curr_date = self.date
        last_check_date = curr_date - datetime.timedelta(days=x * 7)
        days_back = 1
        while days_back <= x and curr_date > last_check_date:
            curr_date = curr_date - datetime.timedelta(days=1)
            dsd = DailySymbolData.objects.filter(symbol=self.symbol,
                                                 data_souce=self.data_souce,
                                                 date=curr_date)
            if dsd.exists():
                days_back += 1
                all_dsds.append(dsd.first())
                if days_back == x + 1:
                    return list(reversed(all_dsds))
        return None

    class Meta:
        unique_together = ('symbol', 'date', 'data_souce')


class IndicatorValues(models.Model):
    sma = models.FloatField(default=0, null=True)
    ema = models.FloatField(default=0, null=True)
    dsd = models.ForeignKey(DailySymbolData, on_delete=models.DO_NOTHING, null=True, blank=True)

    def __str__(self):
        return self.dsd.symbol.symbol_code + '(' + str(self.dsd.date) + ')'