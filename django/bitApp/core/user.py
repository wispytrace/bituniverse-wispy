from bitApp.models import *
from huobi.client.account import AccountClient
from huobi.client.trade import TradeClient


class User:

    def __init__(self, system_id, api_key, secret_key, plantform):

        self.system_id = system_id
        self.api_key = api_key
        self.secret_key = secret_key
        self.plantform = plantform


    @staticmethod
    def load_from_account_id(account_id):

        account = Account.objects.get(account_id=account_id)
        api_id = account.api_id
        api = Api.objects.get(api_id=api_id)
        plantform = account.account_plantform

        return User(account.system_id, api.api_key, api.secret_key, plantform)
