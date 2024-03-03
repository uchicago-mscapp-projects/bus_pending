# Analysis 📝🚌

## Scheduled Data

Take data from transit. Join multiple tables in order to have trip_id, service_id, schedule, and route_id (service_id indicates the days this trip runs).

* Keep only the first and last observation per trip_id. We are only analyzing the total time by route, not station

* Collapse data to only have one observation per trip_id, and create new column "finish_time". This column is the arrival time of the last observation, which is the end of the trip

* Calculate trip_duration by subtracting starting_time and finish_time

* Estimate day_time. Morning is defined from 6 am to 12 pm, afternoon from 12 pm to 6 pm, night from 6 pm to 12 am, and midnight from 12 am to 6 am. Use datetime to parse the string into DeltaTime object

* Group by route, day_time and day. Then, estimate the average trip duration by this groups. For example, how much time, in average, does it take the route 4 on friday afternoon to complete the route?

* Use this group object to compare with real data

## Real Data

* Transform the time stamp to DeltaTime and then estimate the day_time and label them as weekday or weekend (they can be both since there aere service days that runs every day)

* Take the average distance by route. If the observation has less than two standard deviations from the mean then label it as "ghost". Impute a delay of 30 minutes to that route

* Delete observations with characteristics not found in scheduled data. Transit does not have complete schedules

* Delay time is the actual time minus the expected time. If delay time is less than 10 minutes, then do not label the observation as "delayed" and do not count the time as "delayed time"

* Do a new data frame with all the information