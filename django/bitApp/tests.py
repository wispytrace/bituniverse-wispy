import os
import time

import django

from bitApp.core.user import User

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
from bitApp.core.plantform import *

from bitApp.config import *
# from bitApp.services import *
import datetime
import json
from binance.spot import Spot as Client
class Test(TestCase):


    def test_bian(self):
        api_key = "gvFyqKFChhxZhhux3mvuHYabXy0vRNfWQfwDjTDZk8Ad85LWa3IAmtAN30ct5oTo"
        secret_key = "tyNqwXYAP97ifhyfFLhewwdTytYoe8NHkSXZ41h6Xrwqmq32sVgPKhCuxYGmSHpg"
        # spot_client = Client(api_key, secret_key)
        # print(spot_client.user_asset(asset="eth", recvWindow=30000)[0]['free'])
        # spot_client = Client(base_url="https://testnet.binance.vision")

        # print(spot_client.avg_price("ETHUSDT")['price'])
        # if spot_client.sub_account_list(recvWindow=60000)['success'] == True:
        #     print("successful")

        client = Client(api_key, secret_key)
        # print(client.account(recvWindow=60000))

        params = {
            "symbol": "BTCUSDT",
            "side": "BUY",
            "type": "MARKET",
            # "timeInForce": "GTC",
            "quantity": 0.002,
            # "price": 17000,
            "recvWindow": 60000,
        }
        bian = BiAn()
        user = User(-1, api_key, secret_key, bian)
        rid = str(bian.post_order("BTCUSDT", ORDER_SELL, 0.002, 17000, user))
        
        order = Order(order_record_id=rid, robot_id=1,
                      order_currency_type="BTCUSDT", order_type=ORDER_SELL,
                      order_amount=0.002,
                      order_price=17000, order_status=ORDER_WAIT, order_create_time=datetime.datetime.now(),
                      order_finish_time=None)

        # order.save()
        # print(order.order_record_id)
        response = bian.cancel_order(order, user)
        # response = client.new_order(**params)
        # print(response)
        response = client.get_order("BTCUSDT", orderId=order.order_record_id, recvWindow=60000)
        # print(response)
        # response = client.get_order("BTCUSDT", orderId='15960105783', recvWindow=60000)
        print(response)



    # def test_buy_onces(self):
    #     trade_client = TradeClient(api_key=g_api_key, secret_key=g_secret_key)
    #     order_record_id = trade_client.create_order(symbol="btcusdt",
    #                                                            account_id=g_account_id,
    #                                                            order_type=OrderType.SELL_MARKET,
    #                                                            source=OrderSource.API, amount=0.041, price=None)
    # def test_save_order(self):
        
    #     order = Order(order_record_id=12, robot_id=1,
    #             order_currency_type="btcusdt", order_type=0,
    #             order_amount=12,
    #             order_price=1222, order_status=ORDER_WAIT, order_create_time=datetime.datetime.now(),
    #             order_finish_time=None)
    #     order.save()
    #     order = Order(order_id=12, order_record_id=12, robot_id=1,
    #             order_currency_type="btcusdt", order_type=0,
    #             order_amount=12,
    #             order_price=1222, order_status=ORDER_WAIT, order_create_time=datetime.datetime.now(),
    #             order_finish_time=None)
    #     order.save()
    #     orders = Order.objects.all()
    #     orders = Order.objects.all().order_by("-order_id")
    #     if len(orders) == 0:
    #         order_id = 0
    #     else:
    #         order_id = orders[0].order_id + 1
    #     for order in orders:
    #         print(order.__dict__)
    #         print(order_id)
    
    #     print(snowflake.client.get_guid())

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