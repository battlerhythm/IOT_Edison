import json
import edison
import time
from utils import aws

REGION = 'us-east-1'
TOPIC  = 'arn:aws:sns:us-east-1:264539880516:Demo_Topic'

client = aws.getClient('sns',REGION)
while True:
	temperature = edison.get_temperature()
        print(temperature)
	pub = client.publish( TopicArn = TOPIC, Message = "The current temperature is %f" % temperature)
        print("Published")
	time.sleep(5)

#client.subscribe(TopicArn = TOPIC, Protocol = 'sms', Endpoint = 'your phone number here')


