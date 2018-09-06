from django.contrib     import admin
from order_entry.models import *


class LongPositionAdmin(admin.ModelAdmin):

    list_display = ('symbol',
                    'avg_price',
                    'profit_or_loss',
                    'curr_quantity',
                    'initial_quantity',
                    'is_open')
    search_fields = ['symbol__symbol_code']
    list_filter = (
        'is_open',
        'symbol',
    )

admin.site.register(LongPosition, LongPositionAdmin)
