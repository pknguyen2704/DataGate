# Data Overview: green_tripdata_2025-07.parquet

## Dataset Summary

| metric       | value                                                                             |
|:-------------|:----------------------------------------------------------------------------------|
| file         | /root/Dev/DataGate/experiments/data/parquets/green/green_tripdata_2025-07.parquet |
| rows         | 48205                                                                             |
| columns      | 21                                                                                |
| row_groups   | 1                                                                                 |
| file_size_mb | 1.13                                                                              |
| rows_loaded  | 48205                                                                             |

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
| VendorID              | int32          |      48205 |      0 |   0.0000 |        3 |
| lpep_pickup_datetime  | datetime64[us] |      48205 |      0 |   0.0000 |    47431 |
| lpep_dropoff_datetime | datetime64[us] |      48205 |      0 |   0.0000 |    47410 |
| store_and_fwd_flag    | str            |      43020 |   5185 |  10.7561 |        2 |
| RatecodeID            | float64        |      43020 |   5185 |  10.7561 |        6 |
| PULocationID          | int32          |      48205 |      0 |   0.0000 |      242 |
| DOLocationID          | int32          |      48205 |      0 |   0.0000 |      253 |
| passenger_count       | float64        |      43020 |   5185 |  10.7561 |       10 |
| trip_distance         | float64        |      48205 |      0 |   0.0000 |     2080 |
| fare_amount           | float64        |      48205 |      0 |   0.0000 |     1508 |
| extra                 | float64        |      48205 |      0 |   0.0000 |       16 |
| mta_tax               | float64        |      48205 |      0 |   0.0000 |        5 |
| tip_amount            | float64        |      48205 |      0 |   0.0000 |     1508 |
| tolls_amount          | float64        |      48205 |      0 |   0.0000 |       29 |
| ehail_fee             | float64        |          0 |  48205 | 100.0000 |        0 |
| improvement_surcharge | float64        |      48205 |      0 |   0.0000 |        4 |
| total_amount          | float64        |      48205 |      0 |   0.0000 |     5091 |
| payment_type          | float64        |      43020 |   5185 |  10.7561 |        5 |
| trip_type             | float64        |      43020 |   5185 |  10.7561 |        2 |
| congestion_surcharge  | float64        |      43020 |   5185 |  10.7561 |        4 |
| cbd_congestion_fee    | float64        |      48205 |      0 |   0.0000 |        2 |

## Numeric Statistics (full-data)

| column                |       min |     p25 |   median |     mean |      p75 |         max |       std |
|:----------------------|----------:|--------:|---------:|---------:|---------:|------------:|----------:|
| VendorID              |    1.0000 |  2.0000 |   2.0000 |   2.1857 |   2.0000 |      6.0000 |    1.0964 |
| RatecodeID            |    1.0000 |  1.0000 |   1.0000 |   1.2604 |   1.0000 |      6.0000 |    0.9799 |
| PULocationID          |    1.0000 | 74.0000 |  75.0000 |  97.2100 |  97.0000 |    265.0000 |   57.0230 |
| DOLocationID          |    1.0000 | 75.0000 | 140.0000 | 143.0680 | 230.0000 |    265.0000 |   77.5582 |
| passenger_count       |    0.0000 |  1.0000 |   1.0000 |   1.3098 |   1.0000 |      9.0000 |    0.9898 |
| trip_distance         |    0.0000 |  1.2900 |   2.1000 |  21.3911 |   3.7100 | 249852.2400 | 1587.1231 |
| fare_amount           | -300.0000 |  9.3000 |  13.5000 |  18.0091 |  20.5000 |    745.0000 |   17.7901 |
| extra                 |   -2.5000 |  0.0000 |   0.0000 |   0.8853 |   1.0000 |      7.5000 |    1.3646 |
| mta_tax               |   -0.5000 |  0.5000 |   0.5000 |   0.5618 |   0.5000 |      1.5000 |    0.3246 |
| tip_amount            |   -0.9000 |  0.0000 |   2.0000 |   2.6568 |   3.9000 |    300.0000 |    4.0591 |
| tolls_amount          |    0.0000 |  0.0000 |   0.0000 |   0.2980 |   0.0000 |     36.0000 |    1.5169 |
| improvement_surcharge |   -1.0000 |  1.0000 |   1.0000 |   0.9393 |   1.0000 |      1.0000 |    0.2175 |
| total_amount          | -301.0000 | 15.0000 |  20.2500 |  25.6840 |  29.7000 |    746.0000 |   20.0813 |
| payment_type          |    1.0000 |  1.0000 |   1.0000 |   1.2694 |   2.0000 |      5.0000 |    0.4730 |
| trip_type             |    1.0000 |  1.0000 |   1.0000 |   1.0602 |   1.0000 |      2.0000 |    0.2378 |
| congestion_surcharge  |   -2.7500 |  0.0000 |   0.0000 |   0.9000 |   2.7500 |      2.7500 |    1.2904 |
| cbd_congestion_fee    |    0.0000 |  0.0000 |   0.0000 |   0.0721 |   0.0000 |      0.7500 |    0.2210 |

