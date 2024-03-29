# Generated by Django 3.2.5 on 2021-08-13 21:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('DCAstrategies', '0010_auto_20210813_2141'),
    ]

    operations = [
        migrations.AlterField(
            model_name='strategy',
            name='crypto_product',
            field=models.CharField(choices=[('SKL', 'SKL'), ('IOTX', 'IOTX'), ('CTSI', 'CTSI'), ('QNT', 'QNT'), ('REN', 'REN'), ('DASH', 'DASH'), ('MLN', 'MLN'), ('MATIC', 'MATIC'), ('1INCH', '1INCH'), ('TRIBE', 'TRIBE'), ('MASK', 'MASK'), ('TRU', 'TRU'), ('UNI', 'UNI'), ('LRC', 'LRC'), ('NU', 'NU'), ('SOL', 'SOL'), ('RLY', 'RLY'), ('LINK', 'LINK'), ('FORTH', 'FORTH'), ('PAX', 'PAX'), ('LTC', 'LTC'), ('USDT', 'USDT'), ('AXS', 'AXS'), ('BAT', 'BAT'), ('REQ', 'REQ'), ('WBTC', 'WBTC'), ('ZRX', 'ZRX'), ('ORN', 'ORN'), ('RAI', 'RAI'), ('POLY', 'POLY'), ('ALGO', 'ALGO'), ('ACH', 'ACH'), ('MKR', 'MKR'), ('PLA', 'PLA'), ('BTC', 'BTC'), ('ADA', 'ADA'), ('OGN', 'OGN'), ('OMG', 'OMG'), ('STORJ', 'STORJ'), ('MIR', 'MIR'), ('FARM', 'FARM'), ('XTZ', 'XTZ'), ('DOT', 'DOT'), ('XLM', 'XLM'), ('CHZ', 'CHZ'), ('GTC', 'GTC'), ('MANA', 'MANA'), ('BCH', 'BCH'), ('KEEP', 'KEEP'), ('ICP', 'ICP'), ('FIL', 'FIL'), ('ANKR', 'ANKR'), ('ETH', 'ETH'), ('NMR', 'NMR'), ('TRB', 'TRB'), ('AMP', 'AMP'), ('REP', 'REP'), ('SUSHI', 'SUSHI'), ('NKN', 'NKN'), ('WLUNA', 'WLUNA'), ('BAND', 'BAND'), ('KNC', 'KNC'), ('DOGE', 'DOGE'), ('UST', 'UST'), ('ZEC', 'ZEC'), ('OXT', 'OXT'), ('YFI', 'YFI'), ('GRT', 'GRT'), ('ENJ', 'ENJ'), ('DAI', 'DAI'), ('CRV', 'CRV'), ('RLC', 'RLC'), ('LPT', 'LPT'), ('ETC', 'ETC'), ('EOS', 'EOS'), ('ATOM', 'ATOM'), ('BOND', 'BOND'), ('CGLD', 'CGLD'), ('COMP', 'COMP'), ('AAVE', 'AAVE'), ('CLV', 'CLV'), ('FET', 'FET'), ('BNT', 'BNT'), ('UMA', 'UMA'), ('SNX', 'SNX'), ('QUICK', 'QUICK'), ('BAL', 'BAL')], max_length=30),
        ),
        migrations.AlterField(
            model_name='strategy',
            name='execution_frequency',
            field=models.CharField(choices=[('mo', 'Monthly'), ('day', 'Daily'), ('bimo', 'BiMonthly'), ('wk', 'Weekly')], default='day', max_length=100),
        ),
        migrations.AlterField(
            model_name='strategy',
            name='order_type',
            field=models.CharField(choices=[('limit', 'Limit'), ('ladder', 'Ladder'), ('market', 'Market')], default='market', max_length=30),
        ),
        migrations.AlterField(
            model_name='strategy',
            name='quote_currency',
            field=models.CharField(choices=[('EUR', 'Euros'), ('GBP', 'British Pounds'), ('USD', 'US Dollars')], default='USD', max_length=3),
        ),
    ]
