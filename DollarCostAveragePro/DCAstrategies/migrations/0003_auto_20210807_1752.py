# Generated by Django 3.2.5 on 2021-08-07 17:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('DCAstrategies', '0002_auto_20210807_1621'),
    ]

    operations = [
        migrations.AlterField(
            model_name='strategy',
            name='crypto_product',
            field=models.CharField(choices=[('REP', 'REP'), ('CGLD', 'CGLD'), ('LTC', 'LTC'), ('XTZ', 'XTZ'), ('SNX', 'SNX'), ('MASK', 'MASK'), ('CRV', 'CRV'), ('MLN', 'MLN'), ('OGN', 'OGN'), ('SUSHI', 'SUSHI'), ('ENJ', 'ENJ'), ('LINK', 'LINK'), ('LRC', 'LRC'), ('ICP', 'ICP'), ('FIL', 'FIL'), ('GTC', 'GTC'), ('MKR', 'MKR'), ('ALGO', 'ALGO'), ('COMP', 'COMP'), ('ZRX', 'ZRX'), ('ETH', 'ETH'), ('ETC', 'ETC'), ('SOL', 'SOL'), ('BAND', 'BAND'), ('TRB', 'TRB'), ('EOS', 'EOS'), ('DOT', 'DOT'), ('UMA', 'UMA'), ('NMR', 'NMR'), ('GRT', 'GRT'), ('OXT', 'OXT'), ('AMP', 'AMP'), ('MANA', 'MANA'), ('CTSI', 'CTSI'), ('BOND', 'BOND'), ('REN', 'REN'), ('BAT', 'BAT'), ('CLV', 'CLV'), ('RLY', 'RLY'), ('FET', 'FET'), ('YFI', 'YFI'), ('STORJ', 'STORJ'), ('DASH', 'DASH'), ('RAI', 'RAI'), ('NU', 'NU'), ('BNT', 'BNT'), ('1INCH', '1INCH'), ('ZEC', 'ZEC'), ('PAX', 'PAX'), ('WBTC', 'WBTC'), ('BCH', 'BCH'), ('BTC', 'BTC'), ('OMG', 'OMG'), ('USDT', 'USDT'), ('UNI', 'UNI'), ('DOGE', 'DOGE'), ('KEEP', 'KEEP'), ('LPT', 'LPT'), ('ACH', 'ACH'), ('MATIC', 'MATIC'), ('FORTH', 'FORTH'), ('DAI', 'DAI'), ('XLM', 'XLM'), ('CHZ', 'CHZ'), ('NKN', 'NKN'), ('ATOM', 'ATOM'), ('AAVE', 'AAVE'), ('FARM', 'FARM'), ('ANKR', 'ANKR'), ('BAL', 'BAL'), ('SKL', 'SKL'), ('ADA', 'ADA'), ('PLA', 'PLA'), ('RLC', 'RLC'), ('QNT', 'QNT'), ('POLY', 'POLY'), ('MIR', 'MIR'), ('KNC', 'KNC')], max_length=30),
        ),
        migrations.AlterField(
            model_name='strategy',
            name='execution_frequency',
            field=models.CharField(choices=[('mo', 'Monthly'), ('bimo', 'BiMonthly'), ('day', 'Daily'), ('wk', 'Weekly')], default='day', max_length=100),
        ),
        migrations.AlterField(
            model_name='strategy',
            name='order_type',
            field=models.CharField(choices=[('limit', 'Limit'), ('market', 'Market')], default='market', max_length=30),
        ),
    ]
