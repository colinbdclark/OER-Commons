from celery.decorators import periodic_task
from celery.schedules import crontab
from django.contrib.auth.models import User
import datetime


@periodic_task(run_every=crontab(hour=2, minute=0))
def delete_old_inactive_accounts():
    from_date = datetime.datetime.now() - datetime.timedelta(days=30)
    for user in User.objects.filter(is_active=False, date_joined__lte=from_date):
        user.delete()
