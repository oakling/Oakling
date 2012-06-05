from fabric.api import local, run, cd

def hello():
    print("Hello world!")

def prepare_deploy():
  local('git push')

def deploy():
  with cd('/home/ubuntu/akorn/akorn_search'):
    run('git pull')
    run('sudo /etc/init.d/django-akorn restart')

