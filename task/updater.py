from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from . import tasks

def start():
    scheduler = BackgroundScheduler()
    #scheduler.add_job(tasks.checkLinkStatus, 'interval', minutes=1)
    #scheduler.add_job(selenium.get_hcRutasInter, 'cron', day_of_week='0-6', hour='7')
    scheduler.start()
