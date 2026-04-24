# Data Overview: green_tripdata_2025-08.parquet

## Dataset Summary

| metric       | value                                                                             |
|:-------------|:----------------------------------------------------------------------------------|
| file         | /root/Dev/DataGate/experiments/data/parquets/green/green_tripdata_2025-08.parquet |
| rows         | 46306                                                                             |
| columns      | 21                                                                                |
| row_groups   | 1                                                                                 |
| file_size_mb | 1.10                                                                              |
| rows_loaded  | 46306                                                                             |

## Schema

| column                | parquet_type   | nullable   |
|:----------------------|:---------------|:-----------|
| VendorID              | int32          | True       |
| lpep_pickup_datetime  | timestamp[us]  | True       |
| lpep_dropoff_datetime | timestamp[us]  | True       |
| store_and_fwd_flag    | large_string   | True       |
| RatecodeID            | int64          | True       |
| PULocationID          | int32          | True       |
| DOLocationID          | int32          | True       |
| passenger_count       | int64          | True       |
| trip_distance         | double         | True       |
| fare_amount           | double         | True       |
| extra                 | double         | True       |
| mta_tax               | double         | True       |
| tip_amount            | double         | True       |
| tolls_amount          | double         | True       |
| ehail_fee             | double         | True       |
| improvement_surcharge | double         | True       |
| total_amount          | double         | True       |
| payment_type          | int64          | True       |
| trip_type             | int64          | True       |
| congestion_surcharge  | double         | True       |
| cbd_congestion_fee    | double         | True       |

## Column Health (full-data)

| column                | dtype          |   non_null |   null |   null_% |   unique |
|:----------------------|:---------------|-----------:|-------:|---------:|---------:|
| VendorID              | int32          |      46306 |      0 |   0.0000 |        3 |
| lpep_pickup_datetime  | datetime64[us] |      46306 |      0 |   0.0000 |    45578 |
| lpep_dropoff_datetime | datetime64[us] |      46306 |      0 |   0.0000 |    45565 |
| store_and_fwd_flag    | str            |      41564 |   4742 |  10.2406 |        2 |
| RatecodeID            | float64        |      41564 |   4742 |  10.2406 |        6 |
| PULocationID          | int32          |      46306 |      0 |   0.0000 |      231 |
| DOLocationID          | int32          |      46306 |      0 |   0.0000 |      246 |
| passenger_count       | float64        |      41564 |   4742 |  10.2406 |       10 |
| trip_distance         | float64        |      46306 |      0 |   0.0000 |     2158 |
| fare_amount           | float64        |      46306 |      0 |   0.0000 |     1381 |
| extra                 | float64        |      46306 |      0 |   0.0000 |       17 |
| mta_tax               | float64        |      46306 |      0 |   0.0000 |        5 |
| tip_amount            | float64        |      46306 |      0 |   0.0000 |     1603 |
| tolls_amount          | float64        |      46306 |      0 |   0.0000 |       33 |
| ehail_fee             | float64        |          0 |  46306 | 100.0000 |        0 |
| improvement_surcharge | float64        |      46306 |      0 |   0.0000 |        4 |
| total_amount          | float64        |      46306 |      0 |   0.0000 |     5157 |
| payment_type          | float64        |      41564 |   4742 |  10.2406 |        5 |
| trip_type             | float64        |      41563 |   4743 |  10.2427 |        2 |
| congestion_surcharge  | float64        |      41564 |   4742 |  10.2406 |        4 |
| cbd_congestion_fee    | float64        |      46306 |      0 |   0.0000 |        3 |

## Numeric Statistics (full-data)

