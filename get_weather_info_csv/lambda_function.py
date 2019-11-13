import requests
import json
import csv
import configparser

ini = configparser.ConfigParser()
ini.read('./settings.ini', 'UTF-8')
URL_CURRENT  = ini['openweathermap']['url_current']  # current weather data
URL_FORECAST = ini['openweathermap']['url_forecast'] # 5 day / 3 hour forecast data
API_KEY = ini['openweathermap']['api_key']
CSV_HEADER = [
    'coord.lon', # City geo location, longitude
    'coord.lat', # City geo location, latitude
    'weather.id', # Weather condition id
    'weather.main', # Group of weather parameters (Rain, Snow, Extreme etc.)
    'weather.description', # Weather condition within the group
    'weather.icon', # Weather icon id
    'base', #  Internal parameter
    'main.temp', # Temperature. Unit Default: Kelvin, Metric: Celsius, Imperial: Fahrenheit.
    'main.pressure', # Atmospheric pressure (on the sea level, if there is no sea_level or grnd_level　data), hPa
    'main.humidity', # Humidity, %
    'main.temp_min', # Minimum temperature at the moment. This is deviation from current temp that is possible for large cities and megalopolises geographically expanded (use these parameter optionally). 'Unit Default: Kelvin, Metric: Celsius, Imperial: Fahrenheit.
    'main.temp_max', # Maximum temperature at the moment. This is deviation from current temp that is possible for large cities and megalopolises geographically expanded (use these parameter optionally). 'Unit Default: Kelvin, Metric: Celsius, Imperial: Fahrenheit.
    'main.sea_level', # Atmospheric pressure on the sea level, hPa
    'main.grnd_level', # Atmospheric pressure on the ground level, hPa
    'wind.speed', # Wind speed. Unit Default: meter/sec, Metric: meter/sec, Imperial: miles/hour.
    'wind.deg', # Wind direction, degrees (meteorological)
    'clouds.all', # Cloudiness, %
    'rain.1h', # Rain volume for the last 1 hour, mm
    'rain.3h', # Rain volume for the last 3 hours, mm
    'snow.1h', # Snow volume for the last 1 hour, mm
    'snow.3h', # Snow volume for the last 3 hours, mm
    'dt', # Time of data calculation, unix, UTC
    'sys.type', # Internal parameter
    'sys.id', # Internal parameter
    'sys.message', # Internal parameter
    'sys.country', # Country code (GB, JP etc.)
    'sys.sunrise', # Sunrise time, unix, UTC
    'sys.sunset', # Sunset time, unix, UTC
    'timezone', # Shift in seconds from UTC
    'id', # City ID
    'name', # City name
    'cod', # Internal parameter
]

def call_api(url, api_key, city_id):
    '''
    OpenWeatherMapのAPIを呼び出す
    '''
    res = requests.get(url + '&id=' + city_id + '&APPID=' + api_key)
    if res.status_code == 200:
        return True,  res.json()
    else:
        return False, res.json()

def lambda_handler(event, context):
    '''
    OpenWeatherMapから気象情報を取得する
    '''
    city_id = event.get('queryStringParameters', {}).get('id') if event is not None else None

    if city_id:
        c_result, c_response = call_api(URL_CURRENT, API_KEY, city_id)
        f_result, f_response = call_api(URL_FORECAST, API_KEY, city_id)
        if c_result and f_result:
            c_record = [
                c_response.get('coord', {}).get('lon'),
                c_response.get('coord', {}).get('lat'),
                c_response.get('weather', [])[0].get('id'),
                c_response.get('weather', [])[0].get('main'),
                c_response.get('weather', [])[0].get('description'),
                c_response.get('weather', [])[0].get('icon'),
                c_response.get('base'),
                c_response.get('main', {}).get('temp'),
                c_response.get('main', {}).get('pressure'),
                c_response.get('main', {}).get('humidity'),
                c_response.get('main', {}).get('temp_min'),
                c_response.get('main', {}).get('temp_max'),
                c_response.get('main', {}).get('sea_level'),
                c_response.get('main', {}).get('grnd_level'),
                c_response.get('wind', {}).get('speed'),
                c_response.get('wind', {}).get('deg'),
                c_response.get('clouds', {}).get('all'),
                c_response.get('rain', {}).get('1h'),
                c_response.get('rain', {}).get('3h'),
                c_response.get('snow', {}).get('1h'),
                c_response.get('snow', {}).get('3h'),
                c_response.get('dt'),
                c_response.get('sys', {}).get('type'),
                c_response.get('sys', {}).get('id'),
                c_response.get('sys', {}).get('message'),
                c_response.get('sys', {}).get('country'),
                c_response.get('sys', {}).get('sunrise'),
                c_response.get('sys', {}).get('sunset'),
                c_response.get('timezone'),
                c_response.get('id'),
                c_response.get('name'),
                c_response.get('cod'),
            ]
            f_records_str = ''
            for line in f_response.get('list'):
                rec = [
                    f_response.get('city', {}).get('coord', {}).get('lon'),
                    f_response.get('city', {}).get('coord', {}).get('lat'),
                    line.get('weather', [])[0].get('id'),
                    line.get('weather', [])[0].get('main'),
                    line.get('weather', [])[0].get('description'),
                    line.get('weather', [])[0].get('icon'),
                    None,
                    line.get('main', {}).get('temp'),
                    line.get('main', {}).get('pressure'),
                    line.get('main', {}).get('humidity'),
                    line.get('main', {}).get('temp_min'),
                    line.get('main', {}).get('temp_max'),
                    line.get('main', {}).get('sea_level'),
                    line.get('main', {}).get('grnd_level'),
                    line.get('wind', {}).get('speed'),
                    line.get('wind', {}).get('deg'),
                    line.get('clouds', {}).get('all'),
                    None,
                    line.get('rain', {}).get('3h'),
                    None,
                    line.get('snow', {}).get('3h'),
                    line.get('dt'),
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    f_response.get('city', {}).get('timezone'),
                    f_response.get('city', {}).get('id'),
                    f_response.get('city', {}).get('name'),
                    f_response.get('cod'),
                ]
                f_records_str += ",".join(map(str, rec)) + '\n'
            
            # set response (200)
            status_code = 200
            headers = {"Content-Type": "text/csv", "Content-Disposition": "attachment; filename=weatherInfo.csv", "Access-Control-Allow-Origin": "*"}
            body = ",".join(map(str, CSV_HEADER)) + '\n' + ",".join(map(str, c_record)) + '\n' + f_records_str
        else:
            # set response (error)
            if c_result:
                status_code = f_response.get('cod')
                message = f_response.get('message')
            else:
                status_code = c_response.get('cod')
                message = c_response.get('message')
            if not status_code: status_code = 500
            if not message: message = 'Could not receive response'
            headers = {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"}
            dict_msg = {"errorMessage": message}
            body = json.dumps(dict_msg)
    else:
        # set response (400)
        status_code = 400
        headers = {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"}
        dict_msg = {"errorMessage": "query string \'id\' must be set"}
        body = json.dumps(dict_msg)
    
    # return response
    return {
        'statusCode': status_code,
        "headers": headers,
        'body': body,
    }