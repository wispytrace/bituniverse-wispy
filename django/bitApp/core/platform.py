from huobi.client.account import AccountClient
from huobi.client.market import MarketClient
from huobi.client.trade import TradeClient
import datetime
from bitApp.models import *
import logging
from huobi.constant import *

from binance.spot import Spot as Client
import okex.okex.Account_api as AccountAPI
import okex.okex.Funding_api as Funding
import okex.okex.Market_api as Market
import okex.okex.Trade_api as Trade

logger = logging.getLogger('log')


class PlantForm:
    

    def __init__(self) -> None:
        pass

    def post_order(self, currency_type, post_order_type, amount, price, user):
        pass
    
    def create_once_order(self, currency_type, amount, order_type, user):
        pass
    
    def cancel_order(self, order, user):
        pass
    
    def check_order(self, order, user):
        pass

    def get_balance(self, symbol_name, user):
        pass

    def get_currency_price(self, symbol_name):
        pass

    def update_price(self):
        pass
    @staticmethod
    def add_api(api_key, secret_key, account_id):
        pass
    
    @staticmethod
    def update_price(planforms, plantform_name):

        planforms[plantform_name].update_price()
        
        # planforms[OK_STR].price_dict = planforms[HUOBI_STR].price_dict

    @staticmethod
    def add_platnform_api(plantform_name, api_key, secret_key, account_id):
        if plantform_name == HUOBI_STR:
            HuoBi.add_api(api_key, secret_key, account_id)
        elif plantform_name == BIAN_STR:
            BiAn.add_api(api_key, secret_key, account_id)
        elif plantform_name == OK_STR:
            OKEx.add_api(api_key, secret_key, account_id)
        else:
            raise Exception('平台错误')

    @staticmethod
    def get_currencys():

        currency_dict = {}
        currency_count = len(currency_arry)
        for i in range(currency_count):
            currency_dict[i] = currency_arry[i]

        return currency_dict, currency_count

    @staticmethod
    def get_plantforms():

        plantform_dict = {}
        plantform_count = len(plantform_array)
        for i in range(plantform_count):
            plantform_dict[i] = plantform_array[i]

        return plantform_dict, plantform_count
   

    @staticmethod
    def get_accounts_apis():

        accounts = Account.objects.filter(account_status=STATUS_OK)

        account_dict = {}
        api_dict = {}
        nickname_dict = {}
        plantform_dict = {}
        count = len(accounts)

        for i in range(count):
            account_dict[i] = accounts[i].account_id
            api = Api.objects.get(api_id=accounts[i].api_id)
            nickname_dict[i] = accounts[i].account_nickname
            api_dict[i] = api.api_key
            plantform_dict[i] = accounts[i].account_plantform

        return api_dict, account_dict, nickname_dict, plantform_dict, count

    @staticmethod
    def add_account():
        accounts = Account.objects.all()
        account_id = len(accounts)
        apis = Api.objects.all()
        api_id = len(apis)
        api = Api(api_id=api_id, api_key=DEFAULT_API, secret_key=DEFAULT_API)
        account_nickname = "默认账户" + str(account_id)
        account = Account(account_id=account_id, api_id=api_id, system_id=INVALID_ACCOUNT, account_nickname=account_nickname)
        api.save()
        account.save()

    @staticmethod
    def delet_account(account_id):
        account = Account.objects.get(account_id=account_id)
        robots = Robot.objects.filter(robot_account_id=account_id, robot_status=ROBOT_OK)
        if len(robots) > 0:
            return STATUS_ERROR
        account.account_status = ACCOUNT_DELETE
        account.save()

        return STATUS_OK

    @staticmethod
    def modify_account_nickname(account_id, account_nickname):
        account = Account.objects.get(account_id=account_id)
        account.account_nickname = account_nickname
        account.save()

    @staticmethod
    def clear_accounts(self):

        apis = Api.objects.all()
        accounts = Account.objects.all()
        for api in apis:
            api.delete()
        for account in accounts:
            account.delete()


