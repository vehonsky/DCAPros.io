from django.db import models
from django.db.models.aggregates import Max
from django.db.models.deletion import CASCADE
from django.db.models.fields.related import ForeignKey
from django.contrib.auth.models import User
from django.apps import apps
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid, datetime
from decimal import Decimal
from . import functions


#Below starts the actual models


ORDER_CHOICES = {
    ("market", "Market"),
    ("limit", "Limit"), #Limit and ladder should only be for Pro Users
    ("ladder", "Ladder"), #Add a ladder type of trade eventually
}

#Choices for the local currency of the user
CURRENCY_CHOICES = {
    ("USD","US Dollars"),
    ("EUR","Euros"),
    ("GBP","British Pounds"),
}

#Frequency choice for how often the strategy executes
FREQUENCY_CHOICES = {
    ("day","Daily"),
    ("wk","Weekly"),
    ("bimo","BiMonthly"),
    ("mo","Monthly"),
}

class Profile(models.Model):
    id = models.UUIDField(
        primary_key=True,
        editable=False,
        default=uuid.uuid4
    )

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
    )

    is_pro = models.BooleanField(default=False)

class Keys(models.Model):
    id = models.UUIDField(
        primary_key=True,
        editable=False,
        default=uuid.uuid4
    )

    #Only one "keys" model can be attributed to each user
    user = models.OneToOneField(
        User,
        on_delete = models.CASCADE,
    )

    API_secret = models.CharField(max_length=350)
    API_key = models.CharField(max_length=350)
    passphrase = models.CharField(max_length=100)
    scope = models.CharField(max_length=100, default="View; Transfer; Trade;")
    preferred_payment_method_id = models.CharField(max_length=100, blank=True, null=True, default="")
    preferred_payment_method_name = models.CharField(max_length=100, blank=True, null=True, default="")


class CryptoProducts(models.Model):
    #The market ID given by Coinbase e.g. "BTC-USD"
    id = models.CharField(
        max_length=15,
        primary_key=True,
        editable=False,
    )

    #The market pair name displayed to the Coinbase user on their UI e.g. "BTC/USD"
    display_name = models.CharField(max_length=100)

    #The shorthand name for the crypto being sold as xyz/USD e.g. "xyz"
    base_currency = models.CharField(max_length=100)

    #The currency that is used as the quoted price e.g. "USD"
    quote_currency = models.CharField(max_length=100)

    #The smallest divisible amount for the base_currency in question e.g. 0.000000000001 BTC, orders must be a multiple of this > base_min_size
    base_increment = models.CharField(max_length=100)

    #The smallest divisible amount for an order submission for the quote_currency in question e.g. 0.01 USD
    quote_increment = models.CharField(max_length=100)

    #The smallest and largest amounts of a base_currency that can be bought on Coinbase in that market ID
    base_min_size = models.CharField(max_length=100)
    base_max_size = models.CharField(max_length=100)

    #Minimum and maximum of the quote_currency that can be used in a market order
    min_market_funds = models.CharField(max_length=100)
    max_market_funds = models.CharField(max_length=100)

    #The statuses of the trading pair in question, these are the most likely to change e.g. XRP is no longer tradeable
    status = models.CharField(max_length=100)
    status_message = models.CharField(max_length=1000, blank=True)
    cancel_only = models.BooleanField(default=False)
    limit_only = models.BooleanField(default=False)
    post_only = models.BooleanField(default=False)
    trading_disabled = models.BooleanField(default=False)
    fx_stablecoin = models.BooleanField(default=False)
    margin_enabled = models.BooleanField(default=False)

    class Meta:
        ordering = ['base_currency']


def get_crypto_choices():
    quote_currency = "USD"
    existing_cryptos = CryptoProducts.objects.filter(trading_disabled__in=[False]).filter(quote_currency=quote_currency)
    choices = set()
    for crypto in existing_cryptos:
        new_tuple = (crypto.base_currency, crypto.base_currency)
        choices.add(new_tuple)
    
    return choices

CRYPTO_CHOICES = get_crypto_choices()

