from background_task import background
import cbpro, os, time, datetime
from .models import CryptoProducts, Strategy, Keys, Orders
from django.db.models import Q
from decimal import Decimal
from dateutil import parser
from .functions import decrypt_before_use, encrypt_before_storing

#Below are the background tasks that will be run by the server

@background(schedule=10, queue='crypto_product_refresh', remove_existing_tasks=True)
def get_CB_crypto_products():
    start = datetime.datetime.now()
    t_start = time.time()
    print('----------- Start of Crypto Product Check ----------- Time: ' + start.strftime("%d-%b-%Y (%H:%M:%S.%f)"))
    #First make a public client connection
    pub_client = cbpro.PublicClient()
    print("Public Connection Made")
    cryptos = pub_client.get_products()
    print("Received crypto products from Coinbase Pro Public API")
    print("Starting to update DB for Available Cryptos (Total Cryptos: " + str(len(cryptos)) + ")")
    count = 1
    for crypto in cryptos:
        print("Working on Crypto migration to DB: (" + str(count) + "/" + str(len(cryptos)) + ")")
        for item in crypto:
            if item == 'id':
                newCryptoObject, doesExist = CryptoProducts.objects.get_or_create(id = str(crypto[item]))
            else:
                #Sets all the attributes in the CryptoProducts model object to the newly acquired data from CB
                setattr(newCryptoObject, item, crypto[item])
                newCryptoObject.save()
        count += 1
    print("Finished parsing out all crypto products")
    t_finish = time.time()
    print("Total elapsed time: " + str(t_finish - t_start))
    print('----------- End of Crypto Product Check -----------')
    
@background(schedule=5, queue='promote_strategy', remove_existing_tasks=True)
def get_strategies_for_execution():
    start = datetime.datetime.now()
    t_start = time.time()
    print('----------- Start of Strategy Promotion ----------- Time: ' + start.strftime("%d-%b-%Y (%H:%M:%S.%f)"))
    print('Finding all strategies that need to be executed!')
    now = datetime.datetime.now()
    print('The current time is: ' + str(now))

    #First, need to get all strategy objects that have an execution date that is less than the current time and is active
    ready_strats = Strategy.objects.filter(is_active__in=[True]).filter(execution_needed__in=[False]).filter(Q(next_execution_date__lte=now), Q(next_execution_date__lt=now))
    print('Number of strategies ready to be promoted: ' + str(len(ready_strats)))

    count = 1
    for item in ready_strats:
        amount = Decimal(str(item.amount))
        print('Promoting strategy ' + str(count) + '/' + str(len(ready_strats)))
        setattr(item, 'execution_needed', True)
        setattr(item, 'amount', amount)
        item.full_clean()
        item.save()
        execute_strategies(strategy_id = str(item.id))
        count += 1

    
    print('Finished promoting all active strategies that need to be executed')
    t_finish = time.time()
    print("Total elapsed time: " + str(t_finish - t_start))
    print('----------- End of Strategy Promotion -----------')