class HuoBi(PlantForm):

    def __init__(self):
        
        self.quote_arry = {"btcusdt": "btc", "ethusdt": "eth", "ltcusdt":"ltc"}
        self.price_dict = {}
        self.update_price()

    def post_order(self, currency_type, order_type, amount, price, user):

        trade_client = TradeClient(api_key=user.api_key, secret_key=user.secret_key)
        if order_type == ORDER_BUY:
            post_order_type = OrderType.BUY_LIMIT
        else:
            post_order_type = OrderType.SELL_LIMIT    
        order_record_id = trade_client.create_order(symbol=currency_type,
                                                                   account_id=user.system_id,
                                                                   order_type=post_order_type,
                                                                   source=OrderSource.API, amount=amount, price=price)

        return order_record_id
    
    def create_once_order(self, currency_type, amount, order_type, user):
        if order_type == ORDER_BUY:
            post_order_type = OrderType.BUY_MARKET
        else:
            post_order_type = OrderType.SELL_MARKET

        trade_client = TradeClient(api_key=user.api_key, secret_key=user.secret_key)    
        try:
            logger.error("立即交易额度"+str(amount)+" 交易类型为"+str(order_type))
            order_record_id = trade_client.create_order(symbol=currency_type,
                                                                   account_id=user.system_id,
                                                                   order_type=post_order_type,
                                                                   source=OrderSource.API, amount=amount, price=None)
            return order_record_id
        except Exception as e:
            logger.error(repr(e))

    def cancel_order(self, order, user):
        trade_client = TradeClient(api_key=user.api_key, secret_key=user.secret_key)    

        for i in range(MAX_REPOST_NUM):

            try:
                trade_client.cancel_order(order.order_currency_type, order.order_record_id)
                return STATUS_OK

            except Exception as e:
                if i == MAX_REPOST_NUM - 1:
                    logger.error("撤销订单失败"+str(order.order_price)+" "+str(order.order_type))
                    logger.error(repr(e))
                    return STATUS_ERROR
        

    def check_order(self, order, user):

        trade_client = TradeClient(api_key=user.api_key, secret_key=user.secret_key)    
        order_info = trade_client.get_order(order_id=order.order_record_id)
        order_info_dict = {}

        if order_info.state == OrderState.FILLED or order_info.state == OrderState.PARTIAL_CANCELED:
            order_info_dict['order_status'] = ORDER_FINISH
            order_info_dict["order_amount"] = float(order_info.filled_amount)
            order_info_dict["order_price"] = float(order_info.price)
            order_info_dict["order_create_time"] = datetime.datetime.fromtimestamp(int(order_info.created_at / 1000))
            order_info_dict["order_finish_time"] = datetime.datetime.fromtimestamp(int(order_info.finished_at / 1000))
            order_info_dict["order_transfer_fees"] = float(order_info.filled_fees)
        elif order_info.state == OrderState.CANCELED or order_info.state == OrderState.PLACE_TIMEOUT or order_info.state == OrderState.FAILED:
            order_info_dict['order_status'] = ORDER_CANCEL
        else:
            order_info_dict['order_status'] = ORDER_WAIT

        return order_info_dict
    
    def get_balance(self, symbol_name, user):

        account_client = AccountClient(api_key=user.api_key, secret_key=user.secret_key)
        currency_balances = account_client.get_balance(account_id=user.system_id)
        for item in currency_balances:
            if item.currency != symbol_name:
                continue
            return item.balance

    def get_currency_price(self, symbol_name):

        if self.price_dict.get(symbol_name) is None:
            market_client = MarketClient()
            self.price_dict[symbol_name] = market_client.get_market_detail(symbol_name).close
        currency_price = self.price_dict[symbol_name]
        
        return currency_price

    def update_price(self):
        market_client = MarketClient()
        result =  market_client.get_market_tickers()
        for item in result:
            for currency in currency_arry:
                if currency == item.symbol:
                    self.price_dict[currency] = item.close
        # currency_price = self.price_dict[currency]
        # return currency_price

    @staticmethod
    def add_api(api_key, secret_key, account_id):
        account_client = AccountClient(api_key=api_key, secret_key=secret_key)
        accounts = account_client.get_accounts()
        account = Account.objects.get(account_id=account_id)

        api = Api.objects.get(api_id=account.api_id)
        api.api_key = api_key
        api.secret_key = secret_key

        account.account_plantform = HUOBI_STR

        account.system_id = accounts[0].id

        api.save()
        account.save()


