source /root/anaconda3/bin/activate robot
python /root/django/manage.py runserver 0.0.0.0:8000 &
python /root/django/daemon.py > daemon.txt &