@background(schedule=10, queue='execute_strategy', remove_existing_tasks=True)
def execute_strategies(strategy_id):
    start = datetime.datetime.now()
    t_start = time.time()
    print('----------- Start of Strategy Execution ----------- Time: ' + start.strftime("%d-%b-%Y (%H:%M:%S.%f)"))
    error_this_time = False

    #Get promoted strategies
    strategy = Strategy.objects.get(pk=strategy_id)
    print('Executing strategy: ' + str(strategy_id))

    #Update the last execution date of the strategy as the current datetime
    full_execution_time = datetime.datetime.now()
    setattr(strategy, 'last_execution_date', full_execution_time)
    amount = Decimal(str(strategy.amount))
    setattr(strategy, 'amount', amount) #Have to do this for the Decimal 128 problem with Mongo
    strategy.save()
    print('Updated the last execution date of this strategy')

    #Set the next execution date for this strategy based on the last execution date
    setattr(strategy, 'next_execution_date', strategy.get_next_execution_date())
    
    #Reset the execution needed value to false in the strategy after everything else is done
    setattr(strategy, 'execution_needed', False)
    amount = Decimal(str(strategy.amount))
    setattr(strategy, 'amount', amount) #Have to do this for the Decimal 128 problem with Mongo
    strategy.save()
    strategy.full_clean()
    strategy.save()
    print('Updated the next execution date and reset the execution status of this strategy')

    #Take the user of each strategy and get that user's API Keys if they exist
    count = 1
    if strategy:
        print('Getting API Key for User of Strategy ' + str(strategy_id))
        thisUser = strategy.user
        try:
            apiKey = Keys.objects.get(user=thisUser)
        except Keys.DoesNotExist:
            print('No API Key currently exists for this user. Adding this to strategy error code')
            setattr(strategy, 'has_error', True)
            setattr(strategy, 'error_desc', 'API Key has not been provided')
            error_this_time = True
        
        #Check scope of api key for transfer clause
        hasTransferPriv = 'Transfer' in apiKey.scope
        
        #Make the auth client for the rest of the time
        dec_secret = decrypt_before_use(apiKey.API_secret)
        dec_passphrase = decrypt_before_use(apiKey.passphrase)
        auth_client = cbpro.AuthenticatedClient(key=apiKey.API_key, b64secret=dec_secret, passphrase=dec_passphrase)

        #If API key has transfer scope, then do deposit of amount from strategy using preferred payment method
        if hasTransferPriv:
            print('This user does have scope to perform a deposit!')
            print('Depositing funds to user account for the intended strategy')
            payment_method_id = apiKey.preferred_payment_method_id
            print('Got the payment method: ' + str(payment_method_id))
            deposit_amount = str(strategy.amount)
            deposit_currency = strategy.quote_currency
            print('Got the amount requested: ' + str(deposit_amount) + ' ' + str(deposit_currency))
            deposit_response=auth_client.deposit(amount=deposit_amount, currency=deposit_currency, payment_method_id=payment_method_id)
            print(deposit_response)
            print('Finished depositing funds to user account for this strategy')
            time.sleep(30)

        #Regardless of transfer scope, check account available balance in currency of strategy, and send order for that strategy
        accounts = auth_client.get_accounts()
        for account in accounts:
            if account['currency'] == strategy.quote_currency:
                desired_account = account
        
        print(desired_account)
        availableFunds = desired_account['available']
        print(availableFunds)

        has_enough_funds = Decimal(str(availableFunds)) > Decimal(str(strategy.amount))
        
        if has_enough_funds:
            print('The account has the available funds to submit the order for strategy: ' + str(strategy))
            print('Submitting the order of this strategy')

            #Check what kind of order type to submit
            if strategy.order_type == 'market':
                try:
                    product_id = str(strategy.crypto_product) + '-' + str(strategy.quote_currency)
                    order_side = 'buy'
                    order_amount = str(strategy.amount)

                    print('Submitting market order per the strategy intent for ' + str(order_amount) + ' ' + str(strategy.quote_currency) + ' of the trading pair ' + str(product_id))

                    order_response = auth_client.place_market_order(product_id=product_id, side=order_side, funds=order_amount, overdraft_enabled=False)
                    print(order_response)
                except:
                    print('There was an error while submitting the order')
                    setattr(strategy, 'has_error', True)
                    setattr(strategy, 'error_desc', 'Error with order submission from DCAPros')
                    error_this_time = True
                    pass
            elif strategy.order_type == 'limit':
                try:
                    product_id = str(strategy.crypto_product) + '-' + str(strategy.quote_currency)
                    order_side = 'buy'
                    order_amount = str(strategy.amount)
                    print('Submitting limit order per the strategy intent')
                except:
                    print('There was an error while submitting the order')
                    setattr(strategy, 'has_error', True)
                    setattr(strategy, 'error_desc', 'Error with order submission from DCAPros')
                    error_this_time = True
                    pass
            elif strategy.order_type == 'ladder':
                try:
                    product_id = str(strategy.crypto_product) + '-' + str(strategy.quote_currency)
                    order_side = 'buy'
                    order_amount = str(strategy.amount)
                    print('Submitting a ladder of limit orders per the strategy intent')
                except:
                    print('There was an error while submitting the order')
                    setattr(strategy, 'has_error', True)
                    setattr(strategy, 'error_desc', 'Error with order submission from DCAPros')
                    error_this_time = True
                    pass

        else:
            print('There are not enough funds to complete the current strategy: ' + str(strategy))
            setattr(strategy, 'has_error', True)
            setattr(strategy, 'error_desc', 'Not enough funds in user account to complete order')
            error_this_time = True
        #Take in order information from Coinbase API response and save a new model instance referencing the strategy that was used

        if order_response:
            if not 'message' in order_response: #If there is a message, then there was an error from the API Key or connection
                try:
                    if strategy.order_type == 'market':
                        newOrder = Orders.objects.create(strategy=strategy, coinbase_id=order_response['id'])
                        print('Adding Coinbase order ID')
                        print(order_response['id'])
                        setattr(newOrder, 'coinbase_id', order_response['id'])
                        newOrder.save()
                        print('Adding Coinbase product ID')
                        setattr(newOrder, 'product_id', order_response['product_id'])
                        newOrder.save()
                        print('Adding order type')
                        setattr(newOrder, 'order_type', order_response['type'])
                        newOrder.save()
                        print('Adding status')
                        setattr(newOrder, 'status', 'pending')
                        newOrder.save()
                        print('Adding creation date as a string')
                        setattr(newOrder, 'submission_date', order_response['created_at'])
                        newOrder.save()
                        print('Saved the order response information from CoinBase Pro')
                    elif strategy.order_type == 'limit':
                        newOrder = Orders.objects.create(strategy=strategy, coinbase_id=order_response['id'])
                        print('Adding Coinbase order ID')
                        setattr(newOrder, 'coinbase_id', order_response['id'])
                        newOrder.save()
                        print('Adding Coinbase product ID')
                        setattr(newOrder, 'product_id', order_response['product_id'])
                        newOrder.save()
                        print('Adding order type')
                        setattr(newOrder, 'order_type', order_response['type'])
                        newOrder.save()
                        print('Adding intended limit price')
                        setattr(newOrder, 'price', order_response['price'])
                        newOrder.save()
                        print('Adding volume of the trade')
                        setattr(newOrder, 'volume', order_response['size'])
                        newOrder.save()
                        print('Adding the status of the trade')
                        setattr(newOrder, 'status', 'pending')
                        newOrder.save()
                        print('Adding creation date as a string')
                        setattr(newOrder, 'submission_date', order_response['created_at'])
                        newOrder.save()
                        print('Saved the order response information from CoinBase Pro')
                except:
                    print('Order created but could not save its attributes')
                    setattr(strategy, 'has_error', True)
                    setattr(strategy, 'error_desc', 'Could not save order information')
                    error_this_time = True
                    pass
            else:
                print('There was an issue with the order submission to CoinBase')
                setattr(strategy, 'has_error', True)
                setattr(strategy, 'error_desc', 'Failed Order: ' + str(order_response['message']))
                error_this_time = True

        #Reset the error component if runs smoothly
        if not error_this_time:
            setattr(strategy, 'has_error', False)
            setattr(strategy, 'error_desc', '')
            setattr(strategy, 'amount', amount) #Have to do this for the Decimal 128 problem with Mongo
            strategy.save()
            strategy.full_clean()
            strategy.save()

    t_finish = time.time()
    print("Total elapsed time: " + str(t_finish - t_start))
    print('----------- End of Strategy Execution -----------')


