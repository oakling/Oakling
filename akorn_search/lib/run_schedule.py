import celeryconfig
import sys

sched_task = celeryconfig.CELERYBEAT_SCHEDULE[sys.argv[1]]

task_path = sched_task['task'].split('.')

module_name = ".".join(task_path[:-1])
task_name = task_path[-1]

print module_name, task_name

__import__(module_name)
module = sys.modules[module_name]

task = module.__dict__[task_name]

task(*sched_task['args'])

