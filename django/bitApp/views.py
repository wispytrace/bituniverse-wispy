import logging
import os

from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render, redirect

from bitApp.core.user import User
from bitApp.models import *
from bitApp.config import *

from bitApp.core.platform import *
from bitApp.core.robot import *
import datetime

import warnings

from huobi.model import account
warnings.filterwarnings("ignore")

logger = logging.getLogger('log')
huobi = HuoBi()

def test(request):

    return HttpResponse("Hello")


def get_set(request):

    ret = {'status': STATUS_ERROR, 'message': None}

    try:
        ret['currencys'], ret['currency_count'] = huobi.get_currencys()

        ret['apis'], ret['accounts'], ret['nicknames'], ret['count'] = huobi.get_accounts_apis()

        ret['status'] = STATUS_OK

    except Exception as e:
        ret['message'] = repr(e)
        logger.error(repr(e))

    return JsonResponse(ret)

def add_api(request):

    ret = {'status': STATUS_OK, 'message': None}
    reqs = request.POST

    try:
        api_key = reqs['api_key']
        secret_key = reqs['secret_key']
        account_id = int(reqs['account_id'])
        huobi.add_api(api_key, secret_key, account_id)

        ret['valid'] = STATUS_OK
        ret['api_key'] = api_key

    except Exception as e:
        ret['valid'] = STATUS_ERROR
        ret['message'] = repr(e)
        logger.error(repr(e))

    return JsonResponse(ret)

def add_account(request):

    ret = {'status': STATUS_ERROR, 'message': None}

    try:
        huobi.add_account()
        return get_set(request)

    except Exception as e:
        ret['message'] = repr(e)
        logger.error(repr(e))

    return JsonResponse(ret)

def delete_account(request):

    ret = {'status': STATUS_ERROR, 'message': None}
    reqs = request.POST

    try:
        account_id = int(reqs['account_id'])
        ret['valid'] = huobi.delet_account(account_id)
        ret['status'] = STATUS_OK

    except Exception as e:
        ret['valid'] = STATUS_ERROR
        ret['message'] = repr(e)
        logger.error(repr(e))

    return JsonResponse(ret)

def modify_nickname(request):

    ret = {'status': STATUS_ERROR, 'message': None}
    reqs = request.POST

    try:
        account_id = int(reqs['account_id'])
        account_nickname = reqs['account_nickname']
        huobi.modify_account_nickname(account_id, account_nickname)
        ret['account_nickname'] = account_nickname
        ret['status'] = STATUS_OK

    except Exception as e:
        ret['valid'] = STATUS_ERROR
        ret['message'] = repr(e)
        logger.error(repr(e))

    return JsonResponse(ret)

def get_robot_info(request):

    ret = {'status': STATUS_ERROR, 'data': None, 'count': 0, 'balance': 0, 'message': None}
    reqs = request.POST

    try:
        info_list = []
        list_del = []
        list_pause = []
        list_ok = []
        account_id = int(reqs['account_id'])

        robots = Robot.objects.filter(robot_account_id=account_id)
        user = User.load_from_account_id(account_id)

        for robot in robots:
            if robot.robot_status == ROBOT_DELETE:
                continue
            robot_entity = RobotEntity.load_robot(robot)
            robot_entity.set_user(user)
            robot_entity.set_huobi(huobi)
            robot_entity.load_orders()
            robot_info = robot_entity.get_robot_info()
            if robot.robot_status == ROBOT_OK:
                list_ok.append(robot_info)
            elif robot.robot_status == ROBOT_PAUSE:
                list_pause.append(robot_info)
            else:
                list_del.append(robot_info)

        list_ok.sort(key=lambda x: int(x['robot_id']), reverse=True)
        list_pause.sort(key=lambda x: int(x['robot_id']), reverse=True)
        list_del.sort(key=lambda x: int(x['robot_id']), reverse=True)

        info_list += list_ok
        info_list += list_pause
        info_list += list_del

        ret['count'] = len(info_list)
        ret['data'] = info_list
        ret['status'] = STATUS_OK
        ret['message'] = "数据更新成功"
        ret['balance'] = user.get_balance('usdt')

    except Exception as e:
        logger.error(repr(e))
        ret['message'] = repr(e)

    return JsonResponse(ret)


