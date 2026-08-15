import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))
from unrar import UnrarArchive

TEST_ARCHIVE = os.path.join(os.path.dirname(__file__), '..', '..', 'rarfile', 'test', 'files', 'seektest.rar')

class TestUnrarWrapper(unittest.TestCase):
    def test_extract(self):
        dest = os.path.join(os.path.dirname(__file__), 'tmp')
        if os.path.isdir(dest):
            for f in os.listdir(dest):
                os.unlink(os.path.join(dest, f))
        else:
            os.makedirs(dest)
        with UnrarArchive(TEST_ARCHIVE) as arc:
            arc.extract_all(dest)
        self.assertEqual(sorted(os.listdir(dest)), ['stest1.txt', 'stest2.txt'])

if __name__ == '__main__':
    unittest.main()
