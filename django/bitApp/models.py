from django.db import models
from bitApp.config import *
# Create your models here.


class Robot(models.Model):

    robot_id = models.IntegerField(db_column='robot_id', primary_key=True)
    robot_account_id = models.IntegerField(db_column='robot_account_id', default=-1)
    robot_summary_id = models.IntegerField(db_column='robot_summary_id')
    robot_policy_type = models.IntegerField(db_column='robot_policy_type')
    robot_currency_type = models.CharField(db_column='robot_currency_type', max_length=20)
    robot_policy_id = models.IntegerField(db_column='robot_policy_id')
    robot_status = models.IntegerField(db_column='robot_status', default=ROBOT_OK)
    robot_create_time = models.DateTimeField(db_column='robot_create_time')

    class Meta:
        db_table = 'robot'


class RobotSummary(models.Model):

    summary_id = models.IntegerField(db_column='summary_id', primary_key=True)
    invested_money = models.FloatField(db_column='invested_money', default=0.0)
    hold_currency_num = models.FloatField(db_column='hold_currency_num', default=0.0)
    total_transfer_fee = models.FloatField(db_column='total_transfer_fee', default=0.0)
    profit = models.FloatField(db_column='profit', default=0.0)

    class Meta:
        db_table = 'robot_summary'


class GeometricPolicy(models.Model):

    policy_id = models.IntegerField(db_column='policy_id', primary_key=True)
    max_price = models.FloatField(db_column='max_price', default=0)
    min_price = models.FloatField(db_column='min_price', default=0)
    grid_num = models.IntegerField(db_column='grid_num', default=0)
    grid_invest = models.FloatField(db_column='grid_invest')
    expect_money = models.FloatField(db_column='expect_money', default=0)
    grid_profit_rate = models.FloatField(db_column='grid_profit_rate', default=0)

    class Meta:
        db_table = 'geometric_policy'


class InfinitePolicy(models.Model):

    policy_id = models.IntegerField(db_column='policy_id', primary_key=True)
    max_price = models.FloatField(db_column='max_price', default=0)
    min_price = models.FloatField(db_column='min_price', default=0)
    grid_invest = models.FloatField(db_column='grid_invest')
    rate_buy = models.FloatField(db_column='rate_buy')
    rate_sell = models.FloatField(db_column='rate_sell')
    expect_money = models.FloatField(db_column='expect_money', default=0)

    class Meta:
        db_table = 'infinite_policy'


class Order(models.Model):
    
    order_id = models.AutoField(db_column='order_id', primary_key=True)
    order_record_id = models.CharField(db_column='order_record_id', max_length=20)
    robot_id = models.IntegerField(db_column='robot_id')
    order_currency_type = models.CharField(db_column='order_currency_type', max_length=20)
    order_amount = models.FloatField(db_column='order_amount')
    order_price = models.FloatField(db_column='order_price')
    order_type = models.IntegerField(db_column='order_type')
    order_status = models.IntegerField(db_column='order_status')
    order_transfer_fees = models.FloatField(db_column='order_transfer_fees', default=0)
    order_create_time = models.DateTimeField(db_column='order_create_time')
    order_finish_time = models.DateTimeField(db_column='order_finish_time', null=True)
    order_refer_id = models.IntegerField(db_column='order_refer_id', default=ORDER_NONE_REF)
    order_flag = models.IntegerField(db_column='order_flag', default=ORDER_NONE_FLAG)

    class Meta:
        db_table = 'robot_order'


class Api(models.Model):

    api_id = models.IntegerField(db_column='api_id', primary_key=True)
    api_key = models.CharField(db_column='api_key', max_length=100)
    secret_key = models.CharField(db_column='secret_key', max_length=100)

    class Meta:
        db_table = 'api'


class Account(models.Model):

    account_id = models.IntegerField(db_column='account_id', primary_key=True)
    api_id = models.IntegerField(db_column='api_id')
    system_id = models.IntegerField(db_column='system_id')
    account_nickname = models.CharField(db_column='account_nickname', max_length=300, default='')
    account_password = models.CharField(db_column='account_password', max_length=100, default='')
    account_plantform = models.CharField(db_column='account_plantform', max_length=50, default=DEFAULT_PLANTFORM)
    account_status = models.IntegerField(db_column='account_status', default=ACCOUNT_OK)

    class Meta:
        db_table = 'account'

