from tests.BaseTestClasses import CromerTestCase

import time


class TestBasic(CromerTestCase):
    def setUp(self):
        super(TestBasic, self).setUp()

    def test_simple_true(self):
        completed = self.runAsSubProcess('-X 1s true')
        self.assertEqual(completed.stdout, b'')
        self.assertEqual(completed.stderr, b'')
        self.assertEqual(completed.returncode, 0)

    def test_simple_true_quieten(self):
        completed = self.runAsSubProcess('-X 1s -q echo "Hello"')
        self.assertEqual(completed.stdout, b'')
        self.assertEqual(completed.stderr, b'')
        self.assertEqual(completed.returncode, 0)

    def test_simple_false(self):
        completed = self.runAsSubProcess('-X 1s false')
        self.assertEqual(completed.stdout, b'')
        self.assertRegex(completed.stderr, b'(?i)hashfile missing')
        self.assertEqual(completed.returncode, 102)

    def test_timeout(self):
        completed = self.runAsSubProcess('-X 1s sleep 3')
        self.assertEqual(completed.returncode, 0)
        completed = self.runAsSubProcess('-X 1s -t 2s sleep 3')
        self.assertEqual(completed.returncode, 101)

    def test_zerotimeout(self):
        completed = self.runAsSubProcess('-X 0s sleep 2')
        self.assertEqual(completed.returncode, 0)

    def test_zero_defaulttimeout(self):
        completed = self.runAsSubProcess('sleep 2')
        self.assertEqual(completed.returncode, 0)

    def test_basicmocksubprocess(self):
        with self.createMockSubprocessFile() as filename:
            self.createMockSubprocessContent(filename)
            completed = self.runAsSubProcess(filename)
