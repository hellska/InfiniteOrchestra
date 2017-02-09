import pytest
import sys
sys.path.append('/Volumes/ssdData/virtualenv/InfiniteOrchestra/InfiniteOrchestra')
import freesoundscapes as fss

class TestInfiniteOrc:

    def test_connect_db(self):
        assert False

    def test_read_ini_file(self):
        # if no pid is returned
        assert fss.read_ini_file() == 888
        # if an error block file open
        assert fss.read_ini_file() == 999
        # pid found in config file
        assert fss.read_ini_file() > 0