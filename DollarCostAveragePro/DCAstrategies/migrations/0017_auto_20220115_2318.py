# Generated by Django 3.2.9 on 2022-01-15 23:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('DCAstrategies', '0016_auto_20220112_0358'),
    ]

    operations = [
        migrations.AlterField(
            model_name='strategy',
            name='crypto_product',
            field=models.CharField(choices=[('ATOM', 'ATOM'), ('DOGE', 'DOGE'), ('MUSD', 'MUSD'), ('BAND', 'BAND'), ('DAI', 'DAI'), ('NCT', 'NCT'), ('POWR', 'POWR'), ('DOT', 'DOT'), ('MLN', 'MLN'), ('NU', 'NU'), ('IMX', 'IMX'), ('AMP', 'AMP'), ('UMA', 'UMA'), ('REQ', 'REQ'), ('PLA', 'PLA'), ('GFI', 'GFI'), ('POLY', 'POLY'), ('UST', 'UST'), ('TBTC', 'TBTC'), ('KEEP', 'KEEP'), ('ZEN', 'ZEN'), ('SUSHI', 'SUSHI'), ('REN', 'REN'), ('ENJ', 'ENJ'), ('RBN', 'RBN'), ('BICO', 'BICO'), ('MIR', 'MIR'), ('XTZ', 'XTZ'), ('BOND', 'BOND'), ('ZEC', 'ZEC'), ('KNC', 'KNC'), ('BTRST', 'BTRST'), ('UNI', 'UNI'), ('FET', 'FET'), ('FOX', 'FOX'), ('COVAL', 'COVAL'), ('ANKR', 'ANKR'), ('WBTC', 'WBTC'), ('LCX', 'LCX'), ('WLUNA', 'WLUNA'), ('SPELL', 'SPELL'), ('BADGER', 'BADGER'), ('DNT', 'DNT'), ('LOOM', 'LOOM'), ('YFII', 'YFII'), ('COTI', 'COTI'), ('POLS', 'POLS'), ('REP', 'REP'), ('SUKU', 'SUKU'), ('QNT', 'QNT'), ('EOS', 'EOS'), ('TRB', 'TRB'), ('NMR', 'NMR'), ('ENS', 'ENS'), ('AUCTION', 'AUCTION'), ('GODS', 'GODS'), ('ICP', 'ICP'), ('VGX', 'VGX'), ('API3', 'API3'), ('TRU', 'TRU'), ('RLC', 'RLC'), ('CVC', 'CVC'), ('GTC', 'GTC'), ('CRO', 'CRO'), ('ETH', 'ETH'), ('RAI', 'RAI'), ('RGT', 'RGT'), ('RAD', 'RAD'), ('XYO', 'XYO'), ('KRL', 'KRL'), ('GRT', 'GRT'), ('BAT', 'BAT'), ('LPT', 'LPT'), ('MASK', 'MASK'), ('TRAC', 'TRAC'), ('SUPER', 'SUPER'), ('ETC', 'ETC'), ('CHZ', 'CHZ'), ('PAX', 'PAX'), ('DASH', 'DASH'), ('RARI', 'RARI'), ('OMG', 'OMG'), ('BTC', 'BTC'), ('FORTH', 'FORTH'), ('MATIC', 'MATIC'), ('FX', 'FX'), ('ALGO', 'ALGO'), ('MCO2', 'MCO2'), ('MANA', 'MANA'), ('COMP', 'COMP'), ('CLV', 'CLV'), ('OXT', 'OXT'), ('BNT', 'BNT'), ('INV', 'INV'), ('USDT', 'USDT'), ('WCFG', 'WCFG'), ('GALA', 'GALA'), ('YFI', 'YFI'), ('FARM', 'FARM'), ('IDEX', 'IDEX'), ('TRIBE', 'TRIBE'), ('ZRX', 'ZRX'), ('ASM', 'ASM'), ('ARPA', 'ARPA'), ('BAL', 'BAL'), ('SKL', 'SKL'), ('ADA', 'ADA'), ('MKR', 'MKR'), ('ORN', 'ORN'), ('RLY', 'RLY'), ('LTC', 'LTC'), ('LQTY', 'LQTY'), ('CGLD', 'CGLD'), ('AAVE', 'AAVE'), ('XLM', 'XLM'), ('IOTX', 'IOTX'), ('MDT', 'MDT'), ('AVAX', 'AVAX'), ('1INCH', '1INCH'), ('PRO', 'PRO'), ('ALCX', 'ALCX'), ('GYEN', 'GYEN'), ('SNX', 'SNX'), ('JASMY', 'JASMY'), ('PERP', 'PERP'), ('BLZ', 'BLZ'), ('CTSI', 'CTSI'), ('CRV', 'CRV'), ('ACH', 'ACH'), ('FIL', 'FIL'), ('LRC', 'LRC'), ('AGLD', 'AGLD'), ('AXS', 'AXS'), ('DESO', 'DESO'), ('LINK', 'LINK'), ('BCH', 'BCH'), ('SHIB', 'SHIB'), ('QUICK', 'QUICK'), ('OGN', 'OGN'), ('DDX', 'DDX'), ('NKN', 'NKN'), ('STORJ', 'STORJ'), ('SOL', 'SOL')], max_length=30),
        ),
        migrations.AlterField(
            model_name='strategy',
            name='execution_frequency',
            field=models.CharField(choices=[('wk', 'Weekly'), ('day', 'Daily'), ('mo', 'Monthly'), ('bimo', 'BiMonthly')], default='day', max_length=100),
        ),
        migrations.AlterField(
            model_name='strategy',
            name='order_type',
            field=models.CharField(choices=[('market', 'Market'), ('limit', 'Limit'), ('ladder', 'Ladder')], default='market', max_length=30),
        ),
        migrations.AlterField(
            model_name='strategy',
            name='quote_currency',
            field=models.CharField(choices=[('GBP', 'British Pounds'), ('USD', 'US Dollars'), ('EUR', 'Euros')], default='USD', max_length=10),
        ),
    ]
