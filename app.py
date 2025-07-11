from flask import Flask, render_template, request
from utils.astro_calc import get_lat_lon, calculate_planet_positions, calculate_lagna_info
from utils.tamil_utils import TAMIL_SIGNS, TAMIL_PLANETS

app = Flask(__name__)

# Shared memory for charts
latest_data = {}

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        date_str = request.form['date']
        time_str = request.form['time']
        place = request.form['place']
        ayanamsa = request.form['ayanamsa']

        try:
            # Get coordinates
            latitude, longitude = get_lat_lon(place)

            # Planet positions
            planet_data, ayanamsa_val = calculate_planet_positions(
                date_str, time_str, latitude, longitude, ayanamsa
            )

            # Lagna calculation
            lagna_data = calculate_lagna_info(date_str, time_str, place)

            # ✅ Add Lagna to planet list
            planet_data.append({
                "name": "lagna",  # Use lowercase key for mapping
                "degree": lagna_data["lagna_degree"],
                "sign": lagna_data["rasi_name"],
                "sign_degree": lagna_data["sign_degree"],
                "navamsa_sign": lagna_data.get("navamsa_sign", ""),
                "navamsa_degree": lagna_data.get("navamsa_degree", ""),
                "retrograde": "",
                "speed": ""
            })

            # ✅ Translate planet names to Tamil
            for planet in planet_data:
                name = planet["name"].lower()
                if name in TAMIL_PLANETS:
                    planet["name"] = TAMIL_PLANETS[name]

            # ✅ Build navamsa chart
            navamsa_chart = {}
            for planet in planet_data:
                sign = planet.get("navamsa_sign")
                degree = planet.get("navamsa_degree")
                if sign and degree is not None:
                    navamsa_chart.setdefault(sign, []).append((planet["name"], degree))

            # ✅ Store data for chart routes
            latest_data['planet_data'] = planet_data
            latest_data['ayanamsa'] = ayanamsa_val
            latest_data['date'] = date_str
            latest_data['time'] = time_str
            latest_data['place'] = place
            latest_data['lagna_data'] = lagna_data
            latest_data['navamsa_chart'] = navamsa_chart

            # ✅ Render result
            return render_template('result.html',
                                   planet_data=planet_data,
                                   ayanamsa=ayanamsa_val,
                                   lagna_data=lagna_data,
                                   date=date_str,
                                   time=time_str,
                                   place=place,
                                   navamsa_chart=navamsa_chart,
                                   TAMIL_SIGNS=TAMIL_SIGNS)

        except Exception as e:
            return f"Error: {e}"

    return render_template('index.html')


@app.route('/rasi-kattam')
def rasi_kattam():
    return render_template('rasi_kattam.html',
                           planet_data=latest_data.get('planet_data', []),
                           lagna_data=latest_data.get('lagna_data', {}))


@app.route('/navamsa-chart')
def navamsa_chart():
    navamsa_chart = latest_data.get('navamsa_chart', {})
    date = latest_data.get('date', '')
    time = latest_data.get('time', '')
    place = latest_data.get('place', '')

    return render_template(
        'navamsa_charts.html',
        navamsa_chart=navamsa_chart,
        TAMIL_SIGNS=TAMIL_SIGNS,
        date=date,
        time=time,
        place=place
    )


if __name__ == '__main__':
    app.run(debug=True, port=5002)
