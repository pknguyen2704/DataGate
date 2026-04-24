# Data Overview: yellow_tripdata_2025-09.parquet

## Dataset Summary

| metric       | value                                                                               |
|:-------------|:------------------------------------------------------------------------------------|
| file         | /root/Dev/DataGate/experiments/data/parquets/yellow/yellow_tripdata_2025-09.parquet |
| rows         | 4251015                                                                             |
| columns      | 20                                                                                  |
| row_groups   | 5                                                                                   |
| file_size_mb | 69.08                                                                               |
| rows_loaded  | 4251015                                                                             |

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
| VendorID              | int32          |    4251015 |       0 |   0.0000 |        4 |
| tpep_pickup_datetime  | datetime64[us] |    4251015 |       0 |   0.0000 |  1830655 |
| tpep_dropoff_datetime | datetime64[us] |    4251015 |       0 |   0.0000 |  1830279 |
| passenger_count       | float64        |    3183820 | 1067195 |  25.1045 |        9 |
| trip_distance         | float64        |    4251015 |       0 |   0.0000 |     5117 |
| RatecodeID            | float64        |    3183820 | 1067195 |  25.1045 |        7 |
| store_and_fwd_flag    | str            |    3183820 | 1067195 |  25.1045 |        2 |
| PULocationID          | int32          |    4251015 |       0 |   0.0000 |      259 |
| DOLocationID          | int32          |    4251015 |       0 |   0.0000 |      261 |
| payment_type          | int64          |    4251015 |       0 |   0.0000 |        5 |
| fare_amount           | float64        |    4251015 |       0 |   0.0000 |    11139 |
| extra                 | float64        |    4251015 |       0 |   0.0000 |       73 |
| mta_tax               | float64        |    4251015 |       0 |   0.0000 |       10 |
| tip_amount            | float64        |    4251015 |       0 |   0.0000 |     4728 |
| tolls_amount          | float64        |    4251015 |       0 |   0.0000 |     1368 |
| improvement_surcharge | float64        |    4251015 |       0 |   0.0000 |        4 |
| total_amount          | float64        |    4251015 |       0 |   0.0000 |    23356 |
| congestion_surcharge  | float64        |    3183820 | 1067195 |  25.1045 |        4 |
| Airport_fee           | float64        |    3183820 | 1067195 |  25.1045 |        5 |
| cbd_congestion_fee    | float64        |    4251015 |       0 |   0.0000 |        5 |

## Numeric Statistics (full-data)

| column                |        min |      p25 |   median |     mean |      p75 |         max |      std |
|:----------------------|-----------:|---------:|---------:|---------:|---------:|------------:|---------:|
| VendorID              |     1.0000 |   2.0000 |   2.0000 |   1.8769 |   2.0000 |      7.0000 |   0.7216 |
| passenger_count       |     0.0000 |   1.0000 |   1.0000 |   1.2642 |   1.0000 |      8.0000 |   0.6770 |
| trip_distance         |     0.0000 |   1.0700 |   1.9200 |   6.8394 |   3.9300 | 318608.5700 | 660.8708 |
| RatecodeID            |     1.0000 |   1.0000 |   1.0000 |   3.7516 |   1.0000 |     99.0000 |  15.8553 |
| PULocationID          |     1.0000 | 114.0000 | 161.0000 | 160.9733 | 232.0000 |    265.0000 |  66.5538 |
| DOLocationID          |     1.0000 | 107.0000 | 162.0000 | 160.8512 | 233.0000 |    265.0000 |  70.7863 |
| payment_type          |     0.0000 |   0.0000 |   1.0000 |   0.9255 |   1.0000 |      4.0000 |   0.7661 |
| fare_amount           |  -998.0000 |   9.3000 |  14.9000 |  19.2040 |  24.0000 | 323800.2700 | 158.2837 |
| extra                 |    -7.5000 |   0.0000 |   0.0000 |   1.1318 |   2.5000 |     38.6100 |   1.8094 |
| mta_tax               |    -0.5000 |   0.5000 |   0.5000 |   0.4750 |   0.5000 |     10.5000 |   0.1438 |
| tip_amount            |   -88.5500 |   0.0000 |   2.0000 |   2.8579 |   4.0000 |    400.0000 |   4.0489 |
| tolls_amount          |  -109.0600 |   0.0000 |   0.0000 |   0.5181 |   0.0000 |    134.0600 |   2.1653 |
| improvement_surcharge |    -1.0000 |   1.0000 |   1.0000 |   0.9422 |   1.0000 |      1.0000 |   0.3019 |
| total_amount          | -1002.2500 |  16.3200 |  22.1500 |  27.7133 |  31.8200 | 323820.1700 | 158.8736 |
| congestion_surcharge  |    -2.5000 |   2.5000 |   2.5000 |   2.1523 |   2.5000 |      2.5000 |   0.9926 |
| Airport_fee           |    -1.7500 |   0.0000 |   0.0000 |   0.1498 |   0.0000 |      6.7500 |   0.5400 |
| cbd_congestion_fee    |    -0.7500 |   0.0000 |   0.7500 |   0.5343 |   0.7500 |      1.7500 |   0.3592 |

