# utils/ayanamsa.py

from skyfield.api import load
from skyfield.positionlib import ICRF

def get_ayanamsa(ts, t):
    """
    Calculate Lahiri Ayanamsa for a given Skyfield time `t`
    """
    # Load ephemeris
    eph = load('de440.bsp')
    earth = eph['earth']
    sun = eph['sun']

    # Calculate Sun's position
    astrometric = earth.at(t).observe(sun).apparent()

    # Tropical longitude of Sun
    _, lon, _ = astrometric.ecliptic_latlon()

    # Sidereal longitude using Lahiri Ayanamsa
    # Lahiri approx = Tropical longitude - Ayanamsa
    # So Ayanamsa = Tropical longitude - Sidereal longitude
    # Reference Lahiri sidereal longitude = 0° Aries (fixed star)

    # Lahiri Ayanamsa approximation formula (by N.C. Lahiri):
    # Source: Lahiri Ephemeris / Swiss Ephemeris backend
    T = (t.tt - 2451545.0) / 36525  # Julian centuries since J2000.0
    lahiri_ayanamsa = 22.460148 + 1.396042 * T + 3.08e-4 * T**2

    return round(lahiri_ayanamsa, 6)
