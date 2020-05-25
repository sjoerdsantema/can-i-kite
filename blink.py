import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library
from time import sleep # Import the sleep function from the time module
import urllib.request, urllib.parse, urllib.error
import json
import ssl

GPIO.setwarnings(False) # Ignore warning for now
GPIO.setmode(GPIO.BOARD) # Use physical pin numbering
GPIO.setup(8, GPIO.OUT, initial=GPIO.LOW) # Set pin 8 to be an output pin and set initial value to low (off)
GPIO.setup(10, GPIO.OUT, initial=GPIO.LOW) # Set pin 8 to be an output pin and set initial value to low (off)

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

# Blink speed function
def blink(windspeed):
    if 0.7-(float(windspeed)/100) < 0.0001: 
        blink_time = 0.05
        print(f"Lots of wind! Blink period: set to minimum") # To make sure blink_time never becomes a negative
        return blink_time
    else:
        blink_time = 0.7-(float(windspeed)/100) # The more the wind, the faster the blink
        return blink_time
        
while True:
    try:
        uh = urllib.request.urlopen(url, context=ctx) # Collect data
        data = uh.read().decode()
        js = json.loads(data)

        # Select weather values
        windk = js['liveweer'][0]['windk']
        windr = js['liveweer'][0]['windr']
        temp = js['liveweer'][0]['temp']

        # Minimal conditions
        gooddirection = None 
        minwind = 17
        mintemp = 10
        good_wind_dir = ['Z', 'W', 'ZW', 'NW', 'N', 'NNW', 'ZZW']

        # Check wind direction
        if windr in good_wind_dir:
            gooddirection = True
        else: 
            gooddirection = False 

        # Activate the lights
        if float(windk) >= minwind and float(temp) >= mintemp and gooddirection is True:
            print("Conditions are GO!")
            print("#################")
            print(f"Wind is blowing at {windk} knots, temperature is {temp}, direction is {windr}")
            print("Turning the light ON")
            print("Light is GREEN")
            GPIO.output(10, GPIO.LOW) # Turn  the red LED off
            blink_time = blink(windk)
            repeats = int((145/2)/blink_time) # Calculate 290 seconds of repeats @ two blinks
            for i in range(0,repeats): # To make sure no more than 300 calls are sent per day
                GPIO.output(8, GPIO.HIGH) # Turn the green LED on
                sleep(blink_time)
                GPIO.output(8, GPIO.LOW) # And again
                sleep(blink_time) 
            continue     
        else:
            print("No kiting possible right now")
            print("############################")
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
            print("Light is RED")
            GPIO.output(8, GPIO.LOW) # Turn the green LED off
            GPIO.output(10, GPIO.HIGH) # Turn the red LED on
            sleep(288) # To make sure no more than 300 calls are sent per day
            continue
    except: # Error message if something went wrong
        print(f"{service_url}, does not exist or something went wrong")
        for i in range(0,10): # To make sure no more than 300 calls are sent per day
            GPIO.output(8, GPIO.HIGH) # Turn the green LED on
            GPIO.output(10, GPIO.HIGH) # Turn the red LED on
            sleep(1)
            GPIO.output(8, GPIO.LOW) # Turn the green LED off
            GPIO.output(10, GPIO.LOW) # Turn the red LED off
            sleep(1) 
        continue     