def modify_status(request):

    ret = {'status': STATUS_ERROR, 'message': None}

    reqs = request.POST

    try:
        robot_id = int(reqs['robot_id'])

        robot = Robot.objects.get(robot_id=robot_id)
        robot_entity = RobotEntity.load_robot(robot)
        robot_entity.pause_resume_robot()

        ret['status'] = STATUS_OK
        ret['message'] = "数据更新成功"

    except Exception as e:
        logger.error(repr(e))
        ret['message'] = repr(e)

    return JsonResponse(ret)


def delet_robot(request):
    
    ret = {'status': STATUS_ERROR, 'message': None}

    reqs = request.POST

    try:
        robot_id = int(reqs['robot_id'])
        cancel_order = int(reqs['cancel_order'])
        cancel_currency = int(reqs['cancel_currency'])

        robot = Robot.objects.get(robot_id=robot_id)
        robot_entity = RobotEntity.load_robot(robot)

        user = User.load_from_account_id(robot.robot_account_id)
        robot_entity.set_user(user)
        robot_entity.set_huobi(huobi)
        robot_entity.load_orders()
        if cancel_order == 1:
            robot_entity.cancel_orders()
            if cancel_currency == 1:
                robot_entity.cancel_currencys()
        robot_entity.delete_robot()

        ret['status'] = STATUS_OK
        ret['message'] = "数据更新成功"

    except Exception as e:
        logger.error(repr(e))
        ret['message'] = repr(e)

    return JsonResponse(ret)



def get_invest_parameter(request):

    ret = {'status': STATUS_OK, 'message': None, 'invest_data': None, 'valid': STATUS_ERROR}

    reqs = request.POST

    try:

        robot_type = int(reqs['robot_type'])
        account_id = int(reqs['account_id'])
        user = User.load_from_account_id(account_id)

        if robot_type == GEOMETRIC_POLICY:
            currency_type = reqs['currency_type']
            max_price = float(reqs['max_price'])
            min_price = float(reqs['min_price'])
            grid_num = int(reqs['grid_num'])
            per_invest = float(reqs['per_invest'])
            ret['invest_data'] = GeometricRobot.get_robot_invest_parameter(currency_type, max_price, min_price, grid_num,
                                                      per_invest, huobi, user)
        else:
            currency_type = reqs['currency_type']
            sell_percent = float(reqs['sell_percent'])
            expect_money = float(reqs['expect_money'])
            ret['invest_data'] = InfiniteRobot.get_robot_invest_parameter(currency_type, sell_percent, expect_money, huobi, user)

        ret['message'] = '数据更新成功'
        ret['valid'] = STATUS_OK

    except Exception as e:
        logger.error(repr(e))
        ret['message'] = repr(e)

    return JsonResponse(ret)

def add_geometric_robot(request):

    ret = {'status': STATUS_ERROR, 'message': None}

    reqs = request.POST

    try:
        currency_type = reqs['currency_type']
        max_price = float(reqs['max_price'])
        min_price = float(reqs['min_price'])
        grid_num = int(reqs['grid_num'])
        grid_invest = float(reqs['per_invest'])
        expect_money = float(reqs['expect_money'])
        per_grid = float(reqs['per_grid'])
        account_id = int(reqs['account_id'])

        robot = GeometricRobot.create_robot(currency_type, max_price, min_price, grid_num, grid_invest, expect_money, per_grid, account_id)
        user = User.load_from_account_id(account_id)
        robot_entity = RobotEntity.load_robot(robot)
        robot_entity.set_user(user)
        robot_entity.set_huobi(huobi)
        robot_entity.load_orders()
        robot_entity.init_robot_order()

        ret['status'] = STATUS_OK
        ret['message'] = '数据更新成功'

    except Exception as e:
        logger.error(repr(e))
        ret['message'] = repr(e)

    return JsonResponse(ret)


