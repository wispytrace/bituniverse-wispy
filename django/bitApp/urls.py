from django.urls import path

from . import views

urlpatterns = [
    path('test', views.test, name='test'),
    path('get_set', views.get_set, name='get_set'),
    path('add_api', views.add_api, name='add_api'),
    path('add_account', views.add_account, name='add_account'),
    path('delete_account', views.delete_account, name='delete_account'),
    path('get_robot_info', views.get_robot_info, name='get_robot_info'),
    path('modify_status', views.modify_status, name='modify_status'),
    path('delet_robot', views.delet_robot, name='delet_robot'),
    path('get_invest_parameter', views.get_invest_parameter, name='get_invest_parameter'),
    path('add_geometric_robot', views.add_geometric_robot, name='add_geometric_robot'),
    path('add_infinite_robot', views.add_infinite_robot, name='add_infinite_robot'),
    path('get_robot_parameter', views.get_robot_parameter, name='get_robot_parameter'),
    path('update_geometric_robot', views.update_geometric_robot, name='update_geometric_robot'),
    path('update_infinite_robot', views.update_infinite_robot, name='update_infinite_robot'),
    path('get_trade_order_info', views.get_trade_order_info, name='get_trade_order_info'),
    path('get_pender_order_info', views.get_pender_order_info, name='get_pender_order_info'),
    path('get_log', views.get_log, name='get_log'),
    path('update', views.update, name='update'),
    path('update_plantform_price', views.update_plantform_price, name='update_plantform_price'),
    path('clear_orders', views.clear_orders, name='clear_orders'),
    path('clear_api', views.clear_api, name='clear_api'),
    path('check_robots', views.check_robots, name='check_robots'),
    path('modify_nickname', views.modify_nickname, name='modify_nickname')

]