from fabric.api import local, run, cd, sudo, env

import tempfile

env.hosts = ['ubuntu@akorn.org']
env.directory = "/home/ubuntu/akorn/akorn_search"

def get_dump(output):
    local('scp {host}:~/dump/fulldump {out}'.format(host=env.hosts[0],
        out=output))

def load_dump(dump_file=None, couch_url='http://localhost:5984/store/'):
    # Delete database if already present
    local('curl -X DELETE {url}'.format(url=couch_url))
    # Create a new database
    local('curl -X PUT {url}'.format(url=couch_url))
    # If a dump file has not been specified then grab one from the server
    if not dump_file:
        fd, dump_file = tempfile.mkstemp()
        get_dump(dump_file)
    # Load contents into new database
    local('couchdb-load --input={input} {url}'.format(input=dump_file,
        url=couch_url))

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
