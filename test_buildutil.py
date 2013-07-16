import unittest, buildutil

class TestModule:
	pass

class TestSequenceFunctions(unittest.TestCase):
	def setUp(self):
		self.sut = range(10)

	def test_should_parse_args(self):
		module = TestModule()

		tasks = buildutil.parse_args(module, ['t1', '--opt1', 'v1', 't2', 't3'])

		self.assertEqual(tasks, ['t1', 't2', 't3'])
