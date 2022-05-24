import io
import pickle
import xmltodict
import mysql.connector
import voeventparse as vp
import numpy as np
from astropy.time import Time
from pymongo import MongoClient
import lxml.etree as ElementTree
from comet.icomet import IHandler
from twisted.plugin import IPlugin
from zope.interface import implementer
from datetime import datetime
from astropy import units as u
from astropy.coordinates import SkyCoord

# Event handlers must implement IPlugin and IHandler.
@implementer(IPlugin, IHandler)
class EventReceiver(object):
    
    name = "receive-event"
    print("receive event attivo")

    def get_instrumentid_from_packet_type(self, voevent):

        if voevent.What.Param[0].attrib["name"] == "Packet_Type":

            packet_type = voevent.What.Param[0].attrib["value"]
            #https://gcn.gsfc.nasa.gov/sock_pkt_def_doc.html
            #SWIFT [46,47, 60 to 99, 103, 133, 140, 141]
            #FERMI_GBM [110 to 119, 144]
            #FERMI_LAT [120,121,122,123,124,125,127,128]

            if packet_type == 97: #SWIFT 
                return 3
            elif packet_type == 111:  #FERMI_GBM 
                return 1
            elif packet_type == 128: #FERMI_LAT 
                return 2
            elif packet_type == 152: #LIGO or LIGO_TEST
                return 7
            elif packet_type == 158: #ICECUBE_HESE
                return 8
            elif packet_type == 169: #ICECUBE_EHE
                return 10
            elif packet_type == 173: #ICECUBE_ASTROTRACK_GOLD
                return 21
            elif packet_type == 174: #ICECUBE_ASTROTRACK_GOLD
                return 22

        if "CHIME" in voevent.Who.Description: #CHIME
            return 42 
        if voevent.Who.AuthorIVORN == "ivo://INTEGRAL/dummy_demo":
            return 23

        return 0

    def get_time_from_voe(self, voevent):

        iso_time = voevent.WhereWhen.ObsDataLocation.ObservationLocation.AstroCoords.Time.TimeInstant.ISOTime.text

        t = Time(iso_time, format="fits")
        return np.round(t.unix - 1072915200)

    def get_networkID_from_voe(self, voevent):

        #Possible ivorns
        #GCN
        #Chimenet
        #INTEGRAL from James Rodi
        
        network = voevent.Who.AuthorIVORN

        if "gcn" in network:
            return 1
        if "chimenet" in network:
            return 4
        if "ivo://INTEGRAL/dummy_demo" == network:
            return 6

    def get_l_b_from_voe(self, voevent):

        ra = float(voevent.WhereWhen.ObsDataLocation.ObservationLocation.AstroCoords.Position2D.Value2.C1.text)
        dec = float(voevent.WhereWhen.ObsDataLocation.ObservationLocation.AstroCoords.Position2D.Value2.C2.text)

        c = SkyCoord(ra=ra*u.degree, dec=dec*u.degree, frame='icrs')

        return c.galactic.l.degree, c.galactic.b.degree



    def add_notice_mysql(self, voevent):
        
        try:
            cnx = mysql.connector.connect(user='afiss', password='RT@grawita@',
                              host='127.0.0.1', port=60306,
                              database='afiss_rta_pipe_test')

        except mysql.connector.Error as err:
            if err.errno == mysql.connector.errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)

        
        cursor = cnx.cursor()

        instrumentID = self.get_instrumentid_from_packet_type(voevent)
        triggerID = voevent.What.Param[0].attrib["name"] == "TrigID"

        #query = f"SELECT receivedsciencealertid FROM receivedsciencealert WHERE instrumentid = {instrumentID} AND triggerid = {triggerID};"

        #if the query is null the alert is not present -> it will be inserted into receivedsciencealert table

        #insert
        #####################
        networkid = self.get_networkID_from_voe(voevent)

        time = self.get_time_from_voe(voevent)

        query = f"INSERT INTO receivedsciencealert (instrumentid, networkid, time, triggerid) VALUES ({instrumentID}, {networkid}, {time}, {triggerID});"

        #cursor.execute(query)
        #cnx.commit()


        receivedsciencealertid = cursor.lastrowid
        #####################

        #query = f"SELECT seqnum FROM notice n join receivedsciencealert rsa ON (rsa.receivedsciencealertid = n.receivedsciencealertid) WHERE last = 1 AND rsa.instrumentid = {instrumentID} AND rsa.triggerid = {triggerID}"
        
        
        seqnum = 0 #TO IMPLEMENT

        ###########

        l, b = self.get_l_b_from_voe(voevent)
        error = float(voevent.WhereWhen.ObsDataLocation.ObservationLocation.AstroCoords.Position2D.Error2Radius.text)

        packet_type = voevent.What.Param[0].attrib["name"] == "Packet_Type"

        configuration = ""
        last = 1
        noticetime = datetime.now().isoformat()

        notice = vp.prettystr(voevent)

        tstart = 0
        tstop = 0

        contour = 0
        url = ""
        attributes = ""

        query = f"INSERT INTO notice (receivedsciencealertid, seqnum, l, b, error, type, configuration, last, noticetime, notice, tstart, tstop, contour, url, attributes) VALUES ({receivedsciencealertid}, {seqnum}, {l}, {b}, {error}, {packet_type}, {configuration}, {last}, {noticetime}, {notice}, {tstart}, {tstop}, {contour}, {url}, {attributes}); "
        print(query)
        #cursor.execute(query)
        #cnx.commit()

    """
    def add_notice_mongodb(self, event):ls
        client = MongoClient("")
    """

    def __init__(self) -> None:
        pass

    # When the handler is called, it is passed an instance of
    # comet.utility.xml.xml_document.
    def __call__(self, event):

        #db=self.client["AFISS"]
        #collection=db["Events"]

        v = vp.loads(event.raw_bytes)
        print(vp.prettystr(v))
        #self.add_notice_mysql(v)
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