"""
Source: https://github.com/pycontribs/tendo/blob/master/tendo/singleton.py
"""
from unittest import TestCase
import sys
from multiprocessing import Process
from nephos.maintenance.single_instance import SingleInstance, SingleInstanceException


def f(name):
    try:
        me2 = SingleInstance(flavor_id=name)
        del me2
    except SingleInstanceException:
        sys.exit(-1)


class TestSingleton(TestCase):

    def test_simple_instantiation(self):
        me = SingleInstance(flavor_id="test-1")
        del me  # now the lock should be removed
        assert True

    def test_simple_process_instantiation(self):
        p = Process(target=f, args=("test-2",))
        p.start()
        p.join()
        # the called function should succeed
        assert p.exitcode == 0, "%s != 0" % p.exitcode

    def test_error_process_instantiation(self):
        me = SingleInstance(flavor_id="test-3")  # noqa -- me should still kept
        p = Process(target=f, args=("test-3",))
        p.start()
        p.join()
        # the called function should fail because we already have another
        # instance running
        assert p.exitcode != 0, "%s != 0 (2nd execution)" % p.exitcode
        del me
