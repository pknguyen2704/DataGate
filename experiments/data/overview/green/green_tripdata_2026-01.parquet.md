# Data Overview: green_tripdata_2026-01.parquet

## Dataset Summary

| metric       | value                                                                             |
|:-------------|:----------------------------------------------------------------------------------|
| file         | /root/Dev/DataGate/experiments/data/parquets/green/green_tripdata_2026-01.parquet |
| rows         | 40272                                                                             |
| columns      | 21                                                                                |
| row_groups   | 1                                                                                 |
| file_size_mb | 0.95                                                                              |
| rows_loaded  | 40272                                                                             |

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
| VendorID              | int32          |      40272 |      0 |   0.0000 |        3 |
| lpep_pickup_datetime  | datetime64[us] |      40272 |      0 |   0.0000 |    39651 |
| lpep_dropoff_datetime | datetime64[us] |      40272 |      0 |   0.0000 |    39659 |
| store_and_fwd_flag    | str            |      34858 |   5414 |  13.4436 |        2 |
| RatecodeID            | float64        |      34858 |   5414 |  13.4436 |        6 |
| PULocationID          | int32          |      40272 |      0 |   0.0000 |      235 |
| DOLocationID          | int32          |      40272 |      0 |   0.0000 |      240 |
| passenger_count       | float64        |      34858 |   5414 |  13.4436 |       10 |
| trip_distance         | float64        |      40272 |      0 |   0.0000 |     1959 |
| fare_amount           | float64        |      40272 |      0 |   0.0000 |     1362 |
| extra                 | float64        |      40272 |      0 |   0.0000 |       16 |
| mta_tax               | float64        |      40272 |      0 |   0.0000 |        6 |
| tip_amount            | float64        |      40272 |      0 |   0.0000 |     1345 |
| tolls_amount          | float64        |      40272 |      0 |   0.0000 |       33 |
| ehail_fee             | float64        |          0 |  40272 | 100.0000 |        0 |
| improvement_surcharge | float64        |      40272 |      0 |   0.0000 |        4 |
| total_amount          | float64        |      40272 |      0 |   0.0000 |     4547 |
| payment_type          | float64        |      34858 |   5414 |  13.4436 |        4 |
| trip_type             | float64        |      34857 |   5415 |  13.4461 |        2 |
| congestion_surcharge  | float64        |      34858 |   5414 |  13.4436 |        3 |
| cbd_congestion_fee    | float64        |      40272 |      0 |   0.0000 |        2 |

## Numeric Statistics (full-data)

| column                |      min |     p25 |   median |     mean |      p75 |         max |       std |
|:----------------------|---------:|--------:|---------:|---------:|---------:|------------:|----------:|
| VendorID              |   1.0000 |  2.0000 |   2.0000 |   2.2799 |   2.0000 |      6.0000 |    1.2331 |
| RatecodeID            |   1.0000 |  1.0000 |   1.0000 |   1.2072 |   1.0000 |     99.0000 |    1.0181 |
| PULocationID          |   1.0000 | 74.0000 |  75.0000 |  96.1905 |  97.0000 |    265.0000 |   55.6830 |
| DOLocationID          |   1.0000 | 74.0000 | 140.0000 | 141.8784 | 229.0000 |    265.0000 |   77.5831 |
| passenger_count       |   0.0000 |  1.0000 |   1.0000 |   1.2984 |   1.0000 |      9.0000 |    0.9504 |
| trip_distance         |   0.0000 |  1.2000 |   1.9600 |  12.5512 |   3.4700 | 179830.9200 | 1033.8756 |
| fare_amount           | -70.0000 |  8.6000 |  12.8000 |  16.0069 |  19.1000 |    960.0000 |   14.9520 |
| extra                 |  -7.5000 |  0.0000 |   0.0000 |   0.8235 |   1.0000 |      7.5000 |    1.3322 |
| mta_tax               |  -0.5000 |  0.5000 |   0.5000 |   0.5617 |   0.5000 |      4.2500 |    0.3219 |
| tip_amount            |  -2.5200 |  0.0000 |   2.0000 |   2.4766 |   3.7700 |    300.0000 |    3.5643 |
| tolls_amount          |   0.0000 |  0.0000 |   0.0000 |   0.2602 |   0.0000 |     85.0000 |    1.5834 |
| improvement_surcharge |  -1.0000 |  1.0000 |   1.0000 |   0.9222 |   1.0000 |      1.0000 |    0.2452 |
| total_amount          | -76.5000 | 14.6000 |  20.0000 |  24.1955 |  28.8600 |    961.0000 |   17.1775 |
| payment_type          |   1.0000 |  1.0000 |   1.0000 |   1.2597 |   1.0000 |      4.0000 |    0.4712 |
| trip_type             |   1.0000 |  1.0000 |   1.0000 |   1.0466 |   1.0000 |      2.0000 |    0.2107 |
| congestion_surcharge  |   0.0000 |  0.0000 |   0.0000 |   0.8514 |   2.7500 |      2.7500 |    1.2714 |
| cbd_congestion_fee    |   0.0000 |  0.0000 |   0.0000 |   0.0582 |   0.0000 |      0.7500 |    0.2006 |

