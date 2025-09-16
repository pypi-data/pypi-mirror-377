# This file is placed in the Public Domain.


"runtime"


import logging
import queue
import threading
import time
import _thread


"event"


class Event:

    def __init__(self):
        self._ready = threading.Event()
        self._thr = None
        self.args = []
        self.channel = ""
        self.ctime = time.time()
        self.orig = ""
        self.rest = ""
        self.result = {}
        self.txt = ""
        self.type = "event"

    def done(self):
        self.reply("ok")

    def ready(self):
        self._ready.set()

    def reply(self, txt):
        self.result[time.time()] = txt

    def wait(self, timeout=None):
        try:
            self._ready.wait()
            if self._thr:
                self._thr.join()
        except (KeyboardInterrupt, EOFError):
            _thread.interrupt_main()


"handler"


class Handler:

    def __init__(self):
        self.cbs = {}
        self.queue = queue.Queue()
        self.ready = threading.Event()
        self.stopped = threading.Event()

    def available(self, event):
        return event.type in self.cbs

    def callback(self, event):
        func = self.cbs.get(event.type, None)
        if func:
            event._thr = launch(func, event, name=event.txt and event.txt.split()[0])
        else:
            event.ready()

    def loop(self):
        while not self.stopped.is_set():
            try:
                event = self.poll()
                if event is None or self.stopped.is_set():
                    break
                event.orig = repr(self)
                self.callback(event)
            except (KeyboardInterrupt, EOFError):
                _thread.interrupt_main()

    def poll(self):
        return self.queue.get()

    def put(self, event):
        self.queue.put(event)

    def register(self, typ, cbs):
        self.cbs[typ] = cbs

    def start(self, daemon=True):
        self.stopped.clear()
        launch(self.loop, daemon=daemon)

    def stop(self):
        self.stopped.set()
        self.queue.put(None)

    def wait(self):
        pass


"threads"


class Thread(threading.Thread):

    def __init__(self, func, *args, daemon=True, **kwargs):
        super().__init__(None, self.run, None, (), daemon=daemon)
        self.name = kwargs.get("name", name(func))
        self.queue = queue.Queue()
        self.result = None
        self.starttime = time.time()
        self.stopped = threading.Event()
        self.queue.put((func, args))

    def __iter__(self):
        return self

    def __next__(self):
        yield from dir(self)

    def join(self, timeout=None):
        try:
            super().join(timeout)
            return self.result
        except (KeyboardInterrupt, EOFError):
            _thread.interrupt_main()

    def run(self):
        func, args = self.queue.get()
        try:
            self.result = func(*args)
        except (KeyboardInterrupt, EOFError):
            _thread.interrupt_main()
        except Exception as ex:
            logging.exception(ex)
            _thread.interrupt_main()


"timers"


class Timy(threading.Timer):

    def __init__(self, sleep, func, *args, **kwargs):
        super().__init__(sleep, func)
        self.name = kwargs.get("name", name(func))
        self.sleep = sleep
        self.state = {}
        self.state["latest"] = time.time()
        self.state["starttime"] = time.time()
        self.starttime = time.time()


class Timed:

    def __init__(self, sleep, func, *args, thrname="", **kwargs):
        self.args = args
        self.func = func
        self.kwargs = kwargs
        self.sleep = sleep
        self.name = thrname or kwargs.get("name", name(func))
        self.target = time.time() + self.sleep
        self.timer = None

    def run(self):
        self.timer.latest = time.time()
        self.func(*self.args)

    def start(self):
        self.kwargs["name"] = self.name
        timer = Timy(self.sleep, self.run, *self.args, **self.kwargs)
        timer.start()
        self.timer = timer

    def stop(self):
        if self.timer:
            self.timer.cancel()


class Repeater(Timed):

    def run(self):
        launch(self.start)
        super().run()


"utilities"


def launch(func, *args, **kwargs):
    thread = Thread(func, *args, **kwargs)
    thread.start()
    return thread


def name(obj):
    typ = type(obj)
    if "__builtins__" in dir(typ):
        return obj.__name__
    if "__self__" in dir(obj):
        return f"{obj.__self__.__class__.__name__}.{obj.__name__}"
    if "__class__" in dir(obj) and "__name__" in dir(obj):
        return f"{obj.__class__.__name__}.{obj.__name__}"
    if "__class__" in dir(obj):
        return f"{obj.__class__.__module__}.{obj.__class__.__name__}"
    if "__name__" in dir(obj):
        return f"{obj.__class__.__name__}.{obj.__name__}"
    return ""


"interface"


def __dir__():
    return (
        'Event',
        'Handler',
        'Output',
        'Repeater',
        'Thread',
        'Timed',
        'launch',
        'name'
   )
