import requests
import time
import threading
from bitApp.config import *

URL_IP = "http://8.210.174.164:8000/"


def update_orders(plantform):

    data = {'plantform': plantform}

    while True:
        try:
            update_res = requests.get(url=URL_IP+"api/update", params=data)
            # time.sleep(0.5)
            # print("update" + plantform)
        except Exception as e:
            time.sleep(1)
            print(repr(e))

def update_prices(plantform):
    count = 0
    data = {'plantform': plantform}
    while True:
        try:
            update_res = requests.get(url=URL_IP+"api/update_plantform_price", params=data)
            time.sleep(0.5)
            # print("update_price" + plantform)
        except Exception as e:
            time.sleep(1)
            print(repr(e))

def fix_robots():

    count = 0

    while True:
        try:
            count += 1
            if count >= 60000:
                update_res = requests.get(url=URL_IP+"api/clear_orders")
                count = 0
            elif count % 900 == 0:
                pass
                # update_res = requests.get(url=URL_IP+"api/check_robots")
            time.sleep(1)
        except Exception as e:
            time.sleep(1)
            print(repr(e))


if __name__ == '__main__':
    
    for plantform in plantform_array:
        oder_thread = threading.Thread(target=update_orders, args=(plantform,))
        oder_thread.start()
        price_thread = threading.Thread(target=update_prices, args=(plantform,)) 
        price_thread.start()

    fix_thread = threading.Thread(target=fix_robots)
    fix_thread.start()
