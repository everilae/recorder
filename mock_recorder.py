from unittest.mock import Mock, DEFAULT


class Recorder(Mock):
    """
    Mocking recorder that turns the <assert> -> <action> style to
    <record> -> <replay> style.

    >>> r = Recorder()
    >>> with r:
    ...     ret = r(1, 2, 3)
    ...
    >>> r(1, 2, 3) is ret
    True
    >>> with r:
    ...     ret = r(1, 2, 3)
    ...
    >>> r(2, 3, 4)
    Traceback (most recent call last):
        ...
    AssertionError: incorrect call(2, 3, 4), expected call(1, 2, 3)
    >>> r(1, 2, 3)
    Traceback (most recent call last):
        ...
    AssertionError: unexpected call(1, 2, 3)
    """

    _recording = True

    def __call__(self, *args, **kwgs):
        retval = super(Recorder, self).__call__(*args, **kwgs)
        if self._recording:
            return retval

        # ironically this has some serious side effects
        current_call = self.call_args_list.pop()

        if not self.call_args_list:
            # too many calls
            raise AssertionError("unexpected %r" %
                                 (current_call, ))

        expected_call = self.call_args_list.pop(0)
        if current_call != expected_call:
            raise AssertionError("incorrect %r, expected %r" %
                                 (current_call,
                                  expected_call))

        return retval

    def record(self):
        self._recording = True
        return self

    def stop(self):
        self._recording = False

    __enter__ = record
    __exit__ = lambda self, e, v, t: self.stop()
