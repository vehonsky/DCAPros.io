from django.forms import ModelForm
from django.forms import widgets
from django.forms.widgets import ChoiceWidget
import floppyforms.__future__ as forms
from floppyforms.widgets import Input, RangeInput, Select
import requests
from .models import ORDER_CHOICES, Strategy
from .models import Keys, Orders, CryptoProducts, Profile
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
import cbpro
from operator import itemgetter

def get_crypto_choices_form():
    quote_currency = "USD"
    existing_cryptos = CryptoProducts.objects.filter(trading_disabled__in=[False]).filter(quote_currency=quote_currency)
    choices = set()
    for crypto in existing_cryptos:
        new_tuple = crypto.base_currency
        choices.add(new_tuple)
    
    return choices

CRYPTO_CHOICES = get_crypto_choices_form()

def get_order_type_choices_form(user_id):
    ORDER_CHOICES = set()
    try:
        user_profile = Profile.objects.get(user=user_id)
    except Profile.DoesNotExist:
        ORDER_CHOICES.add(("market", "Market"))
        ORDER_CHOICES.add(("test", "Test"))
        return ORDER_CHOICES

    if user_profile.is_pro:
        ORDER_CHOICES.add(("limit", "Limit"))
        ORDER_CHOICES.add(("ladder", "Ladder"))

    ORDER_CHOICES.add(("test", "Test"))
    return ORDER_CHOICES


#class datalist(ChoiceWidget):
#    input_type = 'text'
#    template_name = 'DCAstrategies/forms/datalist.html'
#    option_template_name = 'django/forms/widgets/select_option.html'
#    option_inherits_attrs = False

    #def __init__(self, attrs=None, choices={('-----','-----')}):
    #    super().__init__(attrs, choices)

class StrategyForm(ModelForm):

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        self.user = kwargs.pop('user', None)
        super(StrategyForm, self).__init__(*args, **kwargs)

        ORDER_CHOICES = get_order_type_choices_form(self.user)

        self.fields['order_type'] = forms.ChoiceField(
                choices=sorted(ORDER_CHOICES, key=itemgetter(0)), 
                label='<strong>Choose the Type of Order</strong>',
                help_text="Orders reference the market price at the time of execution.",
                )
        
        self.fields['percent_picker'] = forms.IntegerField(
                widget = RangeInput(attrs={'min': '0', 'max': '10', 'step': 1,'disabled' : "disabled"},),
                label='<strong>Percent Below Market Price:</strong>',
                )
        self.fields['percent_picker'].required = False

        self.helper = FormHelper()
        self.helper.form_class = 'bootstrap5'
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            'crypto_product',
            Row(
                Column('order_type', css_class='form-group col-md-6'),
                Column('percent_picker', css_class='form-group col-md-6'),
            ),
            Row(
                Column('amount', css_class='form-group col-md-4'),
                Column('quote_currency', css_class='form-group col-md-4'),
                Column('execution_frequency', css_class='form-group col-md-4'),
            ),
            Submit('submit', 'Save Strategy'),
        )

    class Meta:
        model = Strategy
        fields = ['quote_currency', 'amount', 'execution_frequency','crypto_product']
        labels = {
            'quote_currency': '<strong>Currency</strong>',
            'amount': '<strong>Amount</strong>',
            'execution_frequency': '<strong>Execution Frequency</strong>',
            'crypto_product': '<strong>Choose Your Crypto</strong>',
        }
        widgets = {
            'crypto_product': Input(datalist=CRYPTO_CHOICES, attrs={'placeholder': 'Enter a crypto ticker...', },),
        }

    order_type = forms.ChoiceField(
        choices={},
        label='<strong>Choose the Type of Order</strong>',
        )
    
    percent_picker = forms.IntegerField(
        widget = RangeInput(attrs={'min': '0', 'max': '10', 'step': 1,'disabled' : "disabled"}, ), #'disabled': 'True'},),
        label='<strong>Percent Below Market Price:</strong>',
        )


class APIKeyForm(ModelForm):
    #def __init__(self, *args, **kwargs):
    #        super().__init__(*args, **kwargs)
    #        self.helper = FormHelper()
    #        self.helper.layout = Layout(
    #            Row(
    #                Column('passphrase', css_class='form-group col-md-2 mb-0'),
    #                Column('API_key', css_class='form-group col-md-2 mb-0'),
    #                css_class='form-row'
    #            ),
    #            'API_secret',
    #            Submit('submit', 'Sign in')
    #        )

    class Meta:
        model = Keys
        fields = ['passphrase', 'API_secret','API_key']
        labels = {
            'passphrase': '<strong>Passphrase</strong>',
            'API_secret': '<strong>API Secret</strong>',
            'API_key': '<strong>API Key</strong>',
        }
        widgets = {
            'passphrase': forms.TextInput(attrs={'placeholder': 'Enter the Passphrase for Your API Key from Coinbase Pro',}),
            'API_secret': forms.TextInput(attrs={'placeholder': 'Enter the API Secret for Your API Key from Coinbase Pro'}),
            'API_key': forms.TextInput(attrs={'placeholder': 'Enter the API Key from Coinbase Pro'})
        }


class PaymentMethodForm(forms.Form):
    
    #Initializes the form with the request so the form can access request.user to pull from a DB object
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        self.user = kwargs.pop('user', None)
        super(PaymentMethodForm, self).__init__(*args, **kwargs)

        METHOD_CHOICES = set()
        try:
            userKey = Keys.objects.get(user=self.user) #can use get instead of filter because it is 1:1 field relation

            #Make an authenticated client for this user to grab the payment methods available to them
            auth_client = cbpro.AuthenticatedClient(userKey.API_key, userKey.API_secret, userKey.passphrase)
            
            #Grab the user's payment methods attached to their CB Pro account
            payMethods = auth_client.get_payment_methods()
            
            for account in payMethods:
                METHOD_CHOICES.add((account['id'], account['name']))
            self.fields['preferred_payment_method'] = forms.ChoiceField(
                choices=METHOD_CHOICES, 
                label='<strong>Choose a payment method:</strong>',
                )
        except:
            print('Couldnt make connection')

    preferred_payment_method = forms.ChoiceField(
        choices={},
        label='<strong>Choose a payment method:</strong>',
        )
