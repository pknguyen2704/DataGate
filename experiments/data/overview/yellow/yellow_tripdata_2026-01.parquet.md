# Data Overview: yellow_tripdata_2026-01.parquet

## Dataset Summary

| metric       | value                                                                               |
|:-------------|:------------------------------------------------------------------------------------|
| file         | /root/Dev/DataGate/experiments/data/parquets/yellow/yellow_tripdata_2026-01.parquet |
| rows         | 3724889                                                                             |
| columns      | 20                                                                                  |
| row_groups   | 4                                                                                   |
| file_size_mb | 61.19                                                                               |
| rows_loaded  | 3724889                                                                             |

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
| VendorID              | int32          |    3724889 |       0 |   0.0000 |        4 |
| tpep_pickup_datetime  | datetime64[us] |    3724889 |       0 |   0.0000 |  1757191 |
| tpep_dropoff_datetime | datetime64[us] |    3724889 |       0 |   0.0000 |  1755995 |
| passenger_count       | float64        |    2636831 | 1088058 |  29.2105 |       10 |
| trip_distance         | float64        |    3724889 |       0 |   0.0000 |     4777 |
| RatecodeID            | float64        |    2636831 | 1088058 |  29.2105 |        7 |
| store_and_fwd_flag    | str            |    2636831 | 1088058 |  29.2105 |        2 |
| PULocationID          | int32          |    3724889 |       0 |   0.0000 |      262 |
| DOLocationID          | int32          |    3724889 |       0 |   0.0000 |      260 |
| payment_type          | int64          |    3724889 |       0 |   0.0000 |        5 |
| fare_amount           | float64        |    3724889 |       0 |   0.0000 |    12867 |
| extra                 | float64        |    3724889 |       0 |   0.0000 |       45 |
| mta_tax               | float64        |    3724889 |       0 |   0.0000 |        6 |
| tip_amount            | float64        |    3724889 |       0 |   0.0000 |     4326 |
| tolls_amount          | float64        |    3724889 |       0 |   0.0000 |     1495 |
| improvement_surcharge | float64        |    3724889 |       0 |   0.0000 |        4 |
| total_amount          | float64        |    3724889 |       0 |   0.0000 |    21228 |
| congestion_surcharge  | float64        |    2636831 | 1088058 |  29.2105 |        3 |
| Airport_fee           | float64        |    2636831 | 1088058 |  29.2105 |        8 |
| cbd_congestion_fee    | float64        |    3724889 |       0 |   0.0000 |        3 |

## Numeric Statistics (full-data)

| column                |        min |      p25 |   median |     mean |      p75 |         max |      std |
|:----------------------|-----------:|---------:|---------:|---------:|---------:|------------:|---------:|
| VendorID              |     1.0000 |   2.0000 |   2.0000 |   1.8736 |   2.0000 |      7.0000 |   0.7015 |
| passenger_count       |     0.0000 |   1.0000 |   1.0000 |   1.2563 |   1.0000 |      9.0000 |   0.6702 |
| trip_distance         |     0.0000 |   1.0000 |   1.8100 |   6.4556 |   3.7300 | 269097.4800 | 648.8855 |
| RatecodeID            |     1.0000 |   1.0000 |   1.0000 |   5.2189 |   1.0000 |     99.0000 |  19.6537 |
| PULocationID          |     1.0000 | 114.0000 | 161.0000 | 161.4372 | 233.0000 |    265.0000 |  67.0666 |
| DOLocationID          |     1.0000 | 107.0000 | 162.0000 | 160.9936 | 234.0000 |    265.0000 |  71.0360 |
| payment_type          |     0.0000 |   0.0000 |   1.0000 |   0.8466 |   1.0000 |      4.0000 |   0.7120 |
| fare_amount           | -2555.2000 |  10.0000 |  15.6000 |  20.8043 |  26.1000 |   2555.2000 |  18.9270 |
| extra                 |    -7.5000 |   0.0000 |   0.0000 |   1.0231 |   2.5000 |     17.4600 |   1.7073 |
| mta_tax               |    -0.5000 |   0.5000 |   0.5000 |   0.4834 |   0.5000 |      4.7500 |   0.1146 |
| tip_amount            |   -88.8800 |   0.0000 |   2.0000 |   2.6081 |   3.7100 |    766.0000 |   3.9174 |
| tolls_amount          |   -94.5000 |   0.0000 |   0.0000 |   0.4984 |   0.0000 |    122.2200 |   2.1317 |
| improvement_surcharge |    -1.0000 |   1.0000 |   1.0000 |   0.9479 |   1.0000 |      1.0000 |   0.2655 |
| total_amount          | -2560.2000 |  17.0000 |  23.0500 |  29.1785 |  33.8300 |   2560.2000 |  22.5855 |
| congestion_surcharge  |    -2.5000 |   2.5000 |   2.5000 |   2.1549 |   2.5000 |      2.5000 |   0.9424 |
| Airport_fee           |    -1.7500 |   0.0000 |   0.0000 |   0.1483 |   0.0000 |     26.7500 |   0.5337 |
| cbd_congestion_fee    |    -0.7500 |   0.0000 |   0.7500 |   0.5196 |   0.7500 |      0.7500 |   0.3568 |

