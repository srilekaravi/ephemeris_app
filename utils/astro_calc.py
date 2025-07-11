import os
import math
import pytz
from datetime import datetime
import swisseph as swe
from skyfield.api import load, Topos
from opencage.geocoder import OpenCageGeocode

OPENCAGE_API_KEY = "ea484554055445888e89a4f95b93d415"

def get_lat_lon(place_name):
    geocoder = OpenCageGeocode(OPENCAGE_API_KEY)
    result = geocoder.geocode(place_name)
    if result and len(result):
        return result[0]['geometry']['lat'], result[0]['geometry']['lng']
    raise Exception("Location not found")


# 🌗 Ayanamsa values
def get_ayanamsa(deg, method="lahiri"):
    return {
        "lahiri": 24.35,
        "raman": 22.56,
        "kp": 23.75,
        "fagan": 24.83
    }.get(method, 24.35)

# 🐚 Tamil Sign Names
TAMIL_SIGNS = [
    "மேஷம்", "ரிஷபம்", "மிதுனம்", "கடகம்", "சிம்மம்", "கன்னி",
    "துலாம்", "விருச்சிகம்", "தனுசு", "மகரம்", "கும்பம்", "மீனம்"
]

# 🔱 Lagna Lords
LAGNA_LORDS = {
    0: 'Mars', 1: 'Venus', 2: 'Mercury', 3: 'Moon', 4: 'Sun', 5: 'Mercury',
    6: 'Venus', 7: 'Mars', 8: 'Jupiter', 9: 'Saturn', 10: 'Saturn', 11: 'Jupiter'
}

# 🌌 Nakshatra List
NAKSHATRAS = [
    "அசுவினி", "பரணி", "கிருத்திகை", "ரோஹிணி", "மிருகசீரிடம்", "திருவாதிரை",
    "புனர்பூசம்", "பூசம்", "ஆயில்யம்", "மகம்", "பூரம்", "உத்திரம்",
    "அஸ்தம்", "சித்திரை", "சுவாதி", "விசாகம்", "அனுஷம்", "கேட்டை",
    "மூலம்", "பூராடம்", "உத்திராடம்", "திருஒணம்", "அவிட்டம்", "சதயம்", "பூரட்டாதி", "உத்திரட்டாதி", "ரேவதி"
]


