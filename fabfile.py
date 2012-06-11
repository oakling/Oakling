from fabric.api import local, run, cd, sudo

def hello():
    print("Hello world!")

def prepare_deploy():
  local('git push')

def deploy():
  with cd('/home/ubuntu/akorn/akorn_search'):
    run('git pull')
    run('python manage.py collectstatic --noinput')
    sudo('/etc/init.d/django-akorn restart')

