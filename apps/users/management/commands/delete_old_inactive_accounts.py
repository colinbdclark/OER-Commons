from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
import datetime


class Command(BaseCommand):

    help = u"Delete old non-activated accounts."
    option_list = BaseCommand.option_list

    def handle(self, **options):
        from_date = datetime.datetime.now() - datetime.timedelta(days=30)
        for user in User.objects.filter(is_active=False, date_joined__lte=from_date):
            user.delete()
