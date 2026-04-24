# Data Overview: yellow_tripdata_2025-12.parquet

## Dataset Summary

| metric       | value                                                                               |
|:-------------|:------------------------------------------------------------------------------------|
| file         | /root/Dev/DataGate/experiments/data/parquets/yellow/yellow_tripdata_2025-12.parquet |
| rows         | 4305006                                                                             |
| columns      | 20                                                                                  |
| row_groups   | 5                                                                                   |
| file_size_mb | 70.29                                                                               |
| rows_loaded  | 4305006                                                                             |

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
| VendorID              | int32          |    4305006 |       0 |   0.0000 |        4 |
| tpep_pickup_datetime  | datetime64[us] |    4305006 |       0 |   0.0000 |  1858364 |
| tpep_dropoff_datetime | datetime64[us] |    4305006 |       0 |   0.0000 |  1857475 |
| passenger_count       | float64        |    3109524 | 1195482 |  27.7696 |       10 |
| trip_distance         | float64        |    4305006 |       0 |   0.0000 |     4977 |
| RatecodeID            | float64        |    3109524 | 1195482 |  27.7696 |        7 |
| store_and_fwd_flag    | str            |    3109524 | 1195482 |  27.7696 |        2 |
| PULocationID          | int32          |    4305006 |       0 |   0.0000 |      260 |
| DOLocationID          | int32          |    4305006 |       0 |   0.0000 |      261 |
| payment_type          | int64          |    4305006 |       0 |   0.0000 |        5 |
| fare_amount           | float64        |    4305006 |       0 |   0.0000 |    14265 |
| extra                 | float64        |    4305006 |       0 |   0.0000 |       52 |
| mta_tax               | float64        |    4305006 |       0 |   0.0000 |        9 |
| tip_amount            | float64        |    4305006 |       0 |   0.0000 |     4611 |
| tolls_amount          | float64        |    4305006 |       0 |   0.0000 |     1466 |
| improvement_surcharge | float64        |    4305006 |       0 |   0.0000 |        4 |
| total_amount          | float64        |    4305006 |       0 |   0.0000 |    22881 |
| congestion_surcharge  | float64        |    3109524 | 1195482 |  27.7696 |        4 |
| Airport_fee           | float64        |    3109524 | 1195482 |  27.7696 |        5 |
| cbd_congestion_fee    | float64        |    4305006 |       0 |   0.0000 |        3 |

## Numeric Statistics (full-data)

| column                |        min |      p25 |   median |     mean |      p75 |         max |      std |
|:----------------------|-----------:|---------:|---------:|---------:|---------:|------------:|---------:|
| VendorID              |     1.0000 |   2.0000 |   2.0000 |   1.8792 |   2.0000 |      7.0000 |   0.7262 |
| passenger_count       |     0.0000 |   1.0000 |   1.0000 |   1.3138 |   1.0000 |      9.0000 |   0.7425 |
| trip_distance         |     0.0000 |   1.0000 |   1.8100 |   6.9412 |   3.7800 | 322576.1700 | 718.4367 |
| RatecodeID            |     1.0000 |   1.0000 |   1.0000 |   4.7952 |   1.0000 |     99.0000 |  18.6367 |
| PULocationID          |     1.0000 | 114.0000 | 161.0000 | 161.7788 | 233.0000 |    265.0000 |  66.6993 |
| DOLocationID          |     1.0000 | 107.0000 | 162.0000 | 161.1376 | 234.0000 |    265.0000 |  70.6869 |
| payment_type          |     0.0000 |   0.0000 |   1.0000 |   0.8732 |   1.0000 |      4.0000 |   0.7200 |
| fare_amount           | -1377.1000 |  10.1900 |  16.9400 |  22.2176 |  28.2000 |   2157.6000 |  19.8522 |
| extra                 |    -7.5000 |   0.0000 |   0.0000 |   1.0721 |   2.5000 |     15.0000 |   1.7565 |
| mta_tax               |    -0.5000 |   0.5000 |   0.5000 |   0.4817 |   0.5000 |     96.0000 |   0.1278 |
| tip_amount            |   -96.5000 |   0.0000 |   2.0000 |   2.8282 |   4.0000 |    800.0000 |   4.1077 |
| tolls_amount          |  -106.9300 |   0.0000 |   0.0000 |   0.5119 |   0.0000 |    106.9300 |   2.1513 |
| improvement_surcharge |    -1.0000 |   1.0000 |   1.0000 |   0.9493 |   1.0000 |      1.0000 |   0.2655 |
| total_amount          | -1382.8500 |  17.6000 |  24.4200 |  30.8767 |  36.5300 |   2162.3500 |  23.7899 |
| congestion_surcharge  |    -2.5000 |   2.5000 |   2.5000 |   2.1665 |   2.5000 |      2.5000 |   0.9374 |
| Airport_fee           |    -1.7500 |   0.0000 |   0.0000 |   0.1475 |   0.0000 |      6.7500 |   0.5238 |
| cbd_congestion_fee    |    -0.7500 |   0.0000 |   0.7500 |   0.5272 |   0.7500 |      0.7500 |   0.3551 |

