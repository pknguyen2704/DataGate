# Data Overview: green_tripdata_2025-01.parquet

## Dataset Summary

| metric       | value                                                                             |
|:-------------|:----------------------------------------------------------------------------------|
| file         | /root/Dev/DataGate/experiments/data/parquets/green/green_tripdata_2025-01.parquet |
| rows         | 48326                                                                             |
| columns      | 21                                                                                |
| row_groups   | 1                                                                                 |
| file_size_mb | 1.12                                                                              |
| rows_loaded  | 48326                                                                             |

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
| VendorID              | int32          |      48326 |      0 |   0.0000 |        2 |
| lpep_pickup_datetime  | datetime64[us] |      48326 |      0 |   0.0000 |    47420 |
| lpep_dropoff_datetime | datetime64[us] |      48326 |      0 |   0.0000 |    47507 |
| store_and_fwd_flag    | str            |      46490 |   1836 |   3.7992 |        2 |
| RatecodeID            | float64        |      46490 |   1836 |   3.7992 |        7 |
| PULocationID          | int32          |      48326 |      0 |   0.0000 |      212 |
| DOLocationID          | int32          |      48326 |      0 |   0.0000 |      241 |
| passenger_count       | float64        |      46490 |   1836 |   3.7992 |       10 |
| trip_distance         | float64        |      48326 |      0 |   0.0000 |     1721 |
| fare_amount           | float64        |      48326 |      0 |   0.0000 |     1430 |
| extra                 | float64        |      48326 |      0 |   0.0000 |       20 |
| mta_tax               | float64        |      48326 |      0 |   0.0000 |        6 |
| tip_amount            | float64        |      48326 |      0 |   0.0000 |     1349 |
| tolls_amount          | float64        |      48326 |      0 |   0.0000 |       22 |
| ehail_fee             | float64        |          0 |  48326 | 100.0000 |        0 |
| improvement_surcharge | float64        |      48326 |      0 |   0.0000 |        5 |
| total_amount          | float64        |      48326 |      0 |   0.0000 |     3940 |
| payment_type          | float64        |      46490 |   1836 |   3.7992 |        5 |
| trip_type             | float64        |      46483 |   1843 |   3.8137 |        2 |
| congestion_surcharge  | float64        |      46490 |   1836 |   3.7992 |        4 |
| cbd_congestion_fee    | float64        |      46490 |   1836 |   3.7992 |        2 |

## Numeric Statistics (full-data)

| column                |       min |     p25 |   median |     mean |      p75 |        max |      std |
|:----------------------|----------:|--------:|---------:|---------:|---------:|-----------:|---------:|
| VendorID              |    1.0000 |  2.0000 |   2.0000 |   1.8702 |   2.0000 |     2.0000 |   0.3361 |
| RatecodeID            |    1.0000 |  1.0000 |   1.0000 |   1.1848 |   1.0000 |    99.0000 |   1.4425 |
| PULocationID          |    3.0000 | 74.0000 |  75.0000 |  94.0945 |  97.0000 |   265.0000 |  54.9681 |
| DOLocationID          |    1.0000 | 74.0000 | 140.0000 | 142.4090 | 230.0000 |   265.0000 |  77.2516 |
| passenger_count       |    0.0000 |  1.0000 |   1.0000 |   1.2781 |   1.0000 |     9.0000 |   0.9372 |
| trip_distance         |    0.0000 |  1.1000 |   1.7400 |  21.5324 |   2.9400 | 84731.5700 | 990.6469 |
| fare_amount           | -113.0000 |  9.3000 |  13.5000 |  16.7625 |  19.1000 |   336.2000 |  13.3083 |
| extra                 |   -5.0000 |  0.0000 |   0.0000 |   0.9323 |   2.5000 |     7.5000 |   1.3486 |
| mta_tax               |   -0.5000 |  0.5000 |   0.5000 |   0.6028 |   0.5000 |     4.2500 |   0.3574 |
| tip_amount            |   -0.9000 |  0.0000 |   2.0700 |   2.4819 |   3.6900 |   252.0500 |   3.2136 |
| tolls_amount          |    0.0000 |  0.0000 |   0.0000 |   0.1775 |   0.0000 |    48.7600 |   1.1930 |
| improvement_surcharge |   -1.0000 |  1.0000 |   1.0000 |   0.9883 |   1.0000 |     1.0000 |   0.1304 |
| total_amount          | -114.0000 | 13.7050 |  18.7500 |  22.6342 |  26.4650 |   371.4000 |  15.4351 |
| payment_type          |    1.0000 |  1.0000 |   1.0000 |   1.2664 |   2.0000 |     5.0000 |   0.4718 |
| trip_type             |    1.0000 |  1.0000 |   1.0000 |   1.0388 |   1.0000 |     2.0000 |   0.1931 |
| congestion_surcharge  |   -2.7500 |  0.0000 |   0.0000 |   0.8531 |   2.7500 |     2.7500 |   1.2719 |
| cbd_congestion_fee    |    0.0000 |  0.0000 |   0.0000 |   0.0534 |   0.0000 |     0.7500 |   0.1928 |

