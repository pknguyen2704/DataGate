# Data Overview: green_tripdata_2025-02.parquet

## Dataset Summary

| metric       | value                                                                             |
|:-------------|:----------------------------------------------------------------------------------|
| file         | /root/Dev/DataGate/experiments/data/parquets/green/green_tripdata_2025-02.parquet |
| rows         | 46621                                                                             |
| columns      | 21                                                                                |
| row_groups   | 1                                                                                 |
| file_size_mb | 1.07                                                                              |
| rows_loaded  | 46621                                                                             |

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
| VendorID              | int32          |      46621 |      0 |   0.0000 |        3 |
| lpep_pickup_datetime  | datetime64[us] |      46621 |      0 |   0.0000 |    45709 |
| lpep_dropoff_datetime | datetime64[us] |      46621 |      0 |   0.0000 |    45756 |
| store_and_fwd_flag    | str            |      44104 |   2517 |   5.3989 |        2 |
| RatecodeID            | float64        |      44104 |   2517 |   5.3989 |        6 |
| PULocationID          | int32          |      46621 |      0 |   0.0000 |      227 |
| DOLocationID          | int32          |      46621 |      0 |   0.0000 |      242 |
| passenger_count       | float64        |      44104 |   2517 |   5.3989 |       10 |
| trip_distance         | float64        |      46621 |      0 |   0.0000 |     1802 |
| fare_amount           | float64        |      46621 |      0 |   0.0000 |     1442 |
| extra                 | float64        |      46621 |      0 |   0.0000 |       17 |
| mta_tax               | float64        |      46621 |      0 |   0.0000 |        5 |
| tip_amount            | float64        |      46621 |      0 |   0.0000 |     1345 |
| tolls_amount          | float64        |      46621 |      0 |   0.0000 |       22 |
| ehail_fee             | float64        |          0 |  46621 | 100.0000 |        0 |
| improvement_surcharge | float64        |      46621 |      0 |   0.0000 |        5 |
| total_amount          | float64        |      46621 |      0 |   0.0000 |     4048 |
| payment_type          | float64        |      44104 |   2517 |   5.3989 |        4 |
| trip_type             | float64        |      44094 |   2527 |   5.4203 |        2 |
| congestion_surcharge  | float64        |      44104 |   2517 |   5.3989 |        4 |
| cbd_congestion_fee    | float64        |      44633 |   1988 |   4.2642 |        2 |

## Numeric Statistics (full-data)

| column                |      min |     p25 |   median |     mean |      p75 |         max |      std |
|:----------------------|---------:|--------:|---------:|---------:|---------:|------------:|---------:|
| VendorID              |   1.0000 |  2.0000 |   2.0000 |   1.9337 |   2.0000 |      6.0000 |   0.6128 |
| RatecodeID            |   1.0000 |  1.0000 |   1.0000 |   1.1958 |   1.0000 |     99.0000 |   1.6798 |
| PULocationID          |   3.0000 | 74.0000 |  75.0000 |  95.3496 |  97.0000 |    265.0000 |  55.6172 |
| DOLocationID          |   1.0000 | 74.0000 | 140.0000 | 141.6369 | 229.0000 |    265.0000 |  77.2967 |
| passenger_count       |   0.0000 |  1.0000 |   1.0000 |   1.2819 |   1.0000 |      9.0000 |   0.9305 |
| trip_distance         |   0.0000 |  1.1200 |   1.7800 |  15.2402 |   3.0400 | 111597.1900 | 883.1680 |
| fare_amount           | -70.0000 |  9.3000 |  13.5000 |  16.6839 |  19.1000 |    633.7000 |  13.6932 |
| extra                 |  -5.0000 |  0.0000 |   0.0000 |   0.9125 |   2.5000 |     12.5000 |   1.3622 |
| mta_tax               |  -0.5000 |  0.5000 |   0.5000 |   0.6016 |   0.5000 |      1.5000 |   0.3565 |
| tip_amount            | -20.0000 |  0.0000 |   2.0200 |   2.4870 |   3.7000 |    150.0000 |   3.1584 |
| tolls_amount          |   0.0000 |  0.0000 |   0.0000 |   0.2029 |   0.0000 |     42.0000 |   1.2613 |
| improvement_surcharge |  -1.0000 |  1.0000 |   1.0000 |   0.9777 |   1.0000 |      1.0000 |   0.1582 |
| total_amount          | -76.5000 | 13.8000 |  18.8000 |  22.8787 |  26.9000 |    642.1400 |  16.0302 |
| payment_type          |   1.0000 |  1.0000 |   1.0000 |   1.2629 |   2.0000 |      4.0000 |   0.4734 |
| trip_type             |   1.0000 |  1.0000 |   1.0000 |   1.0382 |   1.0000 |      2.0000 |   0.1916 |
| congestion_surcharge  |  -2.7500 |  0.0000 |   0.0000 |   0.8552 |   2.7500 |      2.7500 |   1.2731 |
| cbd_congestion_fee    |   0.0000 |  0.0000 |   0.0000 |   0.0647 |   0.0000 |      0.7500 |   0.2106 |