## Datetime Coverage (full-data)

| column                | min_ts              | max_ts              | span             |
|:----------------------|:--------------------|:--------------------|:-----------------|
| tpep_pickup_datetime  | 2025-11-30 20:48:56 | 2025-12-31 23:59:59 | 31 days 03:11:03 |
| tpep_dropoff_datetime | 2025-11-30 20:57:48 | 2026-01-05 13:00:34 | 35 days 16:02:46 |

## Datetime Distribution by Day (full-data)

| column                | day        |   rows |   row_% |
|:----------------------|:-----------|-------:|--------:|
| tpep_pickup_datetime  | 2025-11-30 |      9 |  0.0002 |
| tpep_pickup_datetime  | 2025-12-01 | 125341 |  2.9115 |
| tpep_pickup_datetime  | 2025-12-02 | 146523 |  3.4035 |
| tpep_pickup_datetime  | 2025-12-03 | 150529 |  3.4966 |
| tpep_pickup_datetime  | 2025-12-04 | 171170 |  3.9761 |
| tpep_pickup_datetime  | 2025-12-05 | 170278 |  3.9553 |
| tpep_pickup_datetime  | 2025-12-06 | 168387 |  3.9114 |
| tpep_pickup_datetime  | 2025-12-07 | 141064 |  3.2767 |
| tpep_pickup_datetime  | 2025-12-08 | 142984 |  3.3213 |
| tpep_pickup_datetime  | 2025-12-09 | 159436 |  3.7035 |
| tpep_pickup_datetime  | 2025-12-10 | 165676 |  3.8484 |
| tpep_pickup_datetime  | 2025-12-11 | 181547 |  4.2171 |
| tpep_pickup_datetime  | 2025-12-12 | 182484 |  4.2389 |
| tpep_pickup_datetime  | 2025-12-13 | 180534 |  4.1936 |
| tpep_pickup_datetime  | 2025-12-14 | 159914 |  3.7146 |
| tpep_pickup_datetime  | 2025-12-15 | 150723 |  3.5011 |
| tpep_pickup_datetime  | 2025-12-16 | 158518 |  3.6822 |
| tpep_pickup_datetime  | 2025-12-17 | 159874 |  3.7137 |
| tpep_pickup_datetime  | 2025-12-18 | 166137 |  3.8592 |
| tpep_pickup_datetime  | 2025-12-19 | 171960 |  3.9944 |
| tpep_pickup_datetime  | 2025-12-20 | 156918 |  3.6450 |
| tpep_pickup_datetime  | 2025-12-21 | 124368 |  2.8889 |
| tpep_pickup_datetime  | 2025-12-22 | 114270 |  2.6544 |
| tpep_pickup_datetime  | 2025-12-23 | 112450 |  2.6121 |
| tpep_pickup_datetime  | 2025-12-24 | 100600 |  2.3368 |
| tpep_pickup_datetime  | 2025-12-25 |  68111 |  1.5821 |
| tpep_pickup_datetime  | 2025-12-26 |  83927 |  1.9495 |
| tpep_pickup_datetime  | 2025-12-27 |  85759 |  1.9921 |
| tpep_pickup_datetime  | 2025-12-28 |  91036 |  2.1147 |
| tpep_pickup_datetime  | 2025-12-29 |  96991 |  2.2530 |
| tpep_pickup_datetime  | 2025-12-30 | 105865 |  2.4591 |
| tpep_pickup_datetime  | 2025-12-31 | 111623 |  2.5929 |
| tpep_dropoff_datetime | 2025-11-30 |      4 |  0.0001 |
| tpep_dropoff_datetime | 2025-12-01 | 124427 |  2.8903 |
| tpep_dropoff_datetime | 2025-12-02 | 146365 |  3.3999 |
| tpep_dropoff_datetime | 2025-12-03 | 150068 |  3.4859 |
| tpep_dropoff_datetime | 2025-12-04 | 170173 |  3.9529 |
| tpep_dropoff_datetime | 2025-12-05 | 169764 |  3.9434 |
| tpep_dropoff_datetime | 2025-12-06 | 168094 |  3.9046 |
| tpep_dropoff_datetime | 2025-12-07 | 143704 |  3.3381 |
| tpep_dropoff_datetime | 2025-12-08 | 142663 |  3.3139 |
| tpep_dropoff_datetime | 2025-12-09 | 158955 |  3.6923 |
| tpep_dropoff_datetime | 2025-12-10 | 165263 |  3.8389 |
| tpep_dropoff_datetime | 2025-12-11 | 180467 |  4.1920 |
| tpep_dropoff_datetime | 2025-12-12 | 182353 |  4.2358 |
| tpep_dropoff_datetime | 2025-12-13 | 180114 |  4.1838 |
| tpep_dropoff_datetime | 2025-12-14 | 162583 |  3.7766 |
| tpep_dropoff_datetime | 2025-12-15 | 150618 |  3.4987 |
| tpep_dropoff_datetime | 2025-12-16 | 158175 |  3.6742 |
| tpep_dropoff_datetime | 2025-12-17 | 159477 |  3.7045 |
| tpep_dropoff_datetime | 2025-12-18 | 165343 |  3.8407 |
| tpep_dropoff_datetime | 2025-12-19 | 171893 |  3.9929 |
| tpep_dropoff_datetime | 2025-12-20 | 157220 |  3.6520 |
| tpep_dropoff_datetime | 2025-12-21 | 125887 |  2.9242 |
| tpep_dropoff_datetime | 2025-12-22 | 114242 |  2.6537 |
| tpep_dropoff_datetime | 2025-12-23 | 112536 |  2.6141 |
| tpep_dropoff_datetime | 2025-12-24 | 100590 |  2.3366 |
| tpep_dropoff_datetime | 2025-12-25 |  68238 |  1.5851 |
| tpep_dropoff_datetime | 2025-12-26 |  83849 |  1.9477 |
| tpep_dropoff_datetime | 2025-12-27 |  85331 |  1.9821 |
| tpep_dropoff_datetime | 2025-12-28 |  91148 |  2.1173 |
| tpep_dropoff_datetime | 2025-12-29 |  96933 |  2.2516 |
| tpep_dropoff_datetime | 2025-12-30 | 105809 |  2.4578 |
| tpep_dropoff_datetime | 2025-12-31 | 111946 |  2.6004 |
| tpep_dropoff_datetime | 2026-01-01 |    771 |  0.0179 |
| tpep_dropoff_datetime | 2026-01-02 |      2 |  0.0000 |
| tpep_dropoff_datetime | 2026-01-05 |      1 |  0.0000 |