# Create your models here.
class Strategy(models.Model):

    def get_next_execution_date(self):
        #Grab the strategy model
        #strategy = apps.get_model(app_label='DCAstrategies', model_name='strategy')
    
        frequency = self.execution_frequency
        if frequency == "day":
            delta = 1
        elif frequency == "wk":
            delta = 7
        elif frequency == "bimo":
            delta = 15
        elif frequency == "mo":
            delta = 30
        else:
            delta = 1

        if self.last_execution_date:
            next_execution_date = self.last_execution_date + datetime.timedelta(days = delta)
        else:
            next_execution_date = self.start_date + datetime.timedelta(days = delta)
        
        return next_execution_date

    #def __init__(self):
    #    self.next_execution_date = self.get_next_execution_date()

    #Unique, complex ID of each strategy created by a user
    id = models.UUIDField(
        primary_key=True,
        editable=False,
        default=uuid.uuid4
    )

    #Many strategies can be attributed to one user
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    #Local currency of the user as selected by them from currency_choices
    quote_currency = models.CharField(max_length=10, choices=CURRENCY_CHOICES, default = "USD")

    #Amount of local currency to be used in the strategy, default is 10.00
    amount = models.DecimalField(max_digits=10, 
                                decimal_places=2, 
                                default=Decimal(10.00), 
                                validators=[
                                    MaxValueValidator(Decimal(35000)),
                                    MinValueValidator(Decimal(10)),
                                ],
                                )

    #The crypto currency that the strategy is intended for
    crypto_product = models.CharField(max_length=30, choices=CRYPTO_CHOICES,)

    #The type of order to be executed on CB Pro
    order_type = models.CharField(max_length=30, choices=ORDER_CHOICES, default="market")

    #Frequency that strategy is executed on from frequency_choices
    execution_frequency = models.CharField(max_length=100, choices=FREQUENCY_CHOICES, default="day")

    #Number of times the strategy has been executed
    execution_count = models.IntegerField(default=0)

    #Date and time the strategy was commited by the user
    start_date = models.DateTimeField(auto_now_add=True, editable=False)

    #Date and time that the strategy was last executed
    last_execution_date = models.DateTimeField(blank=True, null=True)

    #Date and time that the strategy will be executed next
    next_execution_date = models.DateTimeField(blank=True, null=True)

    #Check to see that the user has not paused this specific strategy (i.e. it is an active strategy)
    is_active = models.BooleanField(default=True)

    #Marks whether or not a strategy needs to be executed (it is separate so initiated strategies can be run right away)
    execution_needed = models.BooleanField(default=False)

    #Lists any errors attributed to running this strategy
    has_error = models.BooleanField(default=False)
    error_desc = models.CharField(max_length=250, default="", blank=True)

    class Meta:
        ordering = ["next_execution_date"]

    def __str__(self):
        return str(self.id)

    
class Orders(models.Model):

    #Unique, complex ID of each order created by a executed strategy
    id = models.UUIDField(
        primary_key=True,
        editable=False,
        default=uuid.uuid4
    )

    #Many orders can be attributed to one strategy
    strategy = models.ForeignKey(Strategy, on_delete=models.DO_NOTHING, null=True, blank=True)

    #Coinbase Pro order number/identifier for this order in case it needs to be pulled again
    coinbase_id = models.CharField(max_length=255, 
                                    blank=True, 
                                    null=True,
                                    )

    #Date and time that the order was submitted
    submission_date = models.CharField(max_length=100, blank=True, null=True)

    #Boolean check to see if it is still active and needing to be filled
    is_settled = models.BooleanField(default=False, blank=True, null=True)

    #Status message provided by coinbase
    status = models.CharField(max_length=200, default="pending", blank=True)

    #Date and time that the order was filled on Coinbase Pro (can be blank if it is still active)
    fulfilled_date = models.CharField(max_length=100, blank=True, null=True)

    #Order type when submitted
    order_type = models.CharField(max_length=50, default="market")

    #The price the order was submitted with
    price = models.DecimalField(max_digits=15, decimal_places=6, null=True, blank=True)

    #The cryptocurrency that is being bought for these orders, straight from the strategy model
    product_id = models.CharField(max_length=15, blank=True, null=True)

    #Amount of coins/tokens the order was made for
    volume = models.DecimalField(max_digits=50, decimal_places=10, null=True, blank=True)

    #Actual execution value of the order (needed for limits)
    executed_value = models.DecimalField(max_digits=50, decimal_places=10, null=True, blank=True)

    #Fees charged for this order
    fees = models.DecimalField(max_digits=15, decimal_places=6, null=True, blank=True)

    #Fees saved by using CB Pro vs. Regular Coinbase
    fees_saved = models.DecimalField(max_digits=15, decimal_places=6, null=True, blank=True)

    #To check that an order wasn't deleted by the user on CBPro interface
    still_exists = models.BooleanField(default=True, blank=True, null=True)
