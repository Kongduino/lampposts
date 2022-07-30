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
import gmplot

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
    if dev == x['DEVICE_ID']:
      x['dev'] = dev
      return x
  return 0

def closestDataPoint(lat1, lon1):
  global devices, latitude_list, longitude_list
  # We are going to compute the box that encloses all points
  minLat = 100000
  maxLat = -100000
  minLng = 100000
  maxLng = -100000
  dl=10000000
  dp=""
  ln = len(devices)
  for i in range(0, ln):
    x = devices[i]
    lat = x['LP_LATITUDE']
    lng = x['LP_LONGITUDE']
    # calculate the 4 corners
    if lat<minLat:
      minLat = lat
    if lat>maxLat:
      maxLat = lat
    if lng<minLng:
      minLng = lng
    if lng>maxLng:
      maxLng = lng
    # add the current lam post to the list
    latitude_list.append(lat)
    longitude_list.append(lng)
    
    # calculate distance with the reference coords
    d=haversine(lat1, lon1, lat , lng)
    if(d<dl):
      dl=d
      dp=x
      dp['distance']=dl
  # return the closest point with "extras"
  dp['minLat'] = minLat
  dp['maxLat'] = maxLat
  dp['minLng'] = minLng
  dp['maxLng'] = maxLng
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
  latitude_list = []
  longitude_list = []
  loadDicts()
  print(devices)
  myLat = 22.405140
  myLng = 114.139799
  closest = closestDataPoint(myLat, myLng)
  # calculate the center point from the 4 corners
  centerPointLat = (closest['maxLat'] + closest['minLat']) / 2
  centerPointLng = (closest['maxLng'] + closest['minLng']) / 2
  # prepare a gmap with the center point
  gmap1 = gmplot.GoogleMapPlotter(centerPointLat, centerPointLng, 13)
  # scatter the lamp posts
  gmap1.scatter(latitude_list, longitude_list, '#FF0000', size = 50, marker = True)
  # draw the map as HTML
  gmap1.draw("mymap.html")
  # Display results
  print("\nClosest lamp post: " + closest['LP_NUMBER'])
  print(" • coords: " + str(closest['LP_LATITUDE'])+", " + str(closest['LP_LONGITUDE']))
  print(" • distance: " + str(closest['distance'])+" km")
  lp_type = closest['LP_TYPE']
  deets = getDetails(lp_type)
  if deets == 0:
    print("Failed to get details. Aborting...")
    sys.exit()
  print(deets)
  dev_type = deets['dev']
  print(" • type: " + deets['TYPE_NAME'])
  logs = "https://data.weather.gov.hk/weatherAPI/smart-lamppost/smart-lamppost.php?pi="+closest['LP_NUMBER']+"&di="+dev_type;
  print(" • "+logs)
  result = ""
  # get the current datapoints
  try:
    with urllib.request.urlopen(logs) as url:
      result = url.read().decode()
      logs = json.loads(result)
  except:
    print("\nCouldn't load device logs. Aborting...")
    sys.exit()
  try:
    stats = logs['BODY']['HKO']
  except:
    print("JSON Error")
    print(result)
    sys.exit()
  for x in deets['DATA_TYPE_COLLECTED']:
    print(" • " + datapointsNames[x] + " = " + stats[x] + datapointsUnits[x])
  print(" • Timestamp: " + re.sub(r'(\d\d\d\d)(\d\d)(\d\d)(\d\d)(\d\d)(\d\d)', r'\1/\2/\3 \4:\5:\6', stats['TS']))
