import os
import shutil
import subprocess
import tempfile
import unittest

from contextlib import contextmanager
from stat import S_IRUSR, S_IWUSR, S_IXUSR


class CromerTestCase(unittest.TestCase):
    COMMAND = os.path.normpath(os.path.join(os.getcwd(), 'cromer'))

    def setUp(self):
        self.fake_user_dir = tempfile.mkdtemp(dir='/tmp')

    def runAsSubProcess(self, args, wait=True):
        class SubprocessRunPython35Simulator():
            def __init__(self, returncode, output, error):
                self.returncode = returncode
                self.stdout = output
                self.stderr = error

        my_env = os.environ.copy()
        my_env['HOME'] = self.fake_user_dir
        my_process = subprocess.Popen(CromerTestCase.COMMAND + ' ' + args,
                                      shell=True,
                                      stdout=(subprocess.PIPE if wait else subprocess.DEVNULL),
                                      stderr=(subprocess.PIPE if wait else subprocess.DEVNULL),
                                      env=my_env)

        if wait:
            output, error = my_process.communicate()
            my_process.wait()
            return SubprocessRunPython35Simulator(my_process.returncode, output, error)
        else:
            return my_process

    @contextmanager
    def createMockSubprocessFile(self):
        # In one sense this is "insecure" - however it really isn't an issue
        # in this case - the directory being used is used only for this
        # testing and is wiped at the end of a test run.
        file_h = tempfile.NamedTemporaryFile(delete=False, suffix='.sh', dir=self.fake_user_dir)
        file_h.close()
        yield file_h.name
        os.remove(file_h.name)

    def createMockSubprocessContent(self, filename, stdout=False, stderr=False, returncode=0, delay=0):
        with open(filename, 'w') as fp:
            fp.write('#!/bin/sh\n')
            if stdout:
                fp.write('echo "Stdout content"\n')
            if stderr:
                fp.write('echo "Stderr content"\n')
            if delay != 0:
                fp.write('sleep ' + str(delay) + "\n")
            fp.write('exit ' + str(returncode) + "\n")
        os.chmod(filename, S_IRUSR | S_IWUSR | S_IXUSR)

    def tearDown(self):
        shutil.rmtree(self.fake_user_dir)