## Datetime Coverage (full-data)

| column                | min_ts              | max_ts              | span             |
|:----------------------|:--------------------|:--------------------|:-----------------|
| lpep_pickup_datetime  | 2025-06-24 21:06:31 | 2025-08-01 14:11:22 | 37 days 17:04:51 |
| lpep_dropoff_datetime | 2025-06-24 21:29:37 | 2025-08-01 21:12:54 | 37 days 23:43:17 |

## Datetime Distribution by Day (full-data)

| column                | day        |   rows |   row_% |
|:----------------------|:-----------|-------:|--------:|
| lpep_pickup_datetime  | 2025-06-24 |      2 |  0.0041 |
| lpep_pickup_datetime  | 2025-06-25 |      3 |  0.0062 |
| lpep_pickup_datetime  | 2025-06-30 |      5 |  0.0104 |
| lpep_pickup_datetime  | 2025-07-01 |   1721 |  3.5702 |
| lpep_pickup_datetime  | 2025-07-02 |   1649 |  3.4208 |
| lpep_pickup_datetime  | 2025-07-03 |   1592 |  3.3026 |
| lpep_pickup_datetime  | 2025-07-04 |    976 |  2.0247 |
| lpep_pickup_datetime  | 2025-07-05 |   1198 |  2.4852 |
| lpep_pickup_datetime  | 2025-07-06 |   1386 |  2.8752 |
| lpep_pickup_datetime  | 2025-07-07 |   1548 |  3.2113 |
| lpep_pickup_datetime  | 2025-07-08 |   1656 |  3.4353 |
| lpep_pickup_datetime  | 2025-07-09 |   1649 |  3.4208 |
| lpep_pickup_datetime  | 2025-07-10 |   1601 |  3.3212 |
| lpep_pickup_datetime  | 2025-07-11 |   1579 |  3.2756 |
| lpep_pickup_datetime  | 2025-07-12 |   1321 |  2.7404 |
| lpep_pickup_datetime  | 2025-07-13 |   1313 |  2.7238 |
| lpep_pickup_datetime  | 2025-07-14 |   1783 |  3.6988 |
| lpep_pickup_datetime  | 2025-07-15 |   1663 |  3.4498 |
| lpep_pickup_datetime  | 2025-07-16 |   1666 |  3.4561 |
| lpep_pickup_datetime  | 2025-07-17 |   1787 |  3.7071 |
| lpep_pickup_datetime  | 2025-07-18 |   1583 |  3.2839 |
| lpep_pickup_datetime  | 2025-07-19 |   1421 |  2.9478 |
| lpep_pickup_datetime  | 2025-07-20 |   1389 |  2.8814 |
| lpep_pickup_datetime  | 2025-07-21 |   1628 |  3.3772 |
| lpep_pickup_datetime  | 2025-07-22 |   1695 |  3.5162 |
| lpep_pickup_datetime  | 2025-07-23 |   1624 |  3.3689 |
| lpep_pickup_datetime  | 2025-07-24 |   1643 |  3.4084 |
| lpep_pickup_datetime  | 2025-07-25 |   1616 |  3.3523 |
| lpep_pickup_datetime  | 2025-07-26 |   1360 |  2.8213 |
| lpep_pickup_datetime  | 2025-07-27 |   1384 |  2.8711 |
| lpep_pickup_datetime  | 2025-07-28 |   1598 |  3.3150 |
| lpep_pickup_datetime  | 2025-07-29 |   1631 |  3.3835 |
| lpep_pickup_datetime  | 2025-07-30 |   1706 |  3.5391 |
| lpep_pickup_datetime  | 2025-07-31 |   1826 |  3.7880 |
| lpep_pickup_datetime  | 2025-08-01 |      3 |  0.0062 |
| lpep_dropoff_datetime | 2025-06-24 |      2 |  0.0041 |
| lpep_dropoff_datetime | 2025-06-25 |      3 |  0.0062 |
| lpep_dropoff_datetime | 2025-06-30 |      4 |  0.0083 |
| lpep_dropoff_datetime | 2025-07-01 |   1709 |  3.5453 |
| lpep_dropoff_datetime | 2025-07-02 |   1646 |  3.4146 |
| lpep_dropoff_datetime | 2025-07-03 |   1592 |  3.3026 |
| lpep_dropoff_datetime | 2025-07-04 |    973 |  2.0185 |
| lpep_dropoff_datetime | 2025-07-05 |   1203 |  2.4956 |
| lpep_dropoff_datetime | 2025-07-06 |   1389 |  2.8814 |
| lpep_dropoff_datetime | 2025-07-07 |   1547 |  3.2092 |
| lpep_dropoff_datetime | 2025-07-08 |   1652 |  3.4270 |
| lpep_dropoff_datetime | 2025-07-09 |   1648 |  3.4187 |
| lpep_dropoff_datetime | 2025-07-10 |   1603 |  3.3254 |
| lpep_dropoff_datetime | 2025-07-11 |   1570 |  3.2569 |
| lpep_dropoff_datetime | 2025-07-12 |   1330 |  2.7590 |
| lpep_dropoff_datetime | 2025-07-13 |   1310 |  2.7176 |
| lpep_dropoff_datetime | 2025-07-14 |   1790 |  3.7133 |
| lpep_dropoff_datetime | 2025-07-15 |   1667 |  3.4581 |
| lpep_dropoff_datetime | 2025-07-16 |   1661 |  3.4457 |
| lpep_dropoff_datetime | 2025-07-17 |   1782 |  3.6967 |
| lpep_dropoff_datetime | 2025-07-18 |   1581 |  3.2797 |
| lpep_dropoff_datetime | 2025-07-19 |   1422 |  2.9499 |
| lpep_dropoff_datetime | 2025-07-20 |   1396 |  2.8960 |
| lpep_dropoff_datetime | 2025-07-21 |   1630 |  3.3814 |
| lpep_dropoff_datetime | 2025-07-22 |   1690 |  3.5059 |
| lpep_dropoff_datetime | 2025-07-23 |   1625 |  3.3710 |
| lpep_dropoff_datetime | 2025-07-24 |   1643 |  3.4084 |
| lpep_dropoff_datetime | 2025-07-25 |   1611 |  3.3420 |
| lpep_dropoff_datetime | 2025-07-26 |   1350 |  2.8005 |
| lpep_dropoff_datetime | 2025-07-27 |   1394 |  2.8918 |
| lpep_dropoff_datetime | 2025-07-28 |   1610 |  3.3399 |
| lpep_dropoff_datetime | 2025-07-29 |   1617 |  3.3544 |
| lpep_dropoff_datetime | 2025-07-30 |   1707 |  3.5411 |
| lpep_dropoff_datetime | 2025-07-31 |   1828 |  3.7921 |
| lpep_dropoff_datetime | 2025-08-01 |     20 |  0.0415 |

