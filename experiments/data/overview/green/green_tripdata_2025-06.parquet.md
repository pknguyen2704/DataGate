# Data Overview: green_tripdata_2025-06.parquet

## Dataset Summary

| metric       | value                                                                             |
|:-------------|:----------------------------------------------------------------------------------|
| file         | /root/Dev/DataGate/experiments/data/parquets/green/green_tripdata_2025-06.parquet |
| rows         | 49390                                                                             |
| columns      | 21                                                                                |
| row_groups   | 1                                                                                 |
| file_size_mb | 1.16                                                                              |
| rows_loaded  | 49390                                                                             |

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
| VendorID              | int32          |      49390 |      0 |   0.0000 |        3 |
| lpep_pickup_datetime  | datetime64[us] |      49390 |      0 |   0.0000 |    48495 |
| lpep_dropoff_datetime | datetime64[us] |      49390 |      0 |   0.0000 |    48509 |
| store_and_fwd_flag    | str            |      45605 |   3785 |   7.6635 |        2 |
| RatecodeID            | float64        |      45605 |   3785 |   7.6635 |        7 |
| PULocationID          | int32          |      49390 |      0 |   0.0000 |      232 |
| DOLocationID          | int32          |      49390 |      0 |   0.0000 |      249 |
| passenger_count       | float64        |      45605 |   3785 |   7.6635 |       10 |
| trip_distance         | float64        |      49390 |      0 |   0.0000 |     2046 |
| fare_amount           | float64        |      49390 |      0 |   0.0000 |     1707 |
| extra                 | float64        |      49390 |      0 |   0.0000 |       17 |
| mta_tax               | float64        |      49390 |      0 |   0.0000 |        5 |
| tip_amount            | float64        |      49390 |      0 |   0.0000 |     1557 |
| tolls_amount          | float64        |      49390 |      0 |   0.0000 |       29 |
| ehail_fee             | float64        |          0 |  49390 | 100.0000 |        0 |
| improvement_surcharge | float64        |      49390 |      0 |   0.0000 |        4 |
| total_amount          | float64        |      49390 |      0 |   0.0000 |     4814 |
| payment_type          | float64        |      45605 |   3785 |   7.6635 |        5 |
| trip_type             | float64        |      45599 |   3791 |   7.6756 |        2 |
| congestion_surcharge  | float64        |      45605 |   3785 |   7.6635 |        4 |
| cbd_congestion_fee    | float64        |      49390 |      0 |   0.0000 |        3 |

## Numeric Statistics (full-data)

| column                |       min |     p25 |   median |     mean |      p75 |        max |      std |
|:----------------------|----------:|--------:|---------:|---------:|---------:|-----------:|---------:|
| VendorID              |    1.0000 |  2.0000 |   2.0000 |   2.0356 |   2.0000 |     6.0000 |   0.8192 |
| RatecodeID            |    1.0000 |  1.0000 |   1.0000 |   1.2931 |   1.0000 |    99.0000 |   2.0743 |
| PULocationID          |    3.0000 | 74.0000 |  75.0000 |  96.8572 |  97.0000 |   265.0000 |  56.6377 |
| DOLocationID          |    1.0000 | 74.0000 | 140.0000 | 143.3689 | 231.0000 |   265.0000 |  77.6251 |
| passenger_count       |    0.0000 |  1.0000 |   1.0000 |   1.2944 |   1.0000 |     9.0000 |   0.9593 |
| trip_distance         |    0.0000 |  1.2600 |   2.0300 |  10.1201 |   3.5600 | 77463.5500 | 618.7769 |
| fare_amount           | -200.0000 | 10.0000 |  14.2000 |  18.8043 |  21.2000 |   588.2000 |  18.1279 |
| extra                 |   -5.0000 |  0.0000 |   0.0000 |   0.8819 |   1.0000 |     7.5000 |   1.3789 |
| mta_tax               |   -0.5000 |  0.5000 |   0.5000 |   0.5665 |   0.5000 |     1.5000 |   0.3364 |
| tip_amount            |   -0.9000 |  0.0000 |   2.1600 |   2.7723 |   4.0000 |   153.3000 |   3.7599 |
| tolls_amount          |    0.0000 |  0.0000 |   0.0000 |   0.2730 |   0.0000 |    49.9400 |   1.4843 |
| improvement_surcharge |   -1.0000 |  1.0000 |   1.0000 |   0.9631 |   1.0000 |     1.0000 |   0.1871 |
| total_amount          | -201.0000 | 14.7000 |  20.3500 |  25.7975 |  29.7000 |   589.7000 |  20.6425 |
| payment_type          |    1.0000 |  1.0000 |   1.0000 |   1.2670 |   2.0000 |     5.0000 |   0.4781 |
| trip_type             |    1.0000 |  1.0000 |   1.0000 |   1.0580 |   1.0000 |     2.0000 |   0.2338 |
| congestion_surcharge  |   -2.7500 |  0.0000 |   0.0000 |   0.8960 |   2.7500 |     2.7500 |   1.2891 |
| cbd_congestion_fee    |   -0.7500 |  0.0000 |   0.0000 |   0.0745 |   0.0000 |     0.7500 |   0.2245 |

