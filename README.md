# Lamp Posts Contest

Here are 3 JSON files: the list of smart lampposts in HK, with details. Pick a GPS location under the form 22.271046, 114.186849 (not my location!) and parse the JSON file to get the closest lamppost. Pick the language you want. No libraries.

* [Devices Location](https://www.hko.gov.hk/common/hko_data/smart-lamppost/files/smart_lamppost_met_device_location.json)

* [Devices Types](https://www.hko.gov.hk/common/hko_data/smart-lamppost/files/smart_lamppost_met_device_type.json)

* [Devices Details](https://www.hko.gov.hk/common/hko_data/smart-lamppost/files/smart_lamppost_met_device_element.json)

The possible datapoints are:

```JSON
{
  "WD": "Wind Direction",
  "T0": "Air Temperature",
  "RH": "Relative Humidity",
  "W0": "10-minute wind speed"
}
```

Pick GPS coordinates within HK, and find the closest lamp post to that position. Get as much info as possible from the lamp post as you can. Something like this:

```sh
python3 lampposts.py

 • Loading Devices...
 • Loading Device Types...
 • Loading Device Details...

Closest lamp post: DF3644
 • coords: 22.331033, 114.204639
 • distance: 0.01 km
 • type: Full Suite Plus
 • https://data.weather.gov.hk/weatherAPI/smart-lamppost/smart-lamppost.php?pi=DF3644&di=01
 • Air Temperature = 32.3°
 • Relative Humidity = 69.4%
 • 10-minute wind speed = 0.53 km/h
 • Wind Direction = 4°
 • Timestamp: 2022/07/30 16:50:47
```