from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from . import tasks

def start():
    scheduler = BackgroundScheduler()
    # scheduler = BackgroundScheduler(timezone="America/Mexico_City")
    # scheduler.add_job(tasks.checkLinkStatus, 'interval', minutes=2)
    # scheduler.add_job(tasks.verificarSolicitudesVencidas, 'interval', minutes=4)
    # # #scheduler.add_job(selenium.get_hcRutasInter, 'cron', day_of_week='0-6', hour='7')
    # # #activar cada 24 horas
    # scheduler.add_job(tasks.envioRecordatorioConfirmacion, 'interval', minutes=60)
    # scheduler.add_job(tasks.envioRecordatorioPago, 'interval', minutes=59)
    scheduler.start()
