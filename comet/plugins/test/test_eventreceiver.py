import sys
import textwrap
from io import StringIO
import lxml.etree as etree
from comet.icomet import IHandler
from twisted.trial import unittest
from twisted.plugin import IPlugin
from comet.utility.xml import xml_document
from comet.plugins.eventreceiver import EventReceiver
from comet.testutils import DUMMY_VOEVENT_GCN, DUMMY_VOEVENT_INTEGRAL, DUMMY_VOEVENT_CHIME, DUMMY_VOEVENT_LIGO, DUMMY_VOEVENT_LIGO_INITIAL, DUMMY_VOEVENT_LIGO_PRELIMINARY


class DummyEvent(object):
    #Class containing standard voevent from three different networks
    gcn = xml_document(DUMMY_VOEVENT_GCN)
    chime = xml_document(DUMMY_VOEVENT_CHIME)
    integral = xml_document(DUMMY_VOEVENT_INTEGRAL)
    ligo = xml_document(DUMMY_VOEVENT_LIGO)
    ligo_preliminary = xml_document(DUMMY_VOEVENT_LIGO_PRELIMINARY)
    ligo_initial = xml_document(DUMMY_VOEVENT_LIGO_INITIAL)


class EventReceiverTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.dummyevents = DummyEvent()
        self.event_receiver = EventReceiver()

    def test_interface(self):
        self.assertTrue(IHandler.implementedBy(EventReceiver))
        self.assertTrue(IPlugin.implementedBy(EventReceiver))

    def test_name(self):
        self.assertEqual(EventReceiver.name, "receive-event")

    def test_write_chime_event(self):
        request = self.event_receiver(self.dummyevents.chime)
        self.assertTrue(request)

    def test_write_gcn_event(self):
        request = self.event_receiver(self.dummyevents.gcn)
        self.assertTrue(request)
    
    def test_write_integral(self):
        request = self.event_receiver(self.dummyevents.integral)
        self.assertTrue(request)
    
    def test_write_ligo(self):
        request = self.event_receiver(self.dummyevents.ligo)
        self.assertTrue(request)
    
    def test_write_preliminary(self):
        request = self.event_receiver(self.dummyevents.ligo_preliminary)
        self.assertTrue(request)
    
    def test_write_initial(self):
        request = self.event_receiver(self.dummyevents.ligo_initial)
        self.assertTrue(request)