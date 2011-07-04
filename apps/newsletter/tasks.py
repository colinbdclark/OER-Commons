from celery.decorators import task
from django.conf import settings
import mailchimp


@task
def subscribe(email, first_name=None, last_name=None):

    api_key = getattr(settings, "MAILCHIMP_API_KEY", None)
    list_id = getattr(settings, "MAILCHIMP_LIST_ID", None)

    if not api_key or not list_id:
        return

    list = mailchimp.utils.get_connection().get_list_by_id(list_id)
    user_data = {"EMAIL": email}
    if first_name:
        user_data["FNAME"] = first_name
    if last_name:
        user_data["LNAME"] = last_name
    list.subscribe(email, user_data, email_type="html",
                   double_optin=False)
