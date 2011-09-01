from django.core.management.base import AppCommand
from django.conf import settings
from optparse import make_option


class Command(AppCommand):
    help = "Freshens the index for the given app(s)."

    option_list = AppCommand.option_list

    # Django 1.0.X compatibility.
    verbosity_present = False

    for option in option_list:
        if option.get_opt_string() == '--verbosity':
            verbosity_present = True

    if verbosity_present is False:
        option_list = option_list + (
            make_option('--verbosity', action='store', dest='verbosity', default='1',
                type='choice', choices=['0', '1', '2'],
                help='Verbosity level; 0=minimal output, 1=normal output, 2=all output'
            ),
        )

    def handle(self, *apps, **options):
        self.verbosity = int(options.get('verbosity', 1))

        if not apps:
            from django.db.models import get_app
            # Do all, in an INSTALLED_APPS sorted order.
            apps = []

            for app in settings.INSTALLED_APPS:
                try:
                    app_label = app.split('.')[-1]
                    loaded_app = get_app(app_label)
                    apps.append(app_label)
                except:
                    # No models, no problem.
                    pass

        return super(Command, self).handle(*apps, **options)

    def handle_app(self, app, **options):
        # Cause the default site to load.
        from haystack import site
        from django.db.models import get_models
        from haystack.exceptions import NotRegistered
        from haystack_scheduled.indexes import ScheduledSearchIndex

        for model in get_models(app):
            try:
                index = site.get_index(model)
            except NotRegistered:
                if self.verbosity >= 2:
                    print "Skipping '%s' - no index." % model
                continue

            if not isinstance(index, ScheduledSearchIndex):
                if self.verbosity >= 2:
                    print "Skipping '%s' - only ScheduledSearchIndex is supported." % model
                continue

            print "'%s' - unindexing removed objects." % model

            index.unindex_removed()