def add_infinite_robot(request):
    ret = {'status': STATUS_ERROR, 'message': None}

    reqs = request.POST

    try:
        currency_type = reqs['currency_type']
        max_price = float(reqs['max_price'])
        min_price = float(reqs['min_price'])
        sell_percent = float(reqs['sell_percent'])
        buy_percent = float(reqs['buy_percent'])
        expect_money = float(reqs['expect_money'])
        per_invest = float(reqs['per_invest'])
        account_id = int(reqs['account_id'])

        robot = InfiniteRobot.create_robot(currency_type, max_price, min_price, per_invest, buy_percent, sell_percent, expect_money, account_id)
        user = User.load_from_account_id(account_id)
        robot_entity = RobotEntity.load_robot(robot)
        robot_entity.set_huobi(huobi)
        robot_entity.set_user(user)
        robot_entity.load_orders()
        robot_entity.init_robot_order()

        ret['status'] = STATUS_OK
        ret['message'] = '数据更新成功'

    except Exception as e:
        logger.error(repr(e))
        ret['message'] = repr(e)

    return JsonResponse(ret)

def get_robot_parameter(request):

    ret = {'status': STATUS_ERROR, 'data': None}
    reqs = request.POST

    try:
        robot_id = int(reqs['robot_id'])
        robot = Robot.objects.get(robot_id=robot_id)
        robot_entity = RobotEntity.load_robot(robot)
        ret['data'] = robot_entity.get_parameter()

        ret['status'] = STATUS_OK
        ret['message'] = '数据更新成功'

    except Exception as e:
        logger.error(repr(e))
        ret['message'] = repr(e)

    return JsonResponse(ret)



def update_geometric_robot(request):

    ret = {'status': STATUS_ERROR, 'message': None}

    reqs = request.POST

    try:
        robot_id = int(reqs['robot_id'])
        robot = Robot.objects.get(robot_id=robot_id)
        robot_entity = RobotEntity.load_robot(robot)
        max_price = float(reqs['max_price'])
        min_price = float(reqs['min_price'])
        grid_num = int(reqs['grid_num'])
        per_invest = float(reqs['per_invest'])
        expect_money = float(reqs['expect_money'])
        per_grid = float(reqs['per_grid'])
        robot_entity.modify_robot(max_price, min_price, grid_num, per_invest, expect_money, per_grid)

        ret['status'] = STATUS_OK
        ret['message'] = "数据更新成功"

    except Exception as e:
        logger.error(repr(e))
        ret['message'] = repr(e)

    return JsonResponse(ret)



def update_infinite_robot(request):

    ret = {'status': STATUS_ERROR, 'message': None}

    reqs = request.POST

    try:
        robot_id = int(reqs['robot_id'])
        robot = Robot.objects.get(robot_id=robot_id)
        robot_entity = RobotEntity.load_robot(robot)
        user = User.load_from_account_id(robot.robot_account_id)
        robot_entity.set_user(user)
        robot_entity.set_huobi(huobi)
        robot_entity.load_orders()
        max_price = float(reqs['max_price'])
        min_price = float(reqs['min_price'])
        sell_percent = float(reqs['sell_percent'])
        per_invest = float(reqs['per_invest'])
        expect_money = float(reqs['expect_money'])
        buy_percent = float(reqs['buy_percent'])
        robot_entity.modify_robot(max_price, min_price, per_invest, buy_percent, sell_percent, expect_money)

        ret['status'] = STATUS_OK
        ret['message'] = "数据更新成功"

    except Exception as e:
        logger.error(repr(e))
        ret['message'] = repr(e)

    return JsonResponse(ret)


def get_trade_order_info(request):

    ret = {'status': -1, 'trade_data':None, 'trade_count': None, 'message': None}

    reqs = request.POST

    try:
        robot_id = int(reqs['robot_id'])
        robot = Robot.objects.get(robot_id=robot_id)
        robot_entity = RobotEntity.load_robot(robot)
        user = User.load_from_account_id(robot.robot_account_id)
        robot_entity.set_user(user)
        robot_entity.set_huobi(huobi)
        robot_entity.load_orders()
        order_list = robot_entity.get_trade_order_list()

        ret['trade_data'] = order_list
        ret['trade_count'] = len(order_list)

        ret['message'] = '数据更新成功'
        ret['status'] = 0

    except Exception as e:
        logger.error(repr(e))
        ret['message'] = repr(e)

    return JsonResponse(ret)

