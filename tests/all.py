from __future__ import print_function

from multiprocessing import Process, Pipe, Lock
import unittest
import sys

from pipeyield import Parallel, pipeyield

DEBUG = 0
if DEBUG:
    l = Lock()

    def locked_print(*args):
        l.acquire()

        try:
            print(file=sys.stderr, *args)
        finally:
            l.release()
else:
    def locked_print(*args):
        pass

def a():
    v = yield
    locked_print('a', v)
    while True:
        v = yield -v + 1
        locked_print('a', v)

def b():
    v = yield 0
    locked_print('b', v)
    for x in range(10):
        v = yield -v - 1
        locked_print('b', v)

    assert v == 21

    yield Parallel(-v - 1)
    for x in range(10):
        v = yield Parallel(-v - 1)
        locked_print('b', v)

    assert v == 31

    v = yield 0
    for x in range(10):
        v = yield -v - 1
        locked_print('b', v)

    assert v == 21

class TestAll(unittest.TestCase):
    def test_all(self):
        apipe, bpipe = Pipe()
        p = Process(target=pipeyield, args=(a(), apipe))
        p.start()
        assert 0 == pipeyield(b(), bpipe, start=True)
        p.join()

if __name__ == "__main__":
    unittest.main()