# 📌 Calculate Lagna (Ascendant)
def calculate_lagna_info(date_str, time_str, place_name, timezone_str='Asia/Kolkata'):
    # Convert to UTC datetime
    local_tz = pytz.timezone(timezone_str)
    dt_local = local_tz.localize(datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M"))
    dt_utc = dt_local.astimezone(pytz.utc)

    year = dt_utc.year
    month = dt_utc.month
    day = dt_utc.day
    hour = dt_utc.hour + dt_utc.minute / 60.0

    # 🌍 Get Coordinates
    lat, lon = get_lat_lon(place_name)

    # 📘 Swiss Ephemeris Setup
    swe.set_ephe_path(os.path.join(os.getcwd(), 'swisseph'))
    swe.set_sid_mode(swe.SIDM_LAHIRI)

    # 📆 Julian Day
    jd = swe.julday(year, month, day, hour)
    flag = swe.FLG_SIDEREAL
    ascmc = swe.houses_ex(jd, lat, lon, b'A', flag)[0]
    lagna_deg = ascmc[0]

    sign_index = int(lagna_deg // 30)
    sign_degree = lagna_deg % 30
    rasi_name = TAMIL_SIGNS[sign_index]
    lagna_lord = LAGNA_LORDS[sign_index]

    nak_deg = lagna_deg % 360
    nak_index = int(nak_deg // (360 / 27))
    pada = int((nak_deg % (360 / 27)) // (3.3333)) + 1
    nakshatra = NAKSHATRAS[nak_index]

    ayanamsa_val = swe.get_ayanamsa_ut(jd)

    navamsa_sign, navamsa_deg = calculate_navamsa_details(lagna_deg)


    return {
        "lagna_degree": round(lagna_deg, 4),
        "rasi_name": rasi_name,
        "sign_index": sign_index + 1,
        "sign_degree": round(sign_degree, 4),
        "navamsa_sign": navamsa_sign,
        "navamsa_degree": navamsa_deg,
        "nakshatra": nakshatra,
        "pada": pada,
        "lagna_lord": lagna_lord,
        "latitude": lat,
        "longitude": lon,
        "ayanamsa": round(ayanamsa_val, 4)
    }

# ☊ Rahu and Ketu
def calculate_rahu_ketu(ts, t, ayanamsa_method="lahiri"):
    JD = t.tt
    T = (JD - 2451545.0) / 36525.0
    mean_rahu = (125.04452 - 1934.136261 * T) % 360
    mean_ketu = (mean_rahu + 180) % 360

    nodes = []
    for name, deg in [('Rahu', mean_rahu), ('Ketu', mean_ketu)]:
        sidereal = (deg - get_ayanamsa(deg, ayanamsa_method)) % 360
        sign_index = int(sidereal // 30)
        sign_name = TAMIL_SIGNS[sign_index]
        sign_deg = sidereal % 30

        navamsa_sign, navamsa_deg = calculate_navamsa_details(sidereal)

        nodes.append({
            "name": name,
            "degree": round(sidereal, 4),
            "sign": sign_name,
            "sign_degree": round(sign_deg, 4),
            "navamsa_sign": navamsa_sign,
            "navamsa_degree": navamsa_deg,
            "retrograde": "✔️",  # Always retrograde for nodes
            "speed": 0
        })

    return nodes
def calculate_navamsa_details(degree):
    sign_index = int(degree // 30)
    sign_degree = degree % 30
    navamsa_index = int(sign_degree // (30 / 9))

    # Navamsa sign is (sign_index * 9 + navamsa_index) % 12
    navamsa_sign_index = (sign_index * 9 + navamsa_index) % 12
    navamsa_sign_name = TAMIL_SIGNS[navamsa_sign_index]
    navamsa_degree = (sign_degree % (30 / 9)) * 9

    return navamsa_sign_name, round(navamsa_degree, 4)

# 🪐 Planetary Positions (Skyfield)
def calculate_planet_positions(date_str, time_str, latitude, longitude, ayanamsa_method="lahiri"):
    ts = load.timescale()
    year, month, day = map(int, date_str.split('-'))
    hour, minute = map(int, time_str.split(':'))
    t = ts.utc(year, month, day, hour, minute)

    eph = load('de440s.bsp')
    observer = eph['earth'] + Topos(latitude_degrees=latitude, longitude_degrees=longitude)

    planet_keys = {
        'Sun': 'sun',
        'Moon': 'moon',
        'Mercury': 'mercury',
        'Venus': 'venus',
        'Mars': 'mars barycenter',
        'Jupiter': 'jupiter barycenter',
        'Saturn': 'saturn barycenter',
        'Uranus': 'uranus barycenter',
        'Neptune': 'neptune barycenter',
        'Pluto': 'pluto barycenter'
    }

    planet_data = []

    for name, key in planet_keys.items():
        planet = eph[key]
        astrometric = observer.at(t).observe(planet)
        apparent = astrometric.apparent()
        eclip = apparent.ecliptic_latlon()
        degree = eclip[1].degrees

        # Ayanamsa and sidereal calculation
        ayanamsa_val = get_ayanamsa(degree, ayanamsa_method)
        sidereal = (degree - ayanamsa_val) % 360
        sign_index = int(sidereal // 30)
        sign_name = TAMIL_SIGNS[sign_index]
        sign_deg = sidereal % 30

        # Retrograde and speed
        pos_now = degree
        pos_future = observer.at(t + 1).observe(planet).apparent().ecliptic_latlon()[1].degrees
        retrograde = pos_future < pos_now
        speed = abs(pos_future - pos_now)

        # Navamsa
        navamsa_sign, navamsa_deg = calculate_navamsa_details(sidereal)

        # Add to list
        planet_data.append({
            "name": name,
            "degree": round(sidereal, 4),
            "sign": sign_name,
            "sign_degree": round(sign_deg, 4),
            "navamsa_sign": navamsa_sign,
            "navamsa_degree": navamsa_deg,
            "retrograde": "✔️" if retrograde else "❌",
            "speed": round(speed, 6)
        })



    # Add Rahu & Ketu
    planet_data.extend(calculate_rahu_ketu(ts, t, ayanamsa_method))

    return planet_data, get_ayanamsa(0, ayanamsa_method)


