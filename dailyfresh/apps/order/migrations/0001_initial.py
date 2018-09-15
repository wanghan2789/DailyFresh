# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='OrderGoods',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('create_time', models.DateTimeField(verbose_name='create_time', auto_created=True)),
                ('update_time', models.DateTimeField(verbose_name='update_time', auto_now=True)),
                ('is_delete', models.BooleanField(verbose_name='False_not_del', default=False)),
                ('count', models.IntegerField(verbose_name='商品数目', default=1)),
                ('price', models.DecimalField(verbose_name='商品价格', max_digits=10, decimal_places=2)),
                ('comment', models.CharField(verbose_name='评论', max_length=256)),
            ],
            options={
                'verbose_name': '订单商品',
                'db_table': 'df_order_goods',
                'verbose_name_plural': '订单商品',
            },
        ),
        migrations.CreateModel(
            name='OrderInfo',
            fields=[
                ('create_time', models.DateTimeField(verbose_name='create_time', auto_created=True)),
                ('update_time', models.DateTimeField(verbose_name='update_time', auto_now=True)),
                ('is_delete', models.BooleanField(verbose_name='False_not_del', default=False)),
                ('order_id', models.CharField(verbose_name='订单id', primary_key=True, max_length=128, serialize=False)),
                ('pay_method', models.SmallIntegerField(verbose_name='支付方式', choices=[(1, '货到付款'), (2, '微信支付'), (3, '支付宝'), (4, '银联支付')], default=3)),
                ('total_count', models.IntegerField(verbose_name='商品数量', default=1)),
                ('total_price', models.DecimalField(verbose_name='商品总价', max_digits=10, decimal_places=2)),
                ('transit_price', models.DecimalField(verbose_name='订单运费', max_digits=10, decimal_places=2)),
                ('order_status', models.SmallIntegerField(verbose_name='订单状态', choices=[(1, '待支付'), (2, '待发货'), (3, '待收货'), (4, '待评价'), (5, '已完成')], default=1)),
                ('trade_no', models.CharField(verbose_name='支付编号', max_length=128)),
            ],
            options={
                'verbose_name': '订单',
                'db_table': 'df_order_info',
                'verbose_name_plural': '订单',
            },
        ),
    ]
