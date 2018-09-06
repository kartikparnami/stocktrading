from django.db               import models
from market_simulator.models import Symbol


# Create your models here.
class LongPosition(models.Model):
    symbol = models.ForeignKey(Symbol, on_delete=models.DO_NOTHING, null=True, blank=True)
    avg_price = models.FloatField(default=0)
    profit_or_loss = models.FloatField(default=0)
    curr_quantity = models.IntegerField(default=0)
    initial_quantity = models.IntegerField(default=0)
    is_open = models.NullBooleanField(default=None)

    def sell(self, sell_price, quantity):
        if self.curr_quantity and self.curr_quantity >= quantity:
            self.curr_quantity = self.curr_quantity - quantity
            self.profit_or_loss += (sell_price - self.avg_price) * quantity
            if self.curr_quantity == 0:
                self.is_open = False
        else:
            raise Exception('Cannot sell a long position which has not been bought yet or sell more than you hold.')
        self.save()

    def buy(self, buy_price, quantity):
        self.avg_price = (((self.avg_price * self.curr_quantity) + (buy_price * quantity))/(self.curr_quantity + quantity))
        self.curr_quantity = self.curr_quantity + quantity
        self.is_open = True
        self.initial_quantity = self.curr_quantity
        self.save()

    def __str__(self):
        return (self.symbol.symbol_code +
                ' - ' +
                str(self.avg_price) +
                ' (' +
                str(self.curr_quantity) +
                ')' +
                ' - ' +
                (str(self.profit_or_loss) if self.profit_or_loss >= 0 else '(' + str(abs(self.profit_or_loss)) + ')'))


class ShortPosition(models.Model):
    symbol = models.ForeignKey(Symbol, on_delete=models.DO_NOTHING, null=True, blank=True)
    avg_price = models.FloatField(default=0)
    profit_or_loss = models.FloatField(default=0)
    curr_quantity = models.IntegerField(default=0)
    is_open = models.NullBooleanField(default=None)

    def buy(self, buy_price, quantity):
        if self.curr_quantity:
            self.curr_quantity = self.curr_quantity - quantity
            self.profit_or_loss += (self.avg_price - buy_price) * quantity
            if self.curr_quantity == 0:
                self.is_open = False
        else:
            raise Exception('Cannot sell a long position which has not been bought yet.')
        self.save()
