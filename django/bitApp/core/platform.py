from huobi.client.account import AccountClient
from huobi.client.market import MarketClient
from bitApp.models import *

class HuoBi:

    def __init__(self):
        # self.g_api_key = "3cca6511-04f562c0-94f7cb02-mjlpdje3ld"
        # self.g_secret_key = "595e8002-0853b96c-13d863c5-fb6a5"
        # self.g_account_id = 50267759

        # self.account_client = AccountClient(api_key=self.g_api_key, secret_key=self.g_secret_key)
        self.market_client = MarketClient()
        # self.trade_client = TradeClient(api_key=self.g_api_key, secret_key=self.g_secret_key)

        self.price_dict = {}

    def get_currency_price(self, symbol_name):

        if self.price_dict.get(symbol_name) is None:
            self.price_dict[symbol_name] = self.market_client.get_market_detail(symbol_name).close

        currency_price = self.price_dict[symbol_name]
        return currency_price

    def update_price(self):

        for currency in currency_arry:
            self.price_dict[currency] = self.market_client.get_market_detail(currency).close
        currency_price = self.price_dict[currency]
        return currency_price

    def add_api(self, api_key, secret_key, account_id):
        account_client = AccountClient(api_key=api_key, secret_key=secret_key)
        accounts = account_client.get_accounts()
        account = Account.objects.get(account_id=account_id)

        api = Api.objects.get(api_id=account.api_id)
        api.api_key = api_key
        api.secret_key = secret_key

        account.system_id = accounts[0].id

        api.save()
        account.save()


    def get_accounts_apis(self):

        accounts = Account.objects.filter(account_status=STATUS_OK)

        account_dict = {}
        api_dict = {}
        nickname_dict = {}
        count = len(accounts)


        for i in range(count):
            account_dict[i] = accounts[i].account_id
            api = Api.objects.get(api_id=accounts[i].api_id)
            nickname_dict[i] = accounts[i].account_nickname
            api_dict[i] = api.api_key

        return api_dict, account_dict, nickname_dict, count

    def add_account(self):
        accounts = Account.objects.all()
        account_id = len(accounts)
        apis = Api.objects.all()
        api_id = len(apis)
        api = Api(api_id=api_id, api_key=DEFAULT_API, secret_key=DEFAULT_API)
        account_nickname = "默认账户" + str(account_id)
        account = Account(account_id=account_id, api_id=api_id, system_id=INVALID_ACCOUNT, account_nickname=account_nickname)
        api.save()
        account.save()

    def delet_account(self, account_id):
        account = Account.objects.get(account_id=account_id)
        robots = Robot.objects.filter(robot_account_id=account_id, robot_status=ROBOT_OK)
        if len(robots) > 0:
            return STATUS_ERROR
        account.account_status = ACCOUNT_DELETE
        account.save()

        return STATUS_OK

    def modify_account_nickname(self, account_id, account_nickname):
        account = Account.objects.get(account_id=account_id)
        account.account_nickname = account_nickname
        account.save()

    def get_currencys(self):

        currency_dict = {}
        currency_count = len(currency_arry)
        for i in range(currency_count):
            currency_dict[i] = currency_arry[i]

        return currency_dict, currency_count


    def clear_accounts(self):

        apis = Api.objects.all()
        accounts = Account.objects.all()
        for api in apis:
            api.delete()
        for account in accounts:
            account.delete()