## Datetime Coverage (full-data)

| column                | min_ts              | max_ts              | span             |
|:----------------------|:--------------------|:--------------------|:-----------------|
| lpep_pickup_datetime  | 2024-12-25 23:13:15 | 2025-02-05 18:46:24 | 41 days 19:33:09 |
| lpep_dropoff_datetime | 2024-12-25 23:13:17 | 2025-02-05 19:11:47 | 41 days 19:58:30 |

## Datetime Distribution by Day (full-data)

| column                | day        |   rows |   row_% |
|:----------------------|:-----------|-------:|--------:|
| lpep_pickup_datetime  | 2024-12-25 |      1 |  0.0021 |
| lpep_pickup_datetime  | 2024-12-29 |      1 |  0.0021 |
| lpep_pickup_datetime  | 2024-12-31 |      4 |  0.0083 |
| lpep_pickup_datetime  | 2025-01-01 |   1001 |  2.0713 |
| lpep_pickup_datetime  | 2025-01-02 |   1516 |  3.1370 |
| lpep_pickup_datetime  | 2025-01-03 |   1525 |  3.1557 |
| lpep_pickup_datetime  | 2025-01-04 |   1249 |  2.5845 |
| lpep_pickup_datetime  | 2025-01-05 |   1129 |  2.3362 |
| lpep_pickup_datetime  | 2025-01-06 |   1541 |  3.1888 |
| lpep_pickup_datetime  | 2025-01-07 |   1648 |  3.4102 |
| lpep_pickup_datetime  | 2025-01-08 |   1680 |  3.4764 |
| lpep_pickup_datetime  | 2025-01-09 |   1868 |  3.8654 |
| lpep_pickup_datetime  | 2025-01-10 |   1633 |  3.3791 |
| lpep_pickup_datetime  | 2025-01-11 |   1296 |  2.6818 |
| lpep_pickup_datetime  | 2025-01-12 |   1143 |  2.3652 |
| lpep_pickup_datetime  | 2025-01-13 |   1618 |  3.3481 |
| lpep_pickup_datetime  | 2025-01-14 |   1775 |  3.6730 |
| lpep_pickup_datetime  | 2025-01-15 |   1886 |  3.9027 |
| lpep_pickup_datetime  | 2025-01-16 |   1909 |  3.9503 |
| lpep_pickup_datetime  | 2025-01-17 |   1810 |  3.7454 |
| lpep_pickup_datetime  | 2025-01-18 |   1197 |  2.4769 |
| lpep_pickup_datetime  | 2025-01-19 |   1113 |  2.3031 |
| lpep_pickup_datetime  | 2025-01-20 |   1084 |  2.2431 |
| lpep_pickup_datetime  | 2025-01-21 |   1788 |  3.6999 |
| lpep_pickup_datetime  | 2025-01-22 |   1812 |  3.7495 |
| lpep_pickup_datetime  | 2025-01-23 |   1849 |  3.8261 |
| lpep_pickup_datetime  | 2025-01-24 |   1714 |  3.5467 |
| lpep_pickup_datetime  | 2025-01-25 |   1336 |  2.7646 |
| lpep_pickup_datetime  | 2025-01-26 |   1308 |  2.7066 |
| lpep_pickup_datetime  | 2025-01-27 |   1704 |  3.5261 |
| lpep_pickup_datetime  | 2025-01-28 |   1771 |  3.6647 |
| lpep_pickup_datetime  | 2025-01-29 |   1748 |  3.6171 |
| lpep_pickup_datetime  | 2025-01-30 |   1909 |  3.9503 |
| lpep_pickup_datetime  | 2025-01-31 |   1723 |  3.5654 |
| lpep_pickup_datetime  | 2025-02-01 |     19 |  0.0393 |
| lpep_pickup_datetime  | 2025-02-03 |      6 |  0.0124 |
| lpep_pickup_datetime  | 2025-02-04 |      7 |  0.0145 |
| lpep_pickup_datetime  | 2025-02-05 |      5 |  0.0103 |
| lpep_dropoff_datetime | 2024-12-25 |      1 |  0.0021 |
| lpep_dropoff_datetime | 2024-12-29 |      1 |  0.0021 |
| lpep_dropoff_datetime | 2024-12-31 |      4 |  0.0083 |
| lpep_dropoff_datetime | 2025-01-01 |    993 |  2.0548 |
| lpep_dropoff_datetime | 2025-01-02 |   1508 |  3.1205 |
| lpep_dropoff_datetime | 2025-01-03 |   1518 |  3.1412 |
| lpep_dropoff_datetime | 2025-01-04 |   1263 |  2.6135 |
| lpep_dropoff_datetime | 2025-01-05 |   1126 |  2.3300 |
| lpep_dropoff_datetime | 2025-01-06 |   1535 |  3.1763 |
| lpep_dropoff_datetime | 2025-01-07 |   1656 |  3.4267 |
| lpep_dropoff_datetime | 2025-01-08 |   1678 |  3.4723 |
| lpep_dropoff_datetime | 2025-01-09 |   1865 |  3.8592 |
| lpep_dropoff_datetime | 2025-01-10 |   1635 |  3.3833 |
| lpep_dropoff_datetime | 2025-01-11 |   1295 |  2.6797 |
| lpep_dropoff_datetime | 2025-01-12 |   1147 |  2.3735 |
| lpep_dropoff_datetime | 2025-01-13 |   1625 |  3.3626 |
| lpep_dropoff_datetime | 2025-01-14 |   1768 |  3.6585 |
| lpep_dropoff_datetime | 2025-01-15 |   1885 |  3.9006 |
| lpep_dropoff_datetime | 2025-01-16 |   1911 |  3.9544 |
| lpep_dropoff_datetime | 2025-01-17 |   1794 |  3.7123 |
| lpep_dropoff_datetime | 2025-01-18 |   1211 |  2.5059 |
| lpep_dropoff_datetime | 2025-01-19 |   1113 |  2.3031 |
| lpep_dropoff_datetime | 2025-01-20 |   1084 |  2.2431 |
| lpep_dropoff_datetime | 2025-01-21 |   1782 |  3.6875 |
| lpep_dropoff_datetime | 2025-01-22 |   1811 |  3.7475 |
| lpep_dropoff_datetime | 2025-01-23 |   1853 |  3.8344 |
| lpep_dropoff_datetime | 2025-01-24 |   1712 |  3.5426 |
| lpep_dropoff_datetime | 2025-01-25 |   1337 |  2.7666 |
| lpep_dropoff_datetime | 2025-01-26 |   1318 |  2.7273 |
| lpep_dropoff_datetime | 2025-01-27 |   1696 |  3.5095 |
| lpep_dropoff_datetime | 2025-01-28 |   1774 |  3.6709 |
| lpep_dropoff_datetime | 2025-01-29 |   1747 |  3.6150 |
| lpep_dropoff_datetime | 2025-01-30 |   1904 |  3.9399 |
| lpep_dropoff_datetime | 2025-01-31 |   1722 |  3.5633 |
| lpep_dropoff_datetime | 2025-02-01 |     35 |  0.0724 |
| lpep_dropoff_datetime | 2025-02-02 |      1 |  0.0021 |
| lpep_dropoff_datetime | 2025-02-03 |      6 |  0.0124 |
| lpep_dropoff_datetime | 2025-02-04 |      7 |  0.0145 |
| lpep_dropoff_datetime | 2025-02-05 |      5 |  0.0103 |

