# ipy -tt buildutil.py sample_dir\sample.py bool_option=True "int_option = 456" string_option="changed value"

string_option = 'default value'
int_option = 123
bool_option = False

default = ['debug_infos', 'task1', 'task2']

def debug_infos():
	import custom_module
	custom_module.debug_infos()

def task1():
	print('into task1')

def task2():
	print('into task2')
