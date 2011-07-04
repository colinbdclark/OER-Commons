from fabric.api import local, env, cd, sudo


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
        sudo("invoke-rc.d jetty restart")


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
    coverage()