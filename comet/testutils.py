# Comet VOEvent Broker.
# Utilities in support of broker tests.

import shutil
import tempfile
import textwrap
from contextlib import contextmanager
from functools import partial
import lxml.etree as etree
from comet.protocol.messages import authenticateresponse

# All dummy event text should be RAW BYTES, as received over the network.

DUMMY_EVENT_IVOID = u"ivo://comet.broker/test#1234567890".encode('UTF-8')
DUMMY_SERVICE_IVOID = u"ivo://comet.broker/test".encode('UTF-8')

DUMMY_IAMALIVE = u"""
    <?xml version=\'1.0\' encoding=\'UTF-8\'?>
    <trn:Transport xmlns:trn="http://www.telescope-networks.org/xml/Transport/v1.1"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:schemaLocation="http://telescope-networks.org/schema/Transport/v1.1
            http://www.telescope-networks.org/schema/Transport-v1.1.xsd"
        version="1.0" role="iamalive">
        <Origin>%s</Origin>
        <TimeStamp>2012-01-01T00:00:00Z</TimeStamp>
    </trn:Transport>
""" % (DUMMY_EVENT_IVOID.decode(),)
DUMMY_IAMALIVE = textwrap.dedent(DUMMY_IAMALIVE).strip().encode('UTF-8')

DUMMY_AUTHENTICATE = u"""
    <?xml version='1.0' encoding='UTF-8'?>
    <trn:Transport xmlns:trn="http://www.telescope-networks.org/xml/Transport/v1.1"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:schemaLocation="http://telescope-networks.org/schema/Transport/v1.1
            http://www.telescope-networks.org/schema/Transport-v1.1.xsd"
        version="1.0" role="authenticate">
        <Origin>%s</Origin>
        <TimeStamp>2012-01-01T00:00:00Z</TimeStamp>
    </trn:Transport>
""" % (DUMMY_EVENT_IVOID.decode(),)
DUMMY_AUTHENTICATE = textwrap.dedent(DUMMY_AUTHENTICATE).strip().encode('UTF-8')

DUMMY_ACK = u"""
    <?xml version='1.0' encoding='UTF-8'?>
    <trn:Transport xmlns:trn="http://www.telescope-networks.org/xml/Transport/v1.1"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:schemaLocation="http://telescope-networks.org/schema/Transport/v1.1
            http://www.telescope-networks.org/schema/Transport-v1.1.xsd"
        version="1.0" role="ack">
        <Origin>%s</Origin>
        <Response>%s</Response>
        <TimeStamp>2012-01-01T00:00:00Z</TimeStamp>
    </trn:Transport>
""" % (DUMMY_SERVICE_IVOID.decode(), DUMMY_SERVICE_IVOID.decode())
DUMMY_ACK = textwrap.dedent(DUMMY_ACK).strip().encode('UTF-8')

DUMMY_NAK = u"""
    <?xml version='1.0' encoding='UTF-8'?>
    <trn:Transport xmlns:trn="http://www.telescope-networks.org/xml/Transport/v1.1"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:schemaLocation="http://telescope-networks.org/schema/Transport/v1.1
            http://www.telescope-networks.org/schema/Transport-v1.1.xsd"
        version="1.0" role="nak">
        <Origin>%s</Origin>
        <Response>%s</Response>
        <TimeStamp>2012-01-01T00:00:00Z</TimeStamp>
    </trn:Transport>
""" % (DUMMY_SERVICE_IVOID.decode(), DUMMY_SERVICE_IVOID.decode())
DUMMY_NAK = textwrap.dedent(DUMMY_NAK).strip().encode('UTF-8')

DUMMY_AUTHENTICATE_RESPONSE_LEGACY = u"""
    <?xml version='1.0' encoding='UTF-8'?>
    <trn:Transport xmlns:trn="http://www.telescope-networks.org/xml/Transport/v1.1"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:schemaLocation="http://telescope-networks.org/schema/Transport/v1.1
            http://www.telescope-networks.org/schema/Transport-v1.1.xsd"
        version="1.0" role="authenticate">
        <Origin>%s</Origin>
        <Response>%s</Response>
        <TimeStamp>2012-01-01T00:00:00Z</TimeStamp>
        <Meta>
            <filter type="xpath">%s</filter>
        </Meta>
    </trn:Transport>
""" % (DUMMY_SERVICE_IVOID.decode(), DUMMY_SERVICE_IVOID.decode(), "%s")
DUMMY_AUTHENTICATE_RESPONSE_LEGACY = textwrap.dedent(
    DUMMY_AUTHENTICATE_RESPONSE_LEGACY
).strip().encode('UTF-8')

