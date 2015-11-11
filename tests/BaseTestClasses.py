import os
import shutil
import subprocess
import tempfile
import unittest

from subprocess import Popen, PIPE

class CromerTestCase(unittest.TestCase):
    COMMAND = os.path.normpath(os.path.join(os.getcwd(), 'cromer'))

    def setUp(self):
        self.fake_user_dir = tempfile.mkdtemp(dir='/tmp')

    def runAsSubProcess(self, args):
        my_env = os.environ.copy()
        my_env['HOME'] = self.fake_user_dir
        return subprocess.run(CromerTestCase.COMMAND + ' ' + args, shell=True, stdout=PIPE, stderr=PIPE, env=my_env)

    def tearDown(self):
        shutil.rmtree(self.fake_user_dir)
