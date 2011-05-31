from django.core.management.base import BaseCommand
from users.models import RegistrationConfirmation
import datetime


class Command(BaseCommand):

    help = u"Delete old non-confirmed accounts."
    option_list = BaseCommand.option_list

    def handle(self, **options):
        from_date = datetime.datetime.now() - datetime.timedelta(days=30)
        for confirmation in RegistrationConfirmation.objects.filter(timestamp=from_date,
                                                                    confirmed=False):
            user = confirmation.user
            confirmation.delete()
            user.delete()
