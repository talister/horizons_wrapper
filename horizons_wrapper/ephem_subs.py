import logging
from datetime import datetime, timedelta, time
from math import cos, degrees, radians

from numpy import sqrt as np_sqrt
from astropy.time import Time
from astropy.table import Column
from astroquery.jplhorizons import Horizons
try:
    import pyslalib.slalib as S
except:
    pass


def horizons_ephem(obj_name, start, end, site_code, ephem_step_size='1h', alt_limit=0, quantities='1,3,4,9,19,20,23,24,38,42', include_moon=False):
    """Calls JPL HORIZONS for the specified <obj_name> producing an ephemeris
    from <start> (datetime) to <end> (datetime) for the MPC site code <site_code> with step size
    of [ephem_step_size] (defaults to '1h').
    Returns an AstroPy Table of the response with the following columns by default:
    ['targetname',
     'datetime_str',
     'datetime_jd',
     'H',
     'G',
     'solar_presence',
     'flags',
     'RA',
     'DEC',
     'RA_rate',
     'DEC_rate',
     'AZ',
     'EL',
     'V',
     'surfbright',
     'r',
     'r_rate',
     'delta',
     'delta_rate',
     'elong',
     'elongFlag',
     'alpha',
     'RSS_3sigma',
     'hour_angle',
     'datetime']
    If [include_moon] = True, 2 additional columns of the Moon-Object separation
    ('moon_sep'; in degrees) and the Moon phase ('moon_phase'; 0..1) are added
    to the table.
    The returned quantities are described in the HORIZONS docs: https://ssd.jpl.nasa.gov/?horizons_doc#specific_quantities
    and are summarized below
    1.  Astrometric RA & DEC            17. North Pole position angle & distance 33. Galactic longitude & latitude
    2.  Apparent RA & DEC               18. Heliocentric ecliptic lon. & lat.    34. Local apparent SOLAR time
    3.  Rates; RA & DEC                 19. Heliocentric range & range-rate      35. Earth->obs. site light-time
    4.  Apparent AZ & EL                20. Observer range & range-rate          36.   RA & DEC uncertainty
    5.  Rates; AZ & EL                  21. One-way (down-leg) light-time        37.   Plane-of-sky error ellipse
    6.  Satellite X & Y, pos. angle     22. Speed wrt Sun & observer             38.   POS uncertainty (RSS)
    7.  Local apparent sidereal time    23. Sun-Observer-Target ELONG angle      39.   Range & range-rate 3-sigmas
    8.  Airmass & extinction            24. Sun-Target-Observer ~PHASE angle     40.   Doppler & delay 3-sigmas
    9.  Visual mag. & Surface Brght     25. Target-Observer-Moon angle/ Illum%   41. True anomaly angle
    10. Illuminated fraction            26. Observer-Primary-Target angle        42. Local apparent hour angle
    11. Defect of illumination          27. Sun-Target radial & -vel pos. angle  43. PHASE angle & bisector
    12. Satellite angular separ/vis.    28. Orbit plane angle                    44. Apparent longitude Sun (L_s)
    13. Target angular diameter         29. Constellation ID                     45.   Inertial apparent RA & DEC
    14. Observer sub-lon & sub-lat      30. Delta-T (TDB - UT)                   46. Rate: Inertial RA & DEC
    15. Sun sub-longitude & sub-latitude  31.   Observer ecliptic lon. & lat.            
    16. Sub-Sun position angle & distance 32. North pole RA & DEC              
    """

    eph = Horizons(id=obj_name, id_type='smallbody', epochs={'start' : start.strftime("%Y-%m-%d %H:%M"),
            'stop' : end.strftime("%Y-%m-%d %H:%M"), 'step' : ephem_step_size}, location=site_code)

    airmass_limit = 99
    if alt_limit > 0:
        airmass_limit = 1.0/cos(radians(90.0 - alt_limit))

    ha_lowlimit, ha_hilimit, alt_limit = get_mountlimits(site_code)
    ha_limit = max(abs(ha_lowlimit), abs(ha_hilimit)) / 15.0
    should_skip_daylight = True

    # Need Ra/Dec rate at least
    if '3,' not in quantities:
        quantities += ',3'
    
    if len(site_code) >= 1 and site_code[0] == '-':
        # Radar site
        should_skip_daylight = False
    try:
        ephem = eph.ephemerides(quantities=quantities,
            skip_daylight=should_skip_daylight, airmass_lessthan=airmass_limit,
            max_hour_angle=ha_limit)
        ephem = convert_horizons_table(ephem, include_moon)
    except ConnectionError as e:
        logger.error("Unable to connect to HORIZONS")
    except ValueError as e:
        logger.debug("Ambiguous object, trying to determine HORIZONS id")
        ephem = None
        if e.args and len(e.args) > 0:
            choices = e.args[0].split('\n')
            horizons_id = determine_horizons_id(choices)
            logger.debug("HORIZONS id=", horizons_id)
            if horizons_id:
                try:
                    eph = Horizons(id=horizons_id, id_type='id', epochs={'start' : start.strftime("%Y-%m-%d %H:%M:%S"),
                        'stop' : end.strftime("%Y-%m-%d %H:%M:%S"), 'step' : ephem_step_size}, location=site_code)
                    ephem = eph.ephemerides(quantities=quantities,
                        skip_daylight=should_skip_daylight, airmass_lessthan=airmass_limit,
                        max_hour_angle=ha_limit)
                    ephem = convert_horizons_table(ephem, include_moon)
                except ValueError as e:
                    logger.warning("Error querying HORIZONS. Error message: {}".format(e))
            else:
                logger.warning("Unable to determine the HORIZONS id")
        else:
            logger.warning("Error querying HORIZONS. Error message: {}".format(e))
    return ephem