| column                |       min |     p25 |   median |     mean |      p75 |         max |      std |
|:----------------------|----------:|--------:|---------:|---------:|---------:|------------:|---------:|
| VendorID              |    1.0000 |  2.0000 |   2.0000 |   2.1794 |   2.0000 |      6.0000 |   1.0929 |
| RatecodeID            |    1.0000 |  1.0000 |   1.0000 |   1.3724 |   1.0000 |     99.0000 |   1.2477 |
| PULocationID          |    1.0000 | 74.0000 |  75.0000 |  97.6661 |  97.0000 |    265.0000 |  56.7476 |
| DOLocationID          |    1.0000 | 75.0000 | 140.0000 | 142.8873 | 229.0000 |    265.0000 |  77.4720 |
| passenger_count       |    0.0000 |  1.0000 |   1.0000 |   1.3023 |   1.0000 |      9.0000 |   0.9487 |
| trip_distance         |    0.0000 |  1.3200 |   2.2300 |  13.5940 |   4.1000 | 110301.9600 | 870.4899 |
| fare_amount           | -120.0000 |  9.3000 |  14.2000 |  20.0409 |  21.9000 |    998.0000 |  21.9418 |
| extra                 |   -5.0000 |  0.0000 |   0.0000 |   0.8735 |   1.0000 |      7.5000 |   1.3874 |
| mta_tax               |   -0.5000 |  0.5000 |   0.5000 |   0.5490 |   0.5000 |      1.5000 |   0.3369 |
| tip_amount            |   -0.9000 |  0.0000 |   2.0000 |   2.8345 |   4.0000 |    350.0000 |   4.5397 |
| tolls_amount          |   -6.9400 |  0.0000 |   0.0000 |   0.3480 |   0.0000 |     38.0600 |   1.6223 |
| improvement_surcharge |   -1.0000 |  1.0000 |   1.0000 |   0.9365 |   1.0000 |      1.0000 |   0.2255 |
| total_amount          | -121.0000 | 15.1200 |  20.9750 |  27.8710 |  31.4400 |    998.0000 |  24.4294 |
| payment_type          |    1.0000 |  1.0000 |   1.0000 |   1.2733 |   2.0000 |      5.0000 |   0.4766 |
| trip_type             |    1.0000 |  1.0000 |   1.0000 |   1.0849 |   1.0000 |      2.0000 |   0.2787 |
| congestion_surcharge  |   -2.7500 |  0.0000 |   0.0000 |   0.8702 |   2.7500 |      2.7500 |   1.2799 |
| cbd_congestion_fee    |   -0.7500 |  0.0000 |   0.0000 |   0.0786 |   0.0000 |      0.7500 |   0.2298 |

## Datetime Coverage (full-data)

| column                | min_ts              | max_ts              | span             |
|:----------------------|:--------------------|:--------------------|:-----------------|
| lpep_pickup_datetime  | 2025-07-26 17:19:43 | 2025-09-01 20:46:57 | 37 days 03:27:14 |
| lpep_dropoff_datetime | 2025-07-26 17:19:45 | 2025-09-01 21:03:29 | 37 days 03:43:44 |

## Datetime Distribution by Day (full-data)

