import celeryconfig
import sys

if len(sys.argv) >= 2:
  sched_name_contains = sys.argv[1]
else:
  sched_name_contains = None

for sched_name, sched_task in celeryconfig.CELERYBEAT_SCHEDULE.items():
  task_path = sched_task['task'].split('.')

  module_name = ".".join(task_path[:-1])
  task_name = task_path[-1]

  print sched_name_contains, sched_name

  if sched_name_contains is not None and sched_name_contains not in sched_name:
    continue
  
  print module_name, task_name

  __import__(module_name)
  module = sys.modules[module_name]

  task = module.__dict__[task_name]

  if 'args' in sched_task:
    task(*sched_task['args'])
  else:
    task()

