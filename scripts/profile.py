import requests

#remove https warning
requests.packages.urllib3.disable_warnings()

def post(target, city, api_key):
   headers = {
            'content-type': "application/json",
            'Accept': "*/*",
        }
   response = requests.post(target, data={'city' : city, 'api_key' : api_key},verify=False)
   output = response.content
   output = output.decode('utf-8')
   print (".")

#Input target
print("Weather App - Lambda Function")
target = input("Target: ")
city = input("City: ")
api_key =  input("API Key: ")
print ("Working ")
for x in range(0, 3005):
  post(target, city, api_key)