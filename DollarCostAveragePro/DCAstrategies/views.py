from django.http import HttpResponseRedirect, response
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404, redirect, render
from requests import auth
from .models import Strategy, Keys, Orders
from .forms import StrategyForm
from .forms import APIKeyForm
from .forms import PaymentMethodForm
import cbpro
from .tasks import execute_strategies
from decimal import Context, Decimal


# Create your views here.
def home(request):
    activeStrategies = Strategy.objects.filter(is_active__in=[True])
    totalStrategies = len(activeStrategies)
    fulfilledOrders = Orders.objects.filter(is_settled__in=[True]).filter(fees_saved__isnull=False)
    totalOrders = len(fulfilledOrders)
    totalFeesSaved = Decimal(0)
    for order in fulfilledOrders:
        orderFeesSaved = Decimal(str(order.fees_saved))
        totalFeesSaved += orderFeesSaved
    totalFeesSaved = Decimal(round(totalFeesSaved, 2))

    
    user = request.user
    if user.is_authenticated:
        throwaway = Keys.objects.filter(user=user)
    else:
        throwaway = False
    if throwaway:
        APIdoesExist = True
        scope = throwaway[0].scope
        
        if "Transfer" in scope:
            transferPrivs = True
        else:
            transferPrivs = False
        preferredBankAccount = throwaway[0].preferred_payment_method_id
        if preferredBankAccount:
            bankKnown = True
        else:
            bankKnown = False
    else:
        APIdoesExist = False
        transferPrivs = False
        bankKnown = False
    context = {
        "user": user,
        "keyExists": APIdoesExist,
        "transferPrivs": transferPrivs,
        "bankKnown": bankKnown,
        "totalStrategies": totalStrategies,
        "totalOrders": totalOrders,
        "totalFeesSaved": totalFeesSaved,
    }
    return render(request, 'DCAstrategies/home.html', context)

def login(request):
    context = {}
    user = request.user
    if user.is_authenticated:
        return HttpResponseRedirect('/')

    return render(request, 'DCAstrategies/login.html', context)

@login_required
def strategies(request):
    user = request.user
    if user.is_authenticated:
        allStrats = Strategy.objects.filter(user=user)
        throwaway = Keys.objects.filter(user=user)
        if throwaway:
            APIdoesExist = True
        else:
            APIdoesExist = False
        context = {
            "strategies": allStrats,
            "user": user,
            "keyExists": APIdoesExist,
        }
    else:
        context = {
            "user": user,
        }

    return render(request, 'DCAstrategies/strategies.html', context)

