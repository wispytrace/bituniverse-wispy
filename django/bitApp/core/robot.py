from cmath import log
import datetime
import logging

import threading
import math
import time

from bitApp.models import *
from huobi.constant import *

logger = logging.getLogger('log')

class RobotEntity:

    def __init__(self):
        self.robot = None
        self.order_list = None
        self.policy = None
        self.robot_summary = None
        self.huobi = None
        self.user = None

    @staticmethod
    def load_robot(robot):
        if robot.robot_policy_type == GEOMETRIC_POLICY:
            robot_entity = GeometricRobot()
            policy = GeometricPolicy.objects.get(policy_id=robot.robot_policy_id)
        elif robot.robot_policy_type == INFINITE_POLICY:
            robot_entity = InfiniteRobot()
            policy = InfinitePolicy.objects.get(policy_id=robot.robot_policy_id)
        robot_summary = RobotSummary.objects.get(summary_id=robot.robot_summary_id)
        robot_entity.robot = robot
        robot_entity.policy = policy
        robot_entity.robot_summary = robot_summary

        return robot_entity

    def load_orders(self):
        if self.robot is None:
            return
        self.order_list = []
        order_list = Order.objects.filter(robot_id=self.robot.robot_id)
        for order in order_list:
            if order.order_status != ORDER_CANCEL:
                self.order_list.append(order)

    def set_huobi(self, huobi):
        self.huobi = huobi

    def set_user(self, user):
        self.user = user

    def create_once_order(self, amount, order_type):
        try:
            order_record_id = self.user.trade_client.create_order(symbol=self.robot.robot_currency_type,
                                                                   account_id=self.user.system_id,
                                                                   order_type=order_type,
                                                                   source=OrderSource.API, amount=amount, price=None)
        except Exception as e:
            logger.error(repr(e))
            # self.create_once_buy_order(amount)

    def post_order(self, post_order_type, amount, price, count):
        
        if count > MAX_REPOST_NUM:
            raise Exception("创建订单失败")

        try:
            order_record_id = self.user.trade_client.create_order(symbol=self.robot.robot_currency_type,
                                                                   account_id=self.user.system_id,
                                                                   order_type=post_order_type,
                                                                   source=OrderSource.API, amount=amount, price=price)
        except Exception as e:
            logger.error(repr(e))
            order_record_id = self.post_order(post_order_type, amount, price, count+1)
            
        return order_record_id

    def create_order(self, order_type, order_amount, order_price):
        amount = round(order_amount, 6)
        price = round(order_price, 2)

        if order_type == ORDER_BUY:
            post_order_type = OrderType.BUY_LIMIT
        else:
            post_order_type = OrderType.SELL_LIMIT

        order_record_id = self.post_order(post_order_type, amount, price, 0)

        orders = Order.objects.all()
        if len(orders) == 0:
            order_id = 0
        else:
            order_id_list = []
            for order in orders:
                order_id_list.append(order.order_id)
            order_id = max(order_id_list) + 1

        order = Order(order_id=order_id, order_record_id=order_record_id, robot_id=self.robot.robot_id,
                      order_currency_type=self.robot.robot_currency_type, order_type=order_type,
                      order_amount=order_amount,
                      order_price=order_price, order_status=ORDER_WAIT, order_create_time=datetime.datetime.now(),
                      order_finish_time=None)

        order.save()

        return order

    def post_batch_orders(self, order_config_list, count):

        if count > MAX_REPOST_NUM:
            raise Exception("创建订单失败")

        try:
            create_result = self.user.trade_client.batch_create_order(order_config_list=order_config_list)

        except Exception as e:
            logger.error(repr(e))
            create_result = self.post_batch_orders(order_config_list, count+1)

        return create_result

    def create_batch_order(self, order_type, order_amounts, prices):
        order_config_list = []
        order_id_list = []
        order_total_list = []

        if order_type == ORDER_BUY:
            post_order_type = OrderType.BUY_LIMIT
        else:
            post_order_type = OrderType.SELL_LIMIT

        for i in range(len(order_amounts)):
            order_config = {
                "account_id":self.user.system_id,
                "symbol":self.robot.robot_currency_type,
                "order_type": post_order_type,
                "source": OrderSource.API,
                "amount": order_amounts[i],
                "price": prices[i]
            }
            order_config_list.append(order_config)
            if ((i+1)%10)==0 or (i==(len(order_amounts)-1)):
                create_result = self.post_batch_orders(order_config_list, 0)
                if create_result and len(create_result):
                    for item in create_result:
                        order_id_list.append(item.order_id)
                order_total_list = order_total_list + order_config_list
                order_config_list = []

        orders = Order.objects.all()
        if len(orders) == 0:
            order_id = 0
        else:
            order_id_list = []
            for order in orders:
                order_id_list.append(order.order_id)
            order_id = max(order_id_list) + 1

        for i in range(len(order_total_list)):
            order = Order(order_id=order_id, order_record_id=order_id_list[i], robot_id=self.robot.robot_id,
                order_currency_type=self.robot.robot_currency_type, order_type=order_type,
                order_amount=order_total_list[i]["amount"],
                order_price=order_total_list[i]["price"], order_status=ORDER_WAIT, order_create_time=datetime.datetime.now(),
                order_finish_time=None)

            order_id = order_id + 1
            order.save()

    def cancel_order(self, order_record_id, count):
        
        if count > MAX_REPOST_NUM:
            raise Exception("撤销订单失败")

        try:
            canceled_order_id = self.user.trade_client.cancel_order(self.robot.robot_currency_type, order_record_id)

        except Exception as e:
            logger.error(repr(e))
            canceled_order_id = self.cancel_order(order_record_id, count+1)


    def cancel_orders(self):
        for order in self.order_list:
            if order.order_status == ORDER_WAIT:
                try:
                    canceled_order_id = self.cancel_order(order.order_record_id, 0)
                except Exception as e:
                    logger.error(repr(e))
        
        self.update_order(self.order_list)

    def cancel_currencys(self):

        btc_num = float(self.user.get_balance('btc'))
        sell_amount = min(btc_num, max(self.robot_summary.hold_currency_num ,0))
        sell_amount = round(sell_amount, 6)
        if sell_amount < 1e-4:
            return
        self.create_once_order(sell_amount, OrderType.SELL_MARKET)



    def pause_resume_robot(self):

        if self.robot.robot_status == ROBOT_OK:
            # logger.info("尝试暂停机器人" + str(robot_id))
            self.robot.robot_status = ROBOT_PAUSE
        elif self.robot.robot_status == ROBOT_PAUSE:
            # logger.info("尝试恢复机器人" + str(robot_id))
            self.robot.robot_status = ROBOT_OK

        self.robot.save()
        # logger.info("暂停/恢复机器人成功，机器人现在相关参数如下")
        # logger.info(robot.__dict__)

    def delete_robot(self):

        # logger.info("尝试删除机器人 " + str(robot_id))
        # self.cancel_orders()

        self.robot.robot_status = ROBOT_DELETE
        self.robot.save()
        # logger.info("已删除机器人 " + str(robot_id) + "相关参数如下")
        # logger.info(robot.__dict__)

    def get_pender_order_list(self):

        pender_order_list = []
        for order in self.order_list:
            if order.order_status == ORDER_WAIT:

                pender_order = {}
                pender_order['order_price'] = round(float(order.order_price), 2)
                price_now = self.huobi.get_currency_price(self.robot.robot_currency_type)
                pender_order['order_rate'] = round(math.fabs((float(order.order_price) - price_now)) / price_now * 100,
                                                   3)
                pender_order['id'] = order.order_id
                if order.order_type == ORDER_BUY:
                    pender_order['order_type'] = "买入"
                else:
                    pender_order['order_type'] = "卖出"

                pender_order_list.append(pender_order)

        pender_order_list.sort(key=lambda x: x['order_rate'])

        return pender_order_list

    def get_trade_order_list(self):

        trade_order_list = []
        for order in self.order_list:
            if order.order_status == ORDER_CANCEL or order.order_status == ORDER_Fail or order.order_refer_id == ORDER_NONE_REF:
                continue

            trade_order = {}
            order_ref = Order.objects.get(order_id=order.order_refer_id)
            if order.order_type == ORDER_BUY:
                buy_order = order
                sell_order = order_ref
            else:
                buy_order = order_ref
                sell_order = order
            trade_order['buy_price'] = round(buy_order.order_price, 2)
            trade_order['buy_transfee'] = round(buy_order.order_transfer_fees, 6)
            trade_order['buy_amount'] = round(buy_order.order_amount * buy_order.order_price, 6)
            trade_order['buy_time'] = buy_order.order_create_time

            trade_order['sell_price'] = round(sell_order.order_price, 2)
            trade_order['sell_transfee'] = round(sell_order.order_transfer_fees, 6)
            trade_order['sell_amount'] = round(sell_order.order_amount * sell_order.order_price, 6)
            trade_order['sell_time'] = sell_order.order_create_time

            if buy_order.order_status == ORDER_FINISH:
                trade_order['buy_time'] = buy_order.order_finish_time
                if sell_order.order_status == ORDER_FINISH:
                    trade_order['sell_time'] = sell_order.order_finish_time
                    trade_order['order_status'] = '+' + str(round(trade_order['sell_amount'] - trade_order['buy_amount'], 6))
                else:
                    trade_order['order_status'] = '等待卖出'
                    trade_order['sell_amount'] = 0
            else:
                trade_order['sell_time'] = sell_order.order_finish_time
                trade_order['order_status'] = '等待买入'
                trade_order['buy_amount'] = 0

            if int((trade_order['sell_time'] - trade_order['buy_time']).seconds) > 0:
                trade_order['order_time'] = trade_order['sell_time']
            else:
                trade_order['order_time'] = trade_order['buy_time']

            trade_order['order_time'] = (trade_order['order_time']+datetime.timedelta(hours=8)).strftime("%Y/%m/%d %H:%M:%S")
            trade_order['sell_time'] = (trade_order['sell_time']+datetime.timedelta(hours=8)).strftime("%Y/%m/%d %H:%M:%S")
            trade_order['buy_time'] = (trade_order['buy_time']+datetime.timedelta(hours=8)).strftime("%Y/%m/%d %H:%M:%S")

            trade_order['id'] = max(sell_order.order_id, buy_order.order_id)

            trade_order_list.append(trade_order)

        trade_order_list.sort(key=lambda x: int(x['id']), reverse=True)
        size = min(len(trade_order_list), 200)
        trade_order_list = trade_order_list[:size]

        return trade_order_list

    def get_float_profit(self):

        buy_price = 0
        buy_amount = 0
        for order in self.order_list:
            if order.order_status == ORDER_FINISH and order.order_type == ORDER_BUY:
                buy_amount += order.order_amount
                buy_price += order.order_amount * order.order_price

        buy_price = buy_price / buy_amount if buy_amount != 0 else 0
        float_profit = round((self.huobi.get_currency_price(self.robot.robot_currency_type) - buy_price) * max(
            self.robot_summary.hold_currency_num, 0), 6)

        return float_profit

    def get_robot_info(self):

        robot_info = {}
        if self.robot.robot_status == ROBOT_OK:
            robot_info['status'] = '正常运行'
        elif self.robot.robot_status == ROBOT_PAUSE:
            robot_info['status'] = '暂停运行'
        else:
            robot_info['status'] = '已删除'
        robot_info['currency_type'] = self.robot.robot_currency_type
        robot_info['max_price'] = self.policy.max_price
        robot_info['min_price'] = self.policy.min_price

        robot_info['policy_type'] = self.get_robot_name()
        robot_info['grid_num'] = self.get_grid_num()

        robot_info['robot_id'] = self.robot.robot_id
        create_time = self.robot.robot_create_time.replace(tzinfo=None)
        robot_info['runtime'] = str(datetime.timedelta(days=(datetime.datetime.now() - create_time).days))[:-7] + str(
            datetime.timedelta(seconds=(datetime.datetime.now() - create_time).seconds))
        robot_info['trade_num'] = len(self.order_list)

        robot_info['hold_num'] = str('%g' % round(self.robot_summary.hold_currency_num, 6))
        robot_info['invested_num'] = round(self.robot_summary.invested_money, 6)
        robot_info['grid_per'] = str('%g' % self.policy.grid_invest)
        robot_info['grid_profit_rate'] = round(self.get_grid_profit_rate(), 6)
        robot_info['currency_price'] = self.huobi.get_currency_price(self.robot.robot_currency_type)

        robot_info['robot_profit'] = round(self.robot_summary.profit, 6)

        robot_info['float_profit'] = round(self.get_float_profit(), 6)
        robot_info['robot_profit_rate'] = round(robot_info['robot_profit'] / (robot_info['invested_num'] + 1) * 100, 6)
        robot_info['total_profit'] = round(
            robot_info['robot_profit'] + robot_info['float_profit'] - self.robot_summary.total_transfer_fee, 6)
        robot_info['total_year_rate'] = round(robot_info['total_profit'] / (robot_info['invested_num'] + 1) /
                                              (((datetime.datetime.now() - create_time).days + 1) / 365), 6)

        return robot_info


