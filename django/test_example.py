import okex.okex.Account_api as Account
import okex.okex.Funding_api as Funding
import okex.okex.Market_api as Market
import okex.okex.Public_api as Public
import okex.okex.Trade_api as Trade
import okex.okex.subAccount_api as SubAccount
import okex.okex.status_api as Status
import json
from huobi.client.market import MarketClient



api_key = "e0840ede-1025-4883-857d-0b75315dd682"
secret_key = "06034CF106E7DCC4B01897D48956C1F3"
passphrase = "Aa111111."


if __name__ == '__main__':

    # flag是实盘与模拟盘的切换参数 flag is the key parameter which can help you to change between demo and real trading.
    # flag = '1'  # 模拟盘 demo trading
    flag = '0'  # 实盘 real trading

    # account api
    # accountAPI = Account.AccountAPI(api_key, secret_key, passphrase, False, flag)
    # result = accountAPI.get_account("BTC")
    # print(result['data'][0]['details'][0]['availBal'])
    
    # marketAPI = Market.MarketAPI(api_key, secret_key, passphrase, False, flag)
    # result = marketAPI.get_tickers('SWAP')['data']
    # for item in result:
    #     if item['instId'] == 'BTC-USDT-SWAP'  or item['instId'] == 'ETH-USDT-SWAP':
    #         print(item['last'])
    # print(result)
    # print(result['data'][0]['last'])
    # # trade api
    tradeAPI = Trade.TradeAPI(api_key, secret_key, passphrase, False, flag)
    # result = tradeAPI.get_order_list()['data']
    # for item in result:
    #     order_id = item['ordId']
    #     # result = tradeAPI.cancel_order('BTC-USDT', order_id)
    #     print(result)
    # result = tradeAPI.place_order(instId='BTC-USDT', tdMode='cash', side='buy',
    #                               ordType='limit',px='17938', sz='0.0001')
    # # # 下单  Place Order
    # result = tradeAPI.place_order(instId='BTC-USDT', tdMode='cash', side='sell',
    #                               ordType='market', sz='0.1')
    # print(result)
    # order_id = result['data'][0]['ordId']
    # result = tradeAPI.get_orders('BTC-USDT', order_id)
    # print(result)


    # result = accountAPI.get_account("USDT")
    # print(result['data'][0]['details'][0]['availBal'])
    # market_client = MarketClient()
    # result =  market_client.get_market_tickers()
    # for item in result:
    #     print(item.symbol)
    #     print(item.close)

    # # 撤单  Cancel Order
    # print(result)

    result = tradeAPI.get_orders('BTC-USDT', '534424501061640197')
    print(result)

    # print(result)
    # result = marketAPI.get_ticker('BTC-USDT')
    # print(result['data'][0]['last'])

    # print(json.dumps(result))