## Datetime Coverage (full-data)

| column                | min_ts              | max_ts              | span             |
|:----------------------|:--------------------|:--------------------|:-----------------|
| lpep_pickup_datetime  | 2025-12-27 16:49:41 | 2026-02-01 21:08:36 | 36 days 04:18:55 |
| lpep_dropoff_datetime | 2025-12-27 17:02:11 | 2026-02-01 21:15:02 | 36 days 04:12:51 |

## Datetime Distribution by Day (full-data)

| column                | day        |   rows |   row_% |
|:----------------------|:-----------|-------:|--------:|
| lpep_pickup_datetime  | 2025-12-27 |      2 |  0.0050 |
| lpep_pickup_datetime  | 2025-12-29 |      1 |  0.0025 |
| lpep_pickup_datetime  | 2025-12-31 |      1 |  0.0025 |
| lpep_pickup_datetime  | 2026-01-01 |    904 |  2.2447 |
| lpep_pickup_datetime  | 2026-01-02 |   1178 |  2.9251 |
| lpep_pickup_datetime  | 2026-01-03 |    957 |  2.3763 |
| lpep_pickup_datetime  | 2026-01-04 |    921 |  2.2869 |
| lpep_pickup_datetime  | 2026-01-05 |   1391 |  3.4540 |
| lpep_pickup_datetime  | 2026-01-06 |   1408 |  3.4962 |
| lpep_pickup_datetime  | 2026-01-07 |   1414 |  3.5111 |
| lpep_pickup_datetime  | 2026-01-08 |   1468 |  3.6452 |
| lpep_pickup_datetime  | 2026-01-09 |   1447 |  3.5931 |
| lpep_pickup_datetime  | 2026-01-10 |   1172 |  2.9102 |
| lpep_pickup_datetime  | 2026-01-11 |   1048 |  2.6023 |
| lpep_pickup_datetime  | 2026-01-12 |   1487 |  3.6924 |
| lpep_pickup_datetime  | 2026-01-13 |   1463 |  3.6328 |
| lpep_pickup_datetime  | 2026-01-14 |   1516 |  3.7644 |
| lpep_pickup_datetime  | 2026-01-15 |   1622 |  4.0276 |
| lpep_pickup_datetime  | 2026-01-16 |   1542 |  3.8290 |
| lpep_pickup_datetime  | 2026-01-17 |   1049 |  2.6048 |
| lpep_pickup_datetime  | 2026-01-18 |    970 |  2.4086 |
| lpep_pickup_datetime  | 2026-01-19 |   1155 |  2.8680 |
| lpep_pickup_datetime  | 2026-01-20 |   1594 |  3.9581 |
| lpep_pickup_datetime  | 2026-01-21 |   1545 |  3.8364 |
| lpep_pickup_datetime  | 2026-01-22 |   1602 |  3.9779 |
| lpep_pickup_datetime  | 2026-01-23 |   1628 |  4.0425 |
| lpep_pickup_datetime  | 2026-01-24 |   1255 |  3.1163 |
| lpep_pickup_datetime  | 2026-01-25 |    194 |  0.4817 |
| lpep_pickup_datetime  | 2026-01-26 |    659 |  1.6364 |
| lpep_pickup_datetime  | 2026-01-27 |   1497 |  3.7172 |
| lpep_pickup_datetime  | 2026-01-28 |   1680 |  4.1716 |
| lpep_pickup_datetime  | 2026-01-29 |   1680 |  4.1716 |
| lpep_pickup_datetime  | 2026-01-30 |   1602 |  3.9779 |
| lpep_pickup_datetime  | 2026-01-31 |   1202 |  2.9847 |
| lpep_pickup_datetime  | 2026-02-01 |     18 |  0.0447 |
| lpep_dropoff_datetime | 2025-12-27 |      2 |  0.0050 |
| lpep_dropoff_datetime | 2025-12-29 |      1 |  0.0025 |
| lpep_dropoff_datetime | 2025-12-31 |      1 |  0.0025 |
| lpep_dropoff_datetime | 2026-01-01 |    898 |  2.2298 |
| lpep_dropoff_datetime | 2026-01-02 |   1173 |  2.9127 |
| lpep_dropoff_datetime | 2026-01-03 |    960 |  2.3838 |
| lpep_dropoff_datetime | 2026-01-04 |    922 |  2.2894 |
| lpep_dropoff_datetime | 2026-01-05 |   1390 |  3.4515 |
| lpep_dropoff_datetime | 2026-01-06 |   1411 |  3.5037 |
| lpep_dropoff_datetime | 2026-01-07 |   1412 |  3.5062 |
| lpep_dropoff_datetime | 2026-01-08 |   1468 |  3.6452 |
| lpep_dropoff_datetime | 2026-01-09 |   1441 |  3.5782 |
| lpep_dropoff_datetime | 2026-01-10 |   1173 |  2.9127 |
| lpep_dropoff_datetime | 2026-01-11 |   1051 |  2.6098 |
| lpep_dropoff_datetime | 2026-01-12 |   1491 |  3.7023 |
| lpep_dropoff_datetime | 2026-01-13 |   1456 |  3.6154 |
| lpep_dropoff_datetime | 2026-01-14 |   1525 |  3.7868 |
| lpep_dropoff_datetime | 2026-01-15 |   1620 |  4.0226 |
| lpep_dropoff_datetime | 2026-01-16 |   1542 |  3.8290 |
| lpep_dropoff_datetime | 2026-01-17 |   1042 |  2.5874 |
| lpep_dropoff_datetime | 2026-01-18 |    969 |  2.4061 |
| lpep_dropoff_datetime | 2026-01-19 |   1159 |  2.8779 |
| lpep_dropoff_datetime | 2026-01-20 |   1596 |  3.9631 |
| lpep_dropoff_datetime | 2026-01-21 |   1545 |  3.8364 |
| lpep_dropoff_datetime | 2026-01-22 |   1598 |  3.9680 |
| lpep_dropoff_datetime | 2026-01-23 |   1624 |  4.0326 |
| lpep_dropoff_datetime | 2026-01-24 |   1261 |  3.1312 |
| lpep_dropoff_datetime | 2026-01-25 |    203 |  0.5041 |
| lpep_dropoff_datetime | 2026-01-26 |    656 |  1.6289 |
| lpep_dropoff_datetime | 2026-01-27 |   1495 |  3.7123 |
| lpep_dropoff_datetime | 2026-01-28 |   1677 |  4.1642 |
| lpep_dropoff_datetime | 2026-01-29 |   1677 |  4.1642 |
| lpep_dropoff_datetime | 2026-01-30 |   1599 |  3.9705 |
| lpep_dropoff_datetime | 2026-01-31 |   1204 |  2.9897 |
| lpep_dropoff_datetime | 2026-02-01 |     30 |  0.0745 |

