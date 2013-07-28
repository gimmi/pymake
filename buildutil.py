import inspect, sys, traceback

def main():
	build_module = __import__('__main__')
	args = sys.argv[1:]
	run(build_module, args, ironpython_cprint)

def run(build_module, args, cprint):
	try:
		tasks = parse_args(build_module, args)

		dump_cfg(build_module, cprint)

		for task in tasks:
			cprint('Executing %s' % task, 'Cyan')
			task_fn = getattr(build_module, task)
			task_fn()
		cprint('Build Succeeded!', 'Green')
	except:
		cprint('Build Failed!', 'Red')
		raise

def parse_args(build_module, args):
	arg_name = None
	tasks = []
	for arg in args:
		if arg.startswith('--'):
			arg_name = arg[2:]
		elif arg_name:
			arg_type = type(getattr(build_module, arg_name, ''))
			setattr(build_module, arg_name, arg_type(arg))
			arg_name = None
		else:
			tasks.append(arg)
	return tasks

def dump_cfg(build_module, cprint):
	names = [n for n in dir(build_module) if not n.startswith('_') and type(getattr(build_module, n)) in [str, int, bool]]

	if not names:
		return

	pad = max([len(x) for x in names])

	for name in names:
		cprint(name.rjust(pad) + ': ', 'White', '')
		cprint(str(getattr(build_module, name)))

def ironpython_cprint(message, fg='Gray', end='\n'):
	import System
	System.Console.ForegroundColor = getattr(System.ConsoleColor, fg)
	sys.stdout.write(message)
	sys.stdout.write(end)
	System.Console.ResetColor()