## Top Values (full-data, top 5)

| column                | top_5_values                                                          |
|:----------------------|:----------------------------------------------------------------------|
| VendorID              | 2: 3417640, 1: 825421, 7: 57416, 6: 4529                              |
| passenger_count       | 1.0: 2443369, <NULL>: 1195482, 2.0: 428566, 3.0: 112613, 4.0: 89642   |
| RatecodeID            | 1.0: 2824227, <NULL>: 1195482, 99.0: 117021, 2.0: 99471, 5.0: 43038   |
| store_and_fwd_flag    | N: 3104510, <NULL>: 1195482, Y: 5014                                  |
| payment_type          | 1: 2618772, 0: 1195482, 2: 401019, 4: 69145, 3: 20588                 |
| mta_tax               | 0.5: 4193028, 0.0: 66067, -0.5: 45897, 4.75: 6, 3.75: 3               |
| improvement_surcharge | 1.0: 4133747, 0.0: 118357, -1.0: 48516, 0.3: 4386                     |
| congestion_surcharge  | 2.5: 2733570, <NULL>: 1195482, 0.0: 337088, -2.5: 38865, 1.0: 1       |
| Airport_fee           | 0.0: 2831768, <NULL>: 1195482, 1.75: 265639, -1.75: 10259, 6.75: 1437 |
| cbd_congestion_fee    | 0.75: 3059211, 0.0: 1212745, -0.75: 33050                             |

