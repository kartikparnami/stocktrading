from django.shortcuts   import render

from market_simulator.models import Symbol
from order_entry.forms       import LongPositionBuyOrderForm, LongPositionSellOrderForm
from order_entry.models      import LongPosition


def handle_long_position_buy_order(form):
    existing_symbol_long_position = LongPosition.objects.filter(
        symbol__symbol_code=form.cleaned_data['symbol'],
        is_open=True
    ).first()
    if not existing_symbol_long_position:
        existing_symbol_long_position = LongPosition.objects.create(
            symbol=Symbol.objects.get(symbol_code=form.cleaned_data['symbol'], index__index_code='NSE')
        )
    existing_symbol_long_position.buy(form.cleaned_data['price'], form.cleaned_data['quantity'])


def handle_long_position_sell_order(form):
    existing_symbol_long_position = LongPosition.objects.filter(
        symbol__symbol_code=form.cleaned_data['symbol'],
        is_open=True
    ).first()
    if existing_symbol_long_position:
        existing_symbol_long_position.sell(form.cleaned_data['price'], form.cleaned_data['quantity'])


def long_position_buy_order(request):
    if request.method == 'POST':
        form = LongPositionBuyOrderForm(request.POST)
        if form.is_valid():
            handle_long_position_buy_order(form)
    else:
        form = LongPositionBuyOrderForm()
    return render(request, 'order_entry/long_position_buy_order.html', {'form': form})


def long_position_sell_order(request):
    if request.method == 'POST':
        form = LongPositionSellOrderForm(request.POST)
        if form.is_valid():
            handle_long_position_sell_order(form)
    else:
        form = LongPositionSellOrderForm()
    return render(request, 'order_entry/long_position_sell_order.html', {'form': form})
