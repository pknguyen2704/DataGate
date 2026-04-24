# Data Overview: green_tripdata_2025-12.parquet

## Dataset Summary

| metric       | value                                                                             |
|:-------------|:----------------------------------------------------------------------------------|
| file         | /root/Dev/DataGate/experiments/data/parquets/green/green_tripdata_2025-12.parquet |
| rows         | 48236                                                                             |
| columns      | 21                                                                                |
| row_groups   | 1                                                                                 |
| file_size_mb | 1.12                                                                              |
| rows_loaded  | 48236                                                                             |

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
| VendorID              | int32          |      48236 |      0 |   0.0000 |        3 |
| lpep_pickup_datetime  | datetime64[us] |      48236 |      0 |   0.0000 |    47366 |
| lpep_dropoff_datetime | datetime64[us] |      48236 |      0 |   0.0000 |    47397 |
| store_and_fwd_flag    | str            |      42393 |   5843 |  12.1134 |        2 |
| RatecodeID            | float64        |      42393 |   5843 |  12.1134 |        6 |
| PULocationID          | int32          |      48236 |      0 |   0.0000 |      231 |
| DOLocationID          | int32          |      48236 |      0 |   0.0000 |      247 |
| passenger_count       | float64        |      42393 |   5843 |  12.1134 |       10 |
| trip_distance         | float64        |      48236 |      0 |   0.0000 |     2042 |
| fare_amount           | float64        |      48236 |      0 |   0.0000 |     1687 |
| extra                 | float64        |      48236 |      0 |   0.0000 |       16 |
| mta_tax               | float64        |      48236 |      0 |   0.0000 |        5 |
| tip_amount            | float64        |      48236 |      0 |   0.0000 |     1479 |
| tolls_amount          | float64        |      48236 |      0 |   0.0000 |       36 |
| ehail_fee             | float64        |          0 |  48236 | 100.0000 |        0 |
| improvement_surcharge | float64        |      48236 |      0 |   0.0000 |        4 |
| total_amount          | float64        |      48236 |      0 |   0.0000 |     5052 |
| payment_type          | float64        |      42393 |   5843 |  12.1134 |        4 |
| trip_type             | float64        |      42392 |   5844 |  12.1154 |        2 |
| congestion_surcharge  | float64        |      42393 |   5843 |  12.1134 |        4 |
| cbd_congestion_fee    | float64        |      48236 |      0 |   0.0000 |        3 |

## Numeric Statistics (full-data)

| column                |       min |     p25 |   median |     mean |      p75 |         max |       std |
|:----------------------|----------:|--------:|---------:|---------:|---------:|------------:|----------:|
| VendorID              |    1.0000 |  2.0000 |   2.0000 |   2.2142 |   2.0000 |      6.0000 |    1.1443 |
| RatecodeID            |    1.0000 |  1.0000 |   1.0000 |   1.2225 |   1.0000 |     99.0000 |    1.0221 |
| PULocationID          |    1.0000 | 74.0000 |  75.0000 |  96.5574 |  97.0000 |    265.0000 |   55.3604 |
| DOLocationID          |    1.0000 | 74.0000 | 138.0000 | 140.9432 | 228.0000 |    265.0000 |   77.3545 |
| passenger_count       |    0.0000 |  1.0000 |   1.0000 |   1.2792 |   1.0000 |      9.0000 |    0.8889 |
| trip_distance         |    0.0000 |  1.2000 |   1.9700 |  25.7062 |   3.5100 | 262315.9400 | 1539.8794 |
| fare_amount           | -230.0000 |  8.6000 |  13.0200 |  17.0780 |  19.2825 |    993.5000 |   19.4366 |
| extra                 |   -2.5000 |  0.0000 |   0.0000 |   0.8685 |   1.0000 |      7.7500 |    1.3802 |
| mta_tax               |   -0.5000 |  0.5000 |   0.5000 |   0.5669 |   0.5000 |      1.5000 |    0.3256 |
| tip_amount            |   -0.9000 |  0.0000 |   2.0000 |   2.5720 |   3.8400 |    120.0000 |    3.3640 |
| tolls_amount          |    0.0000 |  0.0000 |   0.0000 |   0.2575 |   0.0000 |     60.0000 |    1.4552 |
| improvement_surcharge |   -1.0000 |  1.0000 |   1.0000 |   0.9343 |   1.0000 |      1.0000 |    0.2285 |
| total_amount          | -231.0000 | 14.4300 |  19.9500 |  24.9543 |  28.9500 |    995.0000 |   21.2240 |
| payment_type          |    1.0000 |  1.0000 |   1.0000 |   1.2632 |   2.0000 |      4.0000 |    0.4725 |
| trip_type             |    1.0000 |  1.0000 |   1.0000 |   1.0502 |   1.0000 |      2.0000 |    0.2183 |
| congestion_surcharge  |   -2.7500 |  0.0000 |   0.0000 |   0.8546 |   2.7500 |      2.7500 |    1.2734 |
| cbd_congestion_fee    |   -0.7500 |  0.0000 |   0.0000 |   0.0611 |   0.0000 |      0.7500 |    0.2053 |

