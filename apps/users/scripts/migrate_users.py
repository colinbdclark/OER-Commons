from autoslug.settings import slugify
from common.models import GradeLevel
from django.contrib.auth.models import User
from django.db import connections
from django.db.utils import DatabaseError
from users.models import Profile
from users.backend import BCRYPT_PREFIX


def force_unicode(o):
    if isinstance(o, unicode):
        return o
    if isinstance(o, str):
        return o.decode("utf-8")
    if isinstance(o, list):
        return [force_unicode(item) for item in o]
    raise ValueError()


def run():
    cursor = connections["old"].cursor()

    # Delete existing profiles
    print "Removing existing profiles..."
    Profile.objects.all().delete()

    # Delete existing users
    print "Removing existing users..."
    User.objects.exclude(pk=1).delete()

    cursor.execute("SELECT id, login, encrypted_password, title, description, email, "
                   "homepage, institution, institution_url, grade_levels, department, "
                   "specializations, state, biography, why_interested, publish_portfolio, "
                   "publish_profile, role FROM _principals")

    total_items = cursor.rowcount

    print "Creating users..."
    cnt = 0
    for id, login, encrypted_password, title, description, email, \
        homepage, institution, institution_url, grade_levels, department, \
        specializations, state, biography, why_interested, publish_portfolio, \
        publish_profile, role in cursor.fetchall():

        cnt += 1

        if role is None:
            role = u""
        if specializations is None:
            specializations = []
        if homepage is None:
            homepage = u""
        if institution is None:
            institution = u""
        if institution_url is None:
            institution_url = u""
        if department is None:
            department = u""
        if state is None:
            state = u""
        if biography is None:
            biography = u""
        if why_interested is None:
            why_interested = u""
        if publish_portfolio is None:
            publish_portfolio = False
        if publish_profile is None:
            publish_profile = False
        if grade_levels is None:
            grade_levels = []

        principal_id = "oer.member.%i" % id
        try:
            first_name, last_name = title.split(None, 1)
        except ValueError:
            first_name = title
            last_name = u""


        if len(first_name) > 30:
            first_name = first_name[:30]
        if len(last_name) > 30:
            last_name = last_name[:30]

        password = BCRYPT_PREFIX + encrypted_password
        user = User(username=login,
                    password=password,
                    email=email,
                    first_name=first_name,
                    last_name=last_name
                    )
        user.save()

        profile = Profile(user=user,
                          principal_id=principal_id,
                          homepage=force_unicode(homepage),
                          institution=force_unicode(institution),
                          institution_url=force_unicode(institution_url),
                          department=force_unicode(department),
                          specializations=u"\n".join(force_unicode(specializations)),
                          state=force_unicode(state),
                          biography=force_unicode(biography),
                          why_interested=force_unicode(why_interested),
                          publish_portfolio=publish_portfolio,
                          publish_profile=publish_profile,
                          role=force_unicode(role))

        try:
            profile.save()
        except DatabaseError:
            import pprint
            pprint.pprint(locals())
            raise

        for l in grade_levels:
            l = slugify(l)
            try:
                grade_level = GradeLevel.objects.get(slug=l)
            except GradeLevel.DoesNotExist:
                print l
            profile.grade_level.add(grade_level)

        if cnt % 100 == 0:
            print "%i of %i" % (cnt, total_items)

    print "Done!"