## Datetime Coverage (full-data)

| column                | min_ts              | max_ts              | span             |
|:----------------------|:--------------------|:--------------------|:-----------------|
| tpep_pickup_datetime  | 2025-12-31 23:57:29 | 2026-02-01 00:45:01 | 31 days 00:47:32 |
| tpep_dropoff_datetime | 2025-12-31 23:57:32 | 2026-02-01 23:35:31 | 31 days 23:37:59 |

## Datetime Distribution by Day (full-data)

| column                | day        |   rows |   row_% |
|:----------------------|:-----------|-------:|--------:|
| tpep_pickup_datetime  | 2025-12-31 |      6 |  0.0002 |
| tpep_pickup_datetime  | 2026-01-01 | 114466 |  3.0730 |
| tpep_pickup_datetime  | 2026-01-02 | 100054 |  2.6861 |
| tpep_pickup_datetime  | 2026-01-03 | 108632 |  2.9164 |
| tpep_pickup_datetime  | 2026-01-04 |  93622 |  2.5134 |
| tpep_pickup_datetime  | 2026-01-05 |  96951 |  2.6028 |
| tpep_pickup_datetime  | 2026-01-06 | 107485 |  2.8856 |
| tpep_pickup_datetime  | 2026-01-07 | 113071 |  3.0356 |
| tpep_pickup_datetime  | 2026-01-08 | 119516 |  3.2086 |
| tpep_pickup_datetime  | 2026-01-09 | 124026 |  3.3297 |
| tpep_pickup_datetime  | 2026-01-10 | 145411 |  3.9038 |
| tpep_pickup_datetime  | 2026-01-11 | 116006 |  3.1143 |
| tpep_pickup_datetime  | 2026-01-12 | 112970 |  3.0328 |
| tpep_pickup_datetime  | 2026-01-13 | 123339 |  3.3112 |
| tpep_pickup_datetime  | 2026-01-14 | 130024 |  3.4907 |
| tpep_pickup_datetime  | 2026-01-15 | 141194 |  3.7906 |
| tpep_pickup_datetime  | 2026-01-16 | 134510 |  3.6111 |
| tpep_pickup_datetime  | 2026-01-17 | 128070 |  3.4382 |
| tpep_pickup_datetime  | 2026-01-18 | 119164 |  3.1991 |
| tpep_pickup_datetime  | 2026-01-19 | 100343 |  2.6939 |
| tpep_pickup_datetime  | 2026-01-20 | 130352 |  3.4995 |
| tpep_pickup_datetime  | 2026-01-21 | 130064 |  3.4918 |
| tpep_pickup_datetime  | 2026-01-22 | 136180 |  3.6559 |
| tpep_pickup_datetime  | 2026-01-23 | 143551 |  3.8538 |
| tpep_pickup_datetime  | 2026-01-24 | 145194 |  3.8979 |
| tpep_pickup_datetime  | 2026-01-25 |  44858 |  1.2043 |
| tpep_pickup_datetime  | 2026-01-26 |  69172 |  1.8570 |
| tpep_pickup_datetime  | 2026-01-27 | 122211 |  3.2809 |
| tpep_pickup_datetime  | 2026-01-28 | 132513 |  3.5575 |
| tpep_pickup_datetime  | 2026-01-29 | 143987 |  3.8655 |
| tpep_pickup_datetime  | 2026-01-30 | 153101 |  4.1102 |
| tpep_pickup_datetime  | 2026-01-31 | 144845 |  3.8886 |
| tpep_pickup_datetime  | 2026-02-01 |      1 |  0.0000 |
| tpep_dropoff_datetime | 2025-12-31 |      2 |  0.0001 |
| tpep_dropoff_datetime | 2026-01-01 | 113858 |  3.0567 |
| tpep_dropoff_datetime | 2026-01-02 |  99567 |  2.6730 |
| tpep_dropoff_datetime | 2026-01-03 | 108570 |  2.9147 |
| tpep_dropoff_datetime | 2026-01-04 |  94057 |  2.5251 |
| tpep_dropoff_datetime | 2026-01-05 |  96949 |  2.6027 |
| tpep_dropoff_datetime | 2026-01-06 | 107612 |  2.8890 |
| tpep_dropoff_datetime | 2026-01-07 | 112933 |  3.0318 |
| tpep_dropoff_datetime | 2026-01-08 | 119159 |  3.1990 |
| tpep_dropoff_datetime | 2026-01-09 | 123253 |  3.3089 |
| tpep_dropoff_datetime | 2026-01-10 | 144930 |  3.8909 |
| tpep_dropoff_datetime | 2026-01-11 | 117556 |  3.1560 |
| tpep_dropoff_datetime | 2026-01-12 | 113152 |  3.0377 |
| tpep_dropoff_datetime | 2026-01-13 | 123293 |  3.3100 |
| tpep_dropoff_datetime | 2026-01-14 | 129934 |  3.4883 |
| tpep_dropoff_datetime | 2026-01-15 | 140729 |  3.7781 |
| tpep_dropoff_datetime | 2026-01-16 | 133899 |  3.5947 |
| tpep_dropoff_datetime | 2026-01-17 | 128105 |  3.4392 |
| tpep_dropoff_datetime | 2026-01-18 | 119846 |  3.2174 |
| tpep_dropoff_datetime | 2026-01-19 | 100708 |  2.7037 |
| tpep_dropoff_datetime | 2026-01-20 | 130415 |  3.5012 |
| tpep_dropoff_datetime | 2026-01-21 | 130098 |  3.4927 |
| tpep_dropoff_datetime | 2026-01-22 | 135671 |  3.6423 |
| tpep_dropoff_datetime | 2026-01-23 | 142651 |  3.8297 |
| tpep_dropoff_datetime | 2026-01-24 | 145392 |  3.9033 |
| tpep_dropoff_datetime | 2026-01-25 |  46509 |  1.2486 |
| tpep_dropoff_datetime | 2026-01-26 |  68612 |  1.8420 |
| tpep_dropoff_datetime | 2026-01-27 | 122135 |  3.2789 |
| tpep_dropoff_datetime | 2026-01-28 | 132486 |  3.5568 |
| tpep_dropoff_datetime | 2026-01-29 | 143379 |  3.8492 |
| tpep_dropoff_datetime | 2026-01-30 | 152381 |  4.0909 |
| tpep_dropoff_datetime | 2026-01-31 | 144766 |  3.8865 |
| tpep_dropoff_datetime | 2026-02-01 |   2282 |  0.0613 |