## Datetime Coverage (full-data)

| column                | min_ts              | max_ts              | span             |
|:----------------------|:--------------------|:--------------------|:-----------------|
| tpep_pickup_datetime  | 2025-08-31 23:45:38 | 2025-10-01 00:00:11 | 30 days 00:14:33 |
| tpep_dropoff_datetime | 2025-08-31 23:46:43 | 2025-10-03 14:49:31 | 32 days 15:02:48 |

## Datetime Distribution by Day (full-data)

| column                | day        |   rows |   row_% |
|:----------------------|:-----------|-------:|--------:|
| tpep_pickup_datetime  | 2025-08-31 |      6 |  0.0001 |
| tpep_pickup_datetime  | 2025-09-01 |  98006 |  2.3055 |
| tpep_pickup_datetime  | 2025-09-02 | 118917 |  2.7974 |
| tpep_pickup_datetime  | 2025-09-03 | 131860 |  3.1018 |
| tpep_pickup_datetime  | 2025-09-04 | 150893 |  3.5496 |
| tpep_pickup_datetime  | 2025-09-05 | 147058 |  3.4594 |
| tpep_pickup_datetime  | 2025-09-06 | 148005 |  3.4816 |
| tpep_pickup_datetime  | 2025-09-07 | 128728 |  3.0282 |
| tpep_pickup_datetime  | 2025-09-08 | 124409 |  2.9266 |
| tpep_pickup_datetime  | 2025-09-09 | 140841 |  3.3131 |
| tpep_pickup_datetime  | 2025-09-10 | 152786 |  3.5941 |
| tpep_pickup_datetime  | 2025-09-11 | 155338 |  3.6541 |
| tpep_pickup_datetime  | 2025-09-12 | 161096 |  3.7896 |
| tpep_pickup_datetime  | 2025-09-13 | 166369 |  3.9136 |
| tpep_pickup_datetime  | 2025-09-14 | 145484 |  3.4223 |
| tpep_pickup_datetime  | 2025-09-15 | 129352 |  3.0428 |
| tpep_pickup_datetime  | 2025-09-16 | 143858 |  3.3841 |
| tpep_pickup_datetime  | 2025-09-17 | 149841 |  3.5248 |
| tpep_pickup_datetime  | 2025-09-18 | 161661 |  3.8029 |
| tpep_pickup_datetime  | 2025-09-19 | 155135 |  3.6494 |
| tpep_pickup_datetime  | 2025-09-20 | 157514 |  3.7053 |
| tpep_pickup_datetime  | 2025-09-21 | 137531 |  3.2353 |
| tpep_pickup_datetime  | 2025-09-22 | 119526 |  2.8117 |
| tpep_pickup_datetime  | 2025-09-23 | 116445 |  2.7392 |
| tpep_pickup_datetime  | 2025-09-24 | 135382 |  3.1847 |
| tpep_pickup_datetime  | 2025-09-25 | 152897 |  3.5967 |
| tpep_pickup_datetime  | 2025-09-26 | 155360 |  3.6547 |
| tpep_pickup_datetime  | 2025-09-27 | 163820 |  3.8537 |
| tpep_pickup_datetime  | 2025-09-28 | 138200 |  3.2510 |
| tpep_pickup_datetime  | 2025-09-29 | 124242 |  2.9226 |
| tpep_pickup_datetime  | 2025-09-30 | 140454 |  3.3040 |
| tpep_pickup_datetime  | 2025-10-01 |      1 |  0.0000 |
| tpep_dropoff_datetime | 2025-08-31 |      1 |  0.0000 |
| tpep_dropoff_datetime | 2025-09-01 |  97022 |  2.2823 |
| tpep_dropoff_datetime | 2025-09-02 | 119028 |  2.8000 |
| tpep_dropoff_datetime | 2025-09-03 | 131697 |  3.0980 |
| tpep_dropoff_datetime | 2025-09-04 | 150514 |  3.5407 |
| tpep_dropoff_datetime | 2025-09-05 | 146032 |  3.4352 |
| tpep_dropoff_datetime | 2025-09-06 | 147934 |  3.4800 |
| tpep_dropoff_datetime | 2025-09-07 | 130290 |  3.0649 |
| tpep_dropoff_datetime | 2025-09-08 | 124541 |  2.9297 |
| tpep_dropoff_datetime | 2025-09-09 | 140613 |  3.3078 |
| tpep_dropoff_datetime | 2025-09-10 | 152329 |  3.5834 |
| tpep_dropoff_datetime | 2025-09-11 | 154774 |  3.6409 |
| tpep_dropoff_datetime | 2025-09-12 | 160406 |  3.7734 |
| tpep_dropoff_datetime | 2025-09-13 | 166080 |  3.9068 |
| tpep_dropoff_datetime | 2025-09-14 | 147788 |  3.4765 |
| tpep_dropoff_datetime | 2025-09-15 | 129259 |  3.0407 |
| tpep_dropoff_datetime | 2025-09-16 | 143774 |  3.3821 |
| tpep_dropoff_datetime | 2025-09-17 | 149630 |  3.5199 |
| tpep_dropoff_datetime | 2025-09-18 | 161088 |  3.7894 |
| tpep_dropoff_datetime | 2025-09-19 | 154333 |  3.6305 |
| tpep_dropoff_datetime | 2025-09-20 | 156960 |  3.6923 |
| tpep_dropoff_datetime | 2025-09-21 | 139611 |  3.2842 |
| tpep_dropoff_datetime | 2025-09-22 | 119599 |  2.8134 |
| tpep_dropoff_datetime | 2025-09-23 | 116357 |  2.7372 |
| tpep_dropoff_datetime | 2025-09-24 | 135077 |  3.1775 |
| tpep_dropoff_datetime | 2025-09-25 | 152369 |  3.5843 |
| tpep_dropoff_datetime | 2025-09-26 | 154563 |  3.6359 |
| tpep_dropoff_datetime | 2025-09-27 | 163252 |  3.8403 |
| tpep_dropoff_datetime | 2025-09-28 | 140495 |  3.3050 |
| tpep_dropoff_datetime | 2025-09-29 | 124284 |  2.9236 |
| tpep_dropoff_datetime | 2025-09-30 | 140330 |  3.3011 |
| tpep_dropoff_datetime | 2025-10-01 |    984 |  0.0231 |
| tpep_dropoff_datetime | 2025-10-03 |      1 |  0.0000 |

