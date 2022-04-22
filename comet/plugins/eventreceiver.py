# Comet VOEvent Broker.
# Example event handler: print an event.

import io
import pickle
import xmltodict
import voeventparse as vp
from pymongo import MongoClient
import lxml.etree as ElementTree
from comet.icomet import IHandler
from twisted.plugin import IPlugin
from zope.interface import implementer



# Event handlers must implement IPlugin and IHandler.
@implementer(IPlugin, IHandler)
class EventReceiver(object):
    
    name = "receive-event"
    print("receive event attivo")
    

    def __init__(self) -> None:
        self.client = MongoClient('mongodb://root:root@127.0.0.1:27017/')

    # When the handler is called, it is passed an instance of
    # comet.utility.xml.xml_document.
    def __call__(self, event):

        db=self.client["AFISS"]
        collection=db["Events"]

        v = vp.loads(event.raw_bytes)
        doc = xmltodict.parse(vp.dumps(v))
        # Query exemple: select notices with shortname INTEGRAL (via VO-GCN)
        # {'voe:VOEvent.Who.Author.shortName': "INTEGRAL (via VO-GCN)"}
        x = collection.insert_one(doc)
        #print("Ivorn:", v.attrib['ivorn'])
        #print("Role:", v.attrib['role'])
        #print("AuthorIVORN:", v.Who.AuthorIVORN)
        #print("Short name:", v.Who.Author.shortName)
        #print("Contact:", v.Who.Author.contactEmail)




receive_event = EventReceiver()