## Top Values (full-data, top 5)

| column                | top_5_values                                                         |
|:----------------------|:---------------------------------------------------------------------|
| VendorID              | 2: 2965742, 1: 710425, 7: 44705, 6: 4017                             |
| passenger_count       | 1.0: 2150994, <NULL>: 1088058, 2.0: 334370, 3.0: 72864, 4.0: 49738   |
| RatecodeID            | 1.0: 2390495, <NULL>: 1088058, 99.0: 110864, 2.0: 83592, 5.0: 32030  |
| store_and_fwd_flag    | N: 2634494, <NULL>: 1088058, Y: 2337                                 |
| payment_type          | 1: 2249747, 0: 1088058, 2: 314043, 4: 56400, 3: 16641                |
| mta_tax               | 0.5: 3638730, 0.0: 48423, -0.5: 37730, 3.75: 3, 4.75: 2              |
| improvement_surcharge | 1.0: 3569408, 0.0: 111767, -1.0: 39732, 0.3: 3982                    |
| congestion_surcharge  | 2.5: 2303259, <NULL>: 1088058, 0.0: 303124, -2.5: 30448              |
| Airport_fee           | 0.0: 2399229, <NULL>: 1088058, 1.75: 226970, -1.75: 9225, 6.75: 1034 |
| cbd_congestion_fee    | 0.75: 2606017, 0.0: 1093675, -0.75: 25197                            |