@background(schedule=10, queue='check_orders', remove_existing_tasks=True)
def checkOrders():
    start = datetime.datetime.now()
    t_start = time.time()
    print('----------- Start of Order Check ----------- Time: ' + start.strftime("%d-%b-%Y (%H:%M:%S.%f)"))

    #Get all orders that are still marked as unsettled (these are the only ones needed to be updated potentially), note it can give 404 response if the order was cancelled
    ordersToCheck = Orders.objects.filter(is_settled__in=[False])

    count = 1
    #Iterate through orders and ping CBPro for a message about that specific order ID, then update accordingly
    for order in ordersToCheck:
        print('----------- Working on Order ' + str(count) + '/' + str(len(ordersToCheck)) + ' -----------')
        #Try to get the strategy that it came from so it can get the API key from its user
        try:
            strategyUsed = Strategy.objects.get(id=order.strategy_id)
        except Strategy.DoesNotExist:
            print('Strategy used for this order was deleted')
            continue

        user = strategyUsed.user

        try: #In case they deleted their API key since making the orders/strategy
            apiKey = Keys.objects.get(user=user)
        except Keys.DoesNotExist:
            print('No API Key currently exists for this user. Adding this to strategy error code')
            #error_this_time = True
            continue

        dec_secret = decrypt_before_use(apiKey.API_secret)
        dec_passphrase = decrypt_before_use(apiKey.passphrase)
        auth_client = cbpro.AuthenticatedClient(key=apiKey.API_key, b64secret=dec_secret, passphrase=dec_passphrase)

        order_response = auth_client.get_order(order.coinbase_id)
        print(order_response)

        if not 'message' in order_response:
            if order_response['type'] == 'market':
                print('Updating creation date as a string')
                setattr(order, 'submission_date', order_response['created_at'])
                
                print('Updating status')
                setattr(order, 'status', order_response['status'])
                
                print('Updating Volume')
                setattr(order, 'volume', Decimal(str(order_response['filled_size'])))
                
                print('Updating Executed Value')
                setattr(order, 'executed_value', Decimal(str(order_response['executed_value'])))
                
                print('Updating Fees Taken')
                setattr(order, 'fees', Decimal(str(order_response['fill_fees'])))
                
                print('Updating price')
                ex_value = Decimal(order_response['executed_value'])
                vol = Decimal(order_response['filled_size'])
                setattr(order, 'price', Decimal(ex_value/vol))
                
                print('Updating if settled')
                if order_response['settled']:
                    setattr(order, 'is_settled', True)
                    print('Updating settlement date as a string')
                    setattr(order, 'fulfilled_date', order_response['done_at'])
                    
                order.save()
            
        else:
            print('Order ID no longer exists')
            print('Updating that order no longer exists on CB Pro')
            price = Decimal(str(order.price))
            vol = Decimal(str(order.volume))
            setattr(order, 'still_exists', False)
            setattr(order, 'price', price)
            setattr(order, 'volume', vol)
            order.save()

        
        print('----------- Done with Order ' + str(count) + '/' + str(len(ordersToCheck)) + ' -----------')
        count += 1

    t_finish = time.time()
    print("Total elapsed time: " + str(t_finish - t_start))
    print('----------- End of Order Check -----------')

