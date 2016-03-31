
from __future__ import print_function

from multiprocessing import Process, Pipe, Lock
import sys
import time
import traceback

l = Lock()

def locked_print(*args):
    l.acquire()

    try:
        print(file=sys.stderr, *args)
    finally:
        l.release()

def a():
    v = yield
    locked_print('a', v)
    while True:
        v = yield -v + 1
        locked_print('a', v)

def b():
    v = yield -1
    locked_print('b', v)
    for x in range(10):
        v = yield -v - 1
        locked_print('b', v)
    yield Parallel(-v - 1)
    for x in range(100):
        v = yield Parallel(-v - 1)
        locked_print('b', v)

    v = 0
    yield v
    for x in range(100):
        v = yield -v - 1
        locked_print('b', v)


class Parallel(object):
    def __init__(self, arg):
        self.arg = arg

def pipeyield(iterator, pipe, start=False):
    v = iterator.next()
    if not start and v is not None:
        pipe.close()
        raise ValueError("Waiting chain should not send first value")
    try:

        parallel = 0

        if start:
            pipe.send(v)

        while True:

            if parallel != 1:
                r = pipe.recv()
                if r == "QUIT":
                    return 0

            v = iterator.send(r)

            if v is Parallel or isinstance(v, Parallel):
                parallel += 1
                r = None
                v = v.arg if isinstance(v, Parallel) else None
            else:
                if parallel:
                    r = pipe.recv()
                parallel = 0

            pipe.send(v)

    except StopIteration:
        pipe.send("QUIT")
        return 0
    except Exception as e:
        traceback.print_exc()
        pipe.send("QUIT")
        return 1


def main():
    apipe, bpipe = Pipe()
    p = Process(target=pipeyield, args=(a(), apipe))
    p.start()
    pipeyield(b(), bpipe, start=True)
    p.join()

if __name__ == "__main__":
    main()
