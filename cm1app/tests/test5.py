import unittest,sys
sys.path.append('..')
from particle import coreid2nodeid


class TestPEStuff(unittest.TestCase):

    def test_PEConfig(self):
        self.assertTrue('node-046' == coreid2nodeid('360064001951343334363036'))


if __name__ == '__main__':
    unittest.main()
