class Recorder(mock.Mock):
    def __init__(self, *args, **kwgs):
        super().__init__(*args, **kwgs)
        self.side_effect = partial(Recorder.side_effect, self)

    _recording = True

    def side_effect(self, *args, **kwgs):
        # ironically this if statement has some serious side effects
        if not self._recording and (not self.call_args_list or
                                    self.call_args_list.pop(0) !=
                                    self.call_args_list.pop()):
            raise RuntimeError("incorrect call", args, kwgs)
            
        return mock.DEFAULT
        
    def record(self):
        self._recording = True
        
    def stop(self):
        self._recording = False
        
    __enter__ = record
    __exit__ = lambda self, e, v, t: self.stop()