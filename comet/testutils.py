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
<?xml version = "1.0" encoding = "UTF-8"?>
<voe:VOEvent
      ivorn="ivo://nasa.gsfc.gcn/SWIFT#BAT_QuickLook_Pos_1031728-518"
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
    <Date>2021-02-10T02:00:38</Date>
    <Description>This VOEvent message was created with GCN VOE version: 15.05 18nov20</Description>
  </Who>
  <What>
    <Param name="Packet_Type"   value="97" />
    <Param name="Pkt_Ser_Num"   value="1" />
    <Param name="TrigID"        value="1031728" ucd="meta.id" />
    <Param name="Segment_Num"   value="0" ucd="meta.id.part" />
    <Param name="Burst_TJD"     value="19255" unit="days" ucd="time" />
    <Param name="Burst_SOD"     value="7227.92" unit="sec" ucd="time" />
    <Param name="AT_Slew_Flags" value="0x3" />
    <Param name="Misc_flags"    value="0x0" />
    <Param name="Rate_Signif"   value="16.24" unit="sigma" ucd="stat.snr" />
    <Param name="SC_Long"       value="0.00" unit="deg" ucd="pos.earth.lon" />
    <Param name="SC_Lat"        value="0.00" unit="deg" ucd="pos.earth.lat" />
    <Group name="Misc_Flags" >
      <Param name="Values_Out_of_Range"      value="false" />
      <Param name="Near_Bright_Star"         value="false" />
      <Param name="Err_Circle_in_Galaxy"     value="false" />
      <Param name="Galaxy_in_Err_Circle"     value="false" />
      <Param name="TOO_Generated"            value="false" />
      <Param name="CRC_Error"                value="false" />
    </Group>
    <Param name="Coords_Type"   value="1" unit="dn" />
    <Param name="Coords_String" value="source_object" />
    <Group name="Obs_Support_Info" >
      <Description>The Sun and Moon values are valid at the time the VOEvent XML message was created.</Description>
      <Param name="Sun_RA"        value="323.93" unit="deg" ucd="pos.eq.ra" />
      <Param name="Sun_Dec"       value="-14.32" unit="deg" ucd="pos.eq.dec" />
      <Param name="Sun_Distance"  value="66.81" unit="deg" ucd="pos.angDistance" />
      <Param name="Sun_Hr_Angle"  value="4.06" unit="hr" />
      <Param name="Moon_RA"       value="303.40" unit="deg" ucd="pos.eq.ra" />
      <Param name="Moon_Dec"      value="-23.48" unit="deg" ucd="pos.eq.dec" />
      <Param name="MOON_Distance" value="54.85" unit="deg" ucd="pos.angDistance" />
      <Param name="Moon_Illum"    value="3.35" unit="%" ucd="arith.ratio" />
      <Param name="Galactic_Long" value="37.58" unit="deg" ucd="pos.galactic.lon" />
      <Param name="Galactic_Lat"  value="24.24" unit="deg" ucd="pos.galactic.lat" />
      <Param name="Ecliptic_Long" value="261.18" unit="deg" ucd="pos.ecliptic.lon" />
      <Param name="Ecliptic_Lat"  value="37.87" unit="deg" ucd="pos.ecliptic.lat" />
    </Group>
    <Description>Type=97: The Swift-BAT instrument quick-look position notice.</Description>
  </What>
  <WhereWhen>
    <ObsDataLocation>
      <ObservatoryLocation id="GEOLUN" />
      <ObservationLocation>
        <AstroCoordSystem id="UTC-FK5-GEO" />
        <AstroCoords coord_system_id="UTC-FK5-GEO">
          <Time unit="s">
            <TimeInstant>
              <ISOTime>2021-02-10T02:00:27.92</ISOTime>
            </TimeInstant>
          </Time>
          <Position2D unit="deg">
            <Name1>RA</Name1>
            <Name2>Dec</Name2>
            <Value2>
              <C1>262.8109</C1>
              <C2>14.6481</C2>
            </Value2>
            <Error2Radius>0.0500</Error2Radius>
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
  <Why importance="0.90">
    <Inference probability="0.90">
      <Name>GRB 210210</Name>
      <Concept>process.variation.burst;em.gamma</Concept>
    </Inference>
  </Why>
  <Description>
  </Description>