## Datetime Coverage (full-data)

| column                | min_ts              | max_ts              | span             |
|:----------------------|:--------------------|:--------------------|:-----------------|
| lpep_pickup_datetime  | 2025-05-29 19:20:43 | 2025-07-01 20:35:08 | 33 days 01:14:25 |
| lpep_dropoff_datetime | 2025-05-29 19:42:35 | 2025-07-01 21:11:08 | 33 days 01:28:33 |

## Datetime Distribution by Day (full-data)

| column                | day        |   rows |   row_% |
|:----------------------|:-----------|-------:|--------:|
| lpep_pickup_datetime  | 2025-05-29 |      2 |  0.0040 |
| lpep_pickup_datetime  | 2025-05-30 |      4 |  0.0081 |
| lpep_pickup_datetime  | 2025-05-31 |      6 |  0.0121 |
| lpep_pickup_datetime  | 2025-06-01 |   1466 |  2.9682 |
| lpep_pickup_datetime  | 2025-06-02 |   1566 |  3.1707 |
| lpep_pickup_datetime  | 2025-06-03 |   1643 |  3.3266 |
| lpep_pickup_datetime  | 2025-06-04 |   1811 |  3.6667 |
| lpep_pickup_datetime  | 2025-06-05 |   1801 |  3.6465 |
| lpep_pickup_datetime  | 2025-06-06 |   1529 |  3.0958 |
| lpep_pickup_datetime  | 2025-06-07 |   1445 |  2.9257 |
| lpep_pickup_datetime  | 2025-06-08 |   1404 |  2.8427 |
| lpep_pickup_datetime  | 2025-06-09 |   1745 |  3.5331 |
| lpep_pickup_datetime  | 2025-06-10 |   1837 |  3.7194 |
| lpep_pickup_datetime  | 2025-06-11 |   1871 |  3.7882 |
| lpep_pickup_datetime  | 2025-06-12 |   1967 |  3.9826 |
| lpep_pickup_datetime  | 2025-06-13 |   1793 |  3.6303 |
| lpep_pickup_datetime  | 2025-06-14 |   1457 |  2.9500 |
| lpep_pickup_datetime  | 2025-06-15 |   1455 |  2.9459 |
| lpep_pickup_datetime  | 2025-06-16 |   1710 |  3.4622 |
| lpep_pickup_datetime  | 2025-06-17 |   1769 |  3.5817 |
| lpep_pickup_datetime  | 2025-06-18 |   1857 |  3.7599 |
| lpep_pickup_datetime  | 2025-06-19 |   1403 |  2.8407 |
| lpep_pickup_datetime  | 2025-06-20 |   1684 |  3.4096 |
| lpep_pickup_datetime  | 2025-06-21 |   1496 |  3.0290 |
| lpep_pickup_datetime  | 2025-06-22 |   1417 |  2.8690 |
| lpep_pickup_datetime  | 2025-06-23 |   1852 |  3.7497 |
| lpep_pickup_datetime  | 2025-06-24 |   1783 |  3.6100 |
| lpep_pickup_datetime  | 2025-06-25 |   1812 |  3.6688 |
| lpep_pickup_datetime  | 2025-06-26 |   1890 |  3.8267 |
| lpep_pickup_datetime  | 2025-06-27 |   1591 |  3.2213 |
| lpep_pickup_datetime  | 2025-06-28 |   1358 |  2.7495 |
| lpep_pickup_datetime  | 2025-06-29 |   1349 |  2.7313 |
| lpep_pickup_datetime  | 2025-06-30 |   1613 |  3.2658 |
| lpep_pickup_datetime  | 2025-07-01 |      4 |  0.0081 |
| lpep_dropoff_datetime | 2025-05-29 |      2 |  0.0040 |
| lpep_dropoff_datetime | 2025-05-30 |      4 |  0.0081 |
| lpep_dropoff_datetime | 2025-05-31 |      5 |  0.0101 |
| lpep_dropoff_datetime | 2025-06-01 |   1454 |  2.9439 |
| lpep_dropoff_datetime | 2025-06-02 |   1573 |  3.1849 |
| lpep_dropoff_datetime | 2025-06-03 |   1635 |  3.3104 |
| lpep_dropoff_datetime | 2025-06-04 |   1806 |  3.6566 |
| lpep_dropoff_datetime | 2025-06-05 |   1802 |  3.6485 |
| lpep_dropoff_datetime | 2025-06-06 |   1527 |  3.0917 |
| lpep_dropoff_datetime | 2025-06-07 |   1437 |  2.9095 |
| lpep_dropoff_datetime | 2025-06-08 |   1418 |  2.8710 |
| lpep_dropoff_datetime | 2025-06-09 |   1750 |  3.5432 |
| lpep_dropoff_datetime | 2025-06-10 |   1837 |  3.7194 |
| lpep_dropoff_datetime | 2025-06-11 |   1865 |  3.7761 |
| lpep_dropoff_datetime | 2025-06-12 |   1971 |  3.9907 |
| lpep_dropoff_datetime | 2025-06-13 |   1785 |  3.6141 |
| lpep_dropoff_datetime | 2025-06-14 |   1456 |  2.9480 |
| lpep_dropoff_datetime | 2025-06-15 |   1465 |  2.9662 |
| lpep_dropoff_datetime | 2025-06-16 |   1712 |  3.4663 |
| lpep_dropoff_datetime | 2025-06-17 |   1767 |  3.5776 |
| lpep_dropoff_datetime | 2025-06-18 |   1847 |  3.7396 |
| lpep_dropoff_datetime | 2025-06-19 |   1399 |  2.8326 |
| lpep_dropoff_datetime | 2025-06-20 |   1691 |  3.4238 |
| lpep_dropoff_datetime | 2025-06-21 |   1495 |  3.0269 |
| lpep_dropoff_datetime | 2025-06-22 |   1426 |  2.8872 |
| lpep_dropoff_datetime | 2025-06-23 |   1852 |  3.7497 |
| lpep_dropoff_datetime | 2025-06-24 |   1777 |  3.5979 |
| lpep_dropoff_datetime | 2025-06-25 |   1812 |  3.6688 |
| lpep_dropoff_datetime | 2025-06-26 |   1892 |  3.8307 |
| lpep_dropoff_datetime | 2025-06-27 |   1584 |  3.2071 |
| lpep_dropoff_datetime | 2025-06-28 |   1363 |  2.7597 |
| lpep_dropoff_datetime | 2025-06-29 |   1348 |  2.7293 |
| lpep_dropoff_datetime | 2025-06-30 |   1620 |  3.2800 |
| lpep_dropoff_datetime | 2025-07-01 |     13 |  0.0263 |

