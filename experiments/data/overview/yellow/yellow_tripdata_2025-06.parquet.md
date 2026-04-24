# Data Overview: yellow_tripdata_2025-06.parquet

## Dataset Summary

| metric       | value                                                                               |
|:-------------|:------------------------------------------------------------------------------------|
| file         | /root/Dev/DataGate/experiments/data/parquets/yellow/yellow_tripdata_2025-06.parquet |
| rows         | 4322960                                                                             |
| columns      | 20                                                                                  |
| row_groups   | 5                                                                                   |
| file_size_mb | 70.14                                                                               |
| rows_loaded  | 4322960                                                                             |

## Schema

| column                | parquet_type   | nullable   |
|:----------------------|:---------------|:-----------|
| VendorID              | int32          | True       |
| tpep_pickup_datetime  | timestamp[us]  | True       |
| tpep_dropoff_datetime | timestamp[us]  | True       |
| passenger_count       | int64          | True       |
| trip_distance         | double         | True       |
| RatecodeID            | int64          | True       |
| store_and_fwd_flag    | large_string   | True       |
| PULocationID          | int32          | True       |
| DOLocationID          | int32          | True       |
| payment_type          | int64          | True       |
| fare_amount           | double         | True       |
| extra                 | double         | True       |
| mta_tax               | double         | True       |
| tip_amount            | double         | True       |
| tolls_amount          | double         | True       |
| improvement_surcharge | double         | True       |
| total_amount          | double         | True       |
| congestion_surcharge  | double         | True       |
| Airport_fee           | double         | True       |
| cbd_congestion_fee    | double         | True       |

## Column Health (full-data)

| column                | dtype          |   non_null |    null |   null_% |   unique |
|:----------------------|:---------------|-----------:|--------:|---------:|---------:|
| VendorID              | int32          |    4322960 |       0 |   0.0000 |        4 |
| tpep_pickup_datetime  | datetime64[us] |    4322960 |       0 |   0.0000 |  1854492 |
| tpep_dropoff_datetime | datetime64[us] |    4322960 |       0 |   0.0000 |  1853786 |
| passenger_count       | float64        |    3110014 | 1212946 |  28.0582 |       10 |
| trip_distance         | float64        |    4322960 |       0 |   0.0000 |     5100 |
| RatecodeID            | float64        |    3110014 | 1212946 |  28.0582 |        7 |
| store_and_fwd_flag    | str            |    3110014 | 1212946 |  28.0582 |        2 |
| PULocationID          | int32          |    4322960 |       0 |   0.0000 |      259 |
| DOLocationID          | int32          |    4322960 |       0 |   0.0000 |      261 |
| payment_type          | int64          |    4322960 |       0 |   0.0000 |        6 |
| fare_amount           | float64        |    4322960 |       0 |   0.0000 |    11991 |
| extra                 | float64        |    4322960 |       0 |   0.0000 |       77 |
| mta_tax               | float64        |    4322960 |       0 |   0.0000 |       66 |
| tip_amount            | float64        |    4322960 |       0 |   0.0000 |     4798 |
| tolls_amount          | float64        |    4322960 |       0 |   0.0000 |     1367 |
| improvement_surcharge | float64        |    4322960 |       0 |   0.0000 |        4 |
| total_amount          | float64        |    4322960 |       0 |   0.0000 |    23508 |
| congestion_surcharge  | float64        |    3110014 | 1212946 |  28.0582 |        3 |
| Airport_fee           | float64        |    3110014 | 1212946 |  28.0582 |        5 |
| cbd_congestion_fee    | float64        |    4322960 |       0 |   0.0000 |        4 |

## Numeric Statistics (full-data)