## Top Values (full-data, top 5)

| column                | top_5_values                                             |
|:----------------------|:---------------------------------------------------------|
| VendorID              | 2: 42054, 1: 6272                                        |
| store_and_fwd_flag    | N: 46339, <NULL>: 1836, Y: 151                           |
| RatecodeID            | 1.0: 44409, 5.0: 1906, <NULL>: 1836, 2.0: 100, 4.0: 41   |
| passenger_count       | 1.0: 39271, 2.0: 4196, <NULL>: 1836, 5.0: 1030, 6.0: 788 |
| mta_tax               | 0.5: 40208, 1.5: 6054, 0.0: 1926, -0.5: 131, 1.0: 6      |
| ehail_fee             | <NULL>: 48326                                            |
| improvement_surcharge | 1.0: 47859, 0.3: 187, -1.0: 152, 0.0: 127, -0.3: 1       |
| payment_type          | 1.0: 34635, 2.0: 11424, <NULL>: 1836, 3.0: 332, 4.0: 98  |
| trip_type             | 1.0: 44680, <NULL>: 1843, 2.0: 1803                      |
| congestion_surcharge  | 0.0: 32061, 2.75: 14366, <NULL>: 1836, 2.5: 62, -2.75: 1 |
| cbd_congestion_fee    | 0.0: 43183, 0.75: 3307, <NULL>: 1836                     |