| column                | day        |   rows |   row_% |
|:----------------------|:-----------|-------:|--------:|
| lpep_pickup_datetime  | 2025-07-26 |      4 |  0.0086 |
| lpep_pickup_datetime  | 2025-07-27 |      1 |  0.0022 |
| lpep_pickup_datetime  | 2025-07-31 |      1 |  0.0022 |
| lpep_pickup_datetime  | 2025-08-01 |   1589 |  3.4315 |
| lpep_pickup_datetime  | 2025-08-02 |   1365 |  2.9478 |
| lpep_pickup_datetime  | 2025-08-03 |   1335 |  2.8830 |
| lpep_pickup_datetime  | 2025-08-04 |   1484 |  3.2048 |
| lpep_pickup_datetime  | 2025-08-05 |   1552 |  3.3516 |
| lpep_pickup_datetime  | 2025-08-06 |   1607 |  3.4704 |
| lpep_pickup_datetime  | 2025-08-07 |   1526 |  3.2955 |
| lpep_pickup_datetime  | 2025-08-08 |   1486 |  3.2091 |
| lpep_pickup_datetime  | 2025-08-09 |   1215 |  2.6239 |
| lpep_pickup_datetime  | 2025-08-10 |   1297 |  2.8009 |
| lpep_pickup_datetime  | 2025-08-11 |   1444 |  3.1184 |
| lpep_pickup_datetime  | 2025-08-12 |   1533 |  3.3106 |
| lpep_pickup_datetime  | 2025-08-13 |   1744 |  3.7663 |
| lpep_pickup_datetime  | 2025-08-14 |   1634 |  3.5287 |
| lpep_pickup_datetime  | 2025-08-15 |   1512 |  3.2652 |
| lpep_pickup_datetime  | 2025-08-16 |   1253 |  2.7059 |
| lpep_pickup_datetime  | 2025-08-17 |   1411 |  3.0471 |
| lpep_pickup_datetime  | 2025-08-18 |   1424 |  3.0752 |
| lpep_pickup_datetime  | 2025-08-19 |   1513 |  3.2674 |
| lpep_pickup_datetime  | 2025-08-20 |   1787 |  3.8591 |
| lpep_pickup_datetime  | 2025-08-21 |   1528 |  3.2998 |
| lpep_pickup_datetime  | 2025-08-22 |   1412 |  3.0493 |
| lpep_pickup_datetime  | 2025-08-23 |   1286 |  2.7772 |
| lpep_pickup_datetime  | 2025-08-24 |   1385 |  2.9910 |
| lpep_pickup_datetime  | 2025-08-25 |   1652 |  3.5676 |
| lpep_pickup_datetime  | 2025-08-26 |   1689 |  3.6475 |
| lpep_pickup_datetime  | 2025-08-27 |   1644 |  3.5503 |
| lpep_pickup_datetime  | 2025-08-28 |   1656 |  3.5762 |
| lpep_pickup_datetime  | 2025-08-29 |   1594 |  3.4423 |
| lpep_pickup_datetime  | 2025-08-30 |   1357 |  2.9305 |
| lpep_pickup_datetime  | 2025-08-31 |   1369 |  2.9564 |
| lpep_pickup_datetime  | 2025-09-01 |     17 |  0.0367 |
| lpep_dropoff_datetime | 2025-07-26 |      4 |  0.0086 |
| lpep_dropoff_datetime | 2025-07-27 |      1 |  0.0022 |
| lpep_dropoff_datetime | 2025-08-01 |   1568 |  3.3862 |
| lpep_dropoff_datetime | 2025-08-02 |   1356 |  2.9283 |
| lpep_dropoff_datetime | 2025-08-03 |   1359 |  2.9348 |
| lpep_dropoff_datetime | 2025-08-04 |   1485 |  3.2069 |
| lpep_dropoff_datetime | 2025-08-05 |   1550 |  3.3473 |
| lpep_dropoff_datetime | 2025-08-06 |   1602 |  3.4596 |
| lpep_dropoff_datetime | 2025-08-07 |   1529 |  3.3019 |
| lpep_dropoff_datetime | 2025-08-08 |   1468 |  3.1702 |
| lpep_dropoff_datetime | 2025-08-09 |   1212 |  2.6174 |
| lpep_dropoff_datetime | 2025-08-10 |   1317 |  2.8441 |
| lpep_dropoff_datetime | 2025-08-11 |   1439 |  3.1076 |
| lpep_dropoff_datetime | 2025-08-12 |   1539 |  3.3235 |
| lpep_dropoff_datetime | 2025-08-13 |   1732 |  3.7403 |
| lpep_dropoff_datetime | 2025-08-14 |   1641 |  3.5438 |
| lpep_dropoff_datetime | 2025-08-15 |   1503 |  3.2458 |
| lpep_dropoff_datetime | 2025-08-16 |   1256 |  2.7124 |
| lpep_dropoff_datetime | 2025-08-17 |   1424 |  3.0752 |
| lpep_dropoff_datetime | 2025-08-18 |   1421 |  3.0687 |
| lpep_dropoff_datetime | 2025-08-19 |   1513 |  3.2674 |
| lpep_dropoff_datetime | 2025-08-20 |   1781 |  3.8462 |
| lpep_dropoff_datetime | 2025-08-21 |   1532 |  3.3084 |
| lpep_dropoff_datetime | 2025-08-22 |   1406 |  3.0363 |
| lpep_dropoff_datetime | 2025-08-23 |   1284 |  2.7729 |
| lpep_dropoff_datetime | 2025-08-24 |   1383 |  2.9867 |
| lpep_dropoff_datetime | 2025-08-25 |   1648 |  3.5589 |
| lpep_dropoff_datetime | 2025-08-26 |   1689 |  3.6475 |
| lpep_dropoff_datetime | 2025-08-27 |   1651 |  3.5654 |
| lpep_dropoff_datetime | 2025-08-28 |   1655 |  3.5741 |
| lpep_dropoff_datetime | 2025-08-29 |   1596 |  3.4466 |
| lpep_dropoff_datetime | 2025-08-30 |   1349 |  2.9132 |
| lpep_dropoff_datetime | 2025-08-31 |   1374 |  2.9672 |
| lpep_dropoff_datetime | 2025-09-01 |     39 |  0.0842 |

## Top Values (full-data, top 5)

| column                | top_5_values                                             |
|:----------------------|:---------------------------------------------------------|
| VendorID              | 2: 38336, 1: 4715, 6: 3255                               |
| store_and_fwd_flag    | N: 41364, <NULL>: 4742, Y: 200                           |
| RatecodeID            | 1.0: 37607, <NULL>: 4742, 5.0: 3744, 2.0: 106, 4.0: 86   |
| passenger_count       | 1.0: 34197, <NULL>: 4742, 2.0: 4223, 5.0: 963, 0.0: 682  |
| mta_tax               | 0.5: 38064, 1.5: 4291, 0.0: 3824, -0.5: 117, 1.0: 10     |
| ehail_fee             | <NULL>: 46306                                            |
| improvement_surcharge | 1.0: 42540, 0.3: 3200, 0.0: 430, -1.0: 136               |
| payment_type          | 1.0: 30701, 2.0: 10457, <NULL>: 4742, 3.0: 319, 4.0: 83  |
| trip_type             | 1.0: 38035, <NULL>: 4743, 2.0: 3528                      |
| congestion_surcharge  | 0.0: 28395, 2.75: 13136, <NULL>: 4742, 2.5: 26, -2.75: 7 |
| cbd_congestion_fee    | 0.0: 41449, 0.75: 4856, -0.75: 1                         |

