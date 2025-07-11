ZODIAC_SIGNS = [
    'Aries', 'Taurus', 'Gemini', 'Cancer',
    'Leo', 'Virgo', 'Libra', 'Scorpio',
    'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
]

def generate_rasi_chart(planets):
    chart = {sign: [] for sign in ZODIAC_SIGNS}
    for p in planets:
        sign = p['sign']
        deg = p.get('degree', 0)
        label = f"{p['name']} ({deg:.4f}\u00b0)"
        chart[sign].append(label)
    
    # ✅ Add center box with label 'ராசி'
    chart['Center'] = ['ராசி']
    
    return chart

def generate_rasi_chart(planets):
    chart = {sign: [] for sign in ZODIAC_SIGNS}
    for p in planets:
        sign = p['sign']
        deg = p.get('degree', 0)
        label = f"{p['name']} ({deg}\u00b0)"
        chart[sign].append(label)
    return chart