## Datetime Coverage (full-data)

| column                | min_ts              | max_ts              | span               |
|:----------------------|:--------------------|:--------------------|:-------------------|
| lpep_pickup_datetime  | 2008-12-31 15:13:04 | 2026-01-01 21:09:39 | 6210 days 05:56:35 |
| lpep_dropoff_datetime | 2008-12-31 17:25:57 | 2026-01-01 21:49:52 | 6210 days 04:23:55 |

## Datetime Distribution by Day (full-data)

| column                | day        |   rows |   row_% |
|:----------------------|:-----------|-------:|--------:|
| lpep_pickup_datetime  | 2008-12-31 |      1 |  0.0021 |
| lpep_pickup_datetime  | 2025-11-27 |      3 |  0.0062 |
| lpep_pickup_datetime  | 2025-11-28 |      3 |  0.0062 |
| lpep_pickup_datetime  | 2025-11-30 |      5 |  0.0104 |
| lpep_pickup_datetime  | 2025-12-01 |   1631 |  3.3813 |
| lpep_pickup_datetime  | 2025-12-02 |   1713 |  3.5513 |
| lpep_pickup_datetime  | 2025-12-03 |   1878 |  3.8934 |
| lpep_pickup_datetime  | 2025-12-04 |   1968 |  4.0799 |
| lpep_pickup_datetime  | 2025-12-05 |   1757 |  3.6425 |
| lpep_pickup_datetime  | 2025-12-06 |   1437 |  2.9791 |
| lpep_pickup_datetime  | 2025-12-07 |   1303 |  2.7013 |
| lpep_pickup_datetime  | 2025-12-08 |   1757 |  3.6425 |
| lpep_pickup_datetime  | 2025-12-09 |   1834 |  3.8021 |
| lpep_pickup_datetime  | 2025-12-10 |   1919 |  3.9784 |
| lpep_pickup_datetime  | 2025-12-11 |   2078 |  4.3080 |
| lpep_pickup_datetime  | 2025-12-12 |   1971 |  4.0862 |
| lpep_pickup_datetime  | 2025-12-13 |   1589 |  3.2942 |
| lpep_pickup_datetime  | 2025-12-14 |   1262 |  2.6163 |
| lpep_pickup_datetime  | 2025-12-15 |   1879 |  3.8954 |
| lpep_pickup_datetime  | 2025-12-16 |   1823 |  3.7793 |
| lpep_pickup_datetime  | 2025-12-17 |   1907 |  3.9535 |
| lpep_pickup_datetime  | 2025-12-18 |   1989 |  4.1235 |
| lpep_pickup_datetime  | 2025-12-19 |   1880 |  3.8975 |
| lpep_pickup_datetime  | 2025-12-20 |   1389 |  2.8796 |
| lpep_pickup_datetime  | 2025-12-21 |   1219 |  2.5272 |
| lpep_pickup_datetime  | 2025-12-22 |   1588 |  3.2921 |
| lpep_pickup_datetime  | 2025-12-23 |   1463 |  3.0330 |
| lpep_pickup_datetime  | 2025-12-24 |   1255 |  2.6018 |
| lpep_pickup_datetime  | 2025-12-25 |    795 |  1.6481 |
| lpep_pickup_datetime  | 2025-12-26 |   1136 |  2.3551 |
| lpep_pickup_datetime  | 2025-12-27 |    704 |  1.4595 |
| lpep_pickup_datetime  | 2025-12-28 |    915 |  1.8969 |
| lpep_pickup_datetime  | 2025-12-29 |   1350 |  2.7987 |
| lpep_pickup_datetime  | 2025-12-30 |   1425 |  2.9542 |
| lpep_pickup_datetime  | 2025-12-31 |   1396 |  2.8941 |
| lpep_pickup_datetime  | 2026-01-01 |     14 |  0.0290 |
| lpep_dropoff_datetime | 2008-12-31 |      1 |  0.0021 |
| lpep_dropoff_datetime | 2025-11-27 |      3 |  0.0062 |
| lpep_dropoff_datetime | 2025-11-28 |      3 |  0.0062 |
| lpep_dropoff_datetime | 2025-11-30 |      2 |  0.0041 |
| lpep_dropoff_datetime | 2025-12-01 |   1619 |  3.3564 |
| lpep_dropoff_datetime | 2025-12-02 |   1714 |  3.5534 |
| lpep_dropoff_datetime | 2025-12-03 |   1876 |  3.8892 |
| lpep_dropoff_datetime | 2025-12-04 |   1969 |  4.0820 |
| lpep_dropoff_datetime | 2025-12-05 |   1757 |  3.6425 |
| lpep_dropoff_datetime | 2025-12-06 |   1427 |  2.9584 |
| lpep_dropoff_datetime | 2025-12-07 |   1320 |  2.7365 |
| lpep_dropoff_datetime | 2025-12-08 |   1750 |  3.6280 |
| lpep_dropoff_datetime | 2025-12-09 |   1836 |  3.8063 |
| lpep_dropoff_datetime | 2025-12-10 |   1915 |  3.9701 |
| lpep_dropoff_datetime | 2025-12-11 |   2070 |  4.2914 |
| lpep_dropoff_datetime | 2025-12-12 |   1974 |  4.0924 |
| lpep_dropoff_datetime | 2025-12-13 |   1581 |  3.2776 |
| lpep_dropoff_datetime | 2025-12-14 |   1284 |  2.6619 |
| lpep_dropoff_datetime | 2025-12-15 |   1882 |  3.9017 |
| lpep_dropoff_datetime | 2025-12-16 |   1814 |  3.7607 |
| lpep_dropoff_datetime | 2025-12-17 |   1900 |  3.9390 |
| lpep_dropoff_datetime | 2025-12-18 |   1991 |  4.1276 |
| lpep_dropoff_datetime | 2025-12-19 |   1883 |  3.9037 |
| lpep_dropoff_datetime | 2025-12-20 |   1385 |  2.8713 |
| lpep_dropoff_datetime | 2025-12-21 |   1230 |  2.5500 |
| lpep_dropoff_datetime | 2025-12-22 |   1585 |  3.2859 |
| lpep_dropoff_datetime | 2025-12-23 |   1453 |  3.0123 |
| lpep_dropoff_datetime | 2025-12-24 |   1257 |  2.6059 |
| lpep_dropoff_datetime | 2025-12-25 |    806 |  1.6710 |
| lpep_dropoff_datetime | 2025-12-26 |   1141 |  2.3655 |
| lpep_dropoff_datetime | 2025-12-27 |    702 |  1.4553 |
| lpep_dropoff_datetime | 2025-12-28 |    917 |  1.9011 |
| lpep_dropoff_datetime | 2025-12-29 |   1340 |  2.7780 |
| lpep_dropoff_datetime | 2025-12-30 |   1427 |  2.9584 |
| lpep_dropoff_datetime | 2025-12-31 |   1402 |  2.9065 |
| lpep_dropoff_datetime | 2026-01-01 |     20 |  0.0415 |