| column                |       min |      p25 |   median |     mean |      p75 |         max |      std |
|:----------------------|----------:|---------:|---------:|---------:|---------:|------------:|---------:|
| VendorID              |    1.0000 |   2.0000 |   2.0000 |   1.8874 |   2.0000 |      7.0000 |   0.7589 |
| passenger_count       |    0.0000 |   1.0000 |   1.0000 |   1.2983 |   1.0000 |      9.0000 |   0.7330 |
| trip_distance         |    0.0000 |   1.0700 |   1.9200 |   7.4784 |   3.9000 | 261262.3900 | 694.2321 |
| RatecodeID            |    1.0000 |   1.0000 |   1.0000 |   2.5992 |   1.0000 |     99.0000 |  12.0018 |
| PULocationID          |    1.0000 | 114.0000 | 161.0000 | 160.0238 | 231.0000 |    265.0000 |  66.8666 |
| DOLocationID          |    1.0000 | 107.0000 | 162.0000 | 160.1093 | 233.0000 |    265.0000 |  70.9191 |
| payment_type          |    0.0000 |   0.0000 |   1.0000 |   0.8913 |   1.0000 |      5.0000 |   0.7698 |
| fare_amount           | -990.0000 |   9.3000 |  14.2000 |  18.9780 |  23.9700 | 325478.0500 | 157.7826 |
| extra                 |   -7.5000 |   0.0000 |   0.0000 |   1.1294 |   2.5000 |     42.4600 |   1.8299 |
| mta_tax               |  -21.7400 |   0.5000 |   0.5000 |   0.4773 |   0.5000 |     10.5000 |   0.1407 |
| tip_amount            |  -70.0700 |   0.0000 |   2.0000 |   2.7527 |   3.8700 |    960.9400 |   4.0229 |
| tolls_amount          | -109.0600 |   0.0000 |   0.0000 |   0.5100 |   0.0000 |    716.0500 |   2.1542 |
| improvement_surcharge |   -1.0000 |   1.0000 |   1.0000 |   0.9545 |   1.0000 |      1.0000 |   0.2783 |
| total_amount          | -994.2500 |  16.0100 |  21.7500 |  27.3872 |  31.3900 | 325528.4500 | 158.3694 |
| congestion_surcharge  |   -2.5000 |   2.5000 |   2.5000 |   2.1816 |   2.5000 |      2.5000 |   0.9633 |
| Airport_fee           |   -1.7500 |   0.0000 |   0.0000 |   0.1588 |   0.0000 |      6.7500 |   0.5557 |
| cbd_congestion_fee    |   -0.7500 |   0.0000 |   0.7500 |   0.5332 |   0.7500 |      1.2500 |   0.3586 |

## Datetime Coverage (full-data)

| column                | min_ts              | max_ts              | span             |
|:----------------------|:--------------------|:--------------------|:-----------------|
| tpep_pickup_datetime  | 2025-05-31 22:34:26 | 2025-06-30 23:59:59 | 30 days 01:25:33 |
| tpep_dropoff_datetime | 2025-05-31 22:43:36 | 2025-07-01 22:36:42 | 30 days 23:53:06 |

## Datetime Distribution by Day (full-data)

