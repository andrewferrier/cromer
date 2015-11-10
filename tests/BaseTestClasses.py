import unittest
import os
from subprocess import Popen, PIPE

import subprocess


class CromerTestCase(unittest.TestCase):
    COMMAND = os.path.normpath(os.path.join(os.getcwd(), 'cromer'))

    def setUp(self):
        pass

    def runAsSubProcess(self, args):
        return subprocess.run(CromerTestCase.COMMAND + ' ' + args, shell=True, stdout=PIPE, stderr=PIPE)
