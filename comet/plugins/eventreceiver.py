# Comet VOEvent Broker.
# Example event handler: print an event.

import lxml.etree as ElementTree
from zope.interface import implementer
from twisted.plugin import IPlugin
from comet.icomet import IHandler
import io
import voeventparse as vp
import pickle



# Event handlers must implement IPlugin and IHandler.
@implementer(IPlugin, IHandler)
class EventReceiver(object):
    
    name = "receive-event"
    print("receive event attivo")

    # When the handler is called, it is passed an instance of
    # comet.utility.xml.xml_document.
    def __call__(self, event):

        v = vp.loads(event.raw_bytes)
        print("Ivorn:", v.attrib['ivorn'])
        print("Role:", v.attrib['role'])
        print("AuthorIVORN:", v.Who.AuthorIVORN)
        print("Short name:", v.Who.Author.shortName)
        print("Contact:", v.Who.Author.contactEmail)


receive_event = EventReceiver()