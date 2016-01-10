import time

from tests.BaseTestClasses import CromerTestCase


class TestBasic(CromerTestCase):
    def setUp(self):
        super(TestBasic, self).setUp()

    def test_simple_true(self):
        completed = self.runAsSubProcess('true')
        self.assertEqual(completed.stdout, b'')
        self.assertEqual(completed.stderr, b'')
        self.assertEqual(completed.returncode, 0)

    def test_simple_true_syslogging(self):
        completed = self.runAsSubProcess('-l true')
        self.assertEqual(completed.stdout, b'')
        self.assertEqual(completed.stderr, b'')
        self.assertEqual(completed.returncode, 0)

    def test_simple_true_quieten(self):
        completed = self.runAsSubProcess('-q echo "Hello"')
        self.assertEqual(completed.stdout, b'')
        self.assertEqual(completed.stderr, b'')
        self.assertEqual(completed.returncode, 0)

    def test_simple_false(self):
        completed = self.runAsSubProcess('false')
        self.assertEqual(completed.stdout, b'')
        self.assertRegex(completed.stderr, b'(?i)hashfile missing')
        self.assertEqual(completed.returncode, 102)

    def test_noargs(self):
        completed = self.runAsSubProcess('')
        self.assertEqual(completed.stdout, b'')
        self.assertRegex(completed.stderr, b'(?i)you must provide')
        self.assertEqual(completed.returncode, 103)

    def test_timeout(self):
        completed = self.runAsSubProcess('sleep 2')
        self.assertEqual(completed.returncode, 0)
        completed = self.runAsSubProcess('-t 1s sleep 2')
        self.assertEqual(completed.returncode, 101)

    def test_timeout_junk(self):
        completed = self.runAsSubProcess('-t blah sleep 2')
        self.assertRegex(completed.stderr, b'(?i)time interval must be of type')
        self.assertEqual(completed.returncode, 2)

    def test_zerotimeout(self):
        completed = self.runAsSubProcess('-t 0s sleep 1')
        self.assertEqual(completed.returncode, 0)

    def test_zero_defaulttimeout(self):
        completed = self.runAsSubProcess('sleep 1')
        self.assertEqual(completed.returncode, 0)

    def test_basicmocksubprocess(self):
        with self.createMockSubprocessFile() as filename:
            self.createMockSubprocessContent(filename)
            self.runAsSubProcess(filename)

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

    def test_maxinterval_readable(self):
        with self.createMockSubprocessFile() as filename:
            self.createMockSubprocessContent(filename)
            completed = self.runAsSubProcess('-r ' + filename)
            self.assertEqual(completed.returncode, 0)
            self.assertEqual(completed.stdout, b'')
            self.assertEqual(completed.stderr, b'')
            self.createMockSubprocessContent(filename, stdout=True)
            time.sleep(1)
            completed = self.runAsSubProcess('-r ' + filename)
            self.assertEqual(completed.stdout, b'')
            self.assertRegex(completed.stderr, b'(?i)max interval')
            self.assertEqual(completed.returncode, 101)

    def test_lock(self):
        with self.createMockSubprocessFile() as filename:
            self.createMockSubprocessContent(filename, delay=4)
            self.runAsSubProcess(filename, wait=True)
            completed1 = self.runAsSubProcess(filename, wait=False)
            # The sleep is necessary to ensure the lock is taken, otherwise
            # sometimes the second process gets it first.
            time.sleep(2)
            completed2 = self.runAsSubProcess(filename, wait=True)
            self.assertIsNone(completed1.poll())
            self.assertEqual(completed2.stdout, b'')
            self.assertRegex(completed2.stderr, b'(?i)already running')
            self.assertEqual(completed2.returncode, 104)
            completed1.wait()
            self.assertEqual(completed1.returncode, 0)

    def test_lock_and_restore(self):
        with self.createMockSubprocessFile() as filename:
            self.createMockSubprocessContent(filename, delay=4)
            self.runAsSubProcess(filename, wait=True)
            completed1 = self.runAsSubProcess(filename, wait=False)
            # The sleep is necessary to ensure the lock is taken, otherwise
            # sometimes the second process gets it first.
            time.sleep(2)
            completed2 = self.runAsSubProcess(filename, wait=True)
            self.assertIsNone(completed1.poll())
            time.sleep(3)
            self.assertEqual(completed1.poll(), 0)
            completed3 = self.runAsSubProcess(filename, wait=True)
            self.assertEqual(completed2.stdout, b'')
            self.assertRegex(completed2.stderr, b'(?i)already running')
            self.assertEqual(completed2.returncode, 104)
            self.assertEqual(completed3.stdout, b'')
            self.assertEqual(completed3.stderr, b'')
            self.assertEqual(completed3.returncode, 0)
            completed1.wait()
            self.assertEqual(completed1.returncode, 0)
