# Group 0000
# jo2522, Jeongmin Oh
# al3475, Alexander Loh
# jh3853, Junyang Hu

# *********************************************************************************************
# Program to update dynamodb with latest data from mta feed. It also cleans up stale entried from db
# Usage python dynamodata.py
# *********************************************************************************************
import json, time, sys
from collections import OrderedDict
from threading import Thread
from dynamo import dynamoDB

sys.path.append('utils')
import tripupdate, vehicle, alert, mtaUpdates, aws

mta_key = json.load(open("mta.json", "r"))["api_key"]


def convert_to_record(mta_datum,timestamp):
    record = {
        "tripId": None,
        "routeId": None,
        "startDate": None,
        "direction": None,
        "currentStopId": None,
        "currentStopStatus": None,
        "vehicleTimeStamp": None,
        "futureStopData": None,
        "timeStamp": None
    }
    mta_tripupdate, mta_vehicle, mta_alert = mta_datum
    record["timestamp"] = timestamp
    if mta_tripupdate is not None:
        record["tripId"] = mta_tripupdate.tripId
        record["routeId"] = mta_tripupdate.routeId
        record["startDate"] = mta_tripupdate.startDate
        record["direction"] = mta_tripupdate.direction
        record["futureStopData"] = mta_tripupdate.futureStops
    if mta_vehicle is not None:
        print("!!!" + str(mta_vehicle.timestamp))
        print(mta_tripupdate)
        record["vehicleTimeStamp"] = mta_vehicle.timestamp
        record["currentStopId"] = mta_vehicle.currentStopId
        record["currentStopStatus"] = mta_vehicle.currentStopStatus
    return record


def update_from_mta(db):
    mta = mtaUpdates.mtaUpdates(mta_key)
    while True:
        timestamp,mta_data = mta.getTripUpdates()
        for mta_datum in mta_data:
            mta_record = convert_to_record(mta_datum, timestamp)
            if mta_record["tripId"] is None:
                continue
            mta_record["recordTimeStamp"] = time.time()
            print("Added data %s." % str(mta_record["tripId"]))
            db.add(**mta_record)
        time.sleep(30)


def clean_up_stale_entries(db):
    while True:
        results = db.scan(recordTimeStamp__lt=time.time() - 2 * 60)
        #print list(results)
        for result in results:
            tripId = result["tripId"]
            db.delete(tripId)
            print("Deleted stale data %s." % str(tripId))
        time.sleep(60)


if __name__ == "__main__":
    try:
        db = dynamoDB("mtaData", "tripId")
        mta_daemon = lambda: update_from_mta(db)
        cleanup_daemon = lambda: clean_up_stale_entries(db)
        d = Thread(name='update_from_mta', target=mta_daemon)
        d.setDaemon(True)
        d.start()
        d = Thread(name='clean_up_stale_entries', target=cleanup_daemon)
        d.setDaemon(True)
        d.start()
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        exit