## Top Values (full-data, top 5)

| column                | top_5_values                                            |
|:----------------------|:--------------------------------------------------------|
| VendorID              | 2: 39642, 1: 4809, 6: 3785                              |
| store_and_fwd_flag    | N: 42254, <NULL>: 5843, Y: 139                          |
| RatecodeID            | 1.0: 39952, <NULL>: 5843, 5.0: 2261, 2.0: 108, 4.0: 42  |
| passenger_count       | 1.0: 34951, <NULL>: 5843, 2.0: 4664, 5.0: 908, 0.0: 656 |
| mta_tax               | 0.5: 41080, 1.5: 4582, 0.0: 2430, -0.5: 140, 1.0: 4     |
| ehail_fee             | <NULL>: 48236                                           |
| improvement_surcharge | 1.0: 44129, 0.3: 3660, 0.0: 285, -1.0: 162              |
| payment_type          | 1.0: 31758, 2.0: 10208, <NULL>: 5843, 3.0: 330, 4.0: 97 |
| trip_type             | 1.0: 40265, <NULL>: 5844, 2.0: 2127                     |
| congestion_surcharge  | 0.0: 29208, 2.75: 13178, <NULL>: 5843, -2.75: 5, 2.5: 2 |
| cbd_congestion_fee    | 0.0: 44301, 0.75: 3933, -0.75: 2                        |