class OKEx(PlantForm):
        

    def __init__(self):
        
        self.quote_arry = {"btcusdt": "BTC", "ethusdt": "ETH", "ltcusdt":"LTC"}
        self.currency_trans = {"btcusdt":"BTC-USDT", "ethusdt": "ETH-USDT", "ltcusdt":"LTC-USDT"} 
        self.price_dict = {}
        self.flag = '0'

    def delay_time(self, seconds):
        count = 0
        for i in range(int(seconds*5000000)):
            count += i % 3 + count % 3

    def post_order(self, currency_type, order_type, amount, price, user):
        
        secret_key, passphrase = user.secret_key.split('@ps=')
        tradeAPI = Trade.TradeAPI(user.api_key, secret_key, passphrase, False, self.flag)
        if order_type == ORDER_BUY:
            post_order_type = "buy"
        else:
            post_order_type = "sell"
        result = tradeAPI.place_order(instId=self.currency_trans[currency_type], tdMode='cash', side=post_order_type, ordType='limit',px=str(price), sz=str(amount))
        order_record_id = result['data'][0]['ordId']

        return order_record_id

    def create_once_order(self, currency_type, amount, order_type, user):
        
        secret_key, passphrase = user.secret_key.split('@ps=')
        tradeAPI = Trade.TradeAPI(user.api_key, secret_key, passphrase, False, self.flag)
        if order_type == ORDER_BUY:
            post_order_type = "buy"
        else:
            post_order_type = "sell"
        try:
            logger.error("立即交易额度"+str(amount)+" 交易类型为"+str(order_type))
            result = tradeAPI.place_order(instId=self.currency_trans[currency_type], tdMode='cash', side=post_order_type, ordType='market', sz=str(amount))
            # print(result)
            # print(tradeAPI.get_orders(self.currency_trans[currency_type], result['data'][0]['ordId']))                    
            return result['data'][0]['ordId']
        except Exception as e:
            logger.error(repr(e))

    def cancel_order(self, order, user):

        secret_key, passphrase = user.secret_key.split('@ps=')
        tradeAPI = Trade.TradeAPI(user.api_key, secret_key, passphrase, False, self.flag)

        for i in range(MAX_REPOST_NUM):
            try:
                result = tradeAPI.cancel_order(self.currency_trans[order.order_currency_type], order.order_record_id)

                if result['code'] != '0':
                    raise Exception(result)
                return STATUS_OK
            except Exception as e:
                if i == MAX_REPOST_NUM - 1:
                    logger.error("撤销订单失败"+str(order.order_price)+" "+str(order.order_type))
                    logger.error(repr(e))
                    return STATUS_ERROR


    def check_order(self, order, user):

        secret_key, passphrase = user.secret_key.split('@ps=')
        tradeAPI = Trade.TradeAPI(user.api_key, secret_key, passphrase, False, self.flag)

        order_info_dict = {}

        result = tradeAPI.get_orders(self.currency_trans[order.order_currency_type], order.order_record_id)
        result_data = result['data'][0]

        order_state = result_data['state']

        if order_state == 'filled':
            order_amount = result_data['accFillSz']
            order_price = result_data['avgPx']
            order_create_time = int(result_data['cTime'])
            order_finish_time = int(result_data['fillTime'])
            order_transfer_fees = result_data['fee']
            order_info_dict['order_status'] = ORDER_FINISH
            order_info_dict["order_amount"] = float(order_amount)
            order_info_dict["order_price"] = float(order_price)
            order_info_dict["order_create_time"] = datetime.datetime.fromtimestamp(int(order_create_time / 1000))
            order_info_dict["order_finish_time"] = datetime.datetime.fromtimestamp(int(order_finish_time / 1000))
            order_info_dict["order_transfer_fees"] = -float(order_transfer_fees)
        elif order_state == 'canceled':
            order_info_dict['order_status'] = ORDER_CANCEL
        elif order_state == 'live':
            order_info_dict['order_status'] = ORDER_WAIT
        else:
            order_info_dict['order_status'] = ORDER_Fail

        # self.delay_time(OK_DELAY_TIME)

        return order_info_dict
    
    def get_balance(self, symbol_name, user):
        
        secret_key, passphrase = user.secret_key.split('@ps=')
        accountAPI = AccountAPI.AccountAPI(user.api_key, secret_key, passphrase, False, self.flag)
        result = accountAPI.get_account(symbol_name.upper())

        balance = result['data'][0]['details'][0]['availBal']
        return balance     

    def get_currency_price(self, symbol_name):


        if self.price_dict.get(symbol_name) is None:
            api_key = ""
            secret_key = ""
            passphrase = ""
            marketAPI = Market.MarketAPI(api_key, secret_key, passphrase, False, self.flag)
            result = marketAPI.get_ticker(self.currency_trans[symbol_name])
            self.price_dict[symbol_name] = round(float(result['data'][0]['last']), 2)
        
        currency_price = self.price_dict[symbol_name]
        
        return currency_price

    def update_price(self):
        api_key = ""
        secret_key = ""
        passphrase = ""
        marketAPI = Market.MarketAPI(api_key, secret_key, passphrase, False, self.flag)
        result = marketAPI.get_tickers('SWAP')['data']
        for item in result:
            for currency in currency_arry:
                if item['instId'] == self.currency_trans[currency]+'-SWAP':
                    self.price_dict[currency] = round(float(item['last']), 2)

            # result = marketAPI.get_ticker(self.currency_trans[currency])
            # self.price_dict[currency] = round(float(result['data'][0]['last']), 2)
        # currency_price = self.price_dict[currency]
        # return currency_price

    @staticmethod
    def add_api(api_key, secret_key, account_id):
        
        secret_key_real, passphrase = secret_key.split('@ps=')

        fundingAPI = Funding.FundingAPI(api_key, secret_key_real, passphrase, False, '0')

        result = fundingAPI.get_balances("USDT")
        if result['code'] == '0':
            account = Account.objects.get(account_id=account_id)

            api = Api.objects.get(api_id=account.api_id)
            api.api_key = api_key
            api.secret_key = secret_key

            account.account_plantform = OK_STR

            api.save()
            account.save()



