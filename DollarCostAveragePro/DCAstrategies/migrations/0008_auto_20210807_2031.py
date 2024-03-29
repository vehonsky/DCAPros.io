# Generated by Django 3.2.5 on 2021-08-07 20:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('DCAstrategies', '0007_auto_20210807_2026'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orders',
            name='fees',
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=15, null=True),
        ),
        migrations.AlterField(
            model_name='orders',
            name='fees_saved',
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=15, null=True),
        ),
        migrations.AlterField(
            model_name='strategy',
            name='crypto_product',
            field=models.CharField(choices=[('QNT', 'QNT'), ('OGN', 'OGN'), ('NMR', 'NMR'), ('ICP', 'ICP'), ('MLN', 'MLN'), ('BTC', 'BTC'), ('COMP', 'COMP'), ('RLC', 'RLC'), ('AMP', 'AMP'), ('RAI', 'RAI'), ('UNI', 'UNI'), ('BAND', 'BAND'), ('FET', 'FET'), ('CHZ', 'CHZ'), ('BNT', 'BNT'), ('WBTC', 'WBTC'), ('REP', 'REP'), ('UMA', 'UMA'), ('SUSHI', 'SUSHI'), ('MKR', 'MKR'), ('SOL', 'SOL'), ('DASH', 'DASH'), ('DOGE', 'DOGE'), ('DOT', 'DOT'), ('ZRX', 'ZRX'), ('LRC', 'LRC'), ('LINK', 'LINK'), ('MANA', 'MANA'), ('TRB', 'TRB'), ('ZEC', 'ZEC'), ('ACH', 'ACH'), ('REN', 'REN'), ('FARM', 'FARM'), ('OXT', 'OXT'), ('GRT', 'GRT'), ('MASK', 'MASK'), ('NKN', 'NKN'), ('ATOM', 'ATOM'), ('GTC', 'GTC'), ('LTC', 'LTC'), ('SKL', 'SKL'), ('ALGO', 'ALGO'), ('FORTH', 'FORTH'), ('PLA', 'PLA'), ('1INCH', '1INCH'), ('BOND', 'BOND'), ('MATIC', 'MATIC'), ('USDT', 'USDT'), ('XTZ', 'XTZ'), ('NU', 'NU'), ('ENJ', 'ENJ'), ('CRV', 'CRV'), ('BAT', 'BAT'), ('FIL', 'FIL'), ('EOS', 'EOS'), ('KNC', 'KNC'), ('CLV', 'CLV'), ('XLM', 'XLM'), ('ANKR', 'ANKR'), ('ETH', 'ETH'), ('RLY', 'RLY'), ('POLY', 'POLY'), ('ETC', 'ETC'), ('ADA', 'ADA'), ('SNX', 'SNX'), ('STORJ', 'STORJ'), ('BCH', 'BCH'), ('CGLD', 'CGLD'), ('MIR', 'MIR'), ('AAVE', 'AAVE'), ('PAX', 'PAX'), ('BAL', 'BAL'), ('YFI', 'YFI'), ('LPT', 'LPT'), ('OMG', 'OMG'), ('CTSI', 'CTSI'), ('KEEP', 'KEEP'), ('DAI', 'DAI')], max_length=30),
        ),
        migrations.AlterField(
            model_name='strategy',
            name='execution_frequency',
            field=models.CharField(choices=[('wk', 'Weekly'), ('day', 'Daily'), ('mo', 'Monthly'), ('bimo', 'BiMonthly')], default='day', max_length=100),
        ),
        migrations.AlterField(
            model_name='strategy',
            name='order_type',
            field=models.CharField(choices=[('market', 'Market'), ('limit', 'Limit')], default='market', max_length=30),
        ),
    ]
