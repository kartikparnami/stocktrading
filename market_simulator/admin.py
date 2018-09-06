from django.contrib import admin

from market_simulator.models import *


class CountryAdmin(admin.ModelAdmin):

    list_display = ('country_code',
                    'full_name')
    search_fields = ['country_code',
                     'full_name']
    list_filter = (
        'country_code',
    )


class IndexAdmin(admin.ModelAdmin):

    list_display = ('index_code',
                    'full_name',
                    'country')
    search_fields = ['index_code',
                     'full_name',
                     'country__country_code']
    list_filter = (
        'index_code',
    )


class SymbolAdmin(admin.ModelAdmin):

    list_display = ('symbol_code',
                    'full_name',
                    'sector',
                    'is_active',
                    'index')
    search_fields = ['index__index_code',
                     'sector',
                     'full_name',
                     'symbol_code']
    list_filter = (
        'is_active',
        'sector',
    )


class MarketDataSourceAdmin(admin.ModelAdmin):

    list_display = ('market_data_source_code',
                    'full_name',
                    'source_class_prefix')
    search_fields = ['market_data_source_code',
                     'full_name']
    list_filter = (
        'market_data_source_code',
    )


class DailySymbolDataAdmin(admin.ModelAdmin):

    list_display = ('symbol',
                    'date',
                    'start_price',
                    'close_price',
                    'high_price',
                    'low_price',
                    'volume',
                    'data_souce')
    search_fields = ['symbol__symbol_code',
                     'data_souce__market_data_source_code']
    list_filter = (
        'symbol__symbol_code',
        'data_souce__market_data_source_code',
    )
    raw_id_fields = ('symbol',
                     'data_souce')


# Register your models here.
admin.site.register(Country, CountryAdmin)
admin.site.register(Index, IndexAdmin)
admin.site.register(Symbol, SymbolAdmin)
admin.site.register(DailySymbolData, DailySymbolDataAdmin)
admin.site.register(MarketDataSource, MarketDataSourceAdmin)
