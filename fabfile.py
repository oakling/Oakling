from fabric.api import local, run, cd, sudo, env

env.hosts = ['ubuntu@akorn.org']
env.directory = "/home/ubuntu/akorn/akorn_search"

def prepare_deploy():
    local('git push')

def deploy():
    with cd(env.directory):
        run('git pull')
        collect_static()
        sudo('/etc/init.d/django-akorn restart')

def collect_static():
    with cd(env.directory):
        run('python manage.py collectstatic --noinput')

def celery_restart():
    sudo('/etc/init.d/celeryd restart')

def celerybeat_restart():
    sudo('/etc/init.d/celerybeat restart')

def rabbitmq_restart():
    sudo('/etc/init.d/rabbitmq-server restart')
