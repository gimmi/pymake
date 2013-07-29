# ipy -m unittest discover

import unittest, buildutil

class TestModule:
  pass

class TestBuildutil(unittest.TestCase):
	def setUp(self):
		self.sut = range(10)
		self.module = TestModule()
		self.cprint_out = []

	def fake_cprint(self, message, fg='Gray', end='\n'):
		self.cprint_out.append(message + end)

	def get_out_lines(self):
		out = ''.join(self.cprint_out)
		out = out.split('\n')
		return [x for x in out if x]

	def test_should_parse_args(self):
		self.module.int_option = 123
		self.module.bool_option = False

		tasks = buildutil.parse_args(self.module, [
			't1', 
			'--string_option', 'string_value', 
			't2', 
			'--int_option', '456', 
			't3',
			'--bool_option', 't',
			't4'
		])

		self.assertEqual(tasks, ['t1', 't2', 't3', 't4'])
		self.assertEqual(self.module.string_option, 'string_value')
		self.assertEqual(self.module.int_option, 456)
		self.assertTrue(self.module.bool_option)

	def test_should_expand_list_of_tasks(self):
		self.module.group1 = ['task2', 'task3']
		tasks = buildutil.parse_args(self.module, ['task1', 'group1', 'task4'])

		self.assertEqual(tasks, ['task1', 'task2', 'task3', 'task4'])

	def test_return_default_task_when_no_task_passed(self):
		self.module.default = ['task2', 'task3']
		tasks = buildutil.parse_args(self.module, [])
		self.assertEqual(tasks, ['task2', 'task3'])

	def test_should_dump_cfg(self):
		self.module.string_option = 'a value'
		self.module.int_option = 123
		self.module.bool_option = False
		self.module._private_option = 'secret'

		buildutil.dump_cfg(self.module, self.fake_cprint)

		self.assertEqual(self.get_out_lines(), [
			'  bool_option: False',
			'   int_option: 123',
			'string_option: a value'
		])

	def test_should_dump_empty_cfg(self):
		buildutil.dump_cfg(self.module, self.fake_cprint)
		self.assertEqual(self.get_out_lines(), [])

	def test_should_execute_normally(self):
		executed_tasks = []

		self.module.task1 = lambda: executed_tasks.append('task1')
		self.module.task2 = lambda: executed_tasks.append('task2')

		buildutil.run(self.module, ['task1', 'task2', '--o1', 'v1', '--o2', 'v2'], self.fake_cprint)

		self.assertEqual(executed_tasks, ['task1', 'task2'])
		self.assertEqual('v1', self.module.o1)
		self.assertEqual('v2', self.module.o2)

		self.assertEqual(self.get_out_lines(), [
			'o1: v1',
			'o2: v2',
			'Executing task1',
			'Executing task2',
			'Build Succeeded!',
		])

	def test_should_fail_execution(self):
		def task1():
			raise Exception("AHHH!!")

		self.module.task1 = task1

		with self.assertRaises(Exception) as cm:
			buildutil.run(self.module, ['task1'], self.fake_cprint)

		self.assertEqual(cm.exception.message, 'AHHH!!')

		self.assertEqual(self.get_out_lines(), [
			'Executing task1',
			'Build Failed!',
		])
