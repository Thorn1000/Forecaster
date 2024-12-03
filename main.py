import math
import time
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta


def calculate_percent_beat(outlook, yourself, others):
    slope_you = (yourself[1] - yourself[0]) / 90
    count = 0

    you_value = yourself[1] + slope_you * outlook

    for result in others:
        slope_result = (result[1] - result[0]) / 90
        result_value = result[1] + slope_result * outlook

        if you_value > result_value:
            count += 1

    percent_beat = (count / len(others)) * 100
    return percent_beat


def api_calls(api):
    time.sleep(0.6)
    response = requests.get(api, headers=headers)
    information = response.text

    return information


UA = input("Enter your main nation: ")
target = input("Enter what nation you are forecasting for: ")
target = target.lower().replace(' ', '_')
version = 0.1

headers = {
    "User-Agent": f"Forecaster/{version} (github: https://github.com/Thorn1000 ; user:{UA})"
}

ninety_days_ago = datetime.now() - timedelta(days=90)

epoch_time = int(time.mktime(ninety_days_ago.timetuple()))
days_list = [7, 30, 60, 90, 120, 180, 270, 365]
counter = 1
percent_beat_dict = {}
names = []
result_array = []

loopy = True
while loopy:
    stat = input("Enter what stat ID do you want to forecast for: ")
    url = f"https://www.nationstates.net/cgi-bin/api.cgi?q=censusname;scale={stat}"
    info = api_calls(url)
    info = info.strip('<WORLD>\n<CENSUS id="').strip(str(stat)).strip('">').strip('</CENSUS>\n')
    skip = input("Is " + info + " the stat you want to forecast y/n\n")
    if skip == 'y':
        loopy = False
    else:
        continue

url = f"https://www.nationstates.net/cgi-bin/api.cgi?nation={target};q=census;scale={stat};mode=history;from={epoch_time}"

self = api_calls(url)
root = ET.fromstring(self)
points = root.findall('.//POINT')

if points:
    first_score = points[0].find('SCORE').text
    last_score = points[-1].find('SCORE').text

    you = (float(first_score), float(last_score))
else:
    print("No POINT elements found.")

url = "https://www.nationstates.net/cgi-bin/api.cgi?q=numnations"

numNat = api_calls(url)
numNat = numNat.strip("<WORLD>\n<NUMNATIONS>").strip("</NUMNATIONS>\n</WORLD>")
numNat = int(numNat)
numNat = (math.floor(numNat * 0.01))

url = f"https://www.nationstates.net/cgi-bin/api.cgi?q=censusranks&scale={stat}&start={numNat - 19}"

neighbors = api_calls(url)
root = ET.fromstring(neighbors)

for nation in root.findall('.//NATION'):
    name = nation.find('NAME').text
    names.append(name)

url = f"https://www.nationstates.net/cgi-bin/api.cgi?q=censusranks&scale={stat}&start={numNat + 20}"
neighbors = api_calls(url)
root = ET.fromstring(neighbors)

for nation in root.findall('.//NATION'):
    name = nation.find('NAME').text
    names.append(name)

for name in names:
    print(f"Fetching {counter}/{40}: {name}")
    counter = counter + 1
    url = f"https://www.nationstates.net/cgi-bin/api.cgi?nation={name};q=census;scale={stat};mode=history;from={epoch_time}"
    xml_data = api_calls(url)

    root = ET.fromstring(xml_data)

    points = root.findall('.//POINT')

    if points:
        first_score = points[0].find('SCORE').text
        last_score = points[-1].find('SCORE').text

        results = (float(first_score), float(last_score))
        result_array.append(results)
    else:
        result_array.append((None, None))

print(f"\nProjections for {info}:")
for days in days_list:
    percent_beat_dict[days] = calculate_percent_beat(days, you, result_array)
    print(f"Percent beat after {days} days: {percent_beat_dict[days]:.2f}%")