## Top Values (full-data, top 5)

| column                | top_5_values                                             |
|:----------------------|:---------------------------------------------------------|
| VendorID              | 2: 40019, 1: 4758, 6: 3428                               |
| store_and_fwd_flag    | N: 42679, <NULL>: 5185, Y: 341                           |
| RatecodeID            | 1.0: 40112, <NULL>: 5185, 5.0: 2720, 2.0: 106, 4.0: 50   |
| passenger_count       | 1.0: 35565, <NULL>: 5185, 2.0: 4050, 5.0: 995, 6.0: 782  |
| mta_tax               | 0.5: 40866, 1.5: 4463, 0.0: 2755, -0.5: 110, 1.0: 11     |
| ehail_fee             | <NULL>: 48205                                            |
| improvement_surcharge | 1.0: 44363, 0.3: 3479, 0.0: 233, -1.0: 130               |
| payment_type          | 1.0: 31921, 2.0: 10699, <NULL>: 5185, 3.0: 313, 4.0: 85  |
| trip_type             | 1.0: 40431, <NULL>: 5185, 2.0: 2589                      |
| congestion_surcharge  | 0.0: 28936, 2.75: 14056, <NULL>: 5185, 2.5: 27, -2.75: 1 |
| cbd_congestion_fee    | 0.0: 43574, 0.75: 4631                                   |