## Top Values (full-data, top 5)

| column                | top_5_values                                            |
|:----------------------|:--------------------------------------------------------|
| VendorID              | 2: 32629, 1: 3860, 6: 3783                              |
| store_and_fwd_flag    | N: 34784, <NULL>: 5414, Y: 74                           |
| RatecodeID            | 1.0: 32982, <NULL>: 5414, 5.0: 1723, 2.0: 101, 4.0: 30  |
| passenger_count       | 1.0: 28772, <NULL>: 5414, 2.0: 3637, 5.0: 891, 0.0: 562 |
| mta_tax               | 0.5: 34329, 1.5: 3666, 0.0: 2169, -0.5: 103, 1.0: 4     |
| ehail_fee             | <NULL>: 40272                                           |
| improvement_surcharge | 1.0: 36245, 0.3: 3378, 0.0: 529, -1.0: 120              |
| payment_type          | 1.0: 26230, 2.0: 8297, <NULL>: 5414, 3.0: 237, 4.0: 94  |
| trip_type             | 1.0: 33234, <NULL>: 5415, 2.0: 1623                     |
| congestion_surcharge  | 0.0: 24066, 2.75: 10790, <NULL>: 5414, 2.5: 2           |
| cbd_congestion_fee    | 0.0: 37148, 0.75: 3124                                  |