#A function to get the regular fees that would be paid if using Coinbase recurring buy instead of DCA Pros through Coinbase Pro
def get_regular_fees(trade_amount: Decimal):
    regularFees = Decimal(0)

    if trade_amount <= Decimal(10.00):
        regularFees = Decimal(0.99)
        return regularFees
    elif (trade_amount > Decimal(10.00)) & (trade_amount <= Decimal(25.00)):
        regularFees = Decimal(1.49)
        return regularFees
    elif (trade_amount > Decimal(25.00)) & (trade_amount <= Decimal(50.00)):
        regularFees = Decimal(1.99)
        return regularFees
    elif (trade_amount > Decimal(50.00)) & (trade_amount <= Decimal(200.00)):
        regularFees = Decimal(2.99)
        return regularFees
    elif trade_amount > Decimal(200.00):
        #After $200 it is a percentage fee based on payment method, in this case a US bank account
        regularFees = Decimal(0.0149*trade_amount)
        return regularFees


@background(schedule=10, queue='execution_count_and_fees', remove_existing_tasks=True)
def updateExecutionCountsandFees():
    start = datetime.datetime.now()
    t_start = time.time()
    print('----------- Start of Fees and Execution Count Check ----------- Time: ' + start.strftime("%d-%b-%Y (%H:%M:%S.%f)"))
    print('Grabbing all strategies...')
    #Task to update all the strategies execution counts for successful orders made in total for each
    allStrats = Strategy.objects.all()
    

    for strategy in allStrats:
        print('Calculating fees saved and execution count for strategy: ' + str(strategy))
        amount = Decimal(str(strategy.amount))
        #Grab all the orders from that strategy that have not had their fees counted
        fulfilledOrders = Orders.objects.filter(strategy=strategy).filter(is_settled__in=[True])
        orders = Orders.objects.filter(strategy=strategy).filter(is_settled__in=[True]).filter(fees_saved__isnull=True)
        execution_count = len(fulfilledOrders)

        for order in orders:
            price = Decimal(str(order.price))
            vol = Decimal(str(order.volume))
            exVal = Decimal(str(order.executed_value))
            orderFees = Decimal(str(order.fees))
            regularFees = get_regular_fees(exVal)
            feesSaved = Decimal(round(regularFees - orderFees, 5))
            print('Fees saved on this order: ' + str(feesSaved))

            print('Setting the fees saved for this order...')
            setattr(order, 'fees_saved', feesSaved)
            setattr(order, 'fees', orderFees)
            setattr(order, 'price', price)
            setattr(order, 'volume', vol)
            setattr(order, 'executed_value', exVal)
            order.full_clean()
            order.save()

        setattr(strategy, 'execution_count', execution_count)
        setattr(strategy, 'amount', amount)
        strategy.full_clean()
        strategy.save()

    t_finish = time.time()
    print("Total elapsed time: " + str(t_finish - t_start))
    print('----------- End of Fees and Execution Count Check -----------')