class BiAn(PlantForm):

    def __init__(self):
        
        self.quote_arry = {"btcusdt": "btc", "ethusdt": "eth", "ltcusdt":"ltc"}
        self.price_dict = {}
        # self.update_price()

    def post_order(self, currency_type, order_type, amount, price, user):

        client = Client(user.api_key, user.secret_key)
        if order_type == ORDER_BUY:
            post_order_type = "BUY"
        else:
            post_order_type = "SELL"

        params = {
            "symbol": currency_type.upper(),
            "side": post_order_type,
            "type": "LIMIT",
            "timeInForce": "GTC",
            "quantity": amount,
            "price": price,
            "recvWindow": 60000
        }
        response = client.new_order(**params)
        order_record_id = response['orderId']

        return order_record_id

    def create_once_order(self, currency_type, amount, order_type, user):
        if order_type == ORDER_BUY:
            post_order_type = "BUY"
        else:
            post_order_type = "SELL"

        params = {
            "symbol": currency_type.upper(),
            "side": post_order_type,
            "type": "MARKET",
            "timeInForce": "GTC",
            "quantity": amount,
            "recvWindow": 60000,
        }
        client = Client(user.api_key, user.secret_key)
        try:
            logger.error("立即交易额度"+str(amount)+" 交易类型为"+str(order_type))
            response = client.new_order(**params)
            return response['orderId']
        except Exception as e:
            logger.error(repr(e))

    def cancel_order(self, order, user):

        client = Client(user.api_key, user.secret_key)
        for i in range(MAX_REPOST_NUM):
            try:
                response = client.cancel_order(order.order_currency_type.upper(), orderId=order.order_record_id, recvWindow=60000)
                return STATUS_OK
            except Exception as e:
                if i == MAX_REPOST_NUM - 1:
                    logger.error(client.get_order(order.order_currency_type.upper(), orderId=order.order_record_id, recvWindow=60000))
                    logger.error("撤销订单失败"+str(order.order_price)+" "+str(order.order_type))
                    logger.error(repr(e))
                    return STATUS_ERROR


    def check_order(self, order, user):

        client = Client(user.api_key, user.secret_key)
        order_info_dict = {}
        response = client.get_order(order.order_currency_type.upper(), orderId=order.order_record_id, recvWindow=60000)

        if response['status'] == 'FILLED':
            order_info_dict['order_status'] = ORDER_FINISH
            order_info_dict["order_amount"] = float(response['executedQty'])
            order_info_dict["order_price"] = float(response['price'])
            order_info_dict["order_create_time"] = datetime.datetime.fromtimestamp(int(response['time'] / 1000))
            order_info_dict["order_finish_time"] = datetime.datetime.fromtimestamp(int(response['updateTime'] / 1000))
            order_info_dict["order_transfer_fees"] = float(0)
        elif response['status'] == 'CANCELED' or response['status'] == 'REJECTED' or response['status'] == 'EXPIRED':
            order_info_dict['order_status'] = ORDER_CANCEL
        else:
            order_info_dict['order_status'] = ORDER_WAIT

        return order_info_dict
    
    def get_balance(self, symbol_name, user):
        spot_client = Client(user.api_key, user.secret_key)
        
        return spot_client.user_asset(asset=symbol_name, recvWindow=30000)[0]['free']

    def get_currency_price(self, symbol_name):

        if self.price_dict.get(symbol_name) is None:
            spot_client = Client()
            self.price_dict[symbol_name] = round(float(spot_client.avg_price(symbol_name.upper())['price']), 2)
        currency_price = self.price_dict[symbol_name]
        
        return currency_price

    def update_price(self):
        spot_client = Client()
        for currency in currency_arry:
            self.price_dict[currency] = round(float(spot_client.avg_price(currency.upper())['price']), 2)
        currency_price = self.price_dict[currency]
        return currency_price


    @staticmethod
    def add_api(api_key, secret_key, account_id):
        
        spot_client = Client(api_key, secret_key)
        if spot_client.sub_account_list(recvWindow=60000)['success'] == True:
            account = Account.objects.get(account_id=account_id)

            api = Api.objects.get(api_id=account.api_id)
            api.api_key = api_key
            api.secret_key = secret_key

            account.account_plantform = BIAN_STR

            # account.system_id = 

            api.save()
            account.save()