DUMMY_AUTHENTICATE_RESPONSE = partial(
    authenticateresponse, DUMMY_SERVICE_IVOID, DUMMY_SERVICE_IVOID
)

DUMMY_VOEVENT_INTEGRAL = u"""
<?xml version='1.0' encoding='UTF-8'?>
<voe:VOEvent xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:voe="http://www.ivoa.net/xml/VOEvent/v2.0" xsi:schemaLocation="http://www.ivoa.net/xml/VOEvent/v2.0 http://www.ivoa.net/xml/VOEvent/VOEvent-v2.0.xsd" version="2.0" role="test" ivorn="ivo://dummy.txt#1">
  <Who>
    <Description>VOEvent created with voevent-parse, version 1.0.3. See https://github.com/timstaley/voevent-parse for details.</Description>
    <AuthorIVORN>ivo://INTEGRAL/dummy_demo</AuthorIVORN>
    <Date>2022-05-20T11:10:32</Date>
    <Author>
      <contactName>James Rodi</contactName>
      <title>Hotwired VOEvent Hands-on</title>
    </Author>
  </Who>
  <What>
    <Param ucd="phot.mag" value="18.77" name="mag" dataType="float"/>
    <Group name="historic">
      <Param ucd="phot.mag" value="19.62" name="hist_mag" dataType="float"/>
      <Param ucd="phot.mag" value="0.07" name="hist_scatter" dataType="float"/>
    </Group>
    <Param ucd="phot.mag" value="18.77" name="mag" dataType="float"/>
    <Group name="historic">
      <Param ucd="phot.mag" value="19.62" name="hist_mag" dataType="float"/>
      <Param ucd="phot.mag" value="0.07" name="hist_scatter" dataType="float"/>
    </Group>
  </What>
  <WhereWhen>
    <ObsDataLocation>
      <ObservatoryLocation id="INTEGRAL"/>
      <ObservationLocation>
        <AstroCoordSystem id="UTC-FK5-GEO"/>
        <AstroCoords coord_system_id="UTC-FK5-GEO">
          <Time unit="s">
            <TimeInstant>
              <ISOTime>2022-05-09T08:07:00</ISOTime>
            </TimeInstant>
          </Time>
          <Position2D unit="deg">
            <Name1>RA</Name1>
            <Name2>Dec</Name2>
            <Value2>
              <C1>314.6578836056712</C1>
              <C2>12.45</C2>
            </Value2>
            <Error2Radius>0</Error2Radius>
          </Position2D>
        </AstroCoords>
      </ObservationLocation>
    </ObsDataLocation>
  </WhereWhen>
  <Description>This is not an official INTEGRAL data product.</Description>
</voe:VOEvent>"""
DUMMY_VOEVENT_INTEGRAL = textwrap.dedent(DUMMY_VOEVENT_INTEGRAL).strip().encode('UTF-8')


