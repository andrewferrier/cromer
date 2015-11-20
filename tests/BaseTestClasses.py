import os
import shutil
import subprocess
import tempfile
import unittest

from contextlib import contextmanager
from stat import S_IRUSR, S_IWUSR, S_IXUSR
from subprocess import PIPE


class CromerTestCase(unittest.TestCase):
    COMMAND = os.path.normpath(os.path.join(os.getcwd(), 'cromer'))

    def setUp(self):
        self.fake_user_dir = tempfile.mkdtemp(dir='/tmp')

    def runAsSubProcess(self, args):
        class SubprocessRunPython35Simulator():
            def __init__(self, returncode, output, error):
                self.returncode = returncode
                self.stdout = output
                self.stderr = error

        my_env = os.environ.copy()
        my_env['HOME'] = self.fake_user_dir
        my_process = subprocess.Popen(CromerTestCase.COMMAND + ' ' + args, shell=True, stdout=PIPE, stderr=PIPE, env=my_env)
        output, error = my_process.communicate()
        my_process.wait()
        return SubprocessRunPython35Simulator(my_process.returncode, output, error)

    @contextmanager
    def createMockSubprocessFile(self, stdout=False, stderr=False, returncode=0):
        (fp, name) = tempfile.mkstemp(suffix='.sh', dir=self.fake_user_dir)
        yield name
        os.remove(name)

    def createMockSubprocessContent(self, filename, stdout=False, stderr=False, returncode=0):
        with open(filename, 'w') as fp:
            fp.write('#!/bin/sh\n')
            if stdout:
                fp.write('echo "Stdout content"\n')
            if stderr:
                fp.write('echo "Stderr content"\n')
            fp.write('exit ' + str(returncode) + "\n")
        os.chmod(filename, S_IRUSR | S_IWUSR | S_IXUSR)

    def tearDown(self):
        shutil.rmtree(self.fake_user_dir)