## Top Values (full-data, top 5)

| column                | top_5_values                                                          |
|:----------------------|:----------------------------------------------------------------------|
| VendorID              | 2: 3374033, 1: 817547, 7: 56583, 6: 2852                              |
| passenger_count       | 1.0: 2563028, <NULL>: 1067195, 2.0: 434358, 3.0: 89427, 4.0: 55742    |
| RatecodeID            | 1.0: 2912913, <NULL>: 1067195, 2.0: 113658, 99.0: 85745, 5.0: 44993   |
| store_and_fwd_flag    | N: 3174177, <NULL>: 1067195, Y: 9643                                  |
| payment_type          | 1: 2676305, 0: 1067195, 2: 372069, 4: 107514, 3: 27932                |
| mta_tax               | 0.5: 4110678, -0.5: 73186, 0.0: 66938, 1.0: 199, 10.5: 5              |
| improvement_surcharge | 1.0: 4082962, 0.0: 86937, -1.0: 78311, 0.3: 2805                      |
| congestion_surcharge  | 2.5: 2801412, <NULL>: 1067195, 0.0: 322048, -2.5: 60358, 1.0: 2       |
| Airport_fee           | 0.0: 2881474, <NULL>: 1067195, 1.75: 282935, -1.75: 17441, 6.75: 1498 |
| cbd_congestion_fee    | 0.75: 3080596, 0.0: 1118280, -0.75: 52097, 1.5: 41, 1.75: 1           |

