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
        completed = self.runAsSubProcess('-X 0s sleep 1')
        self.assertEqual(completed.returncode, 0)

    def test_zero_defaulttimeout(self):
        completed = self.runAsSubProcess('sleep 1')
        self.assertEqual(completed.returncode, 0)

    def test_maxinterval_true(self):
        completed = self.runAsSubProcess('true')
        self.assertEqual(completed.stdout, b'')
        self.assertEqual(completed.stderr, b'')
        self.assertEqual(completed.returncode, 0)

    def test_maxinterval_false(self):
        completed = self.runAsSubProcess('false')
        self.assertEqual(completed.stdout, b'')
        self.assertRegex(completed.stderr, b'(?i)hashfile missing')
        self.assertEqual(completed.returncode, 102)

    def test_basicmocksubprocess(self):
        with self.createMockSubprocessFile() as filename:
            self.createMockSubprocessContent(filename)
            completed = self.runAsSubProcess(filename)

    def test_maxinterval_stdout(self):
        with self.createMockSubprocessFile() as filename:
            self.createMockSubprocessContent(filename)
            completed = self.runAsSubProcess(filename)
            self.assertEqual(completed.returncode, 0)
            self.assertEqual(completed.stdout, b'')
            self.assertEqual(completed.stderr, b'')
            self.createMockSubprocessContent(filename, stdout=True)
            time.sleep(1)
            completed = self.runAsSubProcess(filename)
            self.assertEqual(completed.stdout, b'')
            self.assertRegex(completed.stderr, b'(?i)max interval')
            self.assertEqual(completed.returncode, 101)

    def test_maxinterval_stderr(self):
        with self.createMockSubprocessFile() as filename:
            self.createMockSubprocessContent(filename)
            completed = self.runAsSubProcess(filename)
            self.assertEqual(completed.returncode, 0)
            self.assertEqual(completed.stdout, b'')
            self.assertEqual(completed.stderr, b'')
            self.createMockSubprocessContent(filename, stderr=True)
            time.sleep(1)
            completed = self.runAsSubProcess(filename)
            self.assertEqual(completed.stdout, b'')
            self.assertRegex(completed.stderr, b'(?i)max interval')
            self.assertEqual(completed.returncode, 101)

    def test_maxinterval_returncode(self):
        with self.createMockSubprocessFile() as filename:
            self.createMockSubprocessContent(filename)
            completed = self.runAsSubProcess(filename)
            self.assertEqual(completed.returncode, 0)
            self.assertEqual(completed.stdout, b'')
            self.assertEqual(completed.stderr, b'')
            self.createMockSubprocessContent(filename, returncode=1)
            time.sleep(1)
            completed = self.runAsSubProcess(filename)
            self.assertEqual(completed.stdout, b'')
            self.assertRegex(completed.stderr, b'(?i)max interval')
            self.assertEqual(completed.returncode, 101)

    def test_maxinterval_explicit_returncode(self):
        with self.createMockSubprocessFile() as filename:
            self.createMockSubprocessContent(filename)
            completed = self.runAsSubProcess('-X 4s ' + filename)
            self.assertEqual(completed.returncode, 0)
            self.assertEqual(completed.stdout, b'')
            self.assertEqual(completed.stderr, b'')
            self.createMockSubprocessContent(filename, returncode=1)
            time.sleep(2)
            completed = self.runAsSubProcess('-X 4s ' + filename)
            self.assertEqual(completed.returncode, 0)
            self.assertEqual(completed.stdout, b'')
            self.assertEqual(completed.stderr, b'')
            time.sleep(3)
            completed = self.runAsSubProcess('-X 4s ' + filename)
            self.assertEqual(completed.stdout, b'')
            self.assertRegex(completed.stderr, b'(?i)max interval')
            self.assertEqual(completed.returncode, 101)