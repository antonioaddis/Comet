import sys
import textwrap
from io import StringIO
import lxml.etree as etree
from comet.icomet import IHandler
from twisted.trial import unittest
from twisted.plugin import IPlugin
from comet.utility.xml import xml_document
from comet.plugins.eventreceiver import EventReceiver
from comet.testutils import DUMMY_VOEVENT_GCN, DUMMY_VOEVENT_INTEGRAL, DUMMY_VOEVENT_CHIME, DUMMY_VOEVENT_LIGO


class DummyEvent(object):
    #Class containing standard voevent from three different networks
    gcn = xml_document(DUMMY_VOEVENT_GCN)
    chime = xml_document(DUMMY_VOEVENT_CHIME)
    integral = xml_document(DUMMY_VOEVENT_INTEGRAL)
    ligo = xml_document(DUMMY_VOEVENT_LIGO)


class EventReceiverTestCase(unittest.TestCase):
    def test_interface(self):
        self.assertTrue(IHandler.implementedBy(EventReceiver))
        self.assertTrue(IPlugin.implementedBy(EventReceiver))

    def test_name(self):
        self.assertEqual(EventReceiver.name, "receive-event")

    def test_print_event(self):
        event_receiver = EventReceiver()
        dummyevents = DummyEvent()
        event_receiver(dummyevents.chime)
        event_receiver(dummyevents.gcn)
        event_receiver(dummyevents.integral)
        event_receiver(dummyevents.ligo)

        
