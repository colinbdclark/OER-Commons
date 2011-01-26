from django.contrib.auth.models import User
from materials.scripts.migrate_courses import force_unicode
from savedsearches.models import SavedSearch
from users.models import Profile
import cjson
import dateutil.parser


admin = User.objects.get(pk=1)


def run():
    # Delete existing searches
    print "Removing existing searches..."
    SavedSearch.objects.all().delete()

    print "Creating searches..."

    cached_users = dict([(profile.principal_id, profile.user) for profile in Profile.objects.select_related().all()])
    cached_users["zope.manager"] = admin


    cnt = 0

    rows = cjson.decode(open("saved_searches.json").read())
    total_items = len(rows)

    for principal, title, timestamp, url in rows:

        search = SavedSearch(title=force_unicode(title),
                             url=force_unicode(url),
                             user=cached_users[principal])
        search.timestamp = dateutil.parser.parse(timestamp)
        search.save()

        cnt += 1

        print "%i of %i" % (cnt, total_items)

    print "Done!"
