from django.conf import settings
from django.core.mail.message import EmailMessage
from django.template.loader import render_to_string
from stats.views import STATS
import datetime


def send_report(interval=datetime.timedelta(days=7)):
    send_to = getattr(settings, "STATS_SEND_REPORT_TO", None)
    if not send_to:
        return
    now = datetime.datetime.now()
    from_date = now - interval

    stats = []
    for title, getter in STATS:
        stats.append(dict(title=title, value=getter(from_date=from_date)))
    
    body = render_to_string("stats/emails/report.html",
                               dict(stats=stats, from_date=from_date,
                                    now=now))
    message = EmailMessage(u"OER Commons Statisticts",
                           body, None, send_to)
    message.content_subtype = "html"
    message.send()
    