from django                  import forms
from market_simulator.models import Symbol


def get_all_symbol_codes():
    symbol_codes = []
    symbol_codes = Symbol.objects.filter(is_active=True).values_list('symbol_code', flat=True)
    return [(code, code) for code in symbol_codes]


class LongPositionBuyOrderForm(forms.Form):
    symbol = forms.ChoiceField(choices=get_all_symbol_codes(), required=True)
    price = forms.FloatField(required=True)
    quantity = forms.IntegerField(required=True)


class LongPositionSellOrderForm(forms.Form):
    symbol = forms.ChoiceField(choices=get_all_symbol_codes(), required=True)
    price = forms.FloatField(required=True)
    quantity = forms.IntegerField(required=True)