## Data Quality Signals

- Duplicate rows in full data: `0` / `40272`.
- Columns with >= 50% null in full data: `ehail_fee`.
- Near-constant columns in full data: `ehail_fee`.
- High-cardinality / ID-like columns: `lpep_pickup_datetime`, `lpep_dropoff_datetime`.
- Numeric columns containing negative values: `fare_amount`, `extra`, `mta_tax`, `tip_amount`, `improvement_surcharge`, `total_amount`.

## Data Preview

|   VendorID | lpep_pickup_datetime   | lpep_dropoff_datetime   | store_and_fwd_flag   |   RatecodeID |   PULocationID |   DOLocationID |   passenger_count |   trip_distance |   fare_amount |   extra |   mta_tax |   tip_amount |   tolls_amount |   ehail_fee |   improvement_surcharge |   total_amount |   payment_type |   trip_type |   congestion_surcharge |   cbd_congestion_fee |
|-----------:|:-----------------------|:------------------------|:---------------------|-------------:|---------------:|---------------:|------------------:|----------------:|--------------:|--------:|----------:|-------------:|---------------:|------------:|------------------------:|---------------:|---------------:|------------:|-----------------------:|---------------------:|
|          1 | 2026-01-01 00:27:58    | 2026-01-01 00:55:16     | N                    |            1 |             65 |            233 |                 2 |            6.2  |          31.7 |    4.5  |       1.5 |         7.5  |              0 |         nan |                       1 |          45.2  |              1 |           1 |                   2.75 |                 0.75 |
|          2 | 2026-01-01 00:44:33    | 2026-01-01 01:32:56     | N                    |            5 |             66 |            188 |                 5 |            5.36 |          50   |    0    |       0   |        10.2  |              0 |         nan |                       1 |          61.2  |              1 |           2 |                   0    |                 0    |
|          1 | 2026-01-01 00:23:45    | 2026-01-01 00:45:03     | N                    |            1 |             65 |            179 |                 4 |           10.6  |          41.5 |    1    |       1.5 |         2    |              0 |         nan |                       1 |          46    |              1 |           1 |                   0    |                 0    |
|          1 | 2026-01-01 00:44:33    | 2026-01-01 01:00:45     | N                    |            1 |             42 |            141 |                 1 |            4.2  |          19.8 |    3.75 |       1.5 |         0    |              0 |         nan |                       1 |          25.05 |              2 |           1 |                   2.75 |                 0    |
|          2 | 2026-01-01 00:46:04    | 2026-01-01 01:04:40     | N                    |            1 |             95 |             82 |                 1 |            2.76 |          19.1 |    1    |       0.5 |         0    |              0 |         nan |                       1 |          21.6  |              2 |           1 |                   0    |                 0    |
|          2 | 2026-01-01 00:16:31    | 2026-01-01 00:33:57     | N                    |            1 |             66 |             88 |                 1 |            2.6  |          19.8 |    1    |       0.5 |         0    |              0 |         nan |                       1 |          25.8  |              1 |           1 |                   2.75 |                 0.75 |
|          2 | 2026-01-01 00:08:25    | 2026-01-01 00:18:15     | N                    |            1 |            166 |            239 |                 1 |            1.35 |          11.4 |    1    |       0.5 |         3.33 |              0 |         nan |                       1 |          19.98 |              1 |           1 |                   2.75 |                 0    |
|          2 | 2026-01-01 00:51:18    | 2026-01-01 00:58:35     | N                    |            1 |             41 |             42 |                 1 |            1.27 |           9.3 |    1    |       0.5 |         1    |              0 |         nan |                       1 |          12.8  |              1 |           1 |                   0    |                 0    |
|          2 | 2026-01-01 00:53:05    | 2026-01-01 00:56:27     | N                    |            5 |             92 |             92 |                 1 |            0.51 |          15   |    0    |       0   |         0    |              0 |         nan |                       1 |          16    |              1 |           2 |                   0    |                 0    |
|          2 | 2026-01-01 00:19:51    | 2026-01-01 00:48:36     | N                    |            1 |             74 |            211 |                 1 |            9.06 |          41.5 |    1    |       0.5 |         0    |              0 |         nan |                       1 |          47.5  |              2 |           1 |                   2.75 |                 0.75 |
