from unittest.mock import Mock, DEFAULT


class Recorder(Mock):
    """
    Mocking recorder that turns the <assert> -> <action> style to
    <record> -> <replay> style.
    """

    def __init__(self, *args, **kwgs):
        super().__init__(*args, **kwgs)
        self.side_effect = partial(Recorder.side_effect, self)

    _recording = True

    def side_effect(self, *args, **kwgs):
        if self._recording:
            return DEFAULT

        # ironically this has some serious side effects
        current_call = self.call_args_list.pop()

        if not self.call_args_list:
            # too many calls
            raise AssertionError("unexpected %r" %
                                 current_call)

        expected_call = self.call_args_list.pop(0)
        if current_call != expected_call:
            raise AssertionError("incorrect %r, expected %r" %
                                 (current_call,
                                  expected_call))

        return DEFAULT

    def record(self):
        self._recording = True

    def stop(self):
        self._recording = False

    __enter__ = record
    __exit__ = lambda self, e, v, t: self.stop()