## Data Quality Signals

- Duplicate rows in full data: `0` / `48205`.
- Columns with >= 50% null in full data: `ehail_fee`.
- Near-constant columns in full data: `ehail_fee`.
- High-cardinality / ID-like columns: `lpep_pickup_datetime`, `lpep_dropoff_datetime`.
- Numeric columns containing negative values: `fare_amount`, `extra`, `mta_tax`, `tip_amount`, `improvement_surcharge`, `total_amount`, `congestion_surcharge`.

## Data Preview

|   VendorID | lpep_pickup_datetime   | lpep_dropoff_datetime   | store_and_fwd_flag   |   RatecodeID |   PULocationID |   DOLocationID |   passenger_count |   trip_distance |   fare_amount |   extra |   mta_tax |   tip_amount |   tolls_amount |   ehail_fee |   improvement_surcharge |   total_amount |   payment_type |   trip_type |   congestion_surcharge |   cbd_congestion_fee |
|-----------:|:-----------------------|:------------------------|:---------------------|-------------:|---------------:|---------------:|------------------:|----------------:|--------------:|--------:|----------:|-------------:|---------------:|------------:|------------------------:|---------------:|---------------:|------------:|-----------------------:|---------------------:|
|          2 | 2025-07-01 00:48:04    | 2025-07-01 01:03:36     | N                    |            1 |            223 |             82 |                 1 |            7.63 |          31.7 |       1 |       0.5 |          0   |              0 |         nan |                       1 |           34.2 |              2 |           1 |                   0    |                 0    |
|          2 | 2025-07-01 00:37:59    | 2025-07-01 01:06:31     | N                    |            1 |             82 |             83 |                 1 |            3.01 |          25.4 |       1 |       0.5 |          0   |              0 |         nan |                       1 |           27.9 |              2 |           1 |                   0    |                 0    |
|          2 | 2025-07-01 00:19:15    | 2025-07-01 00:33:46     | N                    |            1 |             66 |            162 |                 1 |            6.47 |          26.8 |       1 |       0.5 |          0   |              0 |         nan |                       1 |           32.8 |              1 |           1 |                   2.75 |                 0.75 |
|          2 | 2025-07-01 00:15:26    | 2025-07-01 00:25:02     | N                    |            1 |            129 |            260 |                 1 |            1.47 |          10   |       1 |       0.5 |          0   |              0 |         nan |                       1 |           12.5 |              2 |           1 |                   0    |                 0    |
|          2 | 2025-07-01 00:41:43    | 2025-07-01 01:14:55     | N                    |            1 |            129 |            130 |                 1 |            7.33 |          39.4 |       1 |       0.5 |          0   |              0 |         nan |                       1 |           41.9 |              2 |           1 |                   0    |                 0    |
|          2 | 2025-07-01 00:11:31    | 2025-07-01 00:11:54     | N                    |            5 |            130 |            130 |                 2 |            0.05 |          57   |       0 |       0   |         11.6 |              0 |         nan |                       1 |           69.6 |              1 |           2 |                   0    |                 0    |
|          2 | 2025-07-01 00:44:06    | 2025-07-01 00:44:12     | N                    |            5 |            130 |            130 |                 1 |            0.18 |          10   |       0 |       0   |          0   |              0 |         nan |                       1 |           11   |              1 |           2 |                   0    |                 0    |
|          2 | 2025-07-01 00:05:46    | 2025-07-01 00:24:11     | N                    |            1 |             75 |            235 |                 1 |            5.88 |          27.5 |       1 |       0.5 |          0   |              0 |         nan |                       1 |           30   |              1 |           1 |                   0    |                 0    |
|          2 | 2025-06-30 23:35:13    | 2025-06-30 23:47:00     | N                    |            1 |             82 |              7 |                 1 |            1.66 |          12.8 |       1 |       0.5 |          0   |              0 |         nan |                       1 |           15.3 |              2 |           1 |                   0    |                 0    |
|          2 | 2025-07-01 00:43:28    | 2025-07-01 00:45:57     | N                    |            1 |             82 |            129 |                 1 |            0.53 |           5.1 |       1 |       0.5 |          5   |              0 |         nan |                       1 |           12.6 |              1 |           1 |                   0    |                 0    |