def get_pender_order_info(request):

    ret = {'status': -1, 'pender_data': None, 'pender_count': None, 'message': None}

    reqs = request.POST

    try:
        robot_id = int(reqs['robot_id'])
        robot = Robot.objects.get(robot_id=robot_id)
        robot_entity = RobotEntity.load_robot(robot)
        user = User.load_from_account_id(robot.robot_account_id)
        robot_entity.set_user(user)
        robot_entity.set_huobi(huobi)
        robot_entity.load_orders()
        order_list = robot_entity.get_pender_order_list()
        ret['pender_data'] = order_list
        ret['pender_count'] = len(order_list)
        ret['currency_price'] = robot_entity.huobi.get_currency_price(robot_entity.robot.robot_currency_type)
        ret['per_invest'] = str('%g' % robot_entity.policy.grid_invest)

        ret['message'] = '数据更新成功'
        ret['status'] = 0

    except Exception as e:
        logger.error(repr(e))
        ret['message'] = repr(e)

    return JsonResponse(ret)


def get_log(request):

    ret = {'status': STATUS_ERROR, 'data': None, 'message': None}

    try:

        cur_path = os.path.dirname(os.path.realpath(__file__))
        log_path = os.path.join(os.path.dirname(cur_path), 'logs')
        files = [os.path.join(log_path, 'error.log')]
        # for i in range(3):
        #     day = ((datetime.datetime.now()) + datetime.timedelta(days=-i)).strftime("%Y-%m-%d")
        #     file_name = os.path.join(log_path, 'error-{}.log'.format(day))
        #     if os.path.exists(file_name):
        #         files.append(file_name)
        #     else:
        #         continue

        res = ''
        for file in files:
            f = open(file, 'r', encoding='utf-8')
            res += f.read()
            f.close()

        ret['status'] = STATUS_OK
        ret['data'] = res
        ret['message'] = '数据更新成功'

    except Exception as e:
        logger.error(repr(e))
        ret['message'] = repr(e)

    return JsonResponse(ret)


def update(requests):

    ret = {'status': STATUS_ERROR, 'message': None}

    try:
        huobi.update_price()
        orders = Order.objects.filter(order_status=ORDER_WAIT)
        orders = list(orders)
        orders.sort(key=lambda x: int(math.fabs(x.order_price - huobi.get_currency_price(x.order_currency_type))))
        robot_orders = {}

        order_num = min(len(orders), MAX_ORDER_NUM)

        for i in range(order_num):
            robot_id = orders[i].robot_id
            if robot_id not in robot_orders.keys():
                order_list = [orders[i]]
                robot_orders[robot_id] = order_list
            else:
                robot_orders[robot_id].append(orders[i])

        for k, v in robot_orders.items():
            robot = Robot.objects.get(robot_id=k)
            order_list = v
            robot_entity = RobotEntity.load_robot(robot)
            user = User.load_from_account_id(robot.robot_account_id)
            robot_entity.set_user(user)
            robot_entity.set_huobi(huobi)
            robot_entity.load_orders()
            robot_entity.update_order(order_list)

        infinite_robots = Robot.objects.filter(robot_policy_type=INFINITE_POLICY, robot_status=ROBOT_OK)
        for robot in infinite_robots:
            robot_entity = RobotEntity.load_robot(robot)
            user = User.load_from_account_id(robot.robot_account_id)
            robot_entity.set_user(user)
            robot_entity.set_huobi(huobi)
            robot_entity.check_supply_order()


        ret['status'] = STATUS_OK
        ret['message'] = '数据更新成功'

    except Exception as e:
        logger.error(repr(e))
        ret['message'] = repr(e)

    return JsonResponse(ret)

def clear_api(request):

    ret = {'status': STATUS_ERROR, 'message': None}

    try:
        huobi.clear_accounts()
        ret['status'] = STATUS_OK

    except Exception as e:
        ret['message'] = repr(e)
        logger.error(repr(e))

    return JsonResponse(ret)


def clear_orders(request):

    ret = {'status': STATUS_ERROR, 'message': None}

    try:
        now_time = datetime.datetime.now()
        order_list = Order.objects.all()
        delet_count = 0
        for i in range(len(order_list)):
            create_time = order_list[i].order_create_time.replace(tzinfo=None)
            days = (now_time - create_time).days
            if int(days) > 1 and order_list[i].order_status == ORDER_CANCEL:
                order_list[i].delete()
                delet_count += 1

        ret['status'] = STATUS_OK
        ret['delet_count'] = delet_count



    except Exception as e:
        ret['message'] = repr(e)
        logger.error(repr(e))

    return JsonResponse(ret)
