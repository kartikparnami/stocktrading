from django.db import models

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
    index       = models.ForeignKey(Index, on_delete=models.DO_NOTHING, null=True, blank=True)

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
    start_price = models.FloatField(default=0)
    close_price = models.FloatField(default=0)
    high_price  = models.FloatField(default=0)
    low_price   = models.FloatField(default=0)
    volume      = models.IntegerField(default=0)
    date        = models.DateField(null=True, blank=True)
    high_time   = models.DateTimeField(null=True, blank=True)
    low_time    = models.DateTimeField(null=True, blank=True)
    data_souce  = models.ForeignKey(MarketDataSource, on_delete=models.DO_NOTHING, null=True, blank=True)

    def __str__(self):
        return self.symbol.symbol_code + '(' + str(self.date) + ')'

    class Meta:
        unique_together = ('symbol', 'date', 'data_souce')
