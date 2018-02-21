########################################################################
# * Assignment 2 Part 2. File written by Peter Wei pw2428@columbia.edu #
########################################################################

# Group 0000
# jo2522, Jeongmin Oh
# al3475, Alexander Loh
# jh3853, Junyang Hu

import boto
import boto.dynamodb2
import time
import json
from boto.dynamodb2.table import Table
from boto.dynamodb2.fields import HashKey, RangeKey

ACCOUNT_ID,IDENTITY_POOL_ID,ROLE_ARN = [json.load(open("aws.json","r"))[key] for key in ["account_id","identity_pool_id","role_arn"]]

cognito = boto.connect_cognito_identity()
cognito_id = cognito.get_id(ACCOUNT_ID, IDENTITY_POOL_ID)
oidc = cognito.get_open_id_token(cognito_id['IdentityId'])

sts = boto.connect_sts()
assumedRoleObject = sts.assume_role_with_web_identity(ROLE_ARN, "XX", oidc['Token'])

client_dynamo = boto.dynamodb2.connect_to_region(
        'us-east-1',
        aws_access_key_id=assumedRoleObject.credentials.access_key,
        aws_secret_access_key=assumedRoleObject.credentials.secret_key,
        security_token=assumedRoleObject.credentials.session_token)

class dynamoDB:
    def __init__(self, db_name, partition_key_name):
        self.table_dynamo = None
        self.partition_key_name = partition_key_name
        try:
            self.table_dynamo = Table.create(db_name, schema=[HashKey(partition_key_name)], connection=client_dynamo)
            print ("Wait 20 sec until the table is created")
            time.sleep(20)
            print ("New table created.")
        except Exception as e:
            self.table_dynamo = Table(db_name, connection=client_dynamo)
            print ("Table already exists.")

    def add(self, **kwargs):
        try:
            record = self.get(kwargs[self.partition_key_name])
            for k,v in kwargs.items():
                record[k] = v
            record.save(overwrite=True)
            #print("Record has been updated.\n")
        except Exception as e:
            self.table_dynamo.put_item(data=kwargs)
            #print("New entry created.\n")

    def delete(self, pk):
        try:
            record = self.table_dynamo.get_item(**{self.partition_key_name:pk})
            self.table_dynamo.delete_item(**{self.partition_key_name:pk})
            #print("The record has been deleted.")
            return record
        except Exception as e:
            #print("Cannot delete the record, it does not exist.")
            pass
        return None

    def get(self,pk):
        try:
            item = self.table_dynamo.get_item(**{self.partition_key_name:pk})
            return item
        except Exception as e:
            #print("Cannot get the record, it does not exist.")
            pass
        return None

    def scan(self,**filter_kwargs):
        return self.table_dynamo.scan(**filter_kwargs)

####################################################################
# DON'T MODIFY BELOW HERE -----------------------------------------#
####################################################################

if __name__ == "__main__":
    db = dynamoDB("mtaData","tripId")
    db.add(**{
        "tripId": "My unique trip identifier",
        "routeId": 2,
        "startDate": "1/1/2000",
        "direction": "N",
        "currentStopId": "1",
        "currentStopStatus": 3,
        "vehicleTimeStamp": "noon",
        "futureStopData": {"stop id": [{"arrivalTime":111},{"departureTime":222}]},
        "mtaTimeStamp": 333,
        "recordTimeStamp": time.time()})
    db.add(**{
        "tripId": "My unique trip identifier1",
        "routeId": 2,
        "startDate": "1/1/2000",
        "direction": "N",
        "currentStopId": "1",
        "currentStopStatus": 3,
        "vehicleTimeStamp": "noon",
        "futureStopData": {"stop id": [{"arrivalTime":111},{"departureTime":222}]},
        "mtaTimeStamp": 333,
        "recordTimeStamp": time.time()})
    db.add(**{
        "tripId": "My unique trip identifier2",
        "routeId": 2,
        "startDate": "1/1/2000",
        "direction": "N",
        "currentStopId": "1",
        "currentStopStatus": 3,
        "vehicleTimeStamp": "noon",
        "futureStopData": {"stop id": [{"arrivalTime":111},{"departureTime":222}]},
        "mtaTimeStamp": 333,
        "recordTimeStamp": time.time()})
    sc = list(db.scan())
    db.get("My unique trip identifier")
    db.delete("My unique trip identifier")