class GeometricRobot(RobotEntity):

    def get_grid_profit_rate(self):

        return self.policy.grid_profit_rate

    def get_robot_name(self):

        return "等比网格机器人"

    def get_grid_num(self):

        return self.policy.grid_num

    @staticmethod
    def create_robot(currency_type, max_price, min_price, grid_num, grid_invest, expect_money, grid_profit_rate, account_id):

        policy_id = len(GeometricPolicy.objects.all())
        policy = GeometricPolicy(policy_id=policy_id, max_price=max_price, min_price=min_price, grid_num=grid_num,
                                 grid_invest=grid_invest,
                                 expect_money=expect_money, grid_profit_rate=grid_profit_rate)

        summary_id = len(RobotSummary.objects.all())
        summary = RobotSummary(summary_id=summary_id, invested_money=0)

        robot_id = len(Robot.objects.all())
        robot = Robot(robot_id=robot_id, robot_summary_id=summary_id, robot_policy_type=GEOMETRIC_POLICY,
                      robot_policy_id=policy_id,
                      robot_currency_type=currency_type, robot_status=ROBOT_PAUSE,
                      robot_create_time=datetime.datetime.now())

        robot.robot_account_id = account_id

        policy.save()
        summary.save()
        robot.save()

        return robot

    @staticmethod
    def get_robot_invest_parameter(currency_type, max_price, min_price, grid_num, per_invest, huobi, user):

        parameter = {}
        currency_price = huobi.get_currency_price(currency_type)
        usdt_num = float(user.get_balance('usdt'))
        btc_num = float(user.get_balance('btc'))
        grid_profit_rate = (((max_price / min_price) ** (1 / (grid_num))) - 1) * 100
        usdt_need = 0
        btc_need = 0
        for i in range(grid_num+1):

            grid_price = ((1 + grid_profit_rate / 100) ** i) * min_price

            if grid_price > currency_price and (grid_price / (1+grid_profit_rate/100)) < currency_price:
                continue
            
            grid_price = round(grid_price, 2)

            amount = per_invest
            amount = max(amount, 1e-4)

            if grid_price < currency_price:
                usdt_need += amount * currency_price
            else:
                btc_need += amount

        parameter['currency_price'] = currency_price
        parameter['btc_num'] = str('%g' % btc_num)
        parameter['usdt_num'] = usdt_num
        parameter['per_grid'] = str('%g' % grid_profit_rate)
        parameter['usdt_need'] = usdt_need
        parameter['btc_need'] = str('%g' % btc_need)

        return parameter

    def modify_robot(self, max_price, min_price, grid_num, grid_invest, expect_money, grid_profit_rate):

        self.policy.max_price = max_price
        self.policy.min_price = min_price
        self.policy.grid_invest = grid_invest
        self.policy.grid_num = grid_num
        self.policy.grid_profit_rate = grid_profit_rate
        self.policy.expect_money = expect_money
        self.policy.save()

    def get_parameter(self):
        parameter = {}
        parameter['max_price'] = self.policy.max_price
        parameter['min_price'] = self.policy.min_price
        parameter['grid_num'] = self.policy.grid_num
        parameter['per_invest'] = str('%g' % self.policy.grid_invest)
        parameter['currency_type'] = self.robot.robot_currency_type

        return parameter


    def init_robot_order(self):

        currency_price = self.huobi.get_currency_price(self.robot.robot_currency_type)
        need_amount = math.log(currency_price / self.policy.min_price, (1 + self.policy.grid_profit_rate / 100))
        need_amount =(self.policy.grid_num - (int(need_amount) + 1)) * self.policy.grid_invest
        user_amount = float(self.user.get_balance('btc'))

        if need_amount > user_amount:
            money = round((need_amount - user_amount + 1e-5) * currency_price, 3)
            self.create_once_order(money, OrderType.BUY_MARKET)
            time.sleep(1)

        for i in range(self.policy.grid_num + 1):

            grid_price = ((1 + self.policy.grid_profit_rate / 100) ** i) * self.policy.min_price
            if grid_price >= currency_price and (grid_price / (1 + self.policy.grid_profit_rate / 100)) < currency_price:
                continue
            grid_price = round(grid_price, 2)

            amount = self.policy.grid_invest
            amount = max(amount, 1e-4)

            if grid_price <= currency_price:
                order_type = ORDER_BUY
            else:
                order_type = ORDER_SELL

            self.create_order(order_type, amount, grid_price)

        self.robot_summary.invested_money = self.policy.expect_money
        self.robot_summary.hold_currency_num = need_amount
        self.robot.robot_status = ROBOT_OK

        self.robot.save()
        self.robot_summary.save()

    def supply_order(self, order):

        if self.robot.robot_status != ROBOT_OK:
            return

        amount = round(self.policy.grid_invest, 6)
        amount = max(amount, 1e-4)
        if order.order_type == ORDER_BUY:
            order_price = order.order_price * (1 + self.policy.grid_profit_rate / 100)
            supplied_order = self.create_order(ORDER_SELL, amount, order_price)
        else:
            order_price = order.order_price / (1 + self.policy.grid_profit_rate / 100)
            supplied_order = self.create_order(ORDER_BUY, amount, order_price)

        if order.order_refer_id == ORDER_NONE_REF:
            supplied_order.order_refer_id = order.order_id
            supplied_order.save()

    def update_order(self, orders):


        trade_client = self.user.trade_client

        for order in orders:
            if order.order_status == ORDER_WAIT:
                try:
                    order_info = trade_client.get_order(order_id=order.order_record_id)
                except Exception as e:
                    # logger.error("查询订单失败，其订单号为 " + str(order.order_record_id) + repr(e))
                    if self.robot.robot_status != ROBOT_OK:
                        order.order_status = ORDER_Fail
                        order.save()
                    continue
                if order_info.state == OrderState.FILLED or order_info.state == OrderState.PARTIAL_CANCELED:
                    order.order_status = ORDER_FINISH
                    order.order_amount = float(order_info.filled_amount)
                    order.order_price = float(order_info.price)
                    order.order_create_time = datetime.datetime.fromtimestamp(int(order_info.created_at / 1000))
                    order.order_finish_time = datetime.datetime.fromtimestamp(int(order_info.finished_at / 1000))
                    order.order_transfer_fees = float(order_info.filled_fees)

                    self.robot_summary.total_transfer_fee += float(order_info.filled_fees)
                    if order_info.type == OrderType.SELL_LIMIT:
                        self.robot_summary.hold_currency_num -= float(order_info.filled_amount)
                        self.robot_summary.profit += (1 / (
                                1 + 100 / self.policy.grid_profit_rate)) * float(order_info.filled_amount) * float(
                            order_info.price)
                    else:
                        self.robot_summary.hold_currency_num += float(order_info.filled_amount)
                    self.robot_summary.save()
                    order.save()
                    self.supply_order(order)

                elif order_info.state == OrderState.CANCELED or order_info.state == OrderState.PLACE_TIMEOUT or order_info.state == OrderState.FAILED:

                    order.order_status = ORDER_CANCEL
                    order.save()
                    # order.delete()

           