## Datetime Coverage (full-data)

| column                | min_ts              | max_ts              | span             |
|:----------------------|:--------------------|:--------------------|:-----------------|
| lpep_pickup_datetime  | 2025-01-31 22:34:50 | 2025-03-01 23:29:24 | 29 days 00:54:34 |
| lpep_dropoff_datetime | 2025-01-31 22:35:26 | 2025-03-01 23:36:36 | 29 days 01:01:10 |

## Datetime Distribution by Day (full-data)

| column                | day        |   rows |   row_% |
|:----------------------|:-----------|-------:|--------:|
| lpep_pickup_datetime  | 2025-01-31 |      5 |  0.0107 |
| lpep_pickup_datetime  | 2025-02-01 |   1541 |  3.3054 |
| lpep_pickup_datetime  | 2025-02-02 |   1321 |  2.8335 |
| lpep_pickup_datetime  | 2025-02-03 |   1684 |  3.6121 |
| lpep_pickup_datetime  | 2025-02-04 |   1695 |  3.6357 |
| lpep_pickup_datetime  | 2025-02-05 |   1834 |  3.9338 |
| lpep_pickup_datetime  | 2025-02-06 |   1745 |  3.7429 |
| lpep_pickup_datetime  | 2025-02-07 |   1909 |  4.0947 |
| lpep_pickup_datetime  | 2025-02-08 |   1450 |  3.1102 |
| lpep_pickup_datetime  | 2025-02-09 |   1227 |  2.6319 |
| lpep_pickup_datetime  | 2025-02-10 |   1838 |  3.9424 |
| lpep_pickup_datetime  | 2025-02-11 |   1832 |  3.9296 |
| lpep_pickup_datetime  | 2025-02-12 |   1788 |  3.8352 |
| lpep_pickup_datetime  | 2025-02-13 |   1918 |  4.1140 |
| lpep_pickup_datetime  | 2025-02-14 |   2089 |  4.4808 |
| lpep_pickup_datetime  | 2025-02-15 |   1312 |  2.8142 |
| lpep_pickup_datetime  | 2025-02-16 |   1126 |  2.4152 |
| lpep_pickup_datetime  | 2025-02-17 |   1288 |  2.7627 |
| lpep_pickup_datetime  | 2025-02-18 |   1736 |  3.7236 |
| lpep_pickup_datetime  | 2025-02-19 |   1833 |  3.9317 |
| lpep_pickup_datetime  | 2025-02-20 |   1906 |  4.0883 |
| lpep_pickup_datetime  | 2025-02-21 |   1810 |  3.8824 |
| lpep_pickup_datetime  | 2025-02-22 |   1330 |  2.8528 |
| lpep_pickup_datetime  | 2025-02-23 |   1321 |  2.8335 |
| lpep_pickup_datetime  | 2025-02-24 |   1660 |  3.5606 |
| lpep_pickup_datetime  | 2025-02-25 |   1815 |  3.8931 |
| lpep_pickup_datetime  | 2025-02-26 |   1838 |  3.9424 |
| lpep_pickup_datetime  | 2025-02-27 |   1956 |  4.1955 |
| lpep_pickup_datetime  | 2025-02-28 |   1800 |  3.8609 |
| lpep_pickup_datetime  | 2025-03-01 |     14 |  0.0300 |
| lpep_dropoff_datetime | 2025-01-31 |      2 |  0.0043 |
| lpep_dropoff_datetime | 2025-02-01 |   1520 |  3.2603 |
| lpep_dropoff_datetime | 2025-02-02 |   1332 |  2.8571 |
| lpep_dropoff_datetime | 2025-02-03 |   1680 |  3.6035 |
| lpep_dropoff_datetime | 2025-02-04 |   1700 |  3.6464 |
| lpep_dropoff_datetime | 2025-02-05 |   1833 |  3.9317 |
| lpep_dropoff_datetime | 2025-02-06 |   1741 |  3.7344 |
| lpep_dropoff_datetime | 2025-02-07 |   1908 |  4.0926 |
| lpep_dropoff_datetime | 2025-02-08 |   1454 |  3.1188 |
| lpep_dropoff_datetime | 2025-02-09 |   1228 |  2.6340 |
| lpep_dropoff_datetime | 2025-02-10 |   1848 |  3.9639 |
| lpep_dropoff_datetime | 2025-02-11 |   1827 |  3.9188 |
| lpep_dropoff_datetime | 2025-02-12 |   1777 |  3.8116 |
| lpep_dropoff_datetime | 2025-02-13 |   1926 |  4.1312 |
| lpep_dropoff_datetime | 2025-02-14 |   2080 |  4.4615 |
| lpep_dropoff_datetime | 2025-02-15 |   1317 |  2.8249 |
| lpep_dropoff_datetime | 2025-02-16 |   1133 |  2.4302 |
| lpep_dropoff_datetime | 2025-02-17 |   1291 |  2.7691 |
| lpep_dropoff_datetime | 2025-02-18 |   1727 |  3.7043 |
| lpep_dropoff_datetime | 2025-02-19 |   1830 |  3.9253 |
| lpep_dropoff_datetime | 2025-02-20 |   1910 |  4.0969 |
| lpep_dropoff_datetime | 2025-02-21 |   1806 |  3.8738 |
| lpep_dropoff_datetime | 2025-02-22 |   1335 |  2.8635 |
| lpep_dropoff_datetime | 2025-02-23 |   1323 |  2.8378 |
| lpep_dropoff_datetime | 2025-02-24 |   1651 |  3.5413 |
| lpep_dropoff_datetime | 2025-02-25 |   1818 |  3.8995 |
| lpep_dropoff_datetime | 2025-02-26 |   1844 |  3.9553 |
| lpep_dropoff_datetime | 2025-02-27 |   1945 |  4.1719 |
| lpep_dropoff_datetime | 2025-02-28 |   1794 |  3.8481 |
| lpep_dropoff_datetime | 2025-03-01 |     41 |  0.0879 |

