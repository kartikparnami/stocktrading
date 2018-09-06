from django.db import models

EXPECTED_STOCK_DIRECTION_CHOICES = (
    ('bullish', 'Bullish - Buy'),
    ('bearish', 'Bearish - Sell'),
    ('uncertain', 'Uncertainity'),
)

# Create your models here.
class ChartStrategy(models.Model):
    strategy_code            = models.CharField(max_length=100, unique=True)
    full_name                = models.CharField(max_length=100, null=True, blank=True)
    source_class_prefix      = models.CharField(max_length=255, null=True, blank=True)
    max_days_history         = models.IntegerField(default=0)
    is_active                = models.BooleanField(default=True)
    expected_stock_direction = models.CharField(max_length=100, choices=EXPECTED_STOCK_DIRECTION_CHOICES)


    def __str__(self):
        return self.full_name + '(' + self.source_class_prefix + ')'
