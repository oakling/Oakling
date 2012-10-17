import celeryconfig
import sys

for sched_name, sched_task in celeryconfig.CELERYBEAT_SCHEDULE.items():
  task_path = sched_task['task'].split('.')

  module_name = ".".join(task_path[:-1])
  task_name = task_path[-1]

  print module_name, task_name

  __import__(module_name)
  module = sys.modules[module_name]

  task = module.__dict__[task_name]

  if 'args' in sched_task:
    task(*sched_task['args'])
  else:
    task()

