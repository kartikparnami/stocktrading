from django.contrib import admin

from market_simulator.models import *

# Register your models here.
admin.site.register(Country)
admin.site.register(Index)
admin.site.register(Symbol)
admin.site.register(DailySymbolData)
admin.site.register(MarketDataSource)