## Top Values (full-data, top 5)

| column                | top_5_values                                             |
|:----------------------|:---------------------------------------------------------|
| VendorID              | 2: 42407, 1: 5235, 6: 1748                               |
| store_and_fwd_flag    | N: 45468, <NULL>: 3785, Y: 137                           |
| RatecodeID            | 1.0: 42501, <NULL>: 3785, 5.0: 2857, 2.0: 145, 4.0: 51   |
| passenger_count       | 1.0: 37686, 2.0: 4421, <NULL>: 3785, 5.0: 903, 0.0: 870  |
| mta_tax               | 0.5: 41332, 1.5: 4915, 0.0: 2989, -0.5: 141, 1.0: 13     |
| ehail_fee             | <NULL>: 49390                                            |
| improvement_surcharge | 1.0: 47230, 0.3: 1647, 0.0: 354, -1.0: 159               |
| payment_type          | 1.0: 34026, 2.0: 11126, <NULL>: 3785, 3.0: 312, 4.0: 136 |
| trip_type             | 1.0: 42952, <NULL>: 3791, 2.0: 2647                      |
| congestion_surcharge  | 0.0: 30728, 2.75: 14790, <NULL>: 3785, 2.5: 82, -2.75: 5 |
| cbd_congestion_fee    | 0.0: 44477, 0.75: 4911, -0.75: 2                         |

