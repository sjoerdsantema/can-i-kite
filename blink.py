import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library
from time import sleep # Import the sleep function from the time module
import urllib.request, urllib.parse, urllib.error
import json
import ssl

GPIO.setwarnings(False) # Ignore warning for now
GPIO.setmode(GPIO.BOARD) # Use physical pin numbering
GPIO.setup(8, GPIO.OUT, initial=GPIO.LOW) # Set pin 8 to be an output pin and set initial value to low (off)

# Values for the API
api_key = "4546b131d1"
location = "IJmuiden"
service_url = "http://weerlive.nl/api/json-data-10min.php?"

# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# Construct the url
parms = dict()
parms['locatie'] = location
parms['key'] = api_key
url = service_url + urllib.parse.urlencode(parms)

while True:
    # Collect data
    uh = urllib.request.urlopen(url, context=ctx)
    data = uh.read().decode()
    js = json.loads(data)

    # Select weather values
    windk = js['liveweer'][0]['windk']
    windr = js['liveweer'][0]['windr']
    temp = js['liveweer'][0]['temp']

    # Minimal conditions
    gooddirection = None 
    minwind = 18
    mintemp = 10
    if windr == "ZW" or "Z" or "W" or "NW" or "N":
        gooddirection = True
    else: 
        gooddirection = False 

    if float(windk) >= minwind and float(temp) >= mintemp and gooddirection is True:
        print("Conditions are GO!")
        print(f"Wind is blowing at {windk} knots, temperature is {temp}, direction is {windr}")
        print("Turning the light ON")
        GPIO.output(8, GPIO.HIGH) # Turn the LED on
        sleep(288) # To make sure no more than 300 calls are sent per day
        continue
    else:
        print("No kiting possible right now")
        # Print the wind strength
        if float(windk) <= minwind:
            print("-Not enough wind")
        else:
            print("-The wind is OK")
        # Print the temperature
        if float(temp) <= mintemp:
            print("-Too damn cold")
        else:
            print("-The temperature is OK")
        # Print if the direction is good
        if gooddirection is True:
            print("-Wind direction is OK")
        else:
            print("-Wind direction is wrong")

        print(f"Wind is blowing at {windk} knots, temperature is {temp}, direction is {windr}")
        print("Turning the light OFF")
        GPIO.output(8, GPIO.LOW) # Turn the LED off
        sleep(288) # To make sure no more than 300 calls are sent per day
        continue


