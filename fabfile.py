from fabric.api import local, run, cd, sudo, env

import tempfile

env.hosts = ['ubuntu@akorn.org']
env.directory = "/home/ubuntu/akorn/akorn_search"
env.dumps = {'store': '~/dump/store_25-10-12.couchdump',
    'journals': '~/dump/journals_25-10-12.couchdump'}

def get_dump(output, target='~/dump/fulldump'):
    local('scp {host}:{target} {out}'.format(host=env.hosts[0],
        target=target,
        out=output))

def load_dump(couch_db, dump_file, couch_url='http://localhost:5984/'):
    couch_db_url = couch_url+couch_db
    # Delete database if already present
    local('curl -X DELETE {url}'.format(url=couch_db_url))
    # Create a new database
    local('curl -X PUT {url}'.format(url=couch_db_url))
    # Load contents into new database
    local('couchdb-load --input={input} {url}'.format(input=dump_file,
        url=couch_db_url))

def load_dumps():
    dump_files = {}
    # Get the dump files
    for couch_db, target in env.dumps.items():
        # Create a tmp file to store without risk of collision
        fd, path = tempfile.mkstemp()
        # Download the file
        get_dump(path, target)
        dump_files[couch_db] = path
    # Load the dump files
    for couch_db, dump in dump_files.items():
        load_dump(couch_db, dump)

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
