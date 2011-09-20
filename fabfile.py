from fabric.api import local, env, cd, sudo
import os


CONF = {
    "oercommons.org": {
        "user": "django",
        "path": "/usr/local/django/instances/oercommons/",
        "celeryd-process": "oercommons",
        "buildout-config": "buildout.cfg",
    },
    "staging.oercommons.org": {
        "user": "django",
        "path": "/usr/local/django/instances/oercommons-staging/",
        "celeryd-process": "oercommons-staging",
        "buildout-config": "buildout-staging.cfg",
    },
}


TESTED_APPS = ["users", "project"]


def run_command(command):
    if env.host is None:
        local(command)
    else:
        conf = CONF[env.host]
        path = conf["path"]
        user = conf["user"]
        with cd(path):
            sudo(command, user=user)


def coverage():
    command = "./bin/django test_coverage --settings=project.test_settings %s" % " ".join(TESTED_APPS)
    run_command(command)


def test():
    command= "./bin/django test --settings=project.test_settings %s" % " ".join(TESTED_APPS)
    run_command(command)


def pull():
    run_command("git pull")


def migrate(*args):
    run_command("./bin/django syncdb")
    run_command("./bin/django migrate %s" % " ".join(args))


def build_static():
    run_command("./bin/django build_static -l --noinput")


def restart(*args):
    if not env.host:
        return
    if not args:
        args = ["apache"]
    if "apache" in args:
        sudo("invoke-rc.d apache2 reload")
    if "celery" in args:
        celeryd_process = CONF[env.host]["celeryd-process"]
        run_command("./bin/django celeryd_multi restart %s" % celeryd_process)
    if "jetty" in args:
        sudo("invoke-rc.d jetty stop")
        sudo("invoke-rc.d jetty start")


def build():
    if env.host is None:
        config = "buildout-dev.cfg"
    else:
        config = CONF[env.host]["buildout-config"]
    command= "./bin/buildout -c %s" % config
    run_command(command)


def deploy(*args):
    pull()
    if "build" in args:
        build()
    if "static" in args:
        build_static()
    if "migrate" in args:
        migrate()
    restart_args = ["apache"]
    if "jetty" in args:
        restart_args.append("jetty")
    if "celery" in args:
        restart_args.append("celery")
    restart(*restart_args)
    if "coverage" in args:
        coverage()


CSS_DIR = "./project/media/styles/"


def ie_inline_blocks(*args):
    if env.host is not None:
        print "This command must be run locally."
        return

    print "Creating CSS inline-block rules for IE..."

    local("./bin/django runscript ie_inline_block_rules > %s" % os.path.join(CSS_DIR, "ie-inline-block.css"))


def csscomb(*args):
    if env.host is not None:
        print "This command must be run locally."
        return

    for filename in os.listdir(CSS_DIR):
        if not filename.endswith(".css"):
            continue
        print "Running CSSComb for %s" % filename

        filename = os.path.join(CSS_DIR, filename)

        local("php /Users/andreyfedoseev/Development/csscomb.php %s" % filename)


JS_DIR = "./project/media/javascripts/"


def jshint(*args):
    if env.host is not None:
        print "This command must be run locally."
        return

    for filename in os.listdir(JS_DIR):
        if not filename.endswith(".js"):
            continue
        print "Running JSLint for %s" % filename
        filename = os.path.join(JS_DIR, filename)

        local("/Users/andreyfedoseev/Development/external/jshint/env/jsc.sh %s" % filename)


# Prepare code for commit
def prepare(*args):
    if env.host is not None:
        print "This command must be run locally."
        return

    ie_inline_blocks()
    csscomb()
    jshint()
