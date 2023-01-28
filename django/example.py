import okex.Account_api as Account
import okex.Funding_api as Funding
import okex.Market_api as Market
import okex.Public_api as Public
import okex.Trade_api as Trade
import okex.subAccount_api as SubAccount
import okex.status_api as Status
import json



api_key = "5f87a072-243e-4b95-9480-bcba28a9a922"
secret_key = "7F22FC194BDE5ACBD0BDF41443FC13C9"
passphrase = "Aa111111."




if __name__ == '__main__':

    # flag是实盘与模拟盘的切换参数 flag is the key parameter which can help you to change between demo and real trading.
    # flag = '1'  # 模拟盘 demo trading
    flag = '0'  # 实盘 real trading

    # account api
    accountAPI = Account.AccountAPI(api_key, secret_key, passphrase, False, flag)

    # funding api
    fundingAPI = Funding.FundingAPI(api_key, secret_key, passphrase, False, flag)
    # 获取资金账户余额信息  Get Balance
    result = fundingAPI.get_balances('BTC')
    print(result)
    # print(result['data'][0]['availBal'])

    # 资金流水查询  Asset Bills Details
    # result = fundingAPI.get_bills()
    # print(result)

    # market api
    marketAPI = Market.MarketAPI(api_key, secret_key, passphrase, False, flag)
    # 获取所有产品行情信息  Get Tickers
    # result = marketAPI.get_tickers('SPOT')
    # 获取单个产品行情信息  Get Ticker
    result = marketAPI.get_ticker('BTC-USDT')
    print(result['data'][0]['last'])

    # trade api
    tradeAPI = Trade.TradeAPI(api_key, secret_key, passphrase, False, flag)
    # 下单  Place Order
    result = tradeAPI.place_order(instId='BTC-USDT', tdMode='cash', side='sell',
                                  ordType='market', sz='0.0001')
    # result = tradeAPI.place_order(instId='BTC-USDT', tdMode='cash', side='sell',
    #                               ordType='limit',px='17938', sz='0.0001')

    print(result)
    order_id = result['data'][0]['ordId']
    # 撤单  Cancel Order
    # result = tradeAPI.cancel_order('BTC-USDT', 531858131375595520)
    {'code': '0', 'data': [{'clOrdId': '', 'ordId': '531495586131320832', 'sCode': '0', 'sMsg': ''}], 'msg': ''}

    print(result)

    result = tradeAPI.get_orders('BTC-USDT', order_id)

    print(result)
    result = fundingAPI.get_balances('BTC')
    print(result)
    # 获取未成交订单列表  Get Order List
    # result = tradeAPI.get_order_list()
    # print(result)
    # 获取历史订单记录（近七天） Get Order History (last 7 days）
    # result = tradeAPI.get_orders_history('FUTURES')
    # 获取历史订单记录（近三个月） Get Order History (last 3 months)
    # result = tradeAPI.orders_history_archive('FUTURES')
    # 获取成交明细  Get Transaction Details
    # result = tradeAPI.get_fills()


    # print(json.dumps(result))
