from django.core.management.base import BaseCommand
from users import DAYS_TO_DELETE
import datetime


class Command(BaseCommand):

    help = u"Delete old non-confirmed accounts."
    option_list = BaseCommand.option_list

    def handle(self, **options):
        from users.models import RegistrationConfirmation
        from_date = datetime.datetime.now() - datetime.timedelta(days=DAYS_TO_DELETE)
        for confirmation in RegistrationConfirmation.objects.filter(timestamp__lte=from_date,
                                                                    confirmed=False):
            user = confirmation.user
            confirmation.delete()
            user.delete()
