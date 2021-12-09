import requests

from elfie_modules.backend.abstract import functionalconnector
from elfie_modules.backend.connectors import WEATHER

def getCelsiusFromKelvin(kelvin):
    return kelvin - 273

@functionalconnector(WEATHER)
def getWeather():
    appid="e46024399b538bcf3f625333391d3be4"
    url = f"https://api.openweathermap.org/data/2.5/weather?appid={appid}&q=Indore"
    response = requests.get(url).json()

    low_temp = getCelsiusFromKelvin(response['main']['temp_min']) - 2.5
    max_temp = getCelsiusFromKelvin(response['main']['temp_max']) + 2.5
    actual_temp = getCelsiusFromKelvin(response['main']['feels_like'])

    response['feedback'] = f"The weather in {response['name']} is at the high of {int(max_temp)} " \
                           f"and at the low of {int(low_temp)} Celsius. With the normal temperature of " \
                           f"%.2f" % (actual_temp)

    return response