DUMMY_VOEVENT_CHIME = u"""
<?xml version='1.0' encoding='UTF-8'?>
<voe:VOEvent xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:voe="http://www.ivoa.net/xml/VOEvent/v2.0" xsi:schemaLocation="http://www.ivoa.net/xml/VOEvent/v2.0 http://www.ivoa.net/xml/VOEvent/VOEvent-v2.0.xsd" version="2.0" role="observation" ivorn="ivo://ca.chimenet.frb/FRB-DETECTION-#2022-03-20-10:00:28.960760UTC+0000_996ae14090d1">
  <Who>
    <Description>CHIME/FRB VOEvent Service</Description>
    <AuthorIVORN>ivo://ca.chimenet.frb/contact</AuthorIVORN>
    <Date>2022-03-20T10:00:28+00:00</Date>
    <Author>
      <contactEmail>andrew.zwaniga@mail.mcgill.ca</contactEmail>
      <contactName>Andrew Zwaniga</contactName>
      <shortName>CHIME/FRB VOEvent Service</shortName>
    </Author>
  </Who>
  <What>
    <Group name="observatory parameters">
      <Param ucd="time.resolution" unit="ms" value="0.983" name="sampling_time">
        <Description>FRB search time resolution</Description>
      </Param>
      <Param ucd="instr.bandwidth" unit="MHz" value="400" name="bandwidth">
        <Description>CHIME telescope bandwidth</Description>
      </Param>
      <Param ucd="em.freq;instr" unit="MHz" value="600" name="centre_frequency">
        <Description>CHIME telescope central frequency</Description>
      </Param>
      <Param ucd="" unit="" value="2" name="npol">
        <Description>The CHIME telescope has dual-polarization feeds</Description>
      </Param>
      <Param ucd="" unit="" value="8" name="bits_per_sample">
        <Description>CHIME/FRB samples 16384 frequency channels at 0.983 ms cadence as 8-bit integers</Description>
      </Param>
      <Param ucd="phot.antennaTemp" unit="K" value="50" name="tsys">
        <Description>CHIME receiver noise temperature</Description>
      </Param>
      <Param ucd="" unit="" value="" name="backend">
        <Description>CHIME/FRB backend</Description>
      </Param>
    </Group>
    <Group name="event parameters">
      <Param ucd="" unit="" value="217097677" name="event_no">
        <Description>CHIME/FRB event number assigned by real-time pipeline</Description>
      </Param>
      <Param ucd="" unit="" value="" name="known_source_name">
        <Description>CHIME/FRB internal known source name</Description>
      </Param>
      <Param ucd="" unit="" value="EXTRAGALACTIC" name="event_type">
        <Description>Unknown event type assigned from real-time pipeline e.g. EXTRAGALACTIC, AMBIGUOUS, GALACTIC</Description>
      </Param>
      <Param ucd="" unit="" value="real-time" name="pipeline_name">
        <Description>The name of the pipeline that produced this data</Description>
      </Param>
      <Param ucd="phys.dispMeasure" unit="pc/cm^3" value="308.1332092285156" name="dm">
        <Description>Dispersion measure from real-time pipeline</Description>
      </Param>
      <Param ucd="stat.error;phys.dispMeasure" unit="pc/cm^3" value="0.808748543262481" name="dm_error">
        <Description>Error in dispersion measure from real-time pipeline</Description>
      </Param>
      <Param ucd="" unit="" value="2022-03-20 10:00:28.960760+00:00" name="timestamp_utc">
        <Description>Topocentric arrival time at 400 MHz</Description>
      </Param>
      <Param ucd="" unit="" value="0.007864319719374001" name="timestamp_utc_error">
        <Description>Error in topocentric arrival time at 400 MHz in seconds from real-time pipeline</Description>
      </Param>
      <Param ucd="stat.snr" unit="" value="24.771873474121094" name="snr">
        <Description>Signal-to-noise ratio from real-time pipeline</Description>
      </Param>
      <Param ucd="" unit="degrees" value="0.5392466329194251" name="pos_error_semiminor_deg_95">
        <Description>Localization error ellipse semi-minor axis to 95 percent C.L. in right ascension (J2000) in degrees from real-time pipeline</Description>
      </Param>
      <Param ucd="" unit="degrees" value="0.38229381212162405" name="pos_error_semimajor_deg_95">
        <Description>Localization error ellipse semi-major axis to 95 percent C.L. in declination (J2000) in degrees from real-time pipeline</Description>
      </Param>
    </Group>
    <Group name="advanced parameters">
      <Param ucd="" unit="pc/cm^3" value="26.284419129901345" name="dm_gal_ne_2001_max">
        <Description>Max Milky Way DM contribution (NE 2001 model) from real-time pipeline</Description>
      </Param>
      <Param ucd="" unit="pc/cm^3" value="20.724408436144515" name="dm_gal_ymw_2016_max">
        <Description>Max Milky Way DM contribution (YMW 2016 model) from real-time pipeline</Description>
      </Param>
      <Param ucd="" unit="" value="2022-03-20 10:00:20.969754+00:00" name="timestamp_utc_inf_freq">
        <Description>Topocentric arrival time at infinite frequency</Description>
      </Param>
      <Param ucd="" unit="" value="0.02239969915578273" name="timestamp_utc_inf_freq_error">
        <Description>Error in topocentric arrival time at infinite frequency from real-time pipeline</Description>
      </Param>
    </Group>
  </What>
  <WhereWhen>
    <ObsDataLocation>
      <ObservatoryLocation id="CHIME lives at Dominion Radio Astrophysical Observatory (DRAO)"/>
      <ObservationLocation>
        <AstroCoordSystem id="UTC-FK5-TOPO"/>
        <AstroCoords coord_system_id="UTC-FK5-TOPO">
          <Time unit="s">
            <TimeInstant>
              <ISOTime>2022-03-20T10:00:28.960760</ISOTime>
            </TimeInstant>
          </Time>
          <Position2D unit="deg">
            <Name1>RA</Name1>
            <Name2>Dec</Name2>
            <Value2>
              <C1>207.13546129702095</C1>
              <C2>39.68328005638283</C2>
            </Value2>
            <Error2Radius>0.5392466329194251</Error2Radius>
          </Position2D>
        </AstroCoords>
      </ObservationLocation>
    </ObsDataLocation>
  </WhereWhen>
  <How>
    <Description>Real-time pipeline topocentric time-of-arrival is corrected for dispersion to bottom of CHIME band (400 MHz)</Description>
    <Reference uri="https://www.chime-frb.ca"/>
  </How>
  <Why importance="0.9999834084886757">
    <Inference probability="0" relation="">
      <Name/>
      <Concept>No probabilistic measurement is reported</Concept>
    </Inference>
    <Description>CHIME/FRB VOEvent Service detection-type alert from real-time pipeline</Description>
    <Name/>
    <Concept>Importance is a machine learning score from 0-1 separating RFI (0) from an astrophysical signal (1); Probability is not reported for the detection-type VOEvent</Concept>
  </Why>
</voe:VOEvent>"""
DUMMY_VOEVENT_CHIME = textwrap.dedent(DUMMY_VOEVENT_CHIME).strip().encode('UTF-8')