class InfiniteRobot(RobotEntity):

    def get_grid_profit_rate(self):

        return self.policy.rate_sell

    def get_robot_name(self):

        return "无限网格机器人"

    def get_grid_num(self):

        return "INFINITE"

    @staticmethod
    def create_robot(currency_type, max_price, min_price, grid_invest, rate_buy, rate_sell, expect_money, account_id):

        policy_id = len(InfinitePolicy.objects.all())
        policy = InfinitePolicy(policy_id=policy_id, max_price=max_price, min_price=min_price, grid_invest=grid_invest,
                                rate_buy=rate_buy, rate_sell=rate_sell, expect_money=expect_money)

        summary_id = len(RobotSummary.objects.all())
        summary = RobotSummary(summary_id=summary_id, invested_money=0)

        robot_id = len(Robot.objects.all())
        robot = Robot(robot_id=robot_id, robot_summary_id=summary_id, robot_policy_type=INFINITE_POLICY,
                      robot_policy_id=policy_id,
                      robot_currency_type=currency_type, robot_status=ROBOT_OK,
                      robot_create_time=datetime.datetime.now())
        robot.robot_account_id = account_id
        policy.save()
        summary.save()
        robot.save()

        return robot

    @staticmethod
    def get_robot_invest_parameter(currency_type, sell_percent, expect_money, huobi, user):

        parameter = {}
        currency_price = huobi.get_currency_price(currency_type)
        usdt_num = float(user.get_balance('usdt'))
        btc_num = float(user.get_balance('btc'))
        grid_profit_rate = sell_percent
        usdt_need = expect_money
        btc_need = 0

        parameter['currency_price'] = currency_price
        parameter['btc_num'] = str('%g' % btc_num)
        parameter['usdt_num'] = usdt_num
        parameter['per_grid'] = str('%g' % grid_profit_rate)
        parameter['usdt_need'] = usdt_need
        parameter['btc_need'] = str('%g' % btc_need)

        return parameter

    def modify_robot(self, max_price, min_price, grid_invest, rate_buy, rate_sell, expect_money):
        
        if expect_money >  self.policy.expect_money + grid_invest:
            self.init_robot_order()

        self.policy.max_price = max_price
        self.policy.min_price = min_price
        self.policy.grid_invest = grid_invest
        self.policy.rate_buy = rate_buy
        self.policy.rate_sell = rate_sell
        self.policy.expect_money = expect_money
        
        self.policy.save()

    def get_parameter(self):

        parameter = {}
        parameter['max_price'] = self.policy.max_price
        parameter['min_price'] = self.policy.min_price
        parameter['buy_percent'] = self.policy.rate_buy
        parameter['sell_percent'] = self.policy.rate_sell
        parameter['currency_type'] = self.robot.robot_currency_type
        parameter['per_invest'] = str('%g' % self.policy.grid_invest)
        parameter['expect_money'] = self.policy.expect_money

        return parameter

    def init_robot_order(self):

        currency_price = self.huobi.get_currency_price(self.robot.robot_currency_type)

        order_price = ((1 - self.policy.rate_buy / 100)) * currency_price
        order_price = round(order_price, 2)

        amount = round(self.policy.grid_invest / order_price, 6)
        amount = max(amount, 1e-4)

        self.create_order(ORDER_BUY, amount, order_price)

        self.robot_summary.invested_money += amount * order_price

        self.robot_summary.save()

    def supply_order(self, order):

        if self.robot.robot_status != ROBOT_OK:
            return

        if order.order_type == ORDER_BUY:
            
            order_price = order.order_price * (1 + self.policy.rate_sell / 100)

            if order_price < self.policy.min_price or order_price > self.policy.max_price:
                return

            # amount = round(self.policy.grid_invest / order_price, 6)
            # amount = max(amount, 1e-4)
            supplied_order = self.create_order(ORDER_SELL, order.order_amount, order_price)
            if order.order_refer_id == ORDER_NONE_REF:
                supplied_order.order_refer_id = order.order_id
                supplied_order.save()

            if self.robot_summary.invested_money > self.robot_summary.profit + self.policy.expect_money:
                logger.error("机器人"+str(self.robot.robot_id)+"投资额度已达上限!")
                return
            order_price = (1 - self.policy.rate_buy / 100) * order.order_price
            if order_price < self.policy.min_price or order_price > self.policy.max_price:
                return
            order_price = round(order_price, 2)

            amount = round(self.policy.grid_invest / order_price, 6)
            amount = max(amount, 1e-4)

            self.create_order(ORDER_BUY, amount, order_price)

            self.robot_summary.invested_money += amount * order_price
            self.robot_summary.save()





    def retrieve_order(self, order):

        if (self.robot.robot_status != ROBOT_OK) or (order.order_type != ORDER_BUY):
            return

        currency_price = self.huobi.get_currency_price(self.robot.robot_currency_type)


        if (currency_price - order.order_price >= order.order_price * (self.policy.rate_buy + self.policy.rate_sell) / 100 / (1 - self.policy.rate_buy / 100)):

            order_price = ((1 - self.policy.rate_buy / 100)) * currency_price
            order_price = round(order_price, 2)
            if order_price > self.policy.max_price:
                # logger.info("达到最高价格，所以机器人不会继续下单")
                return

            canceled_order_id = self.cancel_order(order.order_record_id, 0)

            order.order_status = ORDER_CANCEL
            self.robot_summary.invested_money -= float(order.order_amount) * float(order.order_price)
            order.save()

            amount = round(self.policy.grid_invest / order_price, 6)
            amount = max(amount, 1e-4)

            self.create_order(ORDER_BUY, amount, order_price)

            self.robot_summary.invested_money += amount * order_price

            self.robot_summary.save()
            


    def update_order(self, orders):


        trade_client = self.user.trade_client
        for order in orders:
            if order.order_status == ORDER_WAIT:
                try:
                    order_info = trade_client.get_order(order_id=order.order_record_id)
                except Exception as e:
                    if self.robot.robot_status != ROBOT_OK:
                        order.order_status = ORDER_Fail
                        order.save()
                    # logger.error("查询订单失败，其订单号为 " + str(order.order_record_id) + repr(e))
                    continue
                if order_info.state == OrderState.FILLED or order_info.state == OrderState.PARTIAL_CANCELED:
                    order.order_status = ORDER_FINISH
                    order.order_amount = float(order_info.filled_amount)
                    order.order_price = float(order_info.price)
                    order.order_create_time = datetime.datetime.fromtimestamp(int(order_info.created_at / 1000))
                    order.order_finish_time = datetime.datetime.fromtimestamp(int(order_info.finished_at / 1000))
                    order.order_transfer_fees = float(order_info.filled_fees)

                    self.robot_summary.total_transfer_fee += float(order_info.filled_fees)
                    if order_info.type == OrderType.SELL_LIMIT:
                        self.robot_summary.hold_currency_num -= float(order_info.filled_amount)
                        self.robot_summary.profit += (1 / (
                                1 + 100 / self.policy.rate_sell)) * float(order_info.filled_amount) * float(
                            order_info.price)
                        self.robot_summary.invested_money -= order.order_amount * order.order_price
                    else:
                        self.robot_summary.hold_currency_num += float(order_info.filled_amount)


                    self.supply_order(order)
                    order.save()

                elif order_info.state == OrderState.CANCELED or order_info.state == OrderState.PLACE_TIMEOUT or order_info.state == OrderState.FAILED:
                    order.order_status = ORDER_CANCEL
                    order.save()
                    # order.delete()
                else:
                    self.retrieve_order(order)

                self.robot_summary.save()

                # logger.info("订单号为" + str(order.order_record_id) + " 的订单被撤销了")