@login_required
def make_strategy(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = StrategyForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            order_type = form.cleaned_data['order_type']
            currency = form.cleaned_data['quote_currency']
            amount = form.cleaned_data['amount']
            crypto_product = form.cleaned_data['crypto_product']
            frequency = form.cleaned_data['execution_frequency']
            newStrat = Strategy(order_type=order_type, quote_currency=currency, amount=amount, execution_frequency=frequency, crypto_product=crypto_product)
            newStrat.user = request.user
            newStrat.save()
            newStrat.next_execution_date = newStrat.get_next_execution_date()
            newStrat.full_clean()
            newStrat.save()
            #Run the strategy for the first time when newly made
            execute_strategies(strategy_id = str(newStrat.id))
            # redirect to a new URL:
            return HttpResponseRedirect( '/strategies/')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = StrategyForm()

    return render(request, 'DCAstrategies/make_strategy.html', {'form': form})

@login_required
def editStrategy(request, pk):
    strategy = get_object_or_404(Strategy, pk=pk)
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = StrategyForm(request.POST, instance=strategy)
        # check whether it's valid:
        if form.is_valid():
            order_type = form.cleaned_data['order_type']
            currency = form.cleaned_data['quote_currency']
            amount = form.cleaned_data['amount']
            crypto_product = form.cleaned_data['crypto_product']
            frequency = form.cleaned_data['execution_frequency']
            setattr(strategy, 'order_type', order_type)
            setattr(strategy, 'quote_currency', currency)
            setattr(strategy, 'amount', amount)
            setattr(strategy, 'crypto_product', crypto_product)
            setattr(strategy, 'execution_frequency', frequency)
            strategy.save()
            #Need to recheck execution if frequency changed
            setattr(strategy, 'next_execution_date', strategy.get_next_execution_date())
            strategy.full_clean()
            strategy.save()
            # redirect to a new URL:
            return HttpResponseRedirect( '/strategies/')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = StrategyForm(instance=strategy)
    
    return render(request, 'DCAstrategies/edit_strategy.html', {'form': form})

@login_required
def deleteStrategy(request, pk):
    context = {}

    strategy = get_object_or_404(Strategy, pk=pk)
    if request.method == 'POST':
        strategy.delete()
        return HttpResponseRedirect('/strategies')
    
    return render(request, 'DCAstrategies/delete_strategy.html', context)

@login_required
def pauseStrategy(request, pk):
    context = {}

    strategy = get_object_or_404(Strategy, pk=pk)
    if request.method == 'POST':
        setattr(strategy, 'is_active', False)
        amount = Decimal(str(strategy.amount))
        setattr(strategy, 'amount', amount) #Have to do this for the Decimal 128 problem with Mongo
        strategy.save()
        return HttpResponseRedirect('/strategies')
    
    return render(request, 'DCAstrategies/pause_strategy.html', context)

@login_required
def restartStrategy(request, pk):
    context = {}

    strategy = get_object_or_404(Strategy, pk=pk)
    if request.method == 'POST':
        setattr(strategy, 'is_active', True)
        amount = Decimal(str(strategy.amount))
        setattr(strategy, 'amount', amount) #Have to do this for the Decimal 128 problem with Mongo
        strategy.save()
        return HttpResponseRedirect('/strategies')
    
    return render(request, 'DCAstrategies/restart_strategy.html', context)

@login_required
def APIKey(request):
    user = request.user
    if user.is_authenticated:
        try:
            userKeys = Keys.objects.get(user=user)
        except:
            userKeys = None
        context = {
            "keys": userKeys,
            "user": user,
        }
    else:
        context = {
            "user": user,
        }

    return render(request, 'DCAstrategies/api_key.html', context)

#Function to check the scope allowed by the provided API Key for a specific user and if it is valid
def checkAPIKey(API_key, API_secret, passphrase):
    is_valid = False
    scope = ""

    auth_client = cbpro.AuthenticatedClient(API_key, API_secret, passphrase)
    accounts_response = auth_client.get_accounts()
    
    if 'message' in accounts_response:
        response = False
    else:
        response = True

    print(response)

    if response:
        is_valid = True
        scope += "View; "
        print('Authenticated Connection Made')
    
    checkTransferPermResponse = auth_client.get_payment_methods()

    if 'message' in checkTransferPermResponse:
        checkTransferPerm = False
    else:
        checkTransferPerm = True    

    print(checkTransferPerm)

    if checkTransferPerm:
        scope += "Transfer; "
        print('Verified Transfer Scope')
    else:
        print('Transfer Scope Not Provided')

    #checkTradePermResponse = auth_client.place_limit_order('BTC-USD', 'buy',)


    #Need to check if trade scope is given

    return is_valid, scope

@login_required
def addAPIKey(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = APIKeyForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            API_key = form.cleaned_data['API_key']
            API_secret = form.cleaned_data['API_secret']
            passphrase = form.cleaned_data['passphrase']
            user = request.user
            #check if a connection can be made to the authenticated client and grab accounts
            valid, scope = checkAPIKey(API_key=API_key, API_secret=API_secret, passphrase=passphrase)
            if valid:
                newKey, exists = Keys.objects.get_or_create(user=user)
                setattr(newKey, 'API_key', API_key)
                setattr(newKey, 'API_secret', API_secret)
                setattr(newKey, 'passphrase', passphrase)
                setattr(newKey, 'scope', scope)
                newKey.save()
                return HttpResponseRedirect('/api_key/') 
            else:
                print('Authenticated Connection Not Made')
                return HttpResponse('Unable to connect to Coinbase Pro with the provided values. Please try again!', content_type='text/plain') 
    # if a GET (or any other method) we'll create a blank form
    else:
        form = APIKeyForm()

    return render(request, 'DCAstrategies/add_API_Key.html', {'form': form})

@login_required
def editAPIKey(request, pk):
    apiKey = get_object_or_404(Keys, pk=pk)
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = APIKeyForm(request.POST, instance=apiKey)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            API_key = form.cleaned_data['API_key']
            API_secret = form.cleaned_data['API_secret']
            passphrase = form.cleaned_data['passphrase']
            user = request.user
            #check if a connection can be made to the authenticated client and grab accounts
            valid, scope = checkAPIKey(API_key=API_key, API_secret=API_secret, passphrase=passphrase)
            if valid:
                newKey, exists = Keys.objects.get_or_create(user=user)
                setattr(newKey, 'API_key', API_key)
                setattr(newKey, 'API_secret', API_secret)
                setattr(newKey, 'passphrase', passphrase)
                setattr(newKey, 'scope', scope)
                newKey.save()
                return HttpResponseRedirect('/api_key/') 
            else:
                print('Authenticated Connection Not Made')
                return HttpResponse('Unable to connect to Coinbase Pro with the provided values. Please try again!', content_type='text/plain') 
    # if a GET (or any other method) we'll create a blank form
    else:
        form = APIKeyForm(instance=apiKey)
    
    return render(request, 'DCAstrategies/add_api_key.html', {'form': form})

@login_required
def deleteAPIKey(request, pk):
    context = {}

    apiKey = get_object_or_404(Keys, pk=pk)
    if request.method == 'POST':
        apiKey.delete()
        return HttpResponseRedirect('/api_key')
    
    return render(request, 'DCAstrategies/delete_API_key.html', context)

@login_required
def addPaymentMethod(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = PaymentMethodForm(data=request.POST, request=request, user=request.user)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            user = request.user
            keyObject = Keys.objects.get(user=user)
            payMethod = form.cleaned_data['preferred_payment_method']
            #add the new payment method to the existing key object
            setattr(keyObject, 'preferred_payment_method_id', payMethod)
            auth_client = cbpro.AuthenticatedClient(keyObject.API_key, keyObject.API_secret, keyObject.passphrase)
            accounts = auth_client.get_payment_methods()
            for num in accounts:
                if num['id'] == payMethod:
                    bankName = num['name']
                    break
            setattr(keyObject, 'preferred_payment_method_name', bankName)
            keyObject.full_clean()
            keyObject.save()
            return HttpResponseRedirect('/api_key/') 
    # if a GET (or any other method) we'll create a blank form
    else:
        form = PaymentMethodForm(request=request, user=request.user)

    return render(request, 'DCAstrategies/add_payment_method.html', {'form': form})

@login_required
def deleteAccount(request):
    context = {}
    pk = request.user.pk

    if request.method == 'POST':
        auth_logout(request)
        User = get_user_model()
        User.objects.filter(pk=pk).delete()
        return HttpResponseRedirect('/')
    
    return render(request, 'DCAstrategies/delete_account.html', context)