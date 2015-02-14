from unittest.mock import Mock, patch as _patch
from functools import partial


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
    AssertionError: Expected call: mock(1, 2, 3)
    Actual call: mock(2, 3, 4)
    >>> r(1, 2, 3)
    Traceback (most recent call last):
        ...
    AssertionError: Unexpected call: mock(1, 2, 3)
    """

    _recording = True

    def _recorder_check_call(self):
        """
        Check that a call to self matches recorded calls.
        """
        current_call = self.call_args_list.pop()
        current_call_string = self._format_mock_call_signature(*current_call)

        if not self.call_args_list:
            # too many calls
            raise AssertionError("Unexpected call: %s" %
                                 (current_call_string, ))

        expected_call = self.call_args_list.pop(0)
        expected_call_string = self._format_mock_call_signature(*expected_call)

        current_call_key = self._call_matcher(current_call)
        expected_call_key = self._call_matcher(expected_call)
        if current_call_key != expected_call_key:
            raise AssertionError("Expected call: %s\nActual call: %s" %
                                 (expected_call_string,
                                  current_call_string))

    def __call__(self, *args, **kwgs):
        retval = super(Recorder, self).__call__(*args, **kwgs)
        if not self._recording:
            self._recorder_check_call()
        return retval

    def record(self):
        self._recording = True
        return self

    def stop(self):
        self._recording = False
        _type = Recorder
        for child in self._mock_children.values():
            if isinstance(child, _type):
                child.stop()
        ret = self._mock_return_value
        if isinstance(ret, _type) and ret is not self:
            ret.stop()

    __enter__ = record
    __exit__ = lambda self, e, v, t: self.stop()

#: patch using Recorder.
patch = partial(_patch, new_callable=Recorder)

#: patch.object using Recorder.
patch.object = partial(_patch.object, new_callable=Recorder)
