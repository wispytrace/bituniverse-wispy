import datetime
import logging

import math
import numpy as np
from bitApp.models import *
from huobi.constant import *

logger = logging.getLogger('log')

class RobotEntity:

    def __init__(self):
        self.robot = None
        self.order_list = None
        self.policy = None
        self.robot_summary = None
        self.plantform = None
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

    def set_plantform(self, plantform):
        self.plantform = plantform

    def set_user(self, user):
        self.user = user

    def create_order(self, order_type, order_amount, order_price):
        amount = round(order_amount, 4)
        price = round(order_price, 2)

        order_record_id = str(self.plantform.post_order(self.robot.robot_currency_type, order_type, amount, price, self.user))
        
        order = Order(order_record_id=order_record_id, robot_id=self.robot.robot_id,
                      order_currency_type=self.robot.robot_currency_type, order_type=order_type,
                      order_amount=order_amount,
                      order_price=order_price, order_status=ORDER_WAIT, order_create_time=datetime.datetime.now(),
                      order_finish_time=None)

        order.save()

        return order

    def cancel_orders(self):
        for order in self.order_list:
            if order.order_status == ORDER_WAIT:
                try:
                   self.plantform.cancel_order(order, self.user)
                except Exception as e:
                    logger.error(repr(e))
        
        self.update_order(self.order_list)

    def cancel_currencys(self):

        btc_num = float(self.plantform.get_balance(self.plantform.quote_arry[self.robot.robot_currency_type], self.user))
        sell_amount = min(btc_num, self.robot_summary.hold_currency_num)
        sell_amount = round(sell_amount-0.00005, 4)
        sell_amount = max(0, sell_amount)
        logger.error("停止机器人, 并卖出货币数量"+str(sell_amount))
        if sell_amount < 1e-4:
            return
        self.plantform.create_once_order(self.robot.robot_currency_type, sell_amount, ORDER_SELL, self.user)


    def pause_resume_robot(self):

        if self.robot.robot_status == ROBOT_OK:
            self.robot.robot_status = ROBOT_PAUSE
        elif self.robot.robot_status == ROBOT_PAUSE:
            self.robot.robot_status = ROBOT_OK

        self.robot.save()


    def delete_robot(self):

        self.robot.robot_status = ROBOT_DELETE
        self.robot.save()


    def get_pender_order_list(self):

        pender_order_list = []
        for order in self.order_list:
            if order.order_status == ORDER_WAIT:

                pender_order = {}
                pender_order['order_price'] = round(float(order.order_price), 2)
                price_now = self.plantform.get_currency_price(self.robot.robot_currency_type)
                pender_order['order_rate'] = round(np.fabs((float(order.order_price) - price_now)) / price_now * 100,
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

            trade_order_list.append(trade_order)
            
            if len(trade_order_list) > 200:
                break

        return trade_order_list

    def get_float_profit(self):

        buy_price = 0
        buy_amount = 0
        for order in self.order_list:
            if order.order_status == ORDER_FINISH and order.order_type == ORDER_BUY:
                buy_amount += order.order_amount
                buy_price += order.order_amount * order.order_price

        buy_price = buy_price / buy_amount if buy_amount != 0 else 0
        float_profit = round((self.plantform.get_currency_price(self.robot.robot_currency_type) - buy_price) * max(
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
        robot_info['currency_price'] = self.plantform.get_currency_price(self.robot.robot_currency_type)

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
    def get_robot_invest_parameter(currency_type, max_price, min_price, grid_num, per_invest, plantform, user):

        parameter = {}
        currency_price = plantform.get_currency_price(currency_type)
        usdt_num = float(plantform.get_balance('usdt', user))
        btc_num = float(plantform.get_balance(plantform.quote_arry[currency_type], user))
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
        # self.check_orders()


    def get_parameter(self):
        parameter = {}
        parameter['max_price'] = self.policy.max_price
        parameter['min_price'] = self.policy.min_price
        parameter['grid_num'] = self.policy.grid_num
        parameter['per_invest'] = str('%g' % self.policy.grid_invest)
        parameter['currency_type'] = self.robot.robot_currency_type

        return parameter


    def init_robot_order(self):

        currency_price = self.plantform.get_currency_price(self.robot.robot_currency_type)
        need_amount = math.log(currency_price / self.policy.min_price, (1 + self.policy.grid_profit_rate / 100))
        need_amount =(self.policy.grid_num - (int(need_amount) + 1)) * self.policy.grid_invest
        user_amount = float(self.plantform.get_balance(self.plantform.quote_arry[self.robot.robot_currency_type], self.user))

        if need_amount > user_amount:
            money = round((need_amount - user_amount + self.policy.grid_invest/10) * currency_price, 3)
            order_record_id = self.plantform.create_once_order(self.robot.robot_currency_type, money, ORDER_BUY, self.user)
            # for i in range(MAX_REPOST_NUM):
            #     try:
            #         order_info = self.plantform.check_order(order, self.user)
            #         if order_info.state == OrderState.FILLED:
            #             break
            #         else:
            #             continue
            #     except Exception as e:
            #         continue
            user_amount = float(self.plantform.get_balance(self.plantform.quote_arry[self.robot.robot_currency_type], self.user))
            if user_amount < need_amount:
                self.robot.robot_status = ROBOT_DELETE
                self.robot.save()
                raise Exception("购买货币失败, 创建机器人失败" + "现在货币数量:" + str(user_amount) + "需要" + str(need_amount))
            logger.error("建立初始订单成功, 现在货币数量:"+str(user_amount))

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

            try:
                order = self.create_order(order_type, amount, grid_price)
                order.order_flag = i
                order.save()
                
            except Exception as e:
                logger.error(repr(e))
                user_amount = float(self.plantform.get_balance(self.plantform.quote_arry[self.robot.robot_currency_type], self.user))
                if user_amount < amount and order_type == ORDER_SELL:
                    # logger.error("现在货币数量为" + str(user_amount) + ",  货币数量不够,重新购买货币数: " + str(amount))
                    self.plantform.create_once_order(self.robot.robot_currency_type, round(amount * currency_price, 3), ORDER_BUY, self.user)
                    try:
                        self.create_order(order_type, amount, grid_price)
                    except Exception:
                        pass
        
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
        if order.order_type == ORDER_BUY:
            order_price = ((1 + self.policy.grid_profit_rate / 100) ** (order.order_flag + 1)) * self.policy.min_price
            order_price = round(order_price, 2)
            supplied_order = self.create_order(ORDER_SELL, amount, order_price)
            supplied_order.order_flag = order.order_flag + 1
            supplied_order.save()
        else:
            order_price = ((1 + self.policy.grid_profit_rate / 100) ** (order.order_flag - 1)) * self.policy.min_price
            order_price = round(order_price, 2)
            supplied_order = self.create_order(ORDER_BUY, amount, order_price)
            supplied_order.order_flag = order.order_flag - 1
            supplied_order.save()
        if order.order_refer_id == ORDER_NONE_REF:
            supplied_order.order_refer_id = order.order_id
            supplied_order.save()

    def restart_robot(self):

        self.robot.robot_status = ROBOT_CREATING
        self.robot.save()
        self.load_orders()
        self.cancel_orders()

        self.init_robot_order()


    def check_orders(self):

        currency_price = self.plantform.get_currency_price(self.robot.robot_currency_type)
        buy_order_list = Order.objects.filter(robot_id=self.robot.robot_id, order_status=ORDER_WAIT, order_type=ORDER_BUY)
        sell_order_list = Order.objects.filter(robot_id=self.robot.robot_id, order_status=ORDER_WAIT, order_type=ORDER_SELL)
        
        buy_order_list = list(buy_order_list)
        sell_order_list = list(sell_order_list)
        buy_order_list.sort(key=lambda x: x.order_price)
        sell_order_list.sort(key=lambda x: x.order_price)

        buy_base = -1
        sell_base = -1

        if len(buy_order_list) != 0:
            buy_base = buy_order_list[0].order_flag
        
        if len(sell_order_list) != 0:
            sell_base = sell_order_list[0].order_flag

        ordes_num = len(buy_order_list) + len(sell_order_list)

        for order in buy_order_list:
            # logger.error(str(buy_base) + ":  " + str(order.order_price) + ":   flag" + str(order.order_flag))

            if orders_num < self.policy.grid_num:

                if order.order_flag == buy_base:
                    buy_base += 1
                else:
                    if buy_base != -1 and buy_base < sell_order_list[0].order_flag:
                        logger.error("补充缺失买订单" + str(buy_base))
                        order_price = ((1 + self.policy.grid_profit_rate / 100) ** (buy_base)) * self.policy.min_price
                        order_price = round(order_price, 2)
                        amount = round(self.policy.grid_invest, 4)
                        created_order = self.create_order(ORDER_BUY, amount, order_price)
                        created_order.order_flag = buy_base
                        created_order.save()
                        buy_base += 1



            if self.policy.min_price - order.order_price > currency_price * DISTANCE_MAX:
                logger.error("取消不符合下限的订单" + str(order.order_price))
                self.plantform.cancel_order(order, self.user)
                self.update_order_status(order)
                
            if order.order_price > currency_price * (1 + ORDER_DISTANCE):
                updated_order = self.update_order_status(order)
                if updated_order.order_status == ORDER_WAIT:
                    logger.error("设置不合理买的订单为失败" + str(order.order_price))
                    updated_order.order_status = ORDER_Fail
                    updated_order.save()
                    self.plantform.create_once_order(updated_order.order_currency_type, round(updated_order.order_amount * currency_price,3), ORDER_BUY, self.user)
                    amount = round(self.policy.grid_invest, 4)
                    order_price = ((1 + self.policy.grid_profit_rate / 100) ** (updated_order.order_flag + 1)) * self.policy.min_price
                    order_price = round(order_price, 2)
                    created_order = self.create_order(ORDER_SELL, amount, order_price)
                    created_order.order_flag = updated_order.order_flag + 1
                    created_order.order_flag.save()
                    
        for order in sell_order_list:
            # logger.error(str(sell_base) + ":  " + str(order.order_price) + ":   flag" + str(order.order_flag))
            if orders_num < self.policy.grid_num:

                if order.order_flag == sell_base:
                    sell_base += 1
                else:
                    if sell_base != -1 and sell_base <= sell_order_list[-1].order_flag:
                        # logger.error("补充缺失卖订单" + str(sell_base))
                        order_price = ((1 + self.policy.grid_profit_rate / 100) ** (sell_base)) * self.policy.min_price
                        order_price = round(order_price, 2)
                        amount = round(self.policy.grid_invest, 4)
                        created_order = self.create_order(ORDER_SELL, amount, order_price)
                        created_order.order_flag = sell_base
                        created_order.save()
                        sell_base += 1

            if order.order_price - self.policy.max_price > currency_price * DISTANCE_MAX:
                logger.error("取消不符合上限的订单" + str(order.order_price))
                self.plantform.cancel_order(order, self.user)
                self.update_order_status(order)

            if order.order_price < currency_price / (1 + ORDER_DISTANCE):
                updated_order = self.update_order_status(order)
                if updated_order.order_status == ORDER_WAIT:
                    logger.error("设置不合理卖的订单为失败" + str(order.order_price))
                    updated_order.order_status = ORDER_Fail
                    updated_order.save()
                    self.plantform.create_once_order(updated_order.order_currency_type, round(updated_order.order_amount,4), ORDER_SELL, self.user)
                    amount = round(self.policy.grid_invest, 4)
                    order_price = ((1 + self.policy.grid_profit_rate / 100) ** (updated_order.order_flag - 1)) * self.policy.min_price
                    order_price = round(order_price, 2)
                    created_order = self.create_order(ORDER_BUY, amount, order_price)
                    created_order.order_flag = updated_order.order_flag - 1
                    created_order.order_flag.save()

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
        if order.order_status == ORDER_WAIT:
            try:
                order_info_dict = self.plantform.check_order(order, self.user)
            except Exception as e:
                if self.robot.robot_status == ROBOT_DELETE:
                    order.order_status = ORDER_Fail
                    order.save()
                return order
            if order_info_dict['order_status'] == ORDER_FINISH:
                order.order_status = order_info_dict['order_status']
                order.order_amount = order_info_dict["order_amount"] 
                order.order_price = order_info_dict["order_price"]
                order.order_create_time = order_info_dict["order_create_time"]
                order.order_finish_time = order_info_dict["order_finish_time"]
                order.order_transfer_fees = order_info_dict["order_transfer_fees"]

                self.robot_summary.total_transfer_fee += order_info_dict["order_transfer_fees"]
                if order.order_type == ORDER_SELL:
                    self.robot_summary.hold_currency_num -= order_info_dict["order_amount"] 
                    self.robot_summary.profit += (1 / (
                            1 + 100 / self.policy.grid_profit_rate)) * order_info_dict["order_amount"]  * order_info_dict["order_price"]
                else:
                    self.robot_summary.hold_currency_num += order_info_dict["order_amount"] 
                self.robot_summary.save()
                order.save()
                self.supply_order(order)

            elif order_info_dict['order_status'] == ORDER_CANCEL: 

                order.order_status = order_info_dict['order_status']
                order.order_refer_id = ORDER_NONE_REF
                order.save()
                
        return order
        


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
    def get_robot_invest_parameter(currency_type, sell_percent, expect_money, plantform, user):

        parameter = {}
        currency_price = plantform.get_currency_price(currency_type)
        usdt_num = float(plantform.get_balance('usdt', user))
        btc_num = float(plantform.get_balance(plantform.quote_arry[currency_type], user))
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

        currency_price = self.plantform.get_currency_price(self.robot.robot_currency_type)

        order_price = ((1 - self.policy.rate_buy / 100)) * currency_price
        order_price = round(order_price, 2)

        amount = round(self.policy.grid_invest / order_price, 4)
        amount = max(amount, 1e-4)

        self.create_order(ORDER_BUY, amount, order_price)

        self.robot_summary.invested_money += amount * order_price

        self.robot_summary.save()

    def supply_order(self, order):
        # logger.error("supply 1")
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
                # logger.error("supply 2")

            if self.robot_summary.invested_money > self.robot_summary.profit + self.policy.expect_money:
                logger.error("机器人"+str(self.robot.robot_id)+"投资额度已达上限!")
                return
            order_price = (1 - self.policy.rate_buy / 100) * order.order_price
            if order_price < self.policy.min_price or order_price > self.policy.max_price:
                return
            order_price = round(order_price, 2)
            # logger.error("supply 3")
            amount = round(self.policy.grid_invest / order_price, 4)
            amount = max(amount, 1e-4)

            self.create_order(ORDER_BUY, amount, order_price)
            # logger.error("supply 4")
            self.robot_summary.invested_money += amount * order_price
            self.robot_summary.save()
        
        else:
            try:
                buy_orders = self.get_buy_orders()
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

        currency_price = self.plantform.get_currency_price(self.robot.robot_currency_type)

        if (np.fabs(currency_price - order.order_price) >= order.order_price * (self.policy.rate_buy + self.policy.rate_sell) / 100 / (1 - self.policy.rate_buy / 100)) or (retrieve_order_price is not None):
            order_price = ((1 - self.policy.rate_buy / 100)) * currency_price
            order_price = round(order_price, 2)

            if order_price > self.policy.max_price:
                return
            # logger.error("retrieve 2")
            if self.plantform.cancel_order(order, self.user) == STATUS_ERROR:
                updated_order = self.update_order_status(order)
                logger.error("无限机器人"+str(self.robot.robot_id)+"修改订单失败!， 需修改订单状态为" + str(updated_order.order_status))
                if updated_order.order_status == ORDER_FINISH:
                    return
            
            order.order_status = ORDER_CANCEL
            self.robot_summary.invested_money -= float(order.order_amount) * float(order.order_price)
            order.save()
            # logger.error("retrieve 4")
            if retrieve_order_price is not None:
                order_price = retrieve_order_price

            amount = round(self.policy.grid_invest / order_price, 4)
            amount = max(amount, 1e-4)
            # logger.error("retrieve 5")
            self.create_order(ORDER_BUY, amount, order_price)

            self.robot_summary.invested_money += amount * order_price

            self.robot_summary.save()
            # logger.error("retrieve 6")

    def check_orders(self):
        
        currency_price = self.plantform.get_currency_price(self.robot.robot_currency_type)
        buy_orders = Order.objects.filter(robot_id=self.robot.robot_id, order_status=ORDER_WAIT, order_type=ORDER_BUY)

        for order in buy_orders:
            if order.order_price < self.policy.min_price or order.order_price > currency_price * (1 + ORDER_DISTANCE):
                updated_order = self.update_order_status(order)
                if updated_order.order_status == ORDER_WAIT:
                    self.plantform.cancel_order(updated_order, self.user)
                    logger.error("无限机器人取消不合理买订单" + str(updated_order.order_price))
                    updated_order = self.update_order_status(updated_order)
                    if updated_order.order_status == ORDER_WAIT:
                        updated_order.order_status = ORDER_Fail
                        updated_order.save()
                        logger.error("无限机器人设置不合理买订单为失败" + str(updated_order.order_price))

                    
        buy_orders = Order.objects.filter(robot_id=self.robot.robot_id, order_status=ORDER_WAIT, order_type=ORDER_BUY)
        buy_order_nums = len(buy_orders)
        if buy_order_nums > 1:
            logger.error("get extra order " + str(self.robot.robot_id))
            for i in range(1, len(buy_orders)):
                self.plantform.cancel_order(buy_orders[i], self.user)
                self.update_order_status(buy_orders[i])
        elif buy_order_nums == 0:
            for i in range(MAX_REPOST_NUM):
                orders = Order.objects.filter(robot_id=self.robot.robot_id, order_status=ORDER_WAIT, order_type=ORDER_BUY)
                if len(orders) == 0 and i == MAX_REPOST_NUM -1:
                    if self.robot_summary.invested_money < self.robot_summary.profit + self.policy.expect_money:
                        self.init_robot_order()
                        logger.error("重启无限网格机器人 " + str(self.robot.robot_id))
 
        sell_order_list = Order.objects.filter(robot_id=self.robot.robot_id, order_status=ORDER_WAIT, order_type=ORDER_SELL)

        for order in sell_order_list:
            if order.order_price > self.policy.max_price or order.order_price < currency_price / (1+ORDER_DISTANCE):
                updated_order = self.update_order_status(order)
                if updated_order.order_status == ORDER_WAIT :
                    self.plantform.cancel_order(updated_order, self.user)
                    logger.error("无限机器人取消不合理卖订单" + str(updated_order.order_price))
                    updated_order = self.update_order_status(updated_order)
                    if updated_order.order_status == ORDER_WAIT:
                        updated_order.order_status = ORDER_Fail
                        updated_order.save()
                        logger.error("无限机器人设置不合理卖订单为失败" + str(updated_order.order_price))

        
        hold_currency_num = 0
        invested_num = 0
        sell_order_list = Order.objects.filter(robot_id=self.robot.robot_id, order_status=ORDER_WAIT, order_type=ORDER_SELL)
        sell_order_list = list(sell_order_list)
        if len(sell_order_list) == 0:
            self.robot_summary.hold_currency_num = hold_currency_num
            self.robot_summary.invested_money = invested_num + self.policy.grid_invest
            self.robot_summary.save()
            return
        sell_order_list.sort(key=lambda x: x.order_price)
        min_sell_price = sell_order_list[0].order_price
        for i in range(len(sell_order_list)):

            if i < len(sell_order_list) - 1 and (sell_order_list[i+1].order_price - sell_order_list[i].order_price) < (min_sell_price * self.policy.rate_sell / 100 * DISTANCE_RATIO):
                updated_order = self.update_order_status(sell_order_list[i])
                if updated_order.order_status == ORDER_WAIT:
                    self.plantform.cancel_order(updated_order, self.user)
                self.update_order_status(updated_order)
                continue

            hold_currency_num += sell_order_list[i].order_amount
            invested_num += sell_order_list[i].order_amount * sell_order_list[i].order_price

        self.robot_summary.hold_currency_num = hold_currency_num
        self.robot_summary.invested_money = invested_num + self.policy.grid_invest
        self.robot_summary.save()                

    def update_order(self, orders):

        for order in orders:
            self.update_order_status(order)



    def update_order_status(self, order):
        if order.order_status == ORDER_WAIT:
            try:
                order_info_dict = self.plantform.check_order(order, self.user)
            except Exception as e:
                if self.robot.robot_status == ROBOT_DELETE:
                    logger.error(repr(e))
                    order.order_status = ORDER_Fail
                    order.save()
                logger.error(repr(e))
                return order
            if order_info_dict['order_status'] == ORDER_FINISH:
                # logger.error("finish 1")
                order.order_status = order_info_dict['order_status']
                order.order_amount = order_info_dict["order_amount"] 
                order.order_price = order_info_dict["order_price"]
                order.order_create_time = order_info_dict["order_create_time"]
                order.order_finish_time = order_info_dict["order_finish_time"]
                order.order_transfer_fees = order_info_dict["order_transfer_fees"]
                # logger.error("finish 2")
                self.robot_summary.total_transfer_fee += order_info_dict["order_transfer_fees"]
                if order.order_type == ORDER_SELL:
                    self.robot_summary.hold_currency_num -= order_info_dict["order_amount"] 
                    self.robot_summary.profit += (1 / (
                            1 + 100 / self.policy.rate_sell)) * order_info_dict["order_amount"]  * order_info_dict["order_price"]
                else:
                    self.robot_summary.hold_currency_num += order_info_dict["order_amount"] 
                self.robot_summary.save()
                order.save()
                # logger.error("finish and save")
                self.supply_order(order)
                # logger.error("finish 3")

            elif order_info_dict['order_status'] == ORDER_CANCEL: 

                order.order_status = order_info_dict['order_status']
                order.order_refer_id = ORDER_NONE_REF
                order.save()
                
        return order