| column                | day        |   rows |   row_% |
|:----------------------|:-----------|-------:|--------:|
| tpep_pickup_datetime  | 2025-05-31 |     20 |  0.0005 |
| tpep_pickup_datetime  | 2025-06-01 | 131824 |  3.0494 |
| tpep_pickup_datetime  | 2025-06-02 | 114839 |  2.6565 |
| tpep_pickup_datetime  | 2025-06-03 | 140826 |  3.2576 |
| tpep_pickup_datetime  | 2025-06-04 | 158588 |  3.6685 |
| tpep_pickup_datetime  | 2025-06-05 | 177340 |  4.1023 |
| tpep_pickup_datetime  | 2025-06-06 | 163616 |  3.7848 |
| tpep_pickup_datetime  | 2025-06-07 | 163816 |  3.7894 |
| tpep_pickup_datetime  | 2025-06-08 | 139865 |  3.2354 |
| tpep_pickup_datetime  | 2025-06-09 | 128597 |  2.9747 |
| tpep_pickup_datetime  | 2025-06-10 | 141039 |  3.2626 |
| tpep_pickup_datetime  | 2025-06-11 | 151921 |  3.5143 |
| tpep_pickup_datetime  | 2025-06-12 | 167192 |  3.8675 |
| tpep_pickup_datetime  | 2025-06-13 | 146778 |  3.3953 |
| tpep_pickup_datetime  | 2025-06-14 | 146409 |  3.3868 |
| tpep_pickup_datetime  | 2025-06-15 | 125074 |  2.8932 |
| tpep_pickup_datetime  | 2025-06-16 | 119913 |  2.7739 |
| tpep_pickup_datetime  | 2025-06-17 | 136744 |  3.1632 |
| tpep_pickup_datetime  | 2025-06-18 | 157383 |  3.6406 |
| tpep_pickup_datetime  | 2025-06-19 | 143836 |  3.3273 |
| tpep_pickup_datetime  | 2025-06-20 | 140275 |  3.2449 |
| tpep_pickup_datetime  | 2025-06-21 | 157148 |  3.6352 |
| tpep_pickup_datetime  | 2025-06-22 | 135715 |  3.1394 |
| tpep_pickup_datetime  | 2025-06-23 | 141713 |  3.2781 |
| tpep_pickup_datetime  | 2025-06-24 | 157733 |  3.6487 |
| tpep_pickup_datetime  | 2025-06-25 | 158320 |  3.6623 |
| tpep_pickup_datetime  | 2025-06-26 | 152851 |  3.5358 |
| tpep_pickup_datetime  | 2025-06-27 | 138402 |  3.2016 |
| tpep_pickup_datetime  | 2025-06-28 | 142771 |  3.3026 |
| tpep_pickup_datetime  | 2025-06-29 | 129912 |  3.0052 |
| tpep_pickup_datetime  | 2025-06-30 | 112500 |  2.6024 |
| tpep_dropoff_datetime | 2025-05-31 |      7 |  0.0002 |
| tpep_dropoff_datetime | 2025-06-01 | 130962 |  3.0295 |
| tpep_dropoff_datetime | 2025-06-02 | 114985 |  2.6599 |
| tpep_dropoff_datetime | 2025-06-03 | 140429 |  3.2484 |
| tpep_dropoff_datetime | 2025-06-04 | 157991 |  3.6547 |
| tpep_dropoff_datetime | 2025-06-05 | 176539 |  4.0838 |
| tpep_dropoff_datetime | 2025-06-06 | 163472 |  3.7815 |
| tpep_dropoff_datetime | 2025-06-07 | 163708 |  3.7869 |
| tpep_dropoff_datetime | 2025-06-08 | 141442 |  3.2719 |
| tpep_dropoff_datetime | 2025-06-09 | 129125 |  2.9870 |
| tpep_dropoff_datetime | 2025-06-10 | 140399 |  3.2478 |
| tpep_dropoff_datetime | 2025-06-11 | 151621 |  3.5073 |
| tpep_dropoff_datetime | 2025-06-12 | 166515 |  3.8519 |
| tpep_dropoff_datetime | 2025-06-13 | 146403 |  3.3866 |
| tpep_dropoff_datetime | 2025-06-14 | 146941 |  3.3991 |
| tpep_dropoff_datetime | 2025-06-15 | 126429 |  2.9246 |
| tpep_dropoff_datetime | 2025-06-16 | 119627 |  2.7672 |
| tpep_dropoff_datetime | 2025-06-17 | 136841 |  3.1654 |
| tpep_dropoff_datetime | 2025-06-18 | 156343 |  3.6166 |
| tpep_dropoff_datetime | 2025-06-19 | 144460 |  3.3417 |
| tpep_dropoff_datetime | 2025-06-20 | 139281 |  3.2219 |
| tpep_dropoff_datetime | 2025-06-21 | 156824 |  3.6277 |
| tpep_dropoff_datetime | 2025-06-22 | 137223 |  3.1743 |
| tpep_dropoff_datetime | 2025-06-23 | 141752 |  3.2790 |
| tpep_dropoff_datetime | 2025-06-24 | 157621 |  3.6461 |
| tpep_dropoff_datetime | 2025-06-25 | 158172 |  3.6589 |
| tpep_dropoff_datetime | 2025-06-26 | 152318 |  3.5235 |
| tpep_dropoff_datetime | 2025-06-27 | 137933 |  3.1907 |
| tpep_dropoff_datetime | 2025-06-28 | 142587 |  3.2984 |
| tpep_dropoff_datetime | 2025-06-29 | 131378 |  3.0391 |
| tpep_dropoff_datetime | 2025-06-30 | 112887 |  2.6113 |
| tpep_dropoff_datetime | 2025-07-01 |    745 |  0.0172 |

## Top Values (full-data, top 5)

| column                | top_5_values                                                          |
|:----------------------|:----------------------------------------------------------------------|
| VendorID              | 2: 3423020, 1: 830851, 7: 67573, 6: 1516                              |
| passenger_count       | 1.0: 2458387, <NULL>: 1212946, 2.0: 431930, 3.0: 104573, 4.0: 68679   |
| RatecodeID            | 1.0: 2881409, <NULL>: 1212946, 2.0: 119754, 99.0: 47381, 5.0: 38456   |
| store_and_fwd_flag    | N: 3101709, <NULL>: 1212946, Y: 8305                                  |
| payment_type          | 1: 2595374, 0: 1212946, 2: 386552, 4: 100163, 3: 27923                |
| improvement_surcharge | 1.0: 4199610, -1.0: 73717, 0.0: 48193, 0.3: 1440                      |
| congestion_surcharge  | 2.5: 2771954, <NULL>: 1212946, 0.0: 280029, -2.5: 58031               |
| Airport_fee           | 0.0: 2803889, <NULL>: 1212946, 1.75: 288061, -1.75: 15425, 6.75: 2109 |
| cbd_congestion_fee    | 0.75: 3123448, 0.0: 1149581, -0.75: 49930, 1.25: 1                    |

