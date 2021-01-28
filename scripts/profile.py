import requests
from threading import Thread
import time
import sys

#remove https warning
requests.packages.urllib3.disable_warnings()

def post(target, city, api_key):
   for i in range(0, 1505):
       headers = {
                'content-type': "application/json",
                'Accept': "*/*",
            }
       response = requests.post(target, data={'city' : city, 'api_key' : api_key},verify=False)
       time.sleep(0.05)
       output = response.content
       output = output.decode('utf-8')
       print (".", end="")
       sys.stdout.flush()

#Input target
print("Weather App - Lambda Function")
target = input("Target: ")
city = input("City: ")
api_key =  input("API Key: ")
print ("Working ", end="-")

for x in range(0, 200):
  t = Thread(target=post, args=(target, city, api_key)) 
  t.start()  
  