## Data Quality Signals

- Duplicate rows in full data: `0` / `4305006`.
- Numeric columns containing negative values: `fare_amount`, `extra`, `mta_tax`, `tip_amount`, `tolls_amount`, `improvement_surcharge`, `total_amount`, `congestion_surcharge`, `Airport_fee`, `cbd_congestion_fee`.

## Data Preview

|   VendorID | tpep_pickup_datetime   | tpep_dropoff_datetime   |   passenger_count |   trip_distance |   RatecodeID | store_and_fwd_flag   |   PULocationID |   DOLocationID |   payment_type |   fare_amount |   extra |   mta_tax |   tip_amount |   tolls_amount |   improvement_surcharge |   total_amount |   congestion_surcharge |   Airport_fee |   cbd_congestion_fee |
|-----------:|:-----------------------|:------------------------|------------------:|----------------:|-------------:|:---------------------|---------------:|---------------:|---------------:|--------------:|--------:|----------:|-------------:|---------------:|------------------------:|---------------:|-----------------------:|--------------:|---------------------:|
|          1 | 2025-12-01 00:37:08    | 2025-12-01 00:51:10     |                 1 |            2.4  |            1 | N                    |            140 |             48 |              1 |          14.2 |    4.25 |       0.5 |         4    |           0    |                       1 |          23.95 |                    2.5 |          0    |                 0.75 |
|          2 | 2025-12-01 00:03:54    | 2025-12-01 00:19:18     |                 1 |            8.37 |            1 | N                    |            138 |            262 |              1 |          33.1 |    6    |       0.5 |         7.77 |           6.94 |                       1 |          59.56 |                    2.5 |          1.75 |                 0    |
|          2 | 2025-12-01 00:40:50    | 2025-12-01 01:06:54     |                 1 |           15.26 |            1 | N                    |            132 |            255 |              1 |          57.6 |    1    |       0.5 |        12.02 |           0    |                       1 |          73.87 |                    0   |          1.75 |                 0    |
|          1 | 2025-12-01 00:21:30    | 2025-12-01 00:49:35     |                 2 |           18.4  |            2 | N                    |            132 |             79 |              1 |          70   |    5    |       0.5 |        10    |           0    |                       1 |          86.5  |                    2.5 |          1.75 |                 0.75 |
|          2 | 2025-12-01 00:00:24    | 2025-12-01 00:03:34     |                 1 |            0.52 |            1 | N                    |            239 |            238 |              1 |           5.8 |    1    |       0.5 |         1.62 |           0    |                       1 |          12.42 |                    2.5 |          0    |                 0    |
|          1 | 2025-12-01 00:11:36    | 2025-12-01 00:33:17     |                 1 |            0    |            1 | N                    |            138 |             82 |              1 |          16.3 |    7.75 |       0.5 |         5.1  |           0    |                       1 |          30.65 |                    0   |          1.75 |                 0    |
|          2 | 2025-11-30 23:59:23    | 2025-12-01 00:12:43     |                 1 |            2.59 |            1 | N                    |            142 |            263 |              1 |          14.9 |    1    |       0.5 |         3.98 |           0    |                       1 |          23.88 |                    2.5 |          0    |                 0    |
|          2 | 2025-12-01 00:18:25    | 2025-12-01 00:30:09     |                 1 |            2.22 |            1 | N                    |            141 |            238 |              1 |          13.5 |    1    |       0.5 |         2    |           0    |                       1 |          20.5  |                    2.5 |          0    |                 0    |
|          2 | 2025-12-01 00:54:33    | 2025-12-01 01:22:25     |                 1 |            9.06 |            1 | N                    |             48 |            106 |              1 |          38   |    1    |       0.5 |        11.53 |          13.88 |                       1 |          69.16 |                    2.5 |          0    |                 0.75 |
|          2 | 2025-12-01 00:28:35    | 2025-12-01 00:59:37     |                 1 |           18.02 |            1 | N                    |            132 |            145 |              1 |          69.5 |    1    |       0.5 |        14.75 |           0    |                       1 |          88.5  |                    0   |          1.75 |                 0    |
