
import traceback

class Parallel(object):
    def __init__(self, arg):
        self.arg = arg

def pipeyield(iterator, pipe, start=False):
    """
    Execute chain of events represented as an iterator, sending yielded values
    through the pipes.

    Think of this as of yield-generated coroutines executed in the different
    processes.

    The chain is first executed until the first yield and then the yielded
    value is sent to the remote chain where it is pushed into as a value
    returned by yield.

    Whenever a process yields a `Parallel` class or its instance the parallel
    execution of coroutines starts. For this the value is sent to the remote
    end and both local and remote execution continues to the next yield.
    Note that only one coroutine is allowed to start `Parallel` execution.

    The values generated as responses to the `Parallel` start or finish are
    ignored.
    """
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
                    raise StopIteration

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
