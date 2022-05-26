import re
import numpy as np
import voeventparse as vp
from datetime import datetime
from astropy.time import Time
from astropy import units as u
import lxml.etree as ElementTree
from astropy.coordinates import SkyCoord
from comet.utility import voevent
from comet.utility.xml import xml_document

from comet.testutils import DUMMY_VOEVENT_GCN, DUMMY_VOEVENT_INTEGRAL, DUMMY_VOEVENT_CHIME, DUMMY_VOEVENT_LIGO



class DummyEvent(object):
    #Class containing standard voevent from three different networks
    gcn = xml_document(DUMMY_VOEVENT_GCN)
    chime = xml_document(DUMMY_VOEVENT_CHIME)
    integral = xml_document(DUMMY_VOEVENT_INTEGRAL)
    ligo = xml_document(DUMMY_VOEVENT_LIGO)


class Voevent(object):

    def __init__(self, voe) -> None:

        self.voevent = voe

        self.GCN = False
        self.CHIME = False
        self.INTEGRAL = False
        self.LIGO = False
        self.mark_notice()

        self.instrumentId = self.get_instrumentid_from_packet_type()
        self.seqNum = self.get_seqnum()
        self.triggerId = self.get_triggerID()
        self.packetType = self.get_packet_tipe()
        self.isoTime = self.get_time_from_voe()
        self.networkId = self.get_networkID()
        self.l, self.b = self.get_l_b()
        self.error = self.get_position_error()
        self.notice = vp.prettystr(self.voevent)
        self.configuration = "test"
        self.tstart = 0
        self.tstop = 0
        self.last = 1
        self.contour = "test"
        self.url = "test"
        self.attributes = '{"bbh": 0, "bns": 0.9999947011562164, "far": 0.00000000000009110699364861295, "nsbh": 0, "has_ns": 1, "grace_id": "MS210208t", "mass_gap": 0, "has_remnant": 1, "terrestrial": 0.000005298843783562432}'
    

    def mark_notice(self):

        #The only common parameter is the contactName, we discriminate among notices using this parameter
        if "Scott Barthelmy" == self.voevent.Who.Author.contactName.text:
            self.GCN = True
            return
        if "LIGO Scientific Collaboration and Virgo Collaboration" == self.voevent.Who.Author.contactName.text:
            self.LIGO = True
            return
        if "Andrew Zwaniga" == self.voevent.Who.Author.contactName.text:
            self.CHIME = True
            return
        if "James Rodi" == self.voevent.Who.Author.contactName.text:
            self.INTEGRAL = True
            return
        
        raise Exception("notice not supported")
    def get_instrumentid_from_packet_type(self):
        

        if self.GCN or self.LIGO:
            packet_type = int(self.voevent.What.Param[0].attrib["value"])
            #https://gcn.gsfc.nasa.gov/sock_pkt_def_doc.html
            #SWIFT [46,47, 60 to 99, 103, 133, 140, 141]
            #FERMI_GBM [110 to 119, 144]
            #FERMI_LAT [120,121,122,123,124,125,127,128]

            if packet_type == 97: #SWIFT 
                return 3
            elif packet_type == 111:  #FERMI_GBM 
                return 1
            elif packet_type in [125,128]: #FERMI_LAT 
                return 2
            elif packet_type in [150, 151, 152]: #LIGO or LIGO_TEST
                return 7
            elif packet_type == 158: #ICECUBE_HESE
                return 8
            elif packet_type == 169: #ICECUBE_EHE
                return 10
            elif packet_type == 173: #ICECUBE_ASTROTRACK_GOLD
                return 21
            elif packet_type == 174: #ICECUBE_ASTROTRACK_GOLD
                return 22

        if self.CHIME: #CHIME
            return 24 
        if self.INTEGRAL:
            return 23

        raise Exception("Voevent not supported")

    def get_seqnum(self):

        return 0

    def get_triggerID(self):

        if self.GCN:
            return self.voevent.What.Param[2].attrib["value"]
        if self.LIGO:
            graceID = self.voevent.What.Param[3].attrib["value"]
            return re.sub("[^0-9]", "", graceID)
        else:
            return 0

    def get_packet_tipe(self):

        if self.GCN or self.LIGO:
            return self.voevent.What.Param[0].attrib["value"]
        else:
            return 0

    def get_time_from_voe(self):

        iso_time = self.voevent.WhereWhen.ObsDataLocation.ObservationLocation.AstroCoords.Time.TimeInstant.ISOTime.text

        t = Time(iso_time, format="fits")
        return np.round(t.unix - 1072915200)

    def get_networkID(self):

        #Possible ivorns
        #GCN
        #Chimenet
        #INTEGRAL from James Rodi

        if self.GCN or self.LIGO:
            return 1
        if self.CHIME:
            return 4
        if self.INTEGRAL:
            return 6

    def get_l_b(self):

        if self.LIGO:
            return 0,0

        ra = float(self.voevent.WhereWhen.ObsDataLocation.ObservationLocation.AstroCoords.Position2D.Value2.C1.text)
        dec = float(self.voevent.WhereWhen.ObsDataLocation.ObservationLocation.AstroCoords.Position2D.Value2.C2.text)

        c = SkyCoord(ra=ra*u.degree, dec=dec*u.degree, frame='icrs')

        return c.galactic.l.degree, c.galactic.b.degree

    def get_position_error(self):
        if self.LIGO:
            return 0
        return float(self.voevent.WhereWhen.ObsDataLocation.ObservationLocation.AstroCoords.Position2D.Error2Radius.text)

    def __str__(self):
        return f"Voevent \n IntrumentID: {self.instrumentId}, seqNum {self.seqNum}, triggerid: {self.triggerId}, packetType: {self.packetType}, time: {self.isoTime}, l: {self.l}, b: {self.b}"


if __name__ == "__main__":
    
    dummyevents = DummyEvent()

    voe_chime = vp.loads(dummyevents.chime.raw_bytes)
    voe_gcn = vp.loads(dummyevents.gcn.raw_bytes)
    voe_integral = vp.loads(dummyevents.integral.raw_bytes)
    voe_ligo = vp.loads(dummyevents.ligo.raw_bytes)
    
    v_chime = Voevent(voe_chime)
    v_gcn = Voevent(voe_gcn)
    v_integral = Voevent(voe_integral)
    v_ligo = Voevent(voe_ligo)

    print(v_chime)
    print(v_gcn)
    print(v_integral)
    print(v_ligo)

