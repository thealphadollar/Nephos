"""
Source: https://github.com/pycontribs/tendo/blob/master/tendo/singleton.py
"""
from unittest import TestCase
import sys
from multiprocessing import Process
from nephos.maintenance.single_instance import SingleInstance, SingleInstanceException


def func(name):
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
        proc = Process(target=func, args=("test-2",))
        proc.start()
        proc.join()
        # the called function should succeed
        assert proc.exitcode == 0, "%s != 0" % proc.exitcode

    def test_error_process_instantiation(self):
        me = SingleInstance(flavor_id="test-3")  # noqa -- me should still kept
        proc = Process(target=func, args=("test-3",))
        proc.start()
        proc.join()
        # the called function should fail because we already have another
        # instance running
        assert proc.exitcode != 0, "%s != 0 (2nd execution)" % proc.exitcode
        del me
