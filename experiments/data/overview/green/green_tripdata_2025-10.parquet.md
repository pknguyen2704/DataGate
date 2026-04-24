# Data Overview: green_tripdata_2025-10.parquet

## Dataset Summary

| metric       | value                                                                             |
|:-------------|:----------------------------------------------------------------------------------|
| file         | /root/Dev/DataGate/experiments/data/parquets/green/green_tripdata_2025-10.parquet |
| rows         | 49416                                                                             |
| columns      | 21                                                                                |
| row_groups   | 1                                                                                 |
| file_size_mb | 1.15                                                                              |
| rows_loaded  | 49416                                                                             |

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
| VendorID              | int32          |      49416 |      0 |   0.0000 |        3 |
| lpep_pickup_datetime  | datetime64[us] |      49416 |      0 |   0.0000 |    48580 |
| lpep_dropoff_datetime | datetime64[us] |      49416 |      0 |   0.0000 |    48635 |
| store_and_fwd_flag    | str            |      44401 |   5015 |  10.1485 |        2 |
| RatecodeID            | float64        |      44401 |   5015 |  10.1485 |        6 |
| PULocationID          | int32          |      49416 |      0 |   0.0000 |      233 |
| DOLocationID          | int32          |      49416 |      0 |   0.0000 |      241 |
| passenger_count       | float64        |      44401 |   5015 |  10.1485 |       10 |
| trip_distance         | float64        |      49416 |      0 |   0.0000 |     2101 |
| fare_amount           | float64        |      49416 |      0 |   0.0000 |     1552 |
| extra                 | float64        |      49416 |      0 |   0.0000 |       18 |
| mta_tax               | float64        |      49416 |      0 |   0.0000 |        6 |
| tip_amount            | float64        |      49416 |      0 |   0.0000 |     1500 |
| tolls_amount          | float64        |      49416 |      0 |   0.0000 |       29 |
| ehail_fee             | float64        |          0 |  49416 | 100.0000 |        0 |
| improvement_surcharge | float64        |      49416 |      0 |   0.0000 |        4 |
| total_amount          | float64        |      49416 |      0 |   0.0000 |     5003 |
| payment_type          | float64        |      44401 |   5015 |  10.1485 |        5 |
| trip_type             | float64        |      44399 |   5017 |  10.1526 |        2 |
| congestion_surcharge  | float64        |      44401 |   5015 |  10.1485 |        5 |
| cbd_congestion_fee    | float64        |      49416 |      0 |   0.0000 |        3 |

## Numeric Statistics (full-data)

| column                |       min |     p25 |   median |     mean |      p75 |         max |      std |
|:----------------------|----------:|--------:|---------:|---------:|---------:|------------:|---------:|
| VendorID              |    1.0000 |  2.0000 |   2.0000 |   2.1679 |   2.0000 |      6.0000 |   1.0564 |
| RatecodeID            |    1.0000 |  1.0000 |   1.0000 |   1.2546 |   1.0000 |     99.0000 |   1.1633 |
| PULocationID          |    1.0000 | 74.0000 |  75.0000 |  98.3701 | 116.0000 |    265.0000 |  57.3772 |
| DOLocationID          |    1.0000 | 75.0000 | 141.0000 | 143.8872 | 230.0000 |    265.0000 |  76.7947 |
| passenger_count       |    0.0000 |  1.0000 |   1.0000 |   1.2937 |   1.0000 |      9.0000 |   0.9259 |
| trip_distance         |    0.0000 |  1.3000 |   2.0900 |  18.9904 |   3.7000 | 115373.7600 | 995.4541 |
| fare_amount           | -240.0000 |  9.3000 |  14.2000 |  18.1870 |  20.5000 |    990.0000 |  19.0581 |
| extra                 |   -5.0000 |  0.0000 |   0.0000 |   0.9086 |   1.0000 |     10.0000 |   1.4342 |
| mta_tax               |   -0.5000 |  0.5000 |   0.5000 |   0.5594 |   0.5000 |      4.2500 |   0.3198 |
| tip_amount            |   -0.9000 |  0.0000 |   2.2200 |   2.7531 |   4.0000 |    110.0000 |   3.5352 |
| tolls_amount          |    0.0000 |  0.0000 |   0.0000 |   0.2797 |   0.0000 |     43.0000 |   1.4781 |
| improvement_surcharge |   -1.0000 |  1.0000 |   1.0000 |   0.9448 |   1.0000 |      1.0000 |   0.2090 |
| total_amount          | -241.0000 | 15.2000 |  20.8000 |  25.9657 |  30.1325 |    991.0000 |  21.0010 |
| payment_type          |    1.0000 |  1.0000 |   1.0000 |   1.2458 |   1.0000 |      5.0000 |   0.4587 |
| trip_type             |    1.0000 |  1.0000 |   1.0000 |   1.0571 |   1.0000 |      2.0000 |   0.2319 |
| congestion_surcharge  |   -2.7500 |  0.0000 |   0.0000 |   0.8940 |   2.7500 |      2.7500 |   1.2885 |
| cbd_congestion_fee    |   -0.7500 |  0.0000 |   0.0000 |   0.0708 |   0.0000 |      0.7500 |   0.2194 |