## Data Quality Signals

- Duplicate rows in full data: `0` / `4322960`.
- Numeric columns containing negative values: `fare_amount`, `extra`, `mta_tax`, `tip_amount`, `tolls_amount`, `improvement_surcharge`, `total_amount`, `congestion_surcharge`, `Airport_fee`, `cbd_congestion_fee`.

## Data Preview

|   VendorID | tpep_pickup_datetime   | tpep_dropoff_datetime   |   passenger_count |   trip_distance |   RatecodeID | store_and_fwd_flag   |   PULocationID |   DOLocationID |   payment_type |   fare_amount |   extra |   mta_tax |   tip_amount |   tolls_amount |   improvement_surcharge |   total_amount |   congestion_surcharge |   Airport_fee |   cbd_congestion_fee |
|-----------:|:-----------------------|:------------------------|------------------:|----------------:|-------------:|:---------------------|---------------:|---------------:|---------------:|--------------:|--------:|----------:|-------------:|---------------:|------------------------:|---------------:|-----------------------:|--------------:|---------------------:|
|          1 | 2025-06-01 00:02:50    | 2025-06-01 00:39:51     |                 1 |           10    |            1 | N                    |            138 |             50 |              1 |          47.8 |   11    |       0.5 |        20.15 |           6.94 |                       1 |          87.39 |                    2.5 |          1.75 |                 0.75 |
|          2 | 2025-06-01 00:11:27    | 2025-06-01 00:35:35     |                 1 |            3.93 |            1 | N                    |            158 |            237 |              1 |          24.7 |    1    |       0.5 |         6.09 |           0    |                       1 |          36.54 |                    2.5 |          0    |                 0.75 |
|          1 | 2025-06-01 00:43:47    | 2025-06-01 00:49:16     |                 0 |            0.7  |            1 | N                    |            230 |            163 |              1 |           7.2 |    4.25 |       0.5 |         2.59 |           0    |                       1 |          15.54 |                    2.5 |          0    |                 0.75 |
|          1 | 2025-06-01 00:01:15    | 2025-06-01 00:42:16     |                 1 |           17    |            2 | N                    |            132 |            232 |              1 |          70   |    3.25 |       0.5 |         5    |           0    |                       1 |          79.75 |                    2.5 |          0    |                 0.75 |
|          7 | 2025-06-01 00:16:32    | 2025-06-01 00:16:32     |                 1 |            2.22 |            1 | N                    |             48 |            234 |              1 |          20.5 |    0    |       0.5 |         5.25 |           0    |                       1 |          31.5  |                    2.5 |          0    |                 0.75 |
|          1 | 2025-06-01 00:05:23    | 2025-06-01 00:16:57     |                 0 |            0.9  |            1 | N                    |            164 |             90 |              2 |          11.4 |    4.25 |       0.5 |         0    |           0    |                       1 |          17.15 |                    2.5 |          0    |                 0.75 |
|          1 | 2025-06-01 00:23:04    | 2025-06-01 00:35:25     |                 0 |            1.9  |            1 | N                    |            246 |            113 |              1 |          12.8 |    4.25 |       0.5 |         3.7  |           0    |                       1 |          22.25 |                    2.5 |          0    |                 0.75 |
|          1 | 2025-06-01 00:37:37    | 2025-06-01 00:42:28     |                 0 |            0.7  |            1 | N                    |            113 |            113 |              1 |           7.2 |    4.25 |       0.5 |         2.55 |           0    |                       1 |          15.5  |                    2.5 |          0    |                 0.75 |
|          1 | 2025-06-01 00:44:28    | 2025-06-01 00:50:01     |                 0 |            0.5  |            1 | N                    |            249 |            249 |              1 |           7.2 |    4.25 |       0.5 |         2.55 |           0    |                       1 |          15.5  |                    2.5 |          0    |                 0.75 |
|          1 | 2025-06-01 00:52:28    | 2025-06-01 01:03:29     |                 1 |            2.5  |            1 | N                    |            249 |            142 |              1 |          13.5 |    4.25 |       0.5 |         5.75 |           0    |                       1 |          25    |                    2.5 |          0    |                 0.75 |
