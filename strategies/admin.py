from django.contrib import admin

from strategies.models import *


class ChartStrategyAdmin(admin.ModelAdmin):

    list_display = ('strategy_code',
                    'full_name',
                    'source_class_prefix',
                    'max_days_history',
                    'is_active',
                    'expected_stock_direction')
    search_fields = ['strategy_code']
    list_filter = (
        'max_days_history',
        'is_active',
        'expected_stock_direction',
    )


admin.site.register(ChartStrategy, ChartStrategyAdmin)
