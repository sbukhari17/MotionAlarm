import RPi.GPIO as GPIO
import time
from twilio.rest import TwilioRestClient


TRIG = 23
ECHO = 24
LED = 18

account_sid = "SID" # Twilio SID
auth_token  = "Token"  # Twilio Token

client = TwilioRestClient(account_sid, auth_token)


### SETUP STAGE ###
## SCAN FOR 60 SECONDS TO GET THE AVERAGE MEASUREMENT OF THE AREA ##

sumOfInitialMeasurements = 0
for i in range(5):
	GPIO.setmode(GPIO.BCM)

	## CONFIGURE PINS ##
	GPIO.setup(TRIG,GPIO.OUT)
	GPIO.output(TRIG,0)
	GPIO.setup(ECHO,GPIO.IN)
	
	time.sleep(0.1)

	GPIO.output(TRIG,1)
	time.sleep(0.00001)
	GPIO.output(TRIG,0)
	
	while GPIO.input(ECHO) == 0:
		pass
	start = time.time() # Start of duration (begins when we get a HIGH signal or a measurement has been taken)
	
	while GPIO.input(ECHO) == 1:
		pass
	stop = time.time() # End of duration (when we end back on a LOW signal)

	sumOfInitialMeasurements += (stop-start) * 17150
	GPIO.cleanup()
	time.sleep(1)

initAverage = sumOfInitialMeasurements / 5 # This will be our base measurement used for comparison to subsequent measurements


## SCAN STARTING ##
startTime = time.time() # This is the time our scanner starts
while 1:
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(ECHO,GPIO.IN)
	GPIO.setup(TRIG,GPIO.OUT)
	GPIO.setup(LED, GPIO.OUT)

	GPIO.output(TRIG,0)

	GPIO.output(LED, 1) # Blink the light letting the user know the alarm is armed

		
	time.sleep(0.1)

	
	GPIO.output(TRIG,1)
	time.sleep(0.00001)
	GPIO.output(TRIG,0)
	
	while GPIO.input(ECHO) == 0:
		pass
	start = time.time()
	
	while GPIO.input(ECHO) == 1:
		pass
	stop = time.time()
	
	reading = (stop - start) * 17150 #Multiplying by 17150 gets us a measurement in cm
	diff = abs(initAverage - reading)

	if ((diff / initAverage) > 0.33) and (time.time() - startTime > 60) : #If we have found a significant difference in distance AND at least 60 seconds have passed since the last text
		message = client.messages.create(
		body="Intruder Detected!", 
		to="+NumberToSendTo", 
		from_="+YourRegisteredTwilioNumber")
		startTime = time.time()

	GPIO.cleanup() # Clean up GPIO Pins for the next cycle
	time.sleep(1); #Scan every second