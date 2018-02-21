# Group 0000
# jo2522, Jeongmin Oh
# al3475, Alexander Loh
# jh3853, Junyang Hu

import urllib2,contextlib
from datetime import datetime
from collections import OrderedDict

from pytz import timezone
import gtfs_realtime_pb2
import google.protobuf

import vehicle,alert,tripupdate

class mtaUpdates(object):

    # Do not change Timezone
    TIMEZONE = timezone('America/New_York')

    # feed url depends on the routes to which you want updates
    # here we are using feed 1 , which has lines 1,2,3,4,5,6,S
    # While initializing we can read the API Key and add it to the url
    feedurl = 'http://datamine.mta.info/mta_esi.php?feed_id=1&key='

    VCS = {1:"INCOMING_AT", 2:"STOPPED_AT", 3:"IN_TRANSIT_TO"}
    tripUpdates = []
    alerts = []

    def __init__(self,apikey):
        self.feedurl = self.feedurl + apikey

    # Method to get trip updates from mta real time feed
    def getTripUpdates(self):
        feed = gtfs_realtime_pb2.FeedMessage()
        try:
            with contextlib.closing(urllib2.urlopen(self.feedurl)) as response:
                d = feed.ParseFromString(response.read())
        except (urllib2.URLError, google.protobuf.message.DecodeError) as e:
            print "Error while connecting to mta server " +str(e)

        timestamp = feed.header.timestamp
        nytime = datetime.fromtimestamp(timestamp,self.TIMEZONE)

        for entity in feed.entity:
        # Trip update represents a change in timetable
            update = None
            if entity.trip_update and entity.trip_update.trip.trip_id:
                update = tripupdate.tripupdate()
                update.tripId = entity.trip_update.trip.trip_id
                update.routeId = entity.trip_update.trip.route_id
                update.startDate = entity.trip_update.trip.start_date
                m = entity.trip_update.trip.trip_id[::-1]
                update.direction = m[m.find(".")-1]
                update.vehicleData = entity.vehicle

                for e in entity.trip_update.stop_time_update:
                    arrivalTime = e.arrival.time
                    departureTime = e.departure.time
                    v1 = {"arrivalTime": arrivalTime}
                    v2 = {"departureTime": departureTime}
                    value = [v1, v2]
                    update.futureStops[e.stop_id] = value

            v = None
            if entity.vehicle and entity.vehicle.trip.trip_id:
                v = vehicle.vehicle()
                v.currentStopNumber = entity.vehicle.current_stop_sequence
                v.currentStopId = entity.vehicle.stop_id
                v.timestamp = entity.vehicle.timestamp
                v.currentStopStatus = entity.vehicle.current_status

            a = None
            if entity.alert:
                a = alert.alert()
                for trip in entity.alert.informed_entity:
                    a.tripId.append(trip.trip.trip_id)
                    a.routeId[trip.trip.trip_id] = trip.trip.route_id
                    a.startDate[trip.trip.trip_id] = trip.trip.start_date

            self.tripUpdates.append([update, v, a])

        self.tripUpdates = [[u1,v2,None] for (u1,v1,a1),(u2,v2,a2) in zip(self.tripUpdates[0:len(self.tripUpdates):2],self.tripUpdates[1:len(self.tripUpdates):2])]
        return timestamp, self.tripUpdates

if __name__ == "__main__":
    mu = mtaUpdates("6e96fe7b10a798d5c32ef41b93ad6881")
    result = mu.getTripUpdates()
    #open("test.txt","w+").write(str(result))
    # END OF getTripUpdates method