## Data Quality Signals

- Duplicate rows in full data: `0` / `48326`.
- Columns with >= 50% null in full data: `ehail_fee`.
- Near-constant columns in full data: `ehail_fee`.
- High-cardinality / ID-like columns: `lpep_pickup_datetime`, `lpep_dropoff_datetime`.
- Numeric columns containing negative values: `fare_amount`, `extra`, `mta_tax`, `tip_amount`, `improvement_surcharge`, `total_amount`, `congestion_surcharge`.

## Data Preview

|   VendorID | lpep_pickup_datetime   | lpep_dropoff_datetime   | store_and_fwd_flag   |   RatecodeID |   PULocationID |   DOLocationID |   passenger_count |   trip_distance |   fare_amount |   extra |   mta_tax |   tip_amount |   tolls_amount |   ehail_fee |   improvement_surcharge |   total_amount |   payment_type |   trip_type |   congestion_surcharge |   cbd_congestion_fee |
|-----------:|:-----------------------|:------------------------|:---------------------|-------------:|---------------:|---------------:|------------------:|----------------:|--------------:|--------:|----------:|-------------:|---------------:|------------:|------------------------:|---------------:|---------------:|------------:|-----------------------:|---------------------:|
|          2 | 2025-01-01 00:03:01    | 2025-01-01 00:17:12     | N                    |            1 |             75 |            235 |                 1 |            5.93 |         24.7  |       1 |       0.5 |         6.8  |           0    |         nan |                       1 |          34    |              1 |           1 |                   0    |                    0 |
|          2 | 2025-01-01 00:19:59    | 2025-01-01 00:25:52     | N                    |            1 |            166 |             75 |                 1 |            1.32 |          8.6  |       1 |       0.5 |         0    |           0    |         nan |                       1 |          11.1  |              2 |           1 |                   0    |                    0 |
|          2 | 2025-01-01 00:05:29    | 2025-01-01 00:07:21     | N                    |            5 |            171 |             73 |                 1 |            0.41 |         25.55 |       0 |       0   |         0    |           0    |         nan |                       1 |          26.55 |              2 |           2 |                   0    |                    0 |
|          2 | 2025-01-01 00:52:24    | 2025-01-01 01:07:52     | N                    |            1 |             74 |            223 |                 1 |            4.12 |         21.2  |       1 |       0.5 |         6.13 |           6.94 |         nan |                       1 |          36.77 |              1 |           1 |                   0    |                    0 |
|          2 | 2025-01-01 00:25:05    | 2025-01-01 01:01:10     | N                    |            1 |             66 |            158 |                 1 |            4.71 |         33.8  |       1 |       0.5 |         7.81 |           0    |         nan |                       1 |          46.86 |              1 |           1 |                   2.75 |                    0 |
|          2 | 2025-01-01 01:03:45    | 2025-01-01 01:42:09     | N                    |            1 |            260 |            260 |                 1 |            4.26 |         31    |       1 |       0.5 |         0    |           0    |         nan |                       1 |          33.5  |              2 |           1 |                   0    |                    0 |
|          2 | 2025-01-01 00:28:12    | 2025-01-01 00:37:53     | N                    |            1 |              7 |            202 |                 1 |            2    |         11.4  |       1 |       0.5 |        22    |           0    |         nan |                       1 |          35.9  |              1 |           1 |                   0    |                    0 |
|          2 | 2025-01-01 00:25:38    | 2025-01-01 00:36:47     | N                    |            1 |            166 |            244 |                 1 |            2.09 |         13.5  |       1 |       0.5 |         0    |           0    |         nan |                       1 |          16    |              2 |           1 |                   0    |                    0 |
|          2 | 2025-01-01 00:52:04    | 2025-01-01 00:58:36     | N                    |            1 |            166 |            151 |                 1 |            0.95 |          7.9  |       1 |       0.5 |         2.08 |           0    |         nan |                       1 |          12.48 |              1 |           1 |                   0    |                    0 |
|          2 | 2024-12-31 22:42:13    | 2024-12-31 22:42:31     | N                    |            3 |             74 |             74 |                 1 |            0.06 |         23    |       1 |       0   |         0    |           0    |         nan |                       1 |          25    |              2 |           1 |                   0    |                    0 |