## Data Quality Signals

- Duplicate rows in full data: `0` / `3724889`.
- Numeric columns containing negative values: `fare_amount`, `extra`, `mta_tax`, `tip_amount`, `tolls_amount`, `improvement_surcharge`, `total_amount`, `congestion_surcharge`, `Airport_fee`, `cbd_congestion_fee`.

## Data Preview

|   VendorID | tpep_pickup_datetime   | tpep_dropoff_datetime   |   passenger_count |   trip_distance |   RatecodeID | store_and_fwd_flag   |   PULocationID |   DOLocationID |   payment_type |   fare_amount |   extra |   mta_tax |   tip_amount |   tolls_amount |   improvement_surcharge |   total_amount |   congestion_surcharge |   Airport_fee |   cbd_congestion_fee |
|-----------:|:-----------------------|:------------------------|------------------:|----------------:|-------------:|:---------------------|---------------:|---------------:|---------------:|--------------:|--------:|----------:|-------------:|---------------:|------------------------:|---------------:|-----------------------:|--------------:|---------------------:|
|          2 | 2026-01-01 00:54:04    | 2026-01-01 00:59:37     |                 1 |            0.97 |            1 | N                    |            239 |            238 |              1 |           7.2 |    1    |       0.5 |         3.66 |              0 |                       1 |          15.86 |                    2.5 |             0 |                 0    |
|          1 | 2026-01-01 00:34:04    | 2026-01-01 00:39:47     |                 0 |            0.9  |            1 | N                    |            163 |            162 |              2 |           7.9 |    4.25 |       0.5 |         0    |              0 |                       1 |          13.65 |                    2.5 |             0 |                 0.75 |
|          1 | 2026-01-01 00:57:06    | 2026-01-01 01:05:59     |                 0 |            1.4  |            1 | N                    |             43 |            237 |              1 |          10.7 |    4.25 |       0.5 |         2.5  |              0 |                       1 |          18.95 |                    2.5 |             0 |                 0.75 |
|          2 | 2026-01-01 00:15:22    | 2026-01-01 00:58:10     |                 4 |            5.58 |            1 | N                    |            142 |            209 |              1 |          38.7 |    1    |       0.5 |        11.11 |              0 |                       1 |          55.56 |                    2.5 |             0 |                 0.75 |
|          2 | 2026-01-01 00:27:13    | 2026-01-01 00:40:43     |                 0 |            2.16 |            1 | N                    |             88 |            144 |              1 |          13.5 |    1    |       0.5 |         3.85 |              0 |                       1 |          23.1  |                    2.5 |             0 |                 0.75 |
|          2 | 2026-01-01 00:47:11    | 2026-01-01 01:00:47     |                 2 |            2.33 |            1 | N                    |            144 |            137 |              1 |          14.2 |    1    |       0.5 |         4.99 |              0 |                       1 |          24.94 |                    2.5 |             0 |                 0.75 |
|          1 | 2026-01-01 00:17:54    | 2026-01-01 00:28:32     |                 1 |            1.3  |            1 | N                    |            142 |             50 |              2 |          11.4 |    4.25 |       0.5 |         0    |              0 |                       1 |          17.15 |                    2.5 |             0 |                 0.75 |
|          1 | 2026-01-01 00:34:28    | 2026-01-01 00:59:05     |                 0 |            2.9  |            1 | N                    |             50 |            234 |              1 |          22.6 |    4.25 |       0.5 |         5.65 |              0 |                       1 |          34    |                    2.5 |             0 |                 0.75 |
|          2 | 2026-01-01 00:34:14    | 2026-01-01 01:11:58     |                 1 |            5.34 |            1 | N                    |            161 |             45 |              1 |          37.3 |    1    |       0.5 |         8.61 |              0 |                       1 |          51.66 |                    2.5 |             0 |                 0.75 |
|          2 | 2026-01-01 00:41:07    | 2026-01-01 00:50:42     |                 3 |            1.83 |            1 | N                    |            237 |            263 |              1 |          10.7 |    1    |       0.5 |         2.36 |              0 |                       1 |          18.06 |                    2.5 |             0 |                 0    |