## Data Quality Signals

- Duplicate rows in full data: `0` / `49390`.
- Columns with >= 50% null in full data: `ehail_fee`.
- Near-constant columns in full data: `ehail_fee`.
- High-cardinality / ID-like columns: `lpep_pickup_datetime`, `lpep_dropoff_datetime`.
- Numeric columns containing negative values: `fare_amount`, `extra`, `mta_tax`, `tip_amount`, `improvement_surcharge`, `total_amount`, `congestion_surcharge`, `cbd_congestion_fee`.

## Data Preview

|   VendorID | lpep_pickup_datetime   | lpep_dropoff_datetime   | store_and_fwd_flag   |   RatecodeID |   PULocationID |   DOLocationID |   passenger_count |   trip_distance |   fare_amount |   extra |   mta_tax |   tip_amount |   tolls_amount |   ehail_fee |   improvement_surcharge |   total_amount |   payment_type |   trip_type |   congestion_surcharge |   cbd_congestion_fee |
|-----------:|:-----------------------|:------------------------|:---------------------|-------------:|---------------:|---------------:|------------------:|----------------:|--------------:|--------:|----------:|-------------:|---------------:|------------:|------------------------:|---------------:|---------------:|------------:|-----------------------:|---------------------:|
|          2 | 2025-06-01 00:33:43    | 2025-06-01 01:04:33     | N                    |            2 |             74 |            132 |                 1 |           19.6  |          70   |       0 |       0.5 |        19.61 |           6.94 |         nan |                       1 |          98.05 |              1 |           1 |                      0 |                    0 |
|          2 | 2025-06-01 00:07:45    | 2025-06-01 00:14:52     | N                    |            1 |             75 |             74 |                 2 |            1.37 |           9.3 |       1 |       0.5 |         0    |           0    |         nan |                       1 |          11.8  |              2 |           1 |                      0 |                    0 |
|          2 | 2025-06-01 00:24:07    | 2025-06-01 00:48:24     | N                    |            1 |             83 |             83 |                 1 |            4.11 |          25.4 |       1 |       0.5 |         0    |           0    |         nan |                       1 |          27.9  |              2 |           1 |                      0 |                    0 |
|          2 | 2025-06-01 00:00:14    | 2025-06-01 00:08:29     | N                    |            1 |             97 |             49 |                 1 |            1.29 |           9.3 |       1 |       0.5 |         2.36 |           0    |         nan |                       1 |          14.16 |              1 |           1 |                      0 |                    0 |
|          2 | 2025-06-01 00:31:15    | 2025-06-01 00:43:35     | N                    |            1 |             66 |             25 |                 1 |            1.97 |          13.5 |       1 |       0.5 |         0    |           0    |         nan |                       1 |          16    |              1 |           1 |                      0 |                    0 |
|          2 | 2025-06-01 00:31:18    | 2025-06-01 00:31:58     | N                    |            5 |            130 |            130 |                 1 |            0.04 |          65   |       0 |       0   |         0    |           0    |         nan |                       1 |          66    |              2 |           2 |                      0 |                    0 |
|          2 | 2025-06-01 00:33:00    | 2025-06-01 00:33:04     | N                    |            5 |            130 |            130 |                 1 |            0    |          65   |       0 |       0   |         0    |           0    |         nan |                       1 |          66    |              1 |           2 |                      0 |                    0 |
|          2 | 2025-06-01 00:05:42    | 2025-06-01 00:05:49     | N                    |            5 |            244 |            244 |                 1 |            0    |           9.5 |       0 |       0   |         2.1  |           0    |         nan |                       1 |          12.6  |              1 |           2 |                      0 |                    0 |
|          2 | 2025-06-01 00:36:58    | 2025-06-01 00:46:31     | N                    |            1 |            130 |            205 |                 1 |            2.32 |          12.8 |       1 |       0.5 |         3.06 |           0    |         nan |                       1 |          18.36 |              1 |           1 |                      0 |                    0 |
|          1 | 2025-06-01 00:51:33    | 2025-06-01 01:07:17     | N                    |            5 |            255 |             49 |                 1 |            3.4  |          50   |       0 |       0   |        15    |           0    |         nan |                       0 |          65    |              1 |           2 |                      0 |                    0 |