## Top Values (full-data, top 5)

| column                | top_5_values                                             |
|:----------------------|:---------------------------------------------------------|
| VendorID              | 2: 39877, 1: 6013, 6: 731                                |
| store_and_fwd_flag    | N: 44002, <NULL>: 2517, Y: 102                           |
| RatecodeID            | 1.0: 42079, <NULL>: 2517, 5.0: 1847, 2.0: 107, 4.0: 38   |
| passenger_count       | 1.0: 37135, 2.0: 4051, <NULL>: 2517, 5.0: 1066, 6.0: 650 |
| mta_tax               | 0.5: 38817, 1.5: 5800, 0.0: 1854, -0.5: 141, 1.0: 9      |
| ehail_fee             | <NULL>: 46621                                            |
| improvement_surcharge | 1.0: 45488, 0.3: 854, -1.0: 164, 0.0: 114, -0.3: 1       |
| payment_type          | 1.0: 33074, 2.0: 10573, <NULL>: 2517, 3.0: 351, 4.0: 106 |
| trip_type             | 1.0: 42411, <NULL>: 2527, 2.0: 1683                      |
| congestion_surcharge  | 0.0: 30378, 2.75: 13670, <NULL>: 2517, 2.5: 53, -2.75: 3 |
| cbd_congestion_fee    | 0.0: 40782, 0.75: 3851, <NULL>: 1988                     |

## Data Quality Signals