## Datetime Coverage (full-data)

| column                | min_ts              | max_ts              | span             |
|:----------------------|:--------------------|:--------------------|:-----------------|
| lpep_pickup_datetime  | 2025-09-24 22:46:18 | 2025-11-01 21:49:41 | 37 days 23:03:23 |
| lpep_dropoff_datetime | 2025-09-24 23:38:39 | 2025-11-01 21:54:36 | 37 days 22:15:57 |

## Datetime Distribution by Day (full-data)

| column                | day        |   rows |   row_% |
|:----------------------|:-----------|-------:|--------:|
| lpep_pickup_datetime  | 2025-09-24 |      2 |  0.0040 |
| lpep_pickup_datetime  | 2025-09-27 |      1 |  0.0020 |
| lpep_pickup_datetime  | 2025-09-28 |      2 |  0.0040 |
| lpep_pickup_datetime  | 2025-09-30 |      3 |  0.0061 |
| lpep_pickup_datetime  | 2025-10-01 |   1692 |  3.4240 |
| lpep_pickup_datetime  | 2025-10-02 |   1493 |  3.0213 |
| lpep_pickup_datetime  | 2025-10-03 |   1657 |  3.3532 |
| lpep_pickup_datetime  | 2025-10-04 |   1399 |  2.8311 |
| lpep_pickup_datetime  | 2025-10-05 |   1383 |  2.7987 |
| lpep_pickup_datetime  | 2025-10-06 |   1626 |  3.2904 |
| lpep_pickup_datetime  | 2025-10-07 |   1622 |  3.2823 |
| lpep_pickup_datetime  | 2025-10-08 |   1763 |  3.5677 |
| lpep_pickup_datetime  | 2025-10-09 |   1775 |  3.5920 |
| lpep_pickup_datetime  | 2025-10-10 |   1680 |  3.3997 |
| lpep_pickup_datetime  | 2025-10-11 |   1338 |  2.7076 |
| lpep_pickup_datetime  | 2025-10-12 |   1268 |  2.5660 |
| lpep_pickup_datetime  | 2025-10-13 |   1326 |  2.6833 |
| lpep_pickup_datetime  | 2025-10-14 |   1621 |  3.2803 |
| lpep_pickup_datetime  | 2025-10-15 |   1577 |  3.1913 |
| lpep_pickup_datetime  | 2025-10-16 |   1818 |  3.6790 |
| lpep_pickup_datetime  | 2025-10-17 |   1660 |  3.3592 |
| lpep_pickup_datetime  | 2025-10-18 |   1417 |  2.8675 |
| lpep_pickup_datetime  | 2025-10-19 |   1374 |  2.7805 |
| lpep_pickup_datetime  | 2025-10-20 |   1583 |  3.2034 |
| lpep_pickup_datetime  | 2025-10-21 |   1562 |  3.1609 |
| lpep_pickup_datetime  | 2025-10-22 |   1723 |  3.4867 |
| lpep_pickup_datetime  | 2025-10-23 |   1795 |  3.6324 |
| lpep_pickup_datetime  | 2025-10-24 |   1740 |  3.5211 |
| lpep_pickup_datetime  | 2025-10-25 |   1378 |  2.7886 |
| lpep_pickup_datetime  | 2025-10-26 |   1367 |  2.7663 |
| lpep_pickup_datetime  | 2025-10-27 |   1598 |  3.2338 |
| lpep_pickup_datetime  | 2025-10-28 |   1712 |  3.4645 |
| lpep_pickup_datetime  | 2025-10-29 |   1773 |  3.5879 |
| lpep_pickup_datetime  | 2025-10-30 |   1899 |  3.8429 |
| lpep_pickup_datetime  | 2025-10-31 |   1776 |  3.5940 |
| lpep_pickup_datetime  | 2025-11-01 |     13 |  0.0263 |
| lpep_dropoff_datetime | 2025-09-24 |      2 |  0.0040 |
| lpep_dropoff_datetime | 2025-09-27 |      1 |  0.0020 |
| lpep_dropoff_datetime | 2025-09-28 |      2 |  0.0040 |
| lpep_dropoff_datetime | 2025-09-30 |      1 |  0.0020 |
| lpep_dropoff_datetime | 2025-10-01 |   1679 |  3.3977 |
| lpep_dropoff_datetime | 2025-10-02 |   1494 |  3.0233 |
| lpep_dropoff_datetime | 2025-10-03 |   1643 |  3.3248 |
| lpep_dropoff_datetime | 2025-10-04 |   1411 |  2.8554 |
| lpep_dropoff_datetime | 2025-10-05 |   1386 |  2.8048 |
| lpep_dropoff_datetime | 2025-10-06 |   1622 |  3.2823 |
| lpep_dropoff_datetime | 2025-10-07 |   1622 |  3.2823 |
| lpep_dropoff_datetime | 2025-10-08 |   1767 |  3.5758 |
| lpep_dropoff_datetime | 2025-10-09 |   1774 |  3.5899 |
| lpep_dropoff_datetime | 2025-10-10 |   1678 |  3.3957 |
| lpep_dropoff_datetime | 2025-10-11 |   1346 |  2.7238 |
| lpep_dropoff_datetime | 2025-10-12 |   1266 |  2.5619 |
| lpep_dropoff_datetime | 2025-10-13 |   1331 |  2.6935 |
| lpep_dropoff_datetime | 2025-10-14 |   1615 |  3.2682 |
| lpep_dropoff_datetime | 2025-10-15 |   1578 |  3.1933 |
| lpep_dropoff_datetime | 2025-10-16 |   1814 |  3.6709 |
| lpep_dropoff_datetime | 2025-10-17 |   1658 |  3.3552 |
| lpep_dropoff_datetime | 2025-10-18 |   1422 |  2.8776 |
| lpep_dropoff_datetime | 2025-10-19 |   1374 |  2.7805 |
| lpep_dropoff_datetime | 2025-10-20 |   1581 |  3.1994 |
| lpep_dropoff_datetime | 2025-10-21 |   1568 |  3.1731 |
| lpep_dropoff_datetime | 2025-10-22 |   1719 |  3.4786 |
| lpep_dropoff_datetime | 2025-10-23 |   1796 |  3.6345 |
| lpep_dropoff_datetime | 2025-10-24 |   1725 |  3.4908 |
| lpep_dropoff_datetime | 2025-10-25 |   1382 |  2.7967 |
| lpep_dropoff_datetime | 2025-10-26 |   1379 |  2.7906 |
| lpep_dropoff_datetime | 2025-10-27 |   1592 |  3.2216 |
| lpep_dropoff_datetime | 2025-10-28 |   1712 |  3.4645 |
| lpep_dropoff_datetime | 2025-10-29 |   1774 |  3.5899 |
| lpep_dropoff_datetime | 2025-10-30 |   1900 |  3.8449 |
| lpep_dropoff_datetime | 2025-10-31 |   1764 |  3.5697 |
| lpep_dropoff_datetime | 2025-11-01 |     38 |  0.0769 |

