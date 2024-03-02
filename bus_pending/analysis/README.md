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

* Transform the time stamp to DeltaTime and then estimate the day_time and week day

* Take the average distance by route. If the observation has less than two standard deviations from the mean then label it as "ghost". Impute a delay of 30 minutes to that route

* Count number of ghosts, this is the current number of delays per route. Drop those observations to do the final analysis

* Compare real trip_duration to the group object data to estimate the delay time. If the schedule data indicates that route in fridays morning should take 1 hour but it took 5 minutes, add 5 minutes to delay time. If delay time is greater than 10 minutes increased current number of delays by 1