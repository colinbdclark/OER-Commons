from django.db import connections
from information.models import HelpTopic, AboutTopic


models = [
    (HelpTopic, "helptopics"),
    (AboutTopic, "abouttopics"),
]


def run():
    cursor = connections["old"].cursor()

    for model, table in models:
        # Delete existing topics
        print u"Removing existing %s..." % unicode(model._meta.verbose_name_plural)
        model.objects.all().delete()

        print u"Creating %s..." % unicode(model._meta.verbose_name_plural)

        cursor.execute("SELECT * FROM %s" % table)

        total_items = cursor.rowcount

        cnt = 0


        for id, name, title, short_title, text, order in cursor.fetchall():

            cnt += 1

            topic = model(title=title, short_title=short_title, text=text, order=order)
            topic.save()

            print "%i of %i" % (cnt, total_items)

    print "Done!"
