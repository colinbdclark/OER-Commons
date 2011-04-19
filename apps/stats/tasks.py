from celery.decorators import periodic_task
from celery.schedules import crontab
from stats.report import send_report
import datetime


@periodic_task(run_every=crontab(hour=1, minute=0, day_of_week=1))
def send_weekly_report():
    send_report(interval=datetime.timedelta(days=7))