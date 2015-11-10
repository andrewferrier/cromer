from tests.BaseTestClasses import CromerTestCase


class TestBasic(CromerTestCase):
    def setUp(self):
        super(TestBasic, self).setUp()

    def test_simple(self):
        completed = self.runAsSubProcess('-X 1s -t 2s echo "Hello"')
        self.assertRegex(completed.stdout, b'Hello')
        self.assertEqual(completed.stderr, b'')
        self.assertEqual(completed.returncode, 0)

    def test_nohashfile(self):
        completed = self.runAsSubProcess('-X 1s false')
        self.assertRegex(completed.stderr, b'(?i)hashfile missing')
        self.assertEqual(completed.returncode, 102)

    def test_timeout(self):
        completed = self.runAsSubProcess('-X 1s sleep 3')
        self.assertEqual(completed.returncode, 0)
        completed = self.runAsSubProcess('-X 1s -t 2s sleep 3')
        self.assertEqual(completed.returncode, 101)