## Data Quality Signals

- Duplicate rows in full data: `0` / `4251015`.
- Numeric columns containing negative values: `fare_amount`, `extra`, `mta_tax`, `tip_amount`, `tolls_amount`, `improvement_surcharge`, `total_amount`, `congestion_surcharge`, `Airport_fee`, `cbd_congestion_fee`.

## Data Preview

|   VendorID | tpep_pickup_datetime   | tpep_dropoff_datetime   |   passenger_count |   trip_distance |   RatecodeID | store_and_fwd_flag   |   PULocationID |   DOLocationID |   payment_type |   fare_amount |   extra |   mta_tax |   tip_amount |   tolls_amount |   improvement_surcharge |   total_amount |   congestion_surcharge |   Airport_fee |   cbd_congestion_fee |
|-----------:|:-----------------------|:------------------------|------------------:|----------------:|-------------:|:---------------------|---------------:|---------------:|---------------:|--------------:|--------:|----------:|-------------:|---------------:|------------------------:|---------------:|-----------------------:|--------------:|---------------------:|
|          2 | 2025-09-01 00:19:20    | 2025-09-01 00:45:17     |                 1 |            9.92 |            1 | N                    |            138 |            114 |              1 |          42.9 |    6    |       0.5 |        10.73 |              0 |                       1 |          66.13 |                    2.5 |          1.75 |                 0.75 |
|          2 | 2025-09-01 00:15:20    | 2025-09-01 00:26:08     |                 2 |            6.82 |            1 | N                    |             93 |            157 |              1 |          26.8 |    1    |       0.5 |         5.86 |              0 |                       1 |          35.16 |                    0   |          0    |                 0    |
|          2 | 2025-09-01 00:06:07    | 2025-09-01 00:22:23     |                 1 |            3.95 |            1 | N                    |             68 |             13 |              1 |          19.8 |    1    |       0.5 |         5.11 |              0 |                       1 |          30.66 |                    2.5 |          0    |                 0.75 |
|          2 | 2025-09-01 00:49:47    | 2025-09-01 01:04:49     |                 1 |            3.14 |            1 | N                    |            234 |             87 |              1 |          17.7 |    1    |       0.5 |         3.52 |              0 |                       1 |          26.97 |                    2.5 |          0    |                 0.75 |
|          2 | 2025-09-01 00:05:00    | 2025-09-01 00:15:32     |                 6 |            2.81 |            1 | N                    |            230 |            151 |              1 |          14.9 |    1    |       0.5 |         4.13 |              0 |                       1 |          24.78 |                    2.5 |          0    |                 0.75 |
|          1 | 2025-09-01 00:16:53    | 2025-09-01 00:29:36     |                 2 |            2    |            1 | N                    |             79 |            164 |              1 |          14.2 |    4.25 |       0.5 |         4    |              0 |                       1 |          23.95 |                    2.5 |          0    |                 0.75 |
|          1 | 2025-09-01 00:33:01    | 2025-09-01 00:43:13     |                 2 |            3.1  |            1 | N                    |            164 |            236 |              1 |          14.9 |    4.25 |       0.5 |         4.1  |              0 |                       1 |          24.75 |                    2.5 |          0    |                 0.75 |
|          1 | 2025-09-01 00:56:37    | 2025-09-01 01:08:35     |                 1 |            1    |            1 | N                    |            170 |            229 |              1 |          12.1 |    4.25 |       0.5 |         3.55 |              0 |                       1 |          21.4  |                    2.5 |          0    |                 0.75 |
|          2 | 2025-09-01 00:13:47    | 2025-09-01 00:44:46     |                 1 |            6.41 |            1 | N                    |             79 |            177 |              1 |          33.8 |    1    |       0.5 |         7.91 |              0 |                       1 |          47.46 |                    2.5 |          0    |                 0.75 |
|          2 | 2025-09-01 00:13:27    | 2025-09-01 00:21:39     |                 2 |            1.16 |            1 | N                    |             48 |            162 |              1 |           8.6 |    1    |       0.5 |         2.87 |              0 |                       1 |          17.22 |                    2.5 |          0    |                 0.75 |