</voe:VOEvent>
"""
DUMMY_VOEVENT_GCN = textwrap.dedent(DUMMY_VOEVENT_GCN).strip().encode('UTF-8')


DUMMY_VOEVENT_LIGO = u"""
<?xml version="1.0" encoding="UTF-8"?>
<voe:VOEvent xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:voe="http://www.ivoa.net/xml/VOEvent/v2.0" xsi:schemaLocation="http://www.ivoa.net/xml/VOEvent/v2.0 http://www.ivoa.net/xml/VOEvent/VOEvent-v2.0.xsd" version="2.0" role="observation" ivorn="ivo://gwnet/LVC#S191225aq-1-Preliminary">
  <Who>
    <Date>2019-12-25T21:59:57</Date>
    <Author>
      <contactName>LIGO Scientific Collaboration and Virgo Collaboration</contactName>
    </Author>
  </Who>
  <What>
    <Param dataType="int" name="Packet_Type" value="150">
      <Description>The Notice Type number is assigned/used within GCN, eg type=150 is an LVC_PRELIMINARY notice</Description>
    </Param>
    <Param dataType="int" name="internal" value="0">
      <Description>Indicates whether this event should be distributed to LSC/Virgo members only</Description>
    </Param>
    <Param dataType="int" name="Pkt_Ser_Num" value="1">
      <Description>A number that increments by 1 each time a new revision is issued for this event</Description>
    </Param>
    <Param dataType="string" name="GraceID" ucd="meta.id" value="S191225aq">
      <Description>Identifier in GraceDB</Description>
    </Param>
    <Param dataType="string" name="AlertType" ucd="meta.version" value="Preliminary">
      <Description>VOEvent alert type</Description>
    </Param>
    <Param dataType="int" name="HardwareInj" ucd="meta.number" value="0">
      <Description>Indicates that this event is a hardware injection if 1, no if 0</Description>
    </Param>
    <Param dataType="int" name="OpenAlert" ucd="meta.number" value="1">
      <Description>Indicates that this event is an open alert if 1, no if 0</Description>
    </Param>
    <Param dataType="string" name="EventPage" ucd="meta.ref.url" value="https://gracedb.ligo.org/superevents/S191225aq/view/">
      <Description>Web page for evolving status of this GW candidate</Description>
    </Param>
    <Param dataType="string" name="Instruments" ucd="meta.code" value="L1,V1">
      <Description>List of instruments used in analysis to identify this event</Description>
    </Param>
    <Param dataType="float" name="FAR" ucd="arith.rate;stat.falsealarm" unit="Hz" value="1.26701833689754e-08">
      <Description>False alarm rate for GW candidates with this strength or greater</Description>
    </Param>
    <Param dataType="string" name="Group" ucd="meta.code" value="CBC">
      <Description>Data analysis working group</Description>
    </Param>
    <Param dataType="string" name="Pipeline" ucd="meta.code" value="pycbc">
      <Description>Low-latency data analysis pipeline</Description>
    </Param>
    <Param dataType="string" name="Search" ucd="meta.code" value="AllSky">
      <Description>Specific low-latency search</Description>
    </Param>
    <Group name="GW_SKYMAP" type="GW_SKYMAP">
      <Param dataType="string" name="skymap_fits" ucd="meta.ref.url" value="https://gracedb.ligo.org/api/superevents/S191225aq/files/bayestar.fits.gz,0">
        <Description>Sky Map FITS</Description>
      </Param>
    </Group>
    <Group name="Classification" type="Classification">
      <Param dataType="float" name="BNS" ucd="stat.probability" value="0.0">
        <Description>Probability that the source is a binary neutron star merger (both objects lighter than 3 solar masses)</Description>
      </Param>
      <Param dataType="float" name="NSBH" ucd="stat.probability" value="0.0">
        <Description>Probability that the source is a neutron star-black hole merger (primary heavier than 5 solar masses, secondary lighter than 3 solar masses)</Description>
      </Param>
      <Param dataType="float" name="BBH" ucd="stat.probability" value="0.8412799372226022">
        <Description>Probability that the source is a binary black hole merger (both objects heavier than 5 solar masses)</Description>
      </Param>
      <Param dataType="float" name="MassGap" ucd="stat.probability" value="0.0">
        <Description>Probability that the source has at least one object between 3 and 5 solar masses</Description>
      </Param>
      <Param dataType="float" name="Terrestrial" ucd="stat.probability" value="0.1587200627773978">
        <Description>Probability that the source is terrestrial (i.e., a background noise fluctuation or a glitch)</Description>
      </Param>
      <Description>Source classification: binary neutron star (BNS), neutron star-black hole (NSBH), binary black hole (BBH), MassGap, or terrestrial (noise)</Description>
    </Group>
    <Group name="Properties" type="Properties">
      <Param dataType="float" name="HasNS" ucd="stat.probability" value="0.0">
        <Description>Probability that at least one object in the binary has a mass that is less than 3 solar masses</Description>
      </Param>
      <Param dataType="float" name="HasRemnant" ucd="stat.probability" value="0.0">
        <Description>Probability that a nonzero mass was ejected outside the central remnant object</Description>
      </Param>
      <Description>Qualitative properties of the source, conditioned on the assumption that the signal is an astrophysical compact binary merger</Description>
    </Group>
  </What>
  <WhereWhen>
    <ObsDataLocation>
      <ObservatoryLocation id="LIGO Virgo"/>
      <ObservationLocation>
        <AstroCoordSystem id="UTC-FK5-GEO"/>
        <AstroCoords coord_system_id="UTC-FK5-GEO">
          <Time unit="s">
            <TimeInstant>
              <ISOTime>2019-12-25T21:57:15.870117</ISOTime>
            </TimeInstant>
          </Time>
        </AstroCoords>
      </ObservationLocation>
    </ObsDataLocation>
  </WhereWhen>
  <Description>Report of a candidate gravitational wave event</Description>
  <How>
    <Description>Candidate gravitational wave event identified by low-latency analysis</Description>
    <Description>V1: Virgo 3 km gravitational wave detector</Description>
    <Description>L1: LIGO Livingston 4 km gravitational wave detector</Description>
  </How>
</voe:VOEvent>
"""
DUMMY_VOEVENT_LIGO = textwrap.dedent(DUMMY_VOEVENT_LIGO).strip().encode('UTF-8')

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
