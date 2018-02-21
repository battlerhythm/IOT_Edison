########################################################################
# * Assignment 2 Part 3. File written by Peter Wei pw2428@columbia.edu #
########################################################################

# Group 0000
# jo2522, Jeongmin Oh
# al3475, Alexander Loh
# jh3853, Junyang Hu

import boto
import boto.dynamodb2
import mraa
import time
import json
import pyupm_i2clcd as lcd

from boto.dynamodb2.table import Table
from boto.dynamodb2.fields import HashKey
from math import log


DYNAMO_TABLE_NAME = 'edisonLab2Part3'
KINESIS_STREAM_NAME = 'edisonLab2Part3'
ACCOUNT_ID = '264539880516'
IDENTITY_POOL_ID = 'us-east-1:f83298dc-b5b7-4ffc-974d-af61fce2ac61'
ROLE_ARN = 'arn:aws:iam::264539880516:role/Cognito_edisonDemoKinesisUnauth_Role'

#################################################
# Instantiate cognito and obtain security token #
#################################################
# Use cognito to get an identity.
cognito = boto.connect_cognito_identity()
cognito_id = cognito.get_id(ACCOUNT_ID, IDENTITY_POOL_ID)
oidc = cognito.get_open_id_token(cognito_id['IdentityId'])

# Further setup your STS using the code below
sts = boto.connect_sts()
assumedRoleObject = sts.assume_role_with_web_identity(ROLE_ARN, "XX", oidc['Token'])

# Connect to dynamoDB and kinesis
client_dynamo = boto.dynamodb2.connect_to_region(
	'us-east-1',
	aws_access_key_id=assumedRoleObject.credentials.access_key,
    aws_secret_access_key=assumedRoleObject.credentials.secret_key,
    security_token=assumedRoleObject.credentials.session_token)

client_kinesis = boto.connect_kinesis(
	aws_access_key_id=assumedRoleObject.credentials.access_key,
	aws_secret_access_key=assumedRoleObject.credentials.secret_key,
	security_token=assumedRoleObject.credentials.session_token)

######################
# Setup DynamoDB Table
######################

try:
    table_dynamo = Table.create(DYNAMO_TABLE_NAME, schema=[HashKey('Time')], connection=client_dynamo) #HINT: Table.create; #HINT 2: Use CUID as your hashkey
    print ("Wait 20 sec until the table is created")
    time.sleep(20)
    print ("New Table Created in DynamoDB")
except Exception as e:
    table_dynamo = Table(DYNAMO_TABLE_NAME, connection=client_dynamo) #HINT: Remember to use "connection=client.dynamo"
    print ("Table Already Exists in DynamoDB")


#################################################
# Setup switch and temperature sensor #
#################################################

# Switch D8
# Temp Sensor A1
# LCD I2C

switch_pin_number = 8
switch = mraa.Gpio(switch_pin_number)
switch.dir(mraa.DIR_IN)
tempSensor = mraa.Aio(1)

######################
# YOUR CODE HERE #
######################

def getTemp():
    B = 4275
    R0 = 100000
    a = tempSensor.read()
    R = 1023.0 / a - 1.0
    R = R0 * R
    v = 1.0/(log(R/R0)/B+1/298.15)-273.15
    #print(str(v) + " is the current temperature")
    return v

# state 0 : DynamoDB Mode
# state 1 : Kinesis Mode

# Default state is DynamoDB Mode
state = 0

try:
    while(1):
        myLcd = lcd.Jhd1313m1(0, 0x3E, 0x62)
        myLcd.setColor(255, 0, 0) # RGB Color RED
        t = time.asctime( time.localtime(time.time()) )
        temp = round(getTemp(), 4)

        # Change state when every switch pressed
        if(switch.read()):
            state += 1
            state %= 2

        #######################################
		# When button pressed:
		# Post into DynamoDB
		# Change LCD Display
		#######################################

        if(state == 0):
            myLcd.setCursor(0,0)
            myLcd.write('Upload to DynamoDB')
            myLcd.setCursor(1,2)
            myLcd.write(str(temp))
            # Update to DynamoDB
            try:
                record = table_dynamo.get_item(Time=t)
                record['Temperature'] = str(temp)
                record.save(overwrite=True)
                print("Record has been updated in DynamoDB.\n")
            except Exception as e:
                table_dynamo.put_item(data={
                    'Time':t,
                    'Temperature': str(temp)
                })
                print("New entry created in DynamoDB.\n")

        #######################################
		# When button pressed again:
		# Post into Kinesis Stream
		# Change LCD Display
		#######################################
		######################
		# YOUR CODE HERE #
		######################
        elif(state == 1):
            myLcd.setCursor(0,0)
            myLcd.write('Upload to Kinesis')
            myLcd.setCursor(1,2)
            myLcd.write(str(temp))

            # Update to Kinesis
            record = {t:temp}
            client_kinesis.put_record(KINESIS_STREAM_NAME, json.dumps(record), "edison")
            print("New entry created in Kinesis.\n")

        else:
            print ("Undefined state, end loop.\n")
            break


except KeyboardInterrupt:
    exit
