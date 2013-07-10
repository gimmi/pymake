import sys, traceback, System

def main():
  try:
		main_module = get_main_module()

		merge_args(main_module.cfg, sys.argv[1:])

		for task in main_module.cfg['tasks']:
			cprint('Executing %s' % task, 'Cyan')
			task_fn = getattr(main_module, task)
			task_fn()
		cprint('\nBuild Succeeded!', 'Green')
	except:
		cprint('\nBuild Failed!\n', 'Red')
		print(traceback.format_exc())
		sys.exit(1)

def get_main_module():
	return __import__('__main__')

def merge_args(args, commandline_args):
	arg_name = None
	for arg in commandline_args:
		if arg.startswith('--'):
			arg_name = arg[2:]
		elif arg_name in args and type(args[arg_name]) == list:
			args[arg_name].append(arg)
		elif arg_name in args:
			args[arg_name] = arg

def cprint(message, fg=None):
	if fg: System.Console.ForegroundColor = getattr(System.ConsoleColor, fg)
	print(message)
	System.Console.ResetColor()

def dump_cfg():
	main_module = get_main_module()

	pad = max([len(x) for x in main_module.cfg])

	for k, v in main_module.cfg.iteritems():
		System.Console.ForegroundColor = System.ConsoleColor.White
		sys.stdout.write(k.rjust(pad) + ': ')
		System.Console.ResetColor()
		sys.stdout.write(str(v))
		sys.stdout.write('\n')
