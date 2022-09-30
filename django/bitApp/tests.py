import os
import time

import django

# Create your tests here.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bitBack.settings")
django.setup()

from django.test import TestCase
from bitApp.models import *
from huobi.client.generic import GenericClient
from huobi.client.market import MarketClient
from huobi.client.trade import TradeClient
from huobi.client.account import AccountClient
from huobi.constant import *
from bitApp.core.platform import *

from bitApp.config import *
# from bitApp.services import *
import datetime
import json

class Test(TestCase):


    # def test_currency_type(self):
    #     generic_client = GenericClient()
    #     generic_client = GenericClient()
    #     list_symbol = generic_client.get_exchange_symbols()
    #     list_currency = generic_client.get_reference_currencies()
    #     char = "{"
    #     for iten in list_symbol:
    #         char += "\"" + iten.symbol + '\", '
    #         print(iten.symbol)

    #     print(char)

    # def test_currency_log(self):
    #     """
    #     The summary of trading in the market for the last 24 hours

    #     :member
    #         id: response ID
    #         open: The opening price of last 24 hours.
    #         close: The last price of last 24 hours.
    #         amount: The aggregated trading volume in USDT.
    #         high: The high price of last 24 hours.
    #         low: The low price of last 24 hours.
    #         count: The number of completed trades.
    #         volume: The trading volume in base currency of last 24 hours.
    #         version: inner data
    #     """
    #     print(datetime.datetime.now().timestamp())

    #     market_client = MarketClient()
    #     generic_client = GenericClient()
    #     print(generic_client.get_exchange_timestamp())
    #     now_time = int(generic_client.get_exchange_timestamp() / 1000 - 24*3600)
    #     now_time = datetime.datetime.fromtimestamp(now_time)
    #     currency = market_client.get_market_detail('btcusdt')
    #     print(currency.close)

        # res = CurrencyPriceLog.objects.all()
        # new_id = len(res)
        #
        # log = CurrencyPriceLog(id=new_id, type=currency_dict['btcusdt'], date=now_time, price=currency.close)
        # log.save()
        # res = CurrencyPriceLog.objects.all()
        # for var in res:
        #     print(var.__dict__)

    # def test_get_my_account(self):
    #     account_client = AccountClient(api_key=g_api_key, secret_key=g_secret_key)

        # account_type = "spot"
        # asset_valuation = account_client.get_account_asset_valuation(account_type=account_type,
        #                                                              valuation_currency="usd")
        # asset_valuation.print_object()
        #
        # asset_valuation = account_client.get_account_asset_valuation(account_type=account_type,
        #                                                              valuation_currency="btc")
        # asset_valuation.print_object()
        #
    #     acctounts = account_client.get_accounts()
    #     for acctount in acctounts:

    #         print(acctount.print_object(), acctount.id)
    #     list_obj = account_client.get_balance(account_id=g_account_id)
    #     for item in list_obj:
    #         if item.currency != 'btc' and item.currency != 'usdt':
    #             continue
    #         item.print_object()

    # def test_feerate(self):
    #     trade_client = TradeClient(api_key=g_api_key, secret_key=g_secret_key)
    #     list_obj = trade_client.get_feerate(symbols="btcusdt")[0]
    #     print('挂单价: ', list_obj.maker_fee)
    #     print('吃单价: ', list_obj.taker_fee)

    # def test_buy_in(self):
    #     symbol_test = 'btcusdt'
    #     trade_client = TradeClient(api_key=g_api_key, secret_key=g_secret_key)
    #     # amount * price = total money
    #     order_id = trade_client.create_order(symbol=symbol_test, account_id=g_account_id, order_type=OrderType.BUY_LIMIT_MAKER, source=OrderSource.API, amount=0.0001, price=get_currency_price(symbol_test))
    #     print('order id:', order_id)
    #     self.test_get_my_account()
    #     # self.test_cancel(order_id)
    #     pass

    # def test_sell_out(self):
    #     symbol_test = 'btcusdt'
    #     trade_client = TradeClient(api_key=g_api_key, secret_key=g_secret_key)
    #     try:
    #         order_id = trade_client.create_order(symbol=symbol_test, account_id=g_account_id, order_type=OrderType.SELL_LIMIT_MAKER, source=OrderSource.API, amount=0.001, price=get_currency_price(symbol_test))
    #     except Exception as e:
    #         print(e)
    #     print('sell order id=', order_id)
    #     self.test_query()


    # def test_query(self):
    #     symbol_test_list = ["btcusdt"]
    #     trade_client = TradeClient(api_key=g_api_key, secret_key=g_secret_key)
    #     for symbol_test in symbol_test_list:
    #         print(int(datetime.datetime.now().timestamp()*1000 -3600*24*7*1000))
    #         list_obj = trade_client.get_history_orders(symbol=symbol_test, start_time=int(datetime.datetime.now().timestamp()*1000 - 3600*24*7*1000))
    #         for info in list_obj:
    #             try:
    #                 trade_client.cancel_order(symbol_test, info.id)
    #             except Exception as e:
    #                 print(repr(e))
    #                 continue
    #             print('--------------------------------')
    #             print(info.print_object())

        # list_obj = trade_client.get_order(order_id=559250761557186)
        # list_obj.print_object()

    # def test_cancel(self, order_id=596836322187502):
    #     symbol_test = 'btcusdt'
    #     trade_client = TradeClient(api_key=g_api_key, secret_key=g_secret_key)
    #     canceled_order_id = trade_client.cancel_order(symbol_test, order_id)
    #     print(canceled_order_id)
    #     print(order_id)

    # def test_cancel_all(self):
    #     symbol_test = 'btcusdt'
    #     trade_client = TradeClient(api_key=g_api_key, secret_key=g_secret_key)
    #     order_list = Order.objects.all()
    #     print(len(order_list))

    #     for order in order_list:
    #         try:
    #             print(order.order_record_id)
    #             canceled_order_id = trade_client.cancel_order(symbol_test, order.order_record_id)
    #         except Exception as e:
    #             print(repr(e))
    #             continue



    # def test_get_balance(self):
    #     print(get_usdt_balance())

    # def test_add_normal_robot(self):

    #     currency_type = 'btcusdt'
    #     max_price = 150000
    #     min_price = 1500
    #     grid_num = 40
    #     invest_num = 10000
    #     invest_rate = 0.5

    #     add_normal_robot(currency_type, max_price, min_price, grid_num, invest_num, invest_rate)


    #     # pause_robot(robot_id=0)
    #     res = RobotProfit.objects.all()

    #     for item in res:
    #         print(item.__dict__)

    #     res = Robot.objects.all()

    #     for item in res:
    #         print(item.__dict__)

    #     res = RobotPolicy.objects.all()

    #     for item in res:
    #         print(item.__dict__)

    # def test_add_infinite_robot(self):

    #     currency_type = 'btcusdt'
    #     max_price = 150000
    #     min_price = 1500
    #     grid_num = 40
    #     invest_num = 10000
    #     invest_rate = 0.5
    #     grid_profit_rate = 1

    #     add_infinite_robot(currency_type, max_price, min_price, invest_num, grid_profit_rate)

    #     res = Robot.objects.all()

    #     for item in res:
    #         print(item.__dict__)

    #     res = RobotProfit.objects.all()

    #     for item in res:
    #         print(item.__dict__)

    #     res = RobotPolicy.objects.all()

    #     for item in res:
    #         print(item.__dict__)


    # def test_create_order(self):

    #     res = Order.objects.all()
    #     print(res)
    #     order_record_id = 22222222
    #     robot_id = 1
    #     currency_type = 'btcusdt'
    #     order_num = 23213
    #     order_price = 12123213
    #     create_order(order_record_id, robot_id, currency_type, ORDER_SELL, order_num, order_price)

    #     res = Order.objects.all()

    #     for item in res:
    #         print(item.__dict__)

    #     print(get_trade_order_list(robot_id=1))
    #     print(get_pender_order_list(robot_id=1))


    # def test_buy_onces(self):
    #     trade_client = TradeClient(api_key=g_api_key, secret_key=g_secret_key)
    #     order_record_id = trade_client.create_order(symbol="btcusdt",
    #                                                            account_id=g_account_id,
    #                                                            order_type=OrderType.SELL_MARKET,
    #                                                            source=OrderSource.API, amount=0.00735, price=None)
    def test_save_order(self):
        order = Order(order_id=12, order_record_id=12, robot_id=1,
                order_currency_type="btcusdt", order_type=0,
                order_amount=12,
                order_price=1222, order_status=ORDER_WAIT, order_create_time=datetime.datetime.now(),
                order_finish_time=None)
        order.save()
        orders = Order.objects.all()
        for order in orders:
            print(order.__dict__)

    # def test_demo_all(self):

    #     log = open('result.txt', 'w', encoding='utf-8')

    #     currency_type = 'btcusdt'
    #     max_price = 31353.07
    #     min_price = 30000
    #     grid_num = 40
    #     invest_num = 7
    #     invest_rate = 50

    #     grid_profit_rate = 1

    #     robot_id = add_normal_robot(currency_type, max_price, min_price, grid_num, invest_num, invest_rate)
    #     init_robot(robot_id=robot_id)
    #     robot_id = add_infinite_robot(currency_type, max_price, min_price, invest_num, grid_profit_rate)
    #     init_robot(robot_id=robot_id)

    #     self.get_database_status(log)
    #     update_order()
    #     self.get_database_status(log)

    #     print(get_trade_order_list(robot_id))
    #     print(get_pender_order_list(robot_id))
    #     print(json.dumps(get_robot_list()))

    #     self.get_database_status(log)

    #     log.close()

    # def test_log(self):
    #     cur_path = os.path.dirname(os.path.realpath(__file__))
    #     log_path = os.path.join(os.path.dirname(cur_path), 'logs')
    #     files = []
    #     for i in range(3):
    #         day = ((datetime.datetime.now()) + datetime.timedelta(days=-i)).strftime("%Y-%m-%d")
    #         files.append(os.path.join(log_path, 'info-{}.log'.format(day)))

    #     res = ''
    #     for file in files:
    #         f = open(file, 'r')
    #         res += f.read()
    #         f.close()

        # files = os.path.join(log_path, 'info-{}.log'.format(day))
        # res = open(files, 'r')
        # print(res.readlines())
        #
        # print(files)

    # def test_date(self):
    #     robot = Robot(robot_id=1, robot_summary_id='1', robot_policy_type=GEOMETRIC_POLICY,
    #                   robot_policy_id=2,
    #                   robot_currency_type='btcusdt', robot_status=ROBOT_PAUSE,
    #                   robot_create_time=datetime.datetime.now())
    #     time.sleep(1)
    #     first = datetime.datetime.now()
    #     second = robot.robot_create_time
    #     create_time = robot.robot_create_time.replace(tzinfo=None)
    #     print(int(time.mktime(create_time.timetuple())))
    #     day = create_time.strftime("%Y/%m/%d %H:%M:%S")
    #     print(day)
    #     print(int((first-create_time).seconds))
    #     print(str(datetime.timedelta(days=(first-first).days))[:-7])

    # def test_add_api(self):
    #     account_client = AccountClient(api_key=g_api_key, secret_key=g_secret_key)
    #     accounts = account_client.get_accounts()
    #     apis = Api.objects.all()
    #     api_id = len(apis)
    #     api = Api(api_id=api_id, api_key=g_api_key, secret_key=g_secret_key)

    #     account_count = len(Account.objects.all())
    #     for item in accounts:
    #         account = Account(account_id=account_count, api_id=api_id, system_id=item.id)
    #         account.save()
    #     api.save()
    #     huobi = HuoBi()
    #     print(huobi.get_apis())
    #     print(huobi.get_currencys())
    #     print(huobi.get_accounts(api_id))
        # apis = Api.objects.all()[0]
        # accounts = Account.objects.all()[0]
        #
        # akey = apis.api_key
        # skey = apis.secret_key
        # account_client = AccountClient(api_key=akey, secret_key=skey)
        # accounts = account_client.get_accounts()
        # print(akey,skey,accounts)
        # print(apis.__dict__, accounts)

    # def test_dict(self):

    #     robot_orders = {}
    #     orders = [1, 1, 1, 1, 1]
    #     robot_ids = [0, 2, 3, 3, 2]

    #     for i in range(5):
    #         if robot_ids[i] not in robot_orders.keys():
    #             order_list = [orders[i]]
    #             robot_orders[robot_ids[i]] = order_list
    #         else:
    #             robot_orders[robot_ids[i]].append(orders[i])

    #     print(robot_orders)

    #     for k, v in robot_orders.items():
    #         print(k)
    #         print(v)