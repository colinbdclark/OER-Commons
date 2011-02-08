from django.contrib import messages
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.http import HttpResponseRedirect
from django.utils.decorators import available_attrs
from django.utils.functional import wraps
from django.utils.http import urlquote
from tempfile import NamedTemporaryFile
import hotshot
import hotshot.stats


def user_passes_test(test_func, login_url=None, redirect_field_name=REDIRECT_FIELD_NAME):
    """
    Decorator for views that checks that the user passes the given test,
    redirecting to the log-in page if necessary. The test should be a callable
    that takes the user object and returns True if the user passes.
    """
    if not login_url:
        from django.conf import settings
        login_url = settings.LOGIN_URL

    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if test_func(request.user):
                return view_func(request, *args, **kwargs)
            path = urlquote(request.get_full_path())
            tup = login_url, redirect_field_name, path
            messages.warning(request, u"You must be logged in to perform this action.")
            return HttpResponseRedirect('%s?%s=%s' % tup)
        return wraps(view_func, assigned=available_attrs(view_func))(_wrapped_view)
    return decorator


def login_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME):
    """
    Decorator for views that checks that the user is logged in, redirecting
    to the log-in page if necessary.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated(),
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


def profile(f):
    
    def _inner(*args, **kwargs):
        
        log_file = NamedTemporaryFile()
        prof = hotshot.Profile(log_file.name)
        try:
            ret = prof.runcall(f, *args, **kwargs)
            stats = hotshot.stats.load(log_file.name)
            #stats.strip_dirs()
            stats.sort_stats('time', 'calls')
            stats.print_stats(200)
        finally:
            prof.close()
        return ret
    
    return _inner
