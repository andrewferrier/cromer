import os
import shutil
import subprocess
import tempfile
import time
import unittest

from contextlib import contextmanager
from stat import S_IRUSR, S_IWUSR, S_IXUSR
from string import Template


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
    def createMockFile(self):
        # In one sense this is "insecure" - however it really isn't an issue
        # in this case - the directory being used is used only for this
        # testing and is wiped at the end of a test run.
        file_h = tempfile.NamedTemporaryFile(delete=False, dir=self.fake_user_dir)
        file_h.close()
        yield file_h.name
        os.remove(file_h.name)

    def createMockSubprocessContent(self, filename, stdout=False, stderr=False, returncode=0, delay=0):
        with open(filename, 'w') as fp:
            fp.write('#!/bin/sh\n')
            if stdout:
                fp.write('echo "Stdout content"\n')
            if stderr:
                fp.write('>&2 echo "Stderr content"\n')
            if delay != 0:
                fp.write('sleep ' + str(delay) + "\n")
            fp.write('exit ' + str(returncode) + "\n")
        os.chmod(filename, S_IRUSR | S_IWUSR | S_IXUSR)

    def createSwallowSigTerm(self, filename):
        with open(filename, 'w') as fp:
            fp.write('#!/usr/bin/env python3\n')
            fp.write('import signal\n')
            fp.write('signal.signal(signal.SIGTERM, signal.SIG_IGN)\n')
            fp.write('while True:\n')
            fp.write('    pass\n')
        os.chmod(filename, S_IRUSR | S_IWUSR | S_IXUSR)

    def createLoopCommand(self, filename, outputfilename=None):
        LOOP_COMMAND = 'for i in `seq 1 3`; do sleep 1; echo -n $$i $outputfile; done'

        if outputfilename:
            loopCommandFinal = Template(LOOP_COMMAND).substitute({'outputfile': '>> ' + outputfilename})
        else:
            loopCommandFinal = Template(LOOP_COMMAND).substitute({'outputfile': ''})

        with open(filename, 'w') as fp:
            fp.write('#!/bin/bash\n')
            fp.write(loopCommandFinal)
        os.chmod(filename, S_IRUSR | S_IWUSR | S_IXUSR)

    def get_time_in_seconds(self):
        return time.perf_counter()

    def get_file_contents(self, filename):
        with open(filename, "r") as myfile:
            return myfile.read()

    def tearDown(self):
        shutil.rmtree(self.fake_user_dir)