## Data Quality Signals

- Duplicate rows in full data: `0` / `48236`.
- Columns with >= 50% null in full data: `ehail_fee`.
- Near-constant columns in full data: `ehail_fee`.
- High-cardinality / ID-like columns: `lpep_pickup_datetime`, `lpep_dropoff_datetime`.
- Numeric columns containing negative values: `fare_amount`, `extra`, `mta_tax`, `tip_amount`, `improvement_surcharge`, `total_amount`, `congestion_surcharge`, `cbd_congestion_fee`.

## Data Preview

|   VendorID | lpep_pickup_datetime   | lpep_dropoff_datetime   | store_and_fwd_flag   |   RatecodeID |   PULocationID |   DOLocationID |   passenger_count |   trip_distance |   fare_amount |   extra |   mta_tax |   tip_amount |   tolls_amount |   ehail_fee |   improvement_surcharge |   total_amount |   payment_type |   trip_type |   congestion_surcharge |   cbd_congestion_fee |
|-----------:|:-----------------------|:------------------------|:---------------------|-------------:|---------------:|---------------:|------------------:|----------------:|--------------:|--------:|----------:|-------------:|---------------:|------------:|------------------------:|---------------:|---------------:|------------:|-----------------------:|---------------------:|
|          2 | 2025-12-01 00:05:33    | 2025-12-01 00:07:40     | N                    |            1 |            223 |            223 |                 1 |            0.37 |           4.4 |       1 |       0.5 |         0    |              0 |         nan |                       1 |           6.9  |              2 |           1 |                   0    |                 0    |
|          1 | 2025-12-01 00:01:42    | 2025-12-01 00:35:21     | Y                    |            1 |             21 |             11 |                 2 |            1.7  |          28.2 |       1 |       1.5 |         0    |              0 |         nan |                       1 |          30.7  |              2 |           1 |                   0    |                 0    |
|          1 | 2025-12-01 00:36:25    | 2025-12-01 01:17:57     | N                    |            1 |             11 |            210 |                 2 |            6.7  |          38.7 |       1 |       1.5 |         0    |              0 |         nan |                       1 |          41.2  |              2 |           1 |                   0    |                 0    |
|          2 | 2025-12-01 00:51:37    | 2025-12-01 01:09:05     | N                    |            1 |            180 |             82 |                 1 |            4.59 |          22.6 |       1 |       0.5 |         0    |              0 |         nan |                       1 |          25.1  |              2 |           1 |                   0    |                 0    |
|          2 | 2025-12-01 00:08:29    | 2025-12-01 00:12:11     | N                    |            1 |            129 |            260 |                 1 |            0.43 |           5.8 |       1 |       0.5 |         0    |              0 |         nan |                       1 |           8.3  |              2 |           1 |                   0    |                 0    |
|          2 | 2025-12-01 00:02:12    | 2025-12-01 00:55:57     | N                    |            1 |             93 |            145 |                 1 |           13.73 |          68.1 |       1 |       0.5 |         0    |              0 |         nan |                       1 |          74.1  |              2 |           1 |                   2.75 |                 0.75 |
|          2 | 2025-12-01 00:47:33    | 2025-12-01 01:01:09     | N                    |            1 |            244 |            159 |                 1 |            4.12 |          19.8 |       1 |       0.5 |         0    |              0 |         nan |                       1 |          22.3  |              2 |           1 |                   0    |                 0    |
|          2 | 2025-12-01 00:08:44    | 2025-12-01 00:17:12     | N                    |            1 |              7 |            223 |                 5 |            1.68 |          10.7 |       1 |       0.5 |         3.3  |              0 |         nan |                       1 |          16.5  |              1 |           1 |                   0    |                 0    |
|          2 | 2025-11-30 23:56:09    | 2025-12-01 00:14:26     | N                    |            1 |             65 |            234 |                 1 |            4.84 |          24   |       1 |       0.5 |         5    |              0 |         nan |                       1 |          35    |              1 |           1 |                   2.75 |                 0.75 |
|          2 | 2025-12-01 00:00:39    | 2025-12-01 00:11:56     | N                    |            1 |             74 |             42 |                 1 |            2.13 |          13.5 |       1 |       0.5 |         0.01 |              0 |         nan |                       1 |          16.01 |              1 |           1 |                   0    |                 0    |
