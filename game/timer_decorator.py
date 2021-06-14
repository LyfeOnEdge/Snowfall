import time
def timer_dec(proc):
    def t(*args, **kw):
        start = time.time()
        res = proc(*args, **kw)
        stop = time.time()
        print('%r  %2.2f ms' % (proc.__name__, (stop - start) * 1000))
        return res
    return t