## Data Quality Signals

- Duplicate rows in full data: `0` / `46306`.
- Columns with >= 50% null in full data: `ehail_fee`.
- Near-constant columns in full data: `ehail_fee`.
- High-cardinality / ID-like columns: `lpep_pickup_datetime`, `lpep_dropoff_datetime`.
- Numeric columns containing negative values: `fare_amount`, `extra`, `mta_tax`, `tip_amount`, `tolls_amount`, `improvement_surcharge`, `total_amount`, `congestion_surcharge`, `cbd_congestion_fee`.

## Data Preview

|   VendorID | lpep_pickup_datetime   | lpep_dropoff_datetime   | store_and_fwd_flag   |   RatecodeID |   PULocationID |   DOLocationID |   passenger_count |   trip_distance |   fare_amount |   extra |   mta_tax |   tip_amount |   tolls_amount |   ehail_fee |   improvement_surcharge |   total_amount |   payment_type |   trip_type |   congestion_surcharge |   cbd_congestion_fee |
|-----------:|:-----------------------|:------------------------|:---------------------|-------------:|---------------:|---------------:|------------------:|----------------:|--------------:|--------:|----------:|-------------:|---------------:|------------:|------------------------:|---------------:|---------------:|------------:|-----------------------:|---------------------:|
|          2 | 2025-08-01 00:33:57    | 2025-08-01 00:58:10     | N                    |            1 |             70 |             82 |                 1 |            2.44 |          21.9 |       1 |       0.5 |         0    |              0 |         nan |                       1 |          24.4  |              2 |           1 |                   0    |                    0 |
|          2 | 2025-08-01 00:01:00    | 2025-08-01 00:12:58     | N                    |            1 |            130 |            216 |                 1 |            4.06 |          18.4 |       1 |       0.5 |         0    |              0 |         nan |                       1 |          20.9  |              2 |           1 |                   0    |                    0 |
|          2 | 2025-08-01 00:11:02    | 2025-08-01 00:16:06     | N                    |            1 |             74 |            263 |                 1 |            2.09 |          10   |       1 |       0.5 |         3.05 |              0 |         nan |                       1 |          18.3  |              1 |           1 |                   2.75 |                    0 |
|          2 | 2025-08-01 00:44:09    | 2025-08-01 00:47:04     | N                    |            1 |             42 |             41 |                 1 |            0.53 |           5.1 |       1 |       0.5 |         0    |              0 |         nan |                       1 |           7.6  |              2 |           1 |                   0    |                    0 |
|          2 | 2025-08-01 00:57:06    | 2025-08-01 01:05:32     | N                    |            1 |             75 |            239 |                 1 |            2.28 |          12.1 |       1 |       0.5 |         3.47 |              0 |         nan |                       1 |          20.82 |              1 |           1 |                   2.75 |                    0 |
|          2 | 2025-08-01 00:20:48    | 2025-08-01 00:32:47     | N                    |            1 |             83 |            129 |                 1 |            1.61 |          12.1 |       1 |       0.5 |         0    |              0 |         nan |                       1 |          14.6  |              2 |           1 |                   0    |                    0 |
|          2 | 2025-08-01 00:00:53    | 2025-08-01 00:12:24     | N                    |            1 |             74 |            238 |                 1 |            3.15 |          15.6 |       1 |       0.5 |         4.17 |              0 |         nan |                       1 |          25.02 |              1 |           1 |                   2.75 |                    0 |
|          2 | 2025-08-01 00:49:52    | 2025-08-01 00:55:49     | N                    |            1 |             75 |            236 |                 1 |            1.14 |           7.9 |       1 |       0.5 |         1.85 |              0 |         nan |                       1 |          15    |              1 |           1 |                   2.75 |                    0 |
|          2 | 2025-08-01 00:58:45    | 2025-08-01 00:58:48     | N                    |            5 |            181 |            264 |                 1 |            0    |          80   |       0 |       0   |         0.05 |              0 |         nan |                       1 |          81.05 |              1 |           2 |                   0    |                    0 |
|          2 | 2025-08-01 00:17:07    | 2025-08-01 00:17:11     | N                    |            5 |             95 |             95 |                 1 |            0    |           9   |       0 |       0   |         5    |              0 |         nan |                       1 |          15    |              1 |           2 |                   0    |                    0 |
