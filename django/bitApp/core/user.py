from bitApp.models import *
from huobi.client.account import AccountClient
from huobi.client.trade import TradeClient


class User:

    def __init__(self, system_id, api_key, secret_key):

        self.system_id = system_id
        self.api_key = api_key
        self.secret_key = secret_key

        self.trade_client = TradeClient(api_key=self.api_key, secret_key=self.secret_key)
        self.account_client = AccountClient(api_key=self.api_key, secret_key=self.secret_key)

    def get_balance(self, balance_name):
        currency_balances = self.account_client.get_balance(account_id=self.system_id)
        for item in currency_balances:
            if item.currency != balance_name:
                continue
            return item.balance


    @staticmethod
    def load_from_account_id(account_id):

        account = Account.objects.get(account_id=account_id)
        api_id = account.api_id
        api = Api.objects.get(api_id=api_id)

        return User(account.system_id, api.api_key, api.secret_key)