## Top Values (full-data, top 5)

| column                | top_5_values                                             |
|:----------------------|:---------------------------------------------------------|
| VendorID              | 2: 41504, 1: 4670, 6: 3242                               |
| store_and_fwd_flag    | N: 44259, <NULL>: 5015, Y: 142                           |
| RatecodeID            | 1.0: 41492, <NULL>: 5015, 5.0: 2690, 2.0: 134, 4.0: 50   |
| passenger_count       | 1.0: 36486, <NULL>: 5015, 2.0: 4818, 5.0: 934, 0.0: 702  |
| mta_tax               | 0.5: 42134, 1.5: 4414, 0.0: 2747, -0.5: 111, 1.0: 9      |
| ehail_fee             | <NULL>: 49416                                            |
| improvement_surcharge | 1.0: 45852, 0.3: 3232, 0.0: 201, -1.0: 131               |
| payment_type          | 1.0: 33953, 2.0: 10074, <NULL>: 5015, 3.0: 285, 4.0: 88  |
| trip_type             | 1.0: 41866, <NULL>: 5017, 2.0: 2533                      |
| congestion_surcharge  | 0.0: 29952, 2.75: 14392, <NULL>: 5015, 2.5: 52, -2.75: 4 |
| cbd_congestion_fee    | 0.0: 44748, 0.75: 4666, -0.75: 2                         |

