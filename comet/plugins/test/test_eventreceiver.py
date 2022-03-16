# Comet VOEvent Broker.
# Tests for EventPrinter plugin.

import sys
try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO

import lxml.etree as etree

from twisted.trial import unittest
from twisted.plugin import IPlugin

from comet.icomet import IHandler
from comet.plugins.eventreceiver import EventReceiver

DUMMY_XML = u'<xml/>'

class DummyEvent(object):
    element = etree.fromstring(DUMMY_XML)

class EventReceiverTestCase(unittest.TestCase):
    def test_interface(self):
        self.assertTrue(IHandler.implementedBy(EventReceiver))
        self.assertTrue(IPlugin.implementedBy(EventReceiver))

    def test_name(self):
        self.assertEqual(EventReceiver.name, "receive-event")

    def test_print_event(self):
        event_receiver = EventReceiver()
        event_receiver(DummyEvent())
        
