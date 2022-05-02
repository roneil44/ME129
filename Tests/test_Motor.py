import unittest
from Codebase.Motor import *

class TestMotor(unittest.TestCase):

    def test_setvel(self):
        x = Motor("motors", 7, 8, 5, 6, 254, 1000)
        