DUMMY_VOEVENT_GCN = u"""
<?xml version = '1.0' encoding = 'UTF-8'?>
<voe:VOEvent
      ivorn="ivo://nasa.gsfc.gcn/SWIFT#BAT_SubSubThresh_Pos_-1532692135-737"
      role="observation" version="2.0"
      xmlns:voe="http://www.ivoa.net/xml/VOEvent/v2.0"
      xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
      xsi:schemaLocation="http://www.ivoa.net/xml/VOEvent/v2.0  http://www.ivoa.net/xml/VOEvent/VOEvent-v2.0.xsd" >
  <Who>
    <AuthorIVORN>ivo://nasa.gsfc.tan/gcn</AuthorIVORN>
    <Author>
      <shortName>VO-GCN</shortName>
      <contactName>Scott Barthelmy</contactName>
      <contactPhone>+1-301-286-3106</contactPhone>
      <contactEmail>scott.barthelmy@nasa.gov</contactEmail>
    </Author>
    <Date>2022-05-17T10:00:22</Date>
    <Description>This VOEvent message was created with GCN VOE version: 15.08 30dec21</Description>
  </Who>
  <What>
    <Param name="Packet_Type"  value="140" />
    <Param name="Pkt_Ser_Num"  value="60761" />
    <Param name="TrigID"       value="-1532692135" ucd="meta.id" />
    <Param name="Event_TJD"    value="19716" unit="days" ucd="time" />
    <Param name="Event_SOD"    value="16530.00" unit="sec" ucd="time" />
    <Param name="Event_Inten"  value="773" unit="cts" ucd="phot.count;em.gamma.soft" />
    <Param name="Integ_Time"   value="64.000" unit="sec" ucd="time.interval" />
    <Param name="Phi"          value="171.99" unit="deg" ucd="pos.az.azi" />
    <Param name="Theta"        value="17.91" unit="deg" ucd="pos.az.zd" />
    <Param name="Soln_Status"  value="0x800" />
    <Param name="Misc_flags"   value="0x40000000" />
    <Param name="Image_Signif" value="4.22" unit="sigma" ucd="stat.snr" />
    <Group name="Solution_Status" >
      <Param name="Point_Source"             value="false" />
      <Param name="VERY_Lo_Image_Signif"     value="true" />
      <Param name="Target_in_Flt_Catalog"    value="false" />
      <Param name="Target_in_Gnd_Catalog"    value="false" />
      <Param name="Near_Bright_Star"         value="false" />
      <Param name="Spatial_Prox_Match"       value="false" />
      <Param name="Temporal_Prox_Match"      value="false" />
      <Param name="Test_Submission"          value="false" />
    </Group>
    <Group name="Misc_Flags" >
      <Param name="Values_Out_of_Range"      value="false" />
      <Param name="Near_Bright_Star"         value="false" />
      <Param name="Err_Circle_in_Galaxy"     value="false" />
      <Param name="Galaxy_in_Err_Circle"     value="false" />
    </Group>
    <Param name="Coords_Type"   value="1" unit="dn" />
    <Param name="Coords_String" value="source_object" />
    <Group name="Obs_Support_Info" >
      <Description>The Sun and Moon values are valid at the time the VOEvent XML message was created.</Description>
      <Param name="Sun_RA"        value="54.19" unit="deg" ucd="pos.eq.ra" />
      <Param name="Sun_Dec"       value="19.37" unit="deg" ucd="pos.eq.dec" />
      <Param name="Sun_Distance"  value="78.57" unit="deg" ucd="pos.angDistance" />
      <Param name="Sun_Hr_Angle"  value="7.59" unit="hr" />
      <Param name="Moon_RA"       value="252.22" unit="deg" ucd="pos.eq.ra" />
      <Param name="Moon_Dec"      value="-24.29" unit="deg" ucd="pos.eq.dec" />
      <Param name="MOON_Distance" value="101.79" unit="deg" ucd="pos.angDistance" />
      <Param name="Moon_Illum"    value="97.72" unit="%" ucd="arith.ratio" />
      <Param name="Galactic_Long" value="104.63" unit="deg" ucd="pos.galactic.lon" />
      <Param name="Galactic_Lat"  value="20.58" unit="deg" ucd="pos.galactic.lat" />
      <Param name="Ecliptic_Long" value="40.79" unit="deg" ucd="pos.ecliptic.lon" />
      <Param name="Ecliptic_Lat"  value="78.14" unit="deg" ucd="pos.ecliptic.lat" />
    </Group>
    <Description>Type=140: The sub-sub-threshold Swift-BAT trigger position notice.</Description>
  </What>
  <WhereWhen>
    <ObsDataLocation>
      <ObservatoryLocation id="GEOLUN" />
      <ObservationLocation>
        <AstroCoordSystem id="UTC-FK5-GEO" />
        <AstroCoords coord_system_id="UTC-FK5-GEO">
          <Time unit="s">
            <TimeInstant>
              <ISOTime>2022-05-17T04:35:30.00</ISOTime>
            </TimeInstant>
          </Time>
          <Position2D unit="deg">
            <Name1>RA</Name1>
            <Name2>Dec</Name2>
            <Value2>
              <C1>300.3179</C1>
              <C2>72.0460</C2>
            </Value2>
            <Error2Radius>0.0666</Error2Radius>
          </Position2D>
        </AstroCoords>
      </ObservationLocation>
    </ObsDataLocation>
  <Description>The RA,Dec coordinates are of the type: source_object.</Description>
  </WhereWhen>
  <How>
    <Description>Swift Satellite, BAT Instrument</Description>
    <Reference uri="http://gcn.gsfc.nasa.gov/swift.html" type="url" />
  </How>
  <Why importance="0.01">
    <Inference probability="0.001">
      <Name>Noise</Name>
      <Concept>process.variation.burst;em.gamma</Concept>
    </Inference>
  </Why>
  <Description>
  </Description>
</voe:VOEvent>"""
DUMMY_VOEVENT_GCN = textwrap.dedent(DUMMY_VOEVENT_GCN).strip().encode('UTF-8')

class DummyEvent(object):
    def __init__(self, ivoid=DUMMY_EVENT_IVOID):
        self.attrib = {'ivorn': ivoid}
        self.raw_bytes = DUMMY_VOEVENT.replace(DUMMY_EVENT_IVOID, ivoid)
        self.element = etree.fromstring(self.raw_bytes)

class DummyLogObserver(object):
    def __init__(self):
        self.messages = []

    def __call__(self, logentry):
        self.messages.append(logentry['message'])

@contextmanager
def temp_dir():
    """
    Provide a context with a temporary directory. Clean it up when done.
    """
    tmpdir = tempfile.mkdtemp()
    try:
        yield tmpdir
    finally:
        shutil.rmtree(tmpdir)
