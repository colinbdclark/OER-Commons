from django.core.management.base import BaseCommand
import datetime


class Command(BaseCommand):

    help = u"Delete old non-confirmed accounts."
    option_list = BaseCommand.option_list

    def handle(self, **options):
        from users.models import RegistrationConfirmation
        from_date = datetime.datetime.now() - datetime.timedelta(days=30)
        for confirmation in RegistrationConfirmation.objects.filter(timestamp__lte=from_date,
                                                                    confirmed=False):
            user = confirmation.user
            confirmation.delete()
            user.delete()
