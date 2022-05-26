import os
import io
import json
import pickle
import xmltodict
import numpy as np
import mysql.connector
import voeventparse as vp
from datetime import datetime
from astropy.time import Time
from astropy import units as u
from pymongo import MongoClient
import lxml.etree as ElementTree
from comet.icomet import IHandler
from twisted.plugin import IPlugin
from zope.interface import implementer
from astropy.coordinates import SkyCoord

from comet.plugins.Voevent import Voevent

# Event handlers must implement IPlugin and IHandler.
@implementer(IPlugin, IHandler)
class EventReceiver(object):
    
    name = "receive-event"
    print("receive event attivo")


    def add_notice_mysql(self, voevent):
        
        try:
            cnx = mysql.connector.connect(user='afiss', password=os.environ["MYSQL_AFISS"],
                              host='127.0.0.1', port=60306,
                              database='afiss_rta_pipe_test_3')

        except mysql.connector.Error as err:
            if err.errno == mysql.connector.errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)

        
        cursor = cnx.cursor()


        #query = f"SELECT receivedsciencealertid FROM receivedsciencealert WHERE instrumentid = {instrumentID} AND triggerid = {triggerID};"

        #if the query is null the alert is not present -> it will be inserted into receivedsciencealert table

        #insert
        #####################

        query = f"INSERT INTO receivedsciencealert (instrumentid, networkid, time, triggerid) VALUES ({voevent.instrumentId}, {voevent.networkId}, {voevent.isoTime}, {voevent.triggerId});"
        #print(f"query1 {query}")
        cursor.execute(query)
        cnx.commit()


        receivedsciencealertid = cursor.lastrowid
        #print(f"lastrowid: {receivedsciencealertid}")
        #####################

        #query = f"SELECT seqnum FROM notice n join receivedsciencealert rsa ON (rsa.receivedsciencealertid = n.receivedsciencealertid) WHERE last = 1 AND rsa.instrumentid = {instrumentID} AND rsa.triggerid = {triggerID}"
        

        ###########

        noticetime = datetime.now().isoformat(timespec="seconds")


        query = f"INSERT INTO notice (receivedsciencealertid, seqnum, l, b, error, contour, `last`, `type`, configuration, noticetime, notice, tstart, tstop, url, `attributes`, afisscheck) VALUES ({receivedsciencealertid}, {voevent.seqNum}, {voevent.l}, {voevent.b}, {voevent.error}, '{voevent.contour}', {voevent.last}, {voevent.packetType}, '{voevent.configuration}', '{noticetime}', '{voevent.notice}', {voevent.tstart}, {voevent.tstop}, '{voevent.url}', '{voevent.attributes}', 0);"
        cursor.execute(query)
        cnx.commit()

    def __init__(self) -> None:
        pass

    # When the handler is called, it is passed an instance of
    # comet.utility.xml.xml_document.
    def __call__(self, event):

        #db=self.client["AFISS"]
        #collection=db["Events"]

        v = vp.loads(event.raw_bytes)

        voevent = Voevent(v)

        self.add_notice_mysql(voevent)
        #doc = xmltodict.parse(vp.dumps(v))
        # Query exemple: select notices with shortname INTEGRAL (via VO-GCN)
        # {'voe:VOEvent.Who.Author.shortName': "INTEGRAL (via VO-GCN)"}
        #x = collection.insert_one(doc)
        #print("Ivorn:", v.attrib['ivorn'])
        #print("Role:", v.attrib['role'])
        #print("AuthorIVORN:", v.Who.AuthorIVORN)
        #print("Short name:", v.Who.Author.shortName)
        #print("Contact:", v.Who.Author.contactEmail)

receive_event = EventReceiver()