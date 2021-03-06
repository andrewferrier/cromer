import os
import tempfile
import time

from tests.BaseTestClasses import CromerTestCase

TEST_ACCURACY_THRESHOLD = 0.4


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

    def test_simple_true_debug_syslogging(self):
        completed = self.runAsSubProcess('-d true')
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

    def test_pathenv(self):
        with self.createMockFile() as filename:
            self.createMockSubprocessContent(filename)
            completed = self.runAsSubProcess(os.path.basename(filename), path_env=(
                os.environ['PATH'] + ":" + os.path.dirname(filename)))
            self.assertEqual(completed.stdout, b'')
            self.assertEqual(completed.stderr, b'')
            self.assertEqual(completed.returncode, 0)
            completed = self.runAsSubProcess(os.path.basename(filename))
            self.assertEqual(completed.stdout, b'')
            self.assertRegex(completed.stderr, b'No such file or directory')
            self.assertEqual(completed.returncode, 1)

    def test_timeout(self):
        a = self.get_time_in_seconds()
        completed = self.runAsSubProcess('sleep 2')
        b = self.get_time_in_seconds()
        self.assertEqual(completed.returncode, 0)
        self.assertAlmostEqual(a + 2, b, delta=TEST_ACCURACY_THRESHOLD)
        completed = self.runAsSubProcess('-t 1s sleep 2')
        c = self.get_time_in_seconds()
        self.assertAlmostEqual(b + 1, c, delta=TEST_ACCURACY_THRESHOLD)
        self.assertEqual(completed.returncode, 101)

    def test_timeout_swallow_sigterm(self):
        with self.createMockFile() as filename:
            self.createMockSubprocessContent(filename)
            completed = self.runAsSubProcess(filename)
            self.assertEqual(completed.returncode, 0)
            self.assertEqual(completed.stdout, b'')
            self.assertEqual(completed.stderr, b'')
            self.createSwallowSigTerm(filename)
            a = self.get_time_in_seconds()
            completed = self.runAsSubProcess('-t 1s ' + filename)
            b = self.get_time_in_seconds()
            self.assertAlmostEqual(a + 1, b, delta=TEST_ACCURACY_THRESHOLD)
            self.assertEqual(completed.returncode, 101)

    def test_timeout_with_loop_command(self):
        with self.createMockFile() as filename:
            with tempfile.NamedTemporaryFile() as outputfile:
                self.createLoopCommand(filename, outputfile.name)
                completed = self.runAsSubProcess(filename)
                self.assertEqual(completed.returncode, 0)
                self.assertEqual(completed.stdout, b'')
                self.assertEqual(completed.stderr, b'')
                self.assertEqual(self.get_file_contents(outputfile.name), "123")
                a = self.get_time_in_seconds()
                completed = self.runAsSubProcess('-X 1m -t 2s ' + filename)
                b = self.get_time_in_seconds()
                self.assertEqual(completed.returncode, 0)
                self.assertEqual(completed.stdout, b'')
                self.assertEqual(completed.stderr, b'')
                self.assertEqual(self.get_file_contents(outputfile.name), "1231")
                self.assertAlmostEqual(a + 2, b, delta=TEST_ACCURACY_THRESHOLD)

    def test_timeout_with_loop_command_to_stdout(self):
        with self.createMockFile() as filename:
            with tempfile.NamedTemporaryFile() as outputfile:
                self.createLoopCommand(filename, outputfile.name)
                completed = self.runAsSubProcess(filename)
                self.assertEqual(completed.returncode, 0)
                self.assertEqual(completed.stdout, b'')
                self.assertEqual(completed.stderr, b'')
                self.assertEqual(self.get_file_contents(outputfile.name), "123")
                self.createLoopCommand(filename, None)
                a = self.get_time_in_seconds()
                completed = self.runAsSubProcess('-t 2s ' + filename)
                b = self.get_time_in_seconds()
                self.assertEqual(completed.returncode, 101)
                self.assertEqual(completed.stdout, b'')
                self.assertRegex(completed.stderr, b'timed out')
                self.assertRegex(completed.stderr, b'b\'1\'')
                self.assertAlmostEqual(a + 2, b, delta=TEST_ACCURACY_THRESHOLD)

    def test_timeout_junk(self):
        completed = self.runAsSubProcess('-t blah sleep 2')
        self.assertRegex(completed.stderr, b'(?i)time interval must be of type')
        self.assertEqual(completed.returncode, 2)

    def test_zerotimeout(self):
        a = self.get_time_in_seconds()
        completed = self.runAsSubProcess('-t 0s sleep 1')
        b = self.get_time_in_seconds()
        self.assertAlmostEqual(a + 1, b, delta=TEST_ACCURACY_THRESHOLD)
        self.assertEqual(completed.returncode, 0)

    def test_zero_defaulttimeout(self):
        a = self.get_time_in_seconds()
        completed = self.runAsSubProcess('sleep 1')
        b = self.get_time_in_seconds()
        self.assertAlmostEqual(a + 1, b, delta=TEST_ACCURACY_THRESHOLD)
        self.assertEqual(completed.returncode, 0)

    def test_basicmocksubprocess(self):
        with self.createMockFile() as filename:
            self.createMockSubprocessContent(filename)
            self.runAsSubProcess(filename)

    def test_maxinterval_stdout(self):
        with self.createMockFile() as filename:
            self.createMockSubprocessContent(filename)
            completed = self.runAsSubProcess(filename)
            self.assertEqual(completed.returncode, 0)
            self.assertEqual(completed.stdout, b'')
            self.assertEqual(completed.stderr, b'')
            self.createMockSubprocessContent(filename, stdout=True)
            completed = self.runAsSubProcess(filename)
            self.assertEqual(completed.stdout, b'')
            self.assertRegex(completed.stderr, b'(?i)max interval')
            self.assertEqual(completed.returncode, 101)

    def test_maxinterval_stderr(self):
        with self.createMockFile() as filename:
            self.createMockSubprocessContent(filename)
            completed = self.runAsSubProcess(filename)
            self.assertEqual(completed.returncode, 0)
            self.assertEqual(completed.stdout, b'')
            self.assertEqual(completed.stderr, b'')
            self.createMockSubprocessContent(filename, stderr=True)
            completed = self.runAsSubProcess(filename)
            self.assertEqual(completed.stdout, b'')
            self.assertRegex(completed.stderr, b'(?i)max interval')
            self.assertEqual(completed.returncode, 101)

    def test_maxinterval_returncode(self):
        with self.createMockFile() as filename:
            self.createMockSubprocessContent(filename)
            completed = self.runAsSubProcess(filename)
            self.assertEqual(completed.returncode, 0)
            self.assertEqual(completed.stdout, b'')
            self.assertEqual(completed.stderr, b'')
            self.createMockSubprocessContent(filename, returncode=1)
            completed = self.runAsSubProcess(filename)
            self.assertEqual(completed.stdout, b'')
            self.assertRegex(completed.stderr, b'(?i)max interval')
            self.assertEqual(completed.returncode, 101)

    def test_maxinterval_explicit_returncode(self):
        with self.createMockFile() as filename:
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
        with self.createMockFile() as filename:
            self.createMockSubprocessContent(filename)
            completed = self.runAsSubProcess('-r ' + filename)
            self.assertEqual(completed.returncode, 0)
            self.assertEqual(completed.stdout, b'')
            self.assertEqual(completed.stderr, b'')
            self.createMockSubprocessContent(filename, stdout=True)
            completed = self.runAsSubProcess('-r ' + filename)
            self.assertEqual(completed.stdout, b'')
            self.assertRegex(completed.stderr, b'(?i)max interval')
            self.assertEqual(completed.returncode, 101)

    def test_lock(self):
        with self.createMockFile() as filename:
            self.createMockSubprocessContent(filename, delay=4)
            self.runAsSubProcess(filename, wait=True)
            completed1 = self.runAsSubProcess(filename, wait=False)
            # The sleep is necessary to ensure the lock is taken, otherwise
            # sometimes the second process gets it first.
            time.sleep(2)
            completed2 = self.runAsSubProcess(filename, wait=True)
            self.assertEqual(completed2.stdout, b'')
            self.assertRegex(completed2.stderr, b'(?i)within timeout period but not success interval')
            self.assertEqual(completed2.returncode, 108)
            self.assertIsNone(completed1.poll())
            completed1.wait()
            self.assertEqual(completed1.returncode, 0)

    def test_lock_and_restore(self):
        with self.createMockFile() as filename:
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
            self.assertRegex(completed2.stderr, b'(?i)within timeout period but not success interval')
            self.assertEqual(completed2.returncode, 108)
            self.assertEqual(completed3.stdout, b'')
            self.assertEqual(completed3.stderr, b'')
            self.assertEqual(completed3.returncode, 0)
            completed1.wait()
            self.assertEqual(completed1.returncode, 0)

    def test_lock_with_maxinterval(self):
        with self.createMockFile() as filename:
            self.createMockSubprocessContent(filename, delay=4)
            self.runAsSubProcess('-X 1m ' + filename, wait=True)
            completed1 = self.runAsSubProcess('-X 1m ' + filename, wait=False)
            # The sleep is necessary to ensure the lock is taken, otherwise
            # sometimes the second process gets it first.
            time.sleep(2)
            completed2 = self.runAsSubProcess('-X 1m ' + filename, wait=True)
            self.assertIsNone(completed1.poll())
            self.assertEqual(completed2.stdout, b'')
            self.assertRegex(completed2.stderr, b'(?i)within success interval')
            self.assertEqual(completed2.returncode, 104)
            completed1.wait()
            self.assertEqual(completed1.returncode, 0)

    def test_runtwice_exit_trapped(self):
        with self.createMockFile() as filename:
            self.createMockSubprocessContent(filename, delay=999, trapexit=True)
            process1 = self.runAsSubProcess('-vv -l -X 7s -t 4s ' + filename, wait=False)
            time.sleep(10)
            # Assert that it's still running (because timeout has been trapped)
            self.assertIsNone(process1.poll())
            self.createMockSubprocessContent(filename, delay=2)
            a = self.get_time_in_seconds()
            process2 = self.runAsSubProcess('-vv -X 7s -t 4s ' + filename, wait=True)
            b = self.get_time_in_seconds()
            self.assertEqual(process2.returncode, 107)
            self.assertRegex(process2.stderr, b'(?i)never run successfully.*overlapping')
            self.assertAlmostEqual(a, b, delta=TEST_ACCURACY_THRESHOLD)

    def test_runtwice_exit_trapped_with_prior_success(self):
        with self.createMockFile() as filename:
            self.createMockSubprocessContent(filename)
            self.runAsSubProcess('-X 7s -t 4s ' + filename, wait=True)
            self.createMockSubprocessContent(filename, delay=999, trapexit=True)
            process1 = self.runAsSubProcess('-X 7s -t 4s ' + filename, wait=False)
            time.sleep(10)
            # Assert that it's still running (because timeout has been trapped)
            self.assertIsNone(process1.poll())
            self.createMockSubprocessContent(filename, delay=2)
            process2 = self.runAsSubProcess('-vv -X 7s -t 4s ' + filename, wait=True)
            self.assertEqual(process2.returncode, 106)
            self.assertRegex(process2.stderr, b'(?i)cannot kill')
