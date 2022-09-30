from cmath import log
import datetime
import logging

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
            logger.error("立即交易额度"+str(amount)+" 交易类型为"+str(order_type))
            order_record_id = self.user.trade_client.create_order(symbol=self.robot.robot_currency_type,
                                                                   account_id=self.user.system_id,
                                                                   order_type=order_type,
                                                                   source=OrderSource.API, amount=amount, price=None)
            return order_record_id
        except Exception as e:
            logger.error(repr(e))

    def post_order(self, post_order_type, amount, price):
        
            
        try:
            order_record_id = self.user.trade_client.create_order(symbol=self.robot.robot_currency_type,
                                                                   account_id=self.user.system_id,
                                                                   order_type=post_order_type,
                                                                   source=OrderSource.API, amount=amount, price=price)
        except Exception as e:
            logger.error(repr(e))
            raise Exception("资金不够，创建订单失败")
        # logger.error("创建订单 数量"+str(amount) + "价格 "+str(price) + "类型" + str(post_order_type))
        return order_record_id

    def create_order(self, order_type, order_amount, order_price, set_order_id=None):
        amount = round(order_amount, 4)
        price = round(order_price, 2)

        if order_type == ORDER_BUY:
            post_order_type = OrderType.BUY_LIMIT
        else:
            post_order_type = OrderType.SELL_LIMIT

        order_record_id = str(self.post_order(post_order_type, amount, price))

        # if set_order_id is not None:
        #     order_id = set_order_id
        # else:
        #     orders = Order.objects.all().order_by("-order_id")
        #     if len(orders) == 0:
        #         order_id = 0
        #     else:
        #         order_id = orders[0].order_id + 4

        # order = Order(order_id=order_id, order_record_id=order_record_id, robot_id=self.robot.robot_id,
        #               order_currency_type=self.robot.robot_currency_type, order_type=order_type,
        #               order_amount=order_amount,
        #               order_price=order_price, order_status=ORDER_WAIT, order_create_time=datetime.datetime.now(),
        #               order_finish_time=None)
        
        order = Order(order_record_id=order_record_id, robot_id=self.robot.robot_id,
                      order_currency_type=self.robot.robot_currency_type, order_type=order_type,
                      order_amount=order_amount,
                      order_price=order_price, order_status=ORDER_WAIT, order_create_time=datetime.datetime.now(),
                      order_finish_time=None)

        order.save()

        # if self.robot.robot_policy_type == GEOMETRIC_POLICY:
        #     logger.error("*****创建订单,机器人"+ str(self.robot.robot_id)+"， order_type:" + str(order.order_type)+" order amount:"+ str(order.order_amount) + " order_price: "+ str(order.order_price))

        return order

    def create_batch_order(self, orders):

        for order in orders:

            if order.order_type == ORDER_BUY:
                post_order_type = OrderType.BUY_LIMIT
            else:
                post_order_type = OrderType.SELL_LIMIT
            
            order_record_id = str(self.post_order(post_order_type, order.order_amount, order.order_price))
            order.order_record_id = order_record_id
            # logger.error("*****创建订单,机器人"+ str(self.robot.robot_id)+"， order_type:" + str(order.order_type)+" order amount:"+ str(order.order_amount) + " order_price: "+ str(order.order_price))

        
        Order.objects.bulk_create(orders)


    # def post_batch_orders(self, order_config_list, count):

    #     if count > MAX_REPOST_NUM:
    #         raise Exception("创建订单失败")

    #     try:
    #         create_result = self.user.trade_client.batch_create_order(order_config_list=order_config_list)

    #     except Exception as e:
    #         # logger.error(repr(e))
    #         create_result = self.post_batch_orders(order_config_list, count+1)

    #     return create_result

    # def create_batch_order(self, order_type, order_amounts, prices):
    #     order_config_list = []
    #     order_id_list = []
    #     order_total_list = []

    #     if order_type == ORDER_BUY:
    #         post_order_type = OrderType.BUY_LIMIT
    #     else:
    #         post_order_type = OrderType.SELL_LIMIT

    #     for i in range(len(order_amounts)):
    #         order_config = {
    #             "account_id":self.user.system_id,
    #             "symbol":self.robot.robot_currency_type,
    #             "order_type": post_order_type,
    #             "source": OrderSource.API,
    #             "amount": order_amounts[i],
    #             "price": prices[i]
    #         }
    #         order_config_list.append(order_config)
    #         if ((i+1)%10)==0 or (i==(len(order_amounts)-1)):
    #             create_result = self.post_batch_orders(order_config_list, 0)
    #             if create_result and len(create_result):
    #                 for item in create_result:
    #                     order_id_list.append(item.order_id)
    #             order_total_list = order_total_list + order_config_list
    #             order_config_list = []

    #     orders = Order.objects.all()
    #     if len(orders) == 0:
    #         order_id = 0
    #     else:
    #         order_id_list = []
    #         for order in orders:
    #             order_id_list.append(order.order_id)
    #         order_id = max(order_id_list) + 1

    #     for i in range(len(order_total_list)):
    #         order = Order(order_id=order_id, order_record_id=order_id_list[i], robot_id=self.robot.robot_id,
    #             order_currency_type=self.robot.robot_currency_type, order_type=order_type,
    #             order_amount=order_total_list[i]["amount"],
    #             order_price=order_total_list[i]["price"], order_status=ORDER_WAIT, order_create_time=datetime.datetime.now(),
    #             order_finish_time=None)

    #         order_id = order_id + 1
    #         order.save()

    def cancel_order(self, order, count):
        
        if count > MAX_REPOST_NUM:
            logger.error("机器人"+ str(self.robot.robot_id)+"，"+str(order.order_record_id) + "撤销订单失败"+str(order.order_price)+" "+str(order.order_type))
            return STATUS_ERROR

        try:
            canceled_order_id = self.user.trade_client.cancel_order(self.robot.robot_currency_type, order.order_record_id)
            order.order_flag = ORDER_CANCEL_FLAG
            order.save()

        except Exception as e:
            # logger.error(repr(e))
            canceled_order_id = self.cancel_order(order, count+1)


    def cancel_orders(self):
        for order in self.order_list:
            if order.order_status == ORDER_WAIT:
                try:
                    canceled_order_id = self.cancel_order(order, 0)
                except Exception as e:
                    logger.error(repr(e))
        
        self.update_order(self.order_list)

    def cancel_currencys(self):

        btc_num = float(self.user.get_balance(quote_arry[self.robot.robot_currency_type]))
        sell_amount = min(btc_num, self.robot_summary.hold_currency_num)
        sell_amount = round(sell_amount-0.00005, 4)
        sell_amount = max(0, sell_amount)
        logger.error("停止机器人, 并卖出货币数量"+str(sell_amount))
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
        order_list = list(self.order_list)
        order_list.sort(key=lambda x: int(x.order_id), reverse=True)
        for order in order_list:
            if order.order_status == ORDER_CANCEL or order.order_status == ORDER_Fail or order.order_refer_id == ORDER_NONE_REF:
                continue
            refs = Order.objects.filter(order_id=order.order_refer_id)
            if len(refs) == 0:
                continue
            
            order_ref = refs[0]
            trade_order = {}
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

            if trade_order['sell_time'] is None or trade_order['buy_time'] is None:
                continue

            if int((trade_order['sell_time'] - trade_order['buy_time']).seconds) > 0:
                trade_order['order_time'] = trade_order['sell_time']
            else:
                trade_order['order_time'] = trade_order['buy_time']

            trade_order['order_time'] = (trade_order['order_time']+datetime.timedelta(hours=8)).strftime("%Y/%m/%d %H:%M:%S")
            trade_order['sell_time'] = (trade_order['sell_time']+datetime.timedelta(hours=8)).strftime("%Y/%m/%d %H:%M:%S")
            trade_order['buy_time'] = (trade_order['buy_time']+datetime.timedelta(hours=8)).strftime("%Y/%m/%d %H:%M:%S")

            # trade_order['id'] = max(sell_order.order_id, buy_order.order_id)

            trade_order_list.append(trade_order)
            
            if len(trade_order_list) > 200:
                break

        # trade_order_list.sort(key=lambda x: int(x['id']), reverse=True)
        # size = min(len(trade_order_list), 200)
        # trade_order_list = trade_order_list[:size]

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
        elif self.robot.robot_status == ROBOT_CREATING:
            robot_info['status'] = '正在创建'
        elif self.robot.robot_status == ROBOT_DESTORYING:
            robot_info['status'] = '正在删除'
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
                      robot_currency_type=currency_type, robot_status=ROBOT_CREATING,
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
        btc_num = float(user.get_balance(quote_arry[currency_type]))
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
        self.robot_summary.invested_money = expect_money
        self.robot_summary.save()

        self.restart_robot()


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
        user_amount = float(self.user.get_balance(quote_arry[self.robot.robot_currency_type]))

        if need_amount > user_amount:
            money = round((need_amount - user_amount + self.policy.grid_invest/10) * currency_price, 3)
            order_record_id = self.create_once_order(money, OrderType.BUY_MARKET)
            for i in range(MAX_REPOST_NUM):
                try:
                    order_info = self.user.trade_client.get_order(order_id=order_record_id)
                    if order_info.state == OrderState.FILLED:
                        break
                    else:
                        continue
                except Exception as e:
                    continue
            user_amount = float(self.user.get_balance(quote_arry[self.robot.robot_currency_type]))
            if user_amount < need_amount:
                self.robot.robot_status = ROBOT_DELETE
                self.robot.save()
                raise Exception("购买货币失败, 创建机器人失败" + "现在货币数量:" + str(user_amount) + "需要" + str(need_amount))
            logger.error("建立初始订单成功, 现在货币数量:"+str(user_amount))



        # orders = Order.objects.all().order_by("-order_id")
        # if len(orders) == 0:
        #     order_id = 0
        # else:
        #     order_id = orders[0].order_id + 100

        orders = []
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
            # order = Order(order_id=order_id+i, order_record_id="-1", robot_id=self.robot.robot_id,
            #             order_currency_type=self.robot.robot_currency_type, order_type=order_type,
            #             order_amount=amount,
            #             order_price=grid_price, order_status=ORDER_WAIT, order_create_time=datetime.datetime.now(),
            #             order_finish_time=None)
            # orders.append(order)
            try:
                # self.create_order(order_type, amount, grid_price, order_id+i)
                self.create_order(order_type, amount, grid_price)
                
            except Exception as e:
                logger.error(repr(e))
                user_amount = float(self.user.get_balance(quote_arry[self.robot.robot_currency_type]))
                if user_amount < amount and order_type == ORDER_SELL:
                    logger.error("现在货币数量为" + str(user_amount) + ",  货币数量不够,重新购买货币数: " + str(amount))
                    self.create_once_order(round(amount * currency_price, 3), OrderType.BUY_MARKET)
                    try:
                        self.create_order(order_type, amount, grid_price)
                    except Exception:
                        pass
        
        # self.create_batch_order(orders)

        self.robot_summary.invested_money = self.policy.expect_money
        self.robot_summary.hold_currency_num = need_amount
        self.robot.robot_status = ROBOT_OK

        self.robot.save()
        self.robot_summary.save()

    def supply_order(self, order):

        if self.robot.robot_status != ROBOT_OK:
            return

        amount = round(self.policy.grid_invest, 4)
        amount = max(amount, 1e-4)
        # logger.error("----补订单,订单完成,机器人"+ str(self.robot.robot_id)+"， order_type:" + str(order.order_type)+" order amount:"+ str(order.order_amount) + " order_price: "+ str(order.order_price))
        if order.order_type == ORDER_BUY:
            order_price = order.order_price * (1 + self.policy.grid_profit_rate / 100)
            supplied_order = self.create_order(ORDER_SELL, amount, order_price)
        else:
            order_price = order.order_price / (1 + self.policy.grid_profit_rate / 100)
            supplied_order = self.create_order(ORDER_BUY, amount, order_price)
        # logger.error("----补订单,订单创建,机器人"+ str(self.robot.robot_id)+"， order_type:" + str(supplied_order.order_type)+" order amount:"+ str(supplied_order.order_amount) + " order_price: "+ str(supplied_order.order_price))
        if order.order_refer_id == ORDER_NONE_REF:
            supplied_order.order_refer_id = order.order_id
            supplied_order.save()

    def restart_robot(self):

        self.robot.robot_status = ROBOT_CREATING
        self.robot.save()
        self.load_orders()
        self.cancel_orders()
        # self.cancel_currencys()

        self.init_robot_order()


    def check_orders(self):

        currency_price = self.huobi.get_currency_price(self.robot.robot_currency_type)
        buy_order_list = Order.objects.filter(robot_id=self.robot.robot_id, order_status=ORDER_WAIT, order_type=ORDER_BUY)
        sell_order_list = Order.objects.filter(robot_id=self.robot.robot_id, order_status=ORDER_WAIT, order_type=ORDER_SELL)
        
        for order in buy_order_list:

            if order.order_price < self.policy.min_price:
                logger.error("取消不符合上下限的订单" + str(order.order_price))
                self.cancel_order(order, 0)
                self.update_order_status(order)
                
            if order.order_price > currency_price:
                updated_order = self.update_order_status(order)
                    
            # if int((datetime.datetime.now() - order.order_create_time.replace(tzinfo=None)).days) > MAX_DAYS:
            #     order_refer_id = order.order_refer_id
            #     updated_order = self.update_order_status(order)
            #     if updated_order.order_status == ORDER_WAIT:
            #         logger.error("重新下单过期订单"+str(order.order_price))
            #         self.cancel_order(updated_order, 0)
            #         self.update_order_status(updated_order)
            #         try:
            #             new_order = self.create_order(order.order_type, order.order_amount, order.order_price)
            #             new_order.order_refer_id = order_refer_id
            #             new_order.save()
            #         except Exception as e:
            #                 pass

        for order in sell_order_list:

            if int(order.order_price) > int(self.policy.max_price):
                logger.error("取消不符合上下限的订单" + str(order.order_price))
                self.cancel_order(order, 0)
                self.update_order_status(order)

            if order.order_price < currency_price:
                updated_order = self.update_order_status(order)


            # if int((datetime.datetime.now() - order.order_create_time.replace(tzinfo=None)).days) > MAX_DAYS:
            #     order_refer_id = order.order_refer_id
            #     updated_order = self.update_order_status(order)
            #     if updated_order.order_status == ORDER_WAIT:
            #         logger.error("重新下单过期订单"+str(order.order_price))
            #         self.cancel_order(updated_order, 0)
            #         self.update_order_status(updated_order)
            #         try:
            #             new_order = self.create_order(order.order_type, order.order_amount, order.order_price)
            #             new_order.order_refer_id = order_refer_id
            #             new_order.save()
            #         except Exception as e:
            #                 pass
                        

        currency_price = self.huobi.get_currency_price(self.robot.robot_currency_type)

        price_list = []

        for i in range(self.policy.grid_num + 1):
            
            grid_price = ((1 + self.policy.grid_profit_rate / 100) ** i) * self.policy.min_price

            grid_price = round(grid_price, 2)

            if i == 0  and self.policy.min_price > currency_price:
                continue

            if i == self.policy.grid_num and self.policy.max_price < currency_price:
                continue

            if (grid_price >= currency_price and (grid_price / (1 + self.policy.grid_profit_rate / 100)) < currency_price):
                continue

            price_list.append(grid_price)
        
        if len(price_list) >= 2:
            distance = (price_list[1] - price_list[0]) * DISTANCE_RATIO
        else:
            distance = 0

        order_list = Order.objects.filter(robot_id=self.robot.robot_id, order_status=ORDER_WAIT)
        order_list = list(order_list)
        order_list.sort(key=lambda x: x.order_price)
        i = self.policy.grid_num - 1
        j = len(order_list) - 1

        while True:

            if i < 0:
                if j < 0:
                    break
                else:
                    logger.error("取消不符合要求的订单1" + str(order.order_price))
                    self.cancel_order(order_list[j], 0)
                    self.update_order_status(order_list[j])
                    j = j - 1

            order_price = price_list[i]
            if j < 0:

                amount = round(self.policy.grid_invest, 4)
                amount = max(amount, 1e-4)

                if order_price > self.huobi.get_currency_price(self.robot.robot_currency_type):
                    logger.error("创建订单1" + str(order.order_price) + str(order.order_type))

                    try:
                        self.create_order(ORDER_SELL, amount, order_price)
                    except Exception as e:
                        logger.error(repr(e))
                        # user_amount = float(self.user.get_balance(quote_arry[self.robot.robot_currency_type]))
                        # if user_amount < amount:
                        #     logger.error("1货币数量不够,重新购买货币数: "+str(amount))
                        #     self.create_once_order(round(amount * currency_price, 3), OrderType.BUY_MARKET)
                        #     self.create_order(ORDER_SELL, amount, order_price)
                else:
                    try:
                        self.create_order(ORDER_BUY, amount, order_price)
                    except Exception as e:
                        logger.error(repr(e))
                
                i = i - 1
                continue
            
            if math.fabs(order_list[j].order_price - order_price) <  distance  or distance == 0:

                i = i - 1
                j = j - 1

                continue

            if order_list[j].order_price > order_price and j < len(order_list) - 1:
                if (order_list[j+1].order_price - order_list[j].order_price) < distance:
                    logger.error("重单了, 两个订单价格为"+str(order_list[j+1].order_price) + "   "+ str(order_list[j].order_price))
                    self.cancel_order(order_list[j], 0)
                    self.update_order_status(order_list[j])
                    j = j - 1
                    continue

            if order_list[j].order_price < order_price:
                amount = round(self.policy.grid_invest, 4)
                amount = max(amount, 1e-4)

                if order_price > self.huobi.get_currency_price(self.robot.robot_currency_type):
                    logger.error("创建订单2" + str(order.order_price) + str(order.order_type))

                    try:
                        self.create_order(ORDER_SELL, amount, order_price)
                    except Exception as e:
                        # user_amount = float(self.user.get_balance(quote_arry[self.robot.robot_currency_type]))
                        # if user_amount < amount:
                        #     logger.error("2货币数量不够,重新购买货币数: "+str(amount))
                        #     self.create_once_order(round(amount * currency_price, 3), OrderType.BUY_MARKET)
                        #     self.create_order(ORDER_SELL, amount, order_price)
                        pass
                else:
                    try:
                        self.create_order(ORDER_BUY, amount, order_price)
                    except Exception as e:
                        pass
                
                i = i - 1
                continue

            i = i - 1
            j = j - 1

        sell_order_list = Order.objects.filter(robot_id=self.robot.robot_id, order_status=ORDER_WAIT, order_type=ORDER_SELL)
        
        currency_hold = 0
        for order in sell_order_list:
            currency_hold += float(order.order_amount)
        
        self.robot_summary.hold_currency_num = currency_hold
        self.robot_summary.save()
            


    def update_order(self, orders):

        for order in orders:
            self.update_order_status(order)
 
    def update_order_status(self, order):
           trade_client = self.user.trade_client
           if order.order_status == ORDER_WAIT:
                try:
                    order_info = trade_client.get_order(order_id=order.order_record_id)
                except Exception as e:
                    # logger.error("查询订单失败，其订单号为 " + str(order.order_record_id) + repr(e))
                    if self.robot.robot_status != ROBOT_OK:
                        order.order_status = ORDER_Fail
                        order.save()
                    return
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
                    order.order_refer_id = ORDER_NONE_REF
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
        btc_num = float(user.get_balance(quote_arry[currency_type]))
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
        
        self.policy.max_price = max_price
        self.policy.min_price = min_price
        self.policy.grid_invest = grid_invest
        self.policy.rate_buy = rate_buy
        self.policy.rate_sell = rate_sell
        self.policy.expect_money = expect_money
    
        self.policy.save()
        self.check_orders()

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

        amount = round(self.policy.grid_invest / order_price, 4)
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

            amount = round(self.policy.grid_invest / order_price, 4)
            amount = max(amount, 1e-4)

            self.create_order(ORDER_BUY, amount, order_price)

            self.robot_summary.invested_money += amount * order_price
            self.robot_summary.save()
        
        else:
            try:
                buy_orders = self.get_buy_orders()
                # currency_price = self.huobi.get_currency_price(self.robot.robot_currency_type)
                # order_price = None
                # if currency_price < (1 - self.policy.rate_buy / 100) * order.order_price:
                order_price = (1 - self.policy.rate_buy / 100) * order.order_price
                self.retrieve_order(buy_orders[0], order_price)
            except Exception as e:
                return
        
    def get_buy_orders(self):

        buy_orders = Order.objects.filter(robot_id=self.robot.robot_id, order_status=ORDER_WAIT, order_type=ORDER_BUY)
        
        return buy_orders

    def retrieve_order(self, order, retrieve_order_price=None):

        if (self.robot.robot_status != ROBOT_OK) or (order.order_type != ORDER_BUY):
            return

        currency_price = self.huobi.get_currency_price(self.robot.robot_currency_type)


        if (math.fabs(currency_price - order.order_price) >= order.order_price * (self.policy.rate_buy + self.policy.rate_sell) / 100 / (1 - self.policy.rate_buy / 100)) or (retrieve_order_price is not None):
            order_price = ((1 - self.policy.rate_buy / 100)) * currency_price
            order_price = round(order_price, 2)

            if order_price > self.policy.max_price:
                return

            # if self.cancel_order(order, 0) == STATUS_ERROR:
            #     return
            # self.update_order_status(order)
            self.cancel_order(order, 0)
            order.order_status = ORDER_CANCEL
            self.robot_summary.invested_money -= float(order.order_amount) * float(order.order_price)
            order.save()

            if retrieve_order_price is not None:
                order_price = retrieve_order_price

            amount = round(self.policy.grid_invest / order_price, 4)
            amount = max(amount, 1e-4)

            self.create_order(ORDER_BUY, amount, order_price)

            self.robot_summary.invested_money += amount * order_price

            self.robot_summary.save()
            

    def check_orders(self):
        
        currency_price = self.huobi.get_currency_price(self.robot.robot_currency_type)
        buy_orders = Order.objects.filter(robot_id=self.robot.robot_id, order_status=ORDER_WAIT, order_type=ORDER_BUY)

        for order in buy_orders:
            if order.order_price < self.policy.min_price or order.order_price > currency_price:
                updated_order = self.update_order_status(order)
                if updated_order.order_status == ORDER_WAIT and order.order_price < self.policy.min_price:
                    self.cancel_order(updated_order, 0)
                    self.update_order_status(updated_order)
                    
        buy_orders = Order.objects.filter(robot_id=self.robot.robot_id, order_status=ORDER_WAIT, order_type=ORDER_BUY)
        buy_order_nums = len(buy_orders)
        if buy_order_nums > 1:
            pass
            # for order in buy_orders:
            #     self.cancel_order(order, 0)
            #     self.update_order_status(order)
        elif buy_order_nums == 0:
            for i in range(MAX_REPOST_NUM):
                orders = Order.objects.filter(robot_id=self.robot.robot_id, order_status=ORDER_WAIT, order_type=ORDER_BUY)
                if len(orders) == 0 and i == MAX_REPOST_NUM -1:
                    if self.robot_summary.invested_money < self.robot_summary.profit + self.policy.expect_money:
                        self.init_robot_order()
                        logger.error("重启无限网格机器人 " + str(self.robot.robot_id))
                time.sleep(1)

        sell_order_list = Order.objects.filter(robot_id=self.robot.robot_id, order_status=ORDER_WAIT, order_type=ORDER_SELL)

        for order in sell_order_list:
            if order.order_price > self.policy.max_price or order.order_price < currency_price:
                updated_order = self.update_order_status(order)
                if updated_order.order_status == ORDER_WAIT and updated_order.order_price > self.policy.max_price:
                    self.cancel_order(updated_order, 0)
                
            if int((datetime.datetime.now() - order.order_create_time.replace(tzinfo=None)).days) > MAX_DAYS:
                self.cancel_order(order, 0)
                updated_order = self.update_order_status(order)
                try:
                    new_order = self.create_order(updated_order.order_type, updated_order.order_amount, updated_order.order_price)
                    new_order.order_refer_id = updated_order.order_refer_id
                    new_order.save()
                except Exception as e:
                    logger.error("修改到期订单失败, 订单价格为"+str(updated_order.order_price))
        
        hold_currency_num = 0
        invested_num = 0
        sell_order_list = Order.objects.filter(robot_id=self.robot.robot_id, order_status=ORDER_WAIT, order_type=ORDER_SELL)
        sell_order_list = list(sell_order_list)
        if len(sell_order_list) == 0:
            return
        sell_order_list.sort(key=lambda x: x.order_price)
        min_sell_price = sell_order_list[0].order_price
        for i in range(len(sell_order_list)):
            hold_currency_num += sell_order_list[i].order_amount
            invested_num += sell_order_list[i].order_amount * sell_order_list[i].order_price
            # order_price = min_sell_price * ((1 + self.policy.rate_sell / 100) ** i)
            # if math.fabs(order_price - sell_order_list[i].order_price) / order_price >= DISTANCE_RATIO * self.policy.rate_sell / 100:
            #     self.cancel_order(sell_order_list[i], 0)
            #     self.update_order_status(sell_order_list[i])
            #     try:
            #         order_price = round(order_price, 2)
            #         new_order = self.create_order(ORDER_SELL, sell_order_list[i].order_amount, order_price)
            #         new_order.order_refer_id = sell_order_list[i].order_refer_id
            #         new_order.save()                
            #     except Exception as e:
            #         pass
        self.robot_summary.hold_currency_num = hold_currency_num
        self.robot_summary.invested_money = invested_num + self.policy.grid_invest
        self.robot_summary.save()                

    def update_order(self, orders):

        for order in orders:
            self.update_order_status(order)


    def update_order_status(self, order):

        trade_client = self.user.trade_client
        if order.order_status == ORDER_WAIT:
            try:
                order_info = trade_client.get_order(order_id=order.order_record_id)
            except Exception as e:
                # logger.error("查询订单失败，其订单号为 " + str(order.order_record_id) + repr(e))
                # if self.robot.robot_status != ROBOT_OK or (datetime.datetime.now() - order.order_create_time.replace(tzinfo=None)).days > MAX_DAYS:
                if self.robot.robot_status != ROBOT_OK:
                    order.order_status = ORDER_Fail
                    order.save()
                return order
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
                order.save()
                self.supply_order(order)

            elif order_info.state == OrderState.CANCELED or order_info.state == OrderState.PLACE_TIMEOUT or order_info.state == OrderState.FAILED:
                order.order_status = ORDER_CANCEL
                order.order_refer_id = ORDER_NONE_REF
                order.save()
            else:
                pass

            self.robot_summary.save()
        return order