## Data Quality Signals

- Duplicate rows in full data: `0` / `49416`.
- Columns with >= 50% null in full data: `ehail_fee`.
- Near-constant columns in full data: `ehail_fee`.
- High-cardinality / ID-like columns: `lpep_pickup_datetime`, `lpep_dropoff_datetime`.
- Numeric columns containing negative values: `fare_amount`, `extra`, `mta_tax`, `tip_amount`, `improvement_surcharge`, `total_amount`, `congestion_surcharge`, `cbd_congestion_fee`.

## Data Preview

|   VendorID | lpep_pickup_datetime   | lpep_dropoff_datetime   | store_and_fwd_flag   |   RatecodeID |   PULocationID |   DOLocationID |   passenger_count |   trip_distance |   fare_amount |   extra |   mta_tax |   tip_amount |   tolls_amount |   ehail_fee |   improvement_surcharge |   total_amount |   payment_type |   trip_type |   congestion_surcharge |   cbd_congestion_fee |
|-----------:|:-----------------------|:------------------------|:---------------------|-------------:|---------------:|---------------:|------------------:|----------------:|--------------:|--------:|----------:|-------------:|---------------:|------------:|------------------------:|---------------:|---------------:|------------:|-----------------------:|---------------------:|
|          2 | 2025-10-01 00:21:47    | 2025-10-01 00:24:37     | N                    |            1 |            247 |             69 |                 1 |            0.7  |           5.8 |       1 |       0.5 |         1.7  |           0    |         nan |                       1 |          10    |              1 |           1 |                   0    |                 0    |
|          2 | 2025-10-01 00:14:03    | 2025-10-01 00:24:14     | N                    |            1 |             66 |             25 |                 1 |            1.61 |          11.4 |       1 |       0.5 |         2.78 |           0    |         nan |                       1 |          16.68 |              1 |           1 |                   0    |                 0    |
|          2 | 2025-10-01 00:16:44    | 2025-10-01 00:16:47     | N                    |            5 |            244 |            244 |                 1 |            0    |          10   |       0 |       0   |         2.2  |           0    |         nan |                       1 |          13.2  |              1 |           2 |                   0    |                 0    |
|          2 | 2025-10-01 00:07:36    | 2025-10-01 00:32:14     | N                    |            1 |             95 |            170 |                 1 |           10.37 |          43.6 |       1 |       0.5 |        11.31 |           6.94 |         nan |                       1 |          67.85 |              1 |           1 |                   2.75 |                 0.75 |
|          2 | 2025-09-30 21:10:29    | 2025-09-30 21:22:30     | N                    |            1 |             82 |            138 |                 1 |            4.07 |          19.8 |       6 |       0.5 |         6.82 |           0    |         nan |                       1 |          34.12 |              1 |           1 |                   0    |                 0    |
|          2 | 2025-09-30 21:49:46    | 2025-10-01 21:18:42     | N                    |            1 |            129 |             37 |                 1 |            7.13 |          35.2 |       1 |       0.5 |         9.42 |           0    |         nan |                       1 |          47.12 |              1 |           1 |                   0    |                 0    |
|          2 | 2025-10-01 00:11:24    | 2025-10-01 00:18:48     | N                    |            1 |             95 |            134 |                 1 |            1.13 |           9.3 |       1 |       0.5 |         2.08 |           0    |         nan |                       1 |          13.88 |              1 |           1 |                   0    |                 0    |
|          2 | 2025-10-01 00:07:08    | 2025-10-01 00:21:46     | N                    |            1 |             95 |             70 |                 1 |            6.01 |          26.1 |       1 |       0.5 |         5.72 |           0    |         nan |                       1 |          34.32 |              1 |           1 |                   0    |                 0    |
|          2 | 2025-10-01 00:36:08    | 2025-10-01 00:54:59     | N                    |            1 |            181 |            137 |                 1 |            6.45 |          28.9 |       1 |       0.5 |         6.98 |           0    |         nan |                       1 |          41.88 |              1 |           1 |                   2.75 |                 0.75 |
|          2 | 2025-10-01 00:26:55    | 2025-10-01 00:33:00     | N                    |            1 |             74 |            236 |                 1 |            1.74 |           9.3 |       1 |       0.5 |         2.91 |           0    |         nan |                       1 |          17.46 |              1 |           1 |                   2.75 |                 0    |