- Duplicate rows in full data: `0` / `46621`.
- Columns with >= 50% null in full data: `ehail_fee`.
- Near-constant columns in full data: `ehail_fee`.
- High-cardinality / ID-like columns: `lpep_pickup_datetime`, `lpep_dropoff_datetime`.
- Numeric columns containing negative values: `fare_amount`, `extra`, `mta_tax`, `tip_amount`, `improvement_surcharge`, `total_amount`, `congestion_surcharge`.

## Data Preview

|   VendorID | lpep_pickup_datetime   | lpep_dropoff_datetime   | store_and_fwd_flag   |   RatecodeID |   PULocationID |   DOLocationID |   passenger_count |   trip_distance |   fare_amount |   extra |   mta_tax |   tip_amount |   tolls_amount |   ehail_fee |   improvement_surcharge |   total_amount |   payment_type |   trip_type |   congestion_surcharge |   cbd_congestion_fee |
|-----------:|:-----------------------|:------------------------|:---------------------|-------------:|---------------:|---------------:|------------------:|----------------:|--------------:|--------:|----------:|-------------:|---------------:|------------:|------------------------:|---------------:|---------------:|------------:|-----------------------:|---------------------:|
|          2 | 2025-02-01 00:12:15    | 2025-02-01 00:15:48     | N                    |            1 |            166 |             41 |                 1 |            0.65 |           6.5 |     1   |       0.5 |         1.8  |              0 |         nan |                       1 |          10.8  |              1 |           1 |                   0    |                 0    |
|          2 | 2025-01-31 23:57:05    | 2025-02-01 00:24:24     | N                    |            1 |            255 |            161 |                 1 |            6.57 |          31.7 |     1   |       0.5 |         0    |              0 |         nan |                       1 |          37.7  |              2 |           1 |                   2.75 |                 0.75 |
|          2 | 2025-02-01 00:24:26    | 2025-02-01 00:49:54     | N                    |            1 |             75 |            182 |                 2 |            8.36 |          36.6 |     1   |       0.5 |         0    |              0 |         nan |                       1 |          39.1  |              2 |           1 |                   0    |                 0    |
|          1 | 2025-02-01 00:17:15    | 2025-02-01 00:25:56     | N                    |            1 |             97 |            209 |                 1 |            2.4  |          12.8 |     4.5 |       1.5 |         3.75 |              0 |         nan |                       1 |          22.55 |              1 |           1 |                   2.75 |                 0.75 |
|          2 | 2025-02-01 00:17:36    | 2025-02-01 00:26:36     | N                    |            1 |              7 |            223 |                 1 |            1.31 |          10.7 |     1   |       0.5 |         2.64 |              0 |         nan |                       1 |          15.84 |              1 |           1 |                   0    |                 0    |
|          2 | 2025-02-01 00:40:18    | 2025-02-01 00:48:55     | N                    |            1 |              7 |            223 |                 1 |            2.19 |          11.4 |     1   |       0.5 |         4.17 |              0 |         nan |                       1 |          18.07 |              1 |           1 |                   0    |                 0    |
|          2 | 2025-02-01 00:13:43    | 2025-02-01 00:23:26     | N                    |            1 |            130 |            130 |                 1 |            0.81 |           7.2 |     1   |       0.5 |         0    |              0 |         nan |                       1 |           9.7  |              2 |           1 |                   0    |                 0    |
|          2 | 2025-01-31 23:06:19    | 2025-01-31 23:28:32     | N                    |            1 |             75 |            211 |                 1 |            5.45 |          26.1 |     1   |       0.5 |         6.42 |              0 |         nan |                       1 |          38.52 |              1 |           1 |                   2.75 |                 0.75 |
|          2 | 2025-02-01 00:24:21    | 2025-02-01 00:24:22     | N                    |            5 |            264 |            264 |                 0 |            0    |          14   |     0   |       0   |         1    |              0 |         nan |                       1 |          16    |              1 |           2 |                   0    |                 0    |
|          2 | 2025-02-01 00:29:33    | 2025-02-01 00:45:10     | N                    |            1 |             97 |             80 |                 1 |            4.87 |          22.6 |     1   |       0.5 |         5.02 |              0 |         nan |                       1 |          30.12 |              1 |           1 |                   0    |                 0    |
