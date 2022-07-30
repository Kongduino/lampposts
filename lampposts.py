#https://s3-ap-southeast-1.amazonaws.com/historical-resource-archive/2020/08/14/https%253A%252F%252Fwww.hko.gov.hk%252Fcommon%252Fhko_data%252Fsmart-lamppost%252Ffiles%252Fsmart_lamppost_met_device_location.json/1713
#
#http://www.weather.gov.hk/en/abouthko/opendata_intro.htm
#
#https://data.gov.hk/en-data/dataset/hk-hko-rss-smart-lamppost-weather-data
#
#https://data.gov.hk/en-data/dataset/hk-hko-rss-smart-lamppost-weather-data/resource/60867e0a-b3f9-48d9-8faf-ab30f40643fb
#
#https://www.hko.gov.hk/common/hko_data/smart-lamppost/files/smart_lamppost_met_device_location.json
#
#https://www.hko.gov.hk/common/hko_data/smart-lamppost/files/smart_lamppost_met_device_type.json
#
#https://www.hko.gov.hk/common/hko_data/smart-lamppost/files/smart_lamppost_met_device_element.json
#
#https://www.hko.gov.hk/common/hko_data/smart-lamppost/files/smart_lamppost_data_spec.pdf
#
#https://data.weather.gov.hk/weatherAPI/smart-lamppost/smart-lamppost.php?pi=DF3644&di=02
#	{"LP_NUMBER": "DF1020", "LP_LATITUDE": 22.31777, "LP_LONGITUDE": 114.171015, "LP_NORTH": 819863.5, "LP_EAST": 835664.3, "LP_TYPE": "02"}
#	{
#	  "BD": "00",
#    "DI": "04",
#    "GI": "00",
#    "PI": "DF1020",
#    "TS": "0",
#    "BODY": {
#      "HKO": {
#        "RH": "76.9",
#        "T0": "28.0",
#        "TS": "20220730130018",
#        "VN": "1.0",
#        "TP": "20220730130018"
#      }
#    }
#  }

import urllib.request, json, sys, math, re

deviceLocation = "https://www.hko.gov.hk/common/hko_data/smart-lamppost/files/smart_lamppost_met_device_location.json"
deviceType = "https://www.hko.gov.hk/common/hko_data/smart-lamppost/files/smart_lamppost_met_device_type.json"
deviceDetails = "https://www.hko.gov.hk/common/hko_data/smart-lamppost/files/smart_lamppost_met_device_element.json"
datapointsNames = {"WD": "Wind Direction", "T0": "Air Temperature", "RH": "Relative Humidity", "W0": "10-minute wind speed"}
datapointsUnits = {"WD": "°", "T0": "°", "RH": "%", "W0": " km/h"}

def toRad(x):
  return x * 3.141592653 / 180

def haversine(lat1, lon1, lat2, lon2):
  R = 6371
  x1 = lat2-lat1
  dLat = toRad(x1)
  x2 = lon2-lon1
  dLon = toRad(x2)
  a = math.sin(dLat/2) * math.sin(dLat/2) + math.cos(toRad(lat1)) * math.cos(toRad(lat2)) * math.sin(dLon/2) * math.sin(dLon/2)
  c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
  d = R * c
  return round((d + 2.220446049250313e-16) * 100) / 100

def getDetails(lp_type):
  global devices, types, details
  ln = len(types)
  dev = 0
  for i in range(0, ln):
    x = types[i]
    if lp_type == x['LP_TYPE']:
      dev = x['DEVICES'][0]
      break
  if dev == 0:
    return 0
  ln = len(details)
  dt = 0
  for i in range(0, ln):
    x = details[i]
    if lp_type == x['DEVICE_ID']:
      return x
  return 0

def closestDataPoint(lat1, lon1):
  # "LP_LATITUDE": 22.32187, "LP_LONGITUDE": 114.211365
  global devices
  dl=10000000
  dp=""
  ln = len(devices)
  for i in range(0, ln):
    x = devices[i]
    d=haversine(lat1, lon1, x['LP_LATITUDE'], x['LP_LONGITUDE'])
    if(d<dl):
      dl=d
      dp=x
      dp['distance']=dl
  return dp

def loadDicts():
  global devices, types, details
  try:
    print("\n • Loading Devices...")
    with urllib.request.urlopen(deviceLocation) as url:
      devices = json.loads(url.read().decode())
  except:
    print("\nCouldn't load device list. Aborting...")
    sys.exit()

  try:
    print(" • Loading Device Types...")
    with urllib.request.urlopen(deviceType) as url:
      types = json.loads(url.read().decode())
  except:
    print("\nCouldn't load device type list. Aborting...")
    sys.exit()

  try:
    print(" • Loading Device Details...")
    with urllib.request.urlopen(deviceDetails) as url:
      details = json.loads(url.read().decode())
  except:
    print("\nCouldn't load device details list. Aborting...")
    sys.exit()

if __name__ == "__main__":
  devices=""
  types=""
  details=""
  loadDicts()
  closest = closestDataPoint(22.3310, 114.2046)
  print("\nClosest lamp post: " + closest['LP_NUMBER'])
  print(" • coords: " + str(closest['LP_LATITUDE'])+", " + str(closest['LP_LONGITUDE']))
  print(" • distance: " + str(closest['distance'])+" km")
  lp_type = closest['LP_TYPE']
  deets = getDetails(lp_type)
  if deets == 0:
    print("Failed to get details. Aborting...")
    sys.exit()
  print(" • type: " + deets['TYPE_NAME'])
#   print(" • Datapoints:")
#   for x in deets['DATA_TYPE_COLLECTED']:
#     print("  - ["+x+"]: "+datapointsNames[x])
  logs = "https://data.weather.gov.hk/weatherAPI/smart-lamppost/smart-lamppost.php?pi="+closest['LP_NUMBER']+"&di="+lp_type;
  print(" • "+logs)
  try:
    with urllib.request.urlopen(logs) as url:
      logs = json.loads(url.read().decode())
  except:
    print("\nCouldn't load device logs. Aborting...")
    sys.exit()
  stats = logs['BODY']['HKO']
  for x in deets['DATA_TYPE_COLLECTED']:
    print(" • " + datapointsNames[x] + " = " + stats[x] + datapointsUnits[x])
  print(" • Timestamp: " + re.sub(r'(\d\d\d\d)(\d\d)(\d\d)(\d\d)(\d\d)(\d\d)', r'\1/\2/\3 \4:\5:\6', stats['TS']))
