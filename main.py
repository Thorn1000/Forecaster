import math
import time
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

UA = input("Enter your main nation: ")
target = input("Enter what nation you are forecasting for: ")
target = target.lower().replace(' ', '_')
version = 0.1

headers = {
    "User-Agent": f"Forecaster/{version} (github: https://github.com/Thorn1000 ; user:{UA})"
}

ninety_days_ago = datetime.now() - timedelta(days=90)
epoch_time = int(time.mktime(ninety_days_ago.timetuple()))

loopy = True
while loopy:
    stat = input("Enter what stat ID do you want to forecast for: ")
    url = f"https://www.nationstates.net/cgi-bin/api.cgi?q=censusname;scale={stat}"

    response = requests.get(url, headers=headers)
    time.sleep(0.6)
    info = response.text

    info = info.strip('<WORLD>\n<CENSUS id="').strip(str(stat)).strip('">').strip('</CENSUS>\n</WORLD>')

    skip = input("Is " + info + " the stat you want to forecast y/n\n")
    if skip == 'y':
        loopy = False
    else:
        continue

url = f"https://www.nationstates.net/cgi-bin/api.cgi?nation={target};q=census;scale={stat};mode=history;from={epoch_time}"
respond = requests.get(url, headers=headers)
self = respond.text
root = ET.fromstring(self)

points = root.findall('.//POINT')

if points:
    first_score = points[0].find('SCORE').text
    last_score = points[-1].find('SCORE').text

    you = (float(first_score), float(last_score))
else:
    print("No POINT elements found.")

url = "https://www.nationstates.net/cgi-bin/api.cgi?q=numnations"
response = requests.get(url, headers=headers)
time.sleep(0.6)
numNat = response.text

numNat = numNat.strip("<WORLD>\n<NUMNATIONS>").strip("</NUMNATIONS>\n</WORLD>")
numNat = int(numNat)
numNat = (math.floor(numNat*0.01))

names = []

url = f"https://www.nationstates.net/cgi-bin/api.cgi?q=censusranks&scale={stat}&start={numNat - 19}"
response = requests.get(url, headers=headers)
time.sleep(0.6)
neighbors = response.text
root = ET.fromstring(neighbors)

for nation in root.findall('.//NATION'):
    name = nation.find('NAME').text
    names.append(name)

url = f"https://www.nationstates.net/cgi-bin/api.cgi?q=censusranks&scale={stat}&start={numNat + 20}"
response = requests.get(url, headers=headers)
time.sleep(0.6)
neighbors = response.text
root = ET.fromstring(neighbors)

for nation in root.findall('.//NATION'):
    name = nation.find('NAME').text
    names.append(name)


result_array = []
counter = 1

for name in names:
    print(f"Fetching {counter}/{40}: {name}")
    counter = counter + 1
    url = f"https://www.nationstates.net/cgi-bin/api.cgi?nation={name};q=census;scale={stat};mode=history;from={epoch_time}"
    response = requests.get(url, headers=headers)
    time.sleep(0.6)
    xml_data = response.text

    root = ET.fromstring(xml_data)

    points = root.findall('.//POINT')

    if points:
        first_score = points[0].find('SCORE').text
        last_score = points[-1].find('SCORE').text

        results = (float(first_score), float(last_score))
        result_array.append(results)
    else:
        result_array.append((None, None))

slope_you = (you[1] - you[0]) / 90

count_7_days = 0
count_30_days = 0
count_60_days = 0
count_90_days = 0

for result in result_array:
    slope_result = (result[1] - result[0]) / 90

    you_7 = you[1] + slope_you * 7
    you_30 = you[1] + slope_you * 30
    you_60 = you[1] + slope_you * 60
    you_90 = you[1] + slope_you * 90

    result_7 = result[1] + slope_result * 7
    result_30 = result[1] + slope_result * 30
    result_60 = result[1] + slope_result * 60
    result_90 = result[1] + slope_result * 90

    if you_7 > result_7:
        count_7_days += 1
    if you_30 > result_30:
        count_30_days += 1
    if you_60 > result_60:
        count_60_days += 1
    if you_90 > result_90:
        count_90_days += 1

total_results = len(result_array)
percent_7_days = (count_7_days / total_results) * 100
percent_30_days = (count_30_days / total_results) * 100
percent_60_days = (count_60_days / total_results) * 100
percent_90_days = (count_90_days / total_results) * 100

print(f"\nPercent beat after 7 days: {percent_7_days:.2f}%")
print(f"Percent beat after 30 days: {percent_30_days:.2f}%")
print(f"Percent beat after 60 days: {percent_60_days:.2f}%")
print(f"Percent beat after 90 days: {percent_90_days:.2f}%")
