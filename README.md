# weather_info
AWS API Gateway/Lambda から OpenWeatherMap(https://openweathermap.org/)の気象情報APIを呼び出し、結果をCSVとして返却する

## Requirement
* Python 3.7
* pip
* awscli
* aws-sam-cli
* docker

## Usage
```bash
[Installation]
$ git clone https://github.com/numasa/weather_info.git

$ sam init --runtime python3.7

$ cd get_weather_info_csv

$ pip install -r requirements.txt -t .

[Local Test]
$ sam local start-api

$ curl http://127.0.0.1:3000/weather?id=1850147
※クエリパラメータidは、OpenWeatherMapの"city_id"(http://bulk.openweathermap.org/sample/ の「city.list.json.gz」参照)

[Packaging]
$ aws s3 mb s3://{任意のバケット名}

$ sam package --template-file template.yaml --output-template-file packaged.yaml --s3-bucket {任意のバケット名}

[Deploy]
$ sam deploy --template-file packaged.yaml --stack-name weather-deploy --capabilities CAPABILITY_IAM

$ aws cloudformation describe-stacks --stack-name weather-deploy --query 'Stacks[].Outputs'
※「"OutputKey": "WeatherApi"」の「"OutputValue"」がAPI Gatewayのエンドポイント
```

```bash
「get_weather_info_csv/lambda_function.py」から読み込むための設定ファイルが必要です。
$ cat get_weather_info_csv/settings.ini
[openweathermap]
url_current  = https://api.openweathermap.org/data/2.5/weather?lang=ja&units=metric
url_forecast = https://api.openweathermap.org/data/2.5/forecast?lang=ja&units=metric
api_key = {your api key}

```