def convert_horizons_table(ephem, include_moon=False):
    """Modifies a passed table <ephem> from the `astroquery.jplhorizons.ephemerides()
    to add a 'datetime' column, rate columns and adds moon phase and separation
    columns (if [include_moon] is True).
    The modified Astropy Table is returned"""

    dates = Time([datetime.strptime(d, "%Y-%b-%d %H:%M") for d in ephem['datetime_str']])
    if 'datetime' not in ephem.colnames:
        ephem.add_column(dates, name='datetime')
    # Convert units of RA/Dec rate from arcsec/hr to arcsec/min and compute
    # mean rate
    ephem['RA_rate'].convert_unit_to('arcsec/min')
    ephem['DEC_rate'].convert_unit_to('arcsec/min')
    rate_units = ephem['DEC_rate'].unit
    mean_rate = np_sqrt(ephem['RA_rate']**2 + ephem['DEC_rate']**2)
    mean_rate.unit = rate_units
    ephem.add_column(mean_rate, name='mean_rate')
    if include_moon is True:
        moon_seps = []
        moon_phases = []
        for date, obj_ra, obj_dec in ephem[('datetime', 'RA', 'DEC')]:
            moon_alt, moon_obj_sep, moon_phase = calc_moon_sep(date.datetime, radians(obj_ra), radians(obj_dec), '-1')
            moon_seps.append(moon_obj_sep)
            moon_phases.append(moon_phase)
        ephem.add_columns(cols=(Column(moon_seps), Column(moon_phases)), names=('moon_sep', 'moon_phase'))

    return ephem


def determine_horizons_id(lines, now=None):
    """Attempts to determine the HORIZONS id of a target body that has multiple
    possibilities. The passed [lines] (from the .args attribute of the exception)
    are searched for the HORIZONS id (column 1) whose 'epoch year' (column 2)
    which is closest to [now] (a passed-in datetime or defaulting to datetime.utcnow()"""

    now = now or datetime.utcnow()
    timespan = timedelta.max
    horizons_id = None
    for line in lines:
        chunks = line.split()
        if len(chunks) >= 5 and chunks[0].isdigit() is True and chunks[1].isdigit() is True:
            try:
                epoch_yr = datetime.strptime(chunks[1], "%Y")
                if abs(now-epoch_yr) <= timespan:
                    # New closer match to "now"
                    horizons_id = int(chunks[0])
                    timespan = now-epoch_yr
            except ValueError:
                logger.warning("Unable to parse year of epoch from", line)
    return horizons_id


def get_mountlimits(site_code_or_name):
    """Returns the negative, positive and altitude mount limits (in degrees)
    for the LCOGT telescopes specified by <site_code_or_name>.

    <site_code_or_name> can either be a MPC site code e.g. 'V37' (=ELP 1m),
    or by designation e.g. 'OGG-CLMA-2M0A' (=FTN)"""

    site = site_code_or_name.upper()
    ha_pos_limit = 12.0 * 15.0
    ha_neg_limit = -12.0 * 15.0
    alt_limit = 25.0

    if '-1M0A' in site or site in ['V37', 'V39', 'W85', 'W86', 'W87', 'K91', 'K92', 'K93', 'Q63', 'Q64']:
        ha_pos_limit = 4.5 * 15.0
        ha_neg_limit = -4.5 * 15.0
        alt_limit = 30.0
    elif '-AQWA' in site or '-AQWB' in site or 'CLMA-0M4' in site or site in ['Z17', 'Z21', 'Q58', 'Q59', 'T03', 'T04', 'W89', 'W79', 'V38', 'L09']:
        ha_pos_limit = 4.46 * 15.0
        ha_neg_limit = -4.5 * 15.0
        alt_limit = 15.0

    return ha_neg_limit, ha_pos_limit, alt_limit
