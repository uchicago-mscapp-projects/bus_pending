## Sample Restriction

1. Time frame: 20240221 00:00 to 20240229 07:29

2. only include trips that are complete

## Column names

1. group: the ith trip this bus runs after we filter out incomplete trips.

2. vid: bus identification

3. tmstmp: date-time

4. hdg: direction: 0º is North, 90º is East, 180º is South and 270º is West.

5. GroupSize: # of observations of this bus

6. status: if GroupSize == 1, status == 'ghost' so this column should always be na

7. change: whether this bus changes destination from last minute

8. consecutive_counts_x: calculated durations under sample with errors. can safely ignore. somewhat did not manage to drop.

9. error: if duration < 10: error == error; if group == minimum or max group number, error == middle cut 

10. consecutive_counts_y: duration!

11. total_dist: total distance this bus has traveled in this trip

12. last_value: last 'hdg' value of this bus in this trip

13. Direction: [0,90): North, [90,180): East, [180,270): South, [270,360): West

        
