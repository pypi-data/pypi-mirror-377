import tango.server
import taurus
from taurus.core import TaurusEventType
from taurus.core.tango.test.nodb import NamedDeviceTestContext
from unittest.mock import Mock


class Issue1159_Exception(Exception):
    pass


class Issue1159(tango.server.Device):
    def read_attr_hardware(self, attr_ids):
        raise Issue1159_Exception("!")

    @tango.server.attribute
    def a1(self):
        return 1


def test_issue1159():
    """Check that attribute read errors during asynchronous poll of a DS are
    properly handled (they should generate an error event)"""
    with NamedDeviceTestContext(
        Issue1159, process=True, timeout=15
    ) as full_name:
        dev = taurus.Device(full_name)
        a1 = taurus.Attribute(full_name + "/a1")
        listener = Mock()
        a1.addListener(listener)
        attrs = {"a1": a1}
        req_id = dev.poll(attrs, asynch=True)
        dev.poll(attrs, req_id=req_id)

        # check that exactly one event was received
        # Note: `Mock.assert_called_once` is not available in py35
        listener.eventReceived.call_count == 1

        # check that the event is from a1, of type error and caused by
        # Issue1159_Exception
        s, t, v = listener.eventReceived.call_args[0]
        assert s is a1
        assert t is TaurusEventType.Error
        assert isinstance(v, tango.DevFailed)
        assert "Issue1159_Exception" in repr(v)
