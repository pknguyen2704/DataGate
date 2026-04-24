# Data Overview: green_tripdata_2025-09.parquet

## Dataset Summary

| metric       | value                                                                             |
|:-------------|:----------------------------------------------------------------------------------|
| file         | /root/Dev/DataGate/experiments/data/parquets/green/green_tripdata_2025-09.parquet |
| rows         | 48893                                                                             |
| columns      | 21                                                                                |
| row_groups   | 1                                                                                 |
| file_size_mb | 1.15                                                                              |
| rows_loaded  | 48893                                                                             |

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
| VendorID              | int32          |      48893 |      0 |   0.0000 |        3 |
| lpep_pickup_datetime  | datetime64[us] |      48893 |      0 |   0.0000 |    48058 |
| lpep_dropoff_datetime | datetime64[us] |      48893 |      0 |   0.0000 |    48121 |
| store_and_fwd_flag    | str            |      43486 |   5407 |  11.0588 |        2 |
| RatecodeID            | float64        |      43486 |   5407 |  11.0588 |        7 |
| PULocationID          | int32          |      48893 |      0 |   0.0000 |      235 |
| DOLocationID          | int32          |      48893 |      0 |   0.0000 |      250 |
| passenger_count       | float64        |      43486 |   5407 |  11.0588 |       10 |
| trip_distance         | float64        |      48893 |      0 |   0.0000 |     2142 |
| fare_amount           | float64        |      48893 |      0 |   0.0000 |     1519 |
| extra                 | float64        |      48893 |      0 |   0.0000 |       18 |
| mta_tax               | float64        |      48893 |      0 |   0.0000 |        7 |
| tip_amount            | float64        |      48893 |      0 |   0.0000 |     1594 |
| tolls_amount          | float64        |      48893 |      0 |   0.0000 |       33 |
| ehail_fee             | float64        |          0 |  48893 | 100.0000 |        0 |
| improvement_surcharge | float64        |      48893 |      0 |   0.0000 |        4 |
| total_amount          | float64        |      48893 |      0 |   0.0000 |     5259 |
| payment_type          | float64        |      43486 |   5407 |  11.0588 |        5 |
| trip_type             | float64        |      43485 |   5408 |  11.0609 |        2 |
| congestion_surcharge  | float64        |      43486 |   5407 |  11.0588 |        4 |
| cbd_congestion_fee    | float64        |      48893 |      0 |   0.0000 |        3 |

## Numeric Statistics (full-data)

| column                |       min |     p25 |   median |     mean |      p75 |         max |       std |
|:----------------------|----------:|--------:|---------:|---------:|---------:|------------:|----------:|
| VendorID              |    1.0000 |  2.0000 |   2.0000 |   2.2013 |   2.0000 |      6.0000 |    1.1140 |
| RatecodeID            |    1.0000 |  1.0000 |   1.0000 |   1.3143 |   1.0000 |     99.0000 |    1.1632 |
| PULocationID          |    3.0000 | 74.0000 |  75.0000 |  97.5704 | 102.0000 |    265.0000 |   56.7875 |
| DOLocationID          |    1.0000 | 75.0000 | 141.0000 | 144.1565 | 230.0000 |    265.0000 |   76.7845 |
| passenger_count       |    0.0000 |  1.0000 |   1.0000 |   1.2865 |   1.0000 |      9.0000 |    0.9167 |
| trip_distance         |    0.0000 |  1.3300 |   2.1900 |  20.5498 |   3.9100 | 256323.1800 | 1596.2646 |
| fare_amount           | -180.0000 |  9.3000 |  14.2000 |  19.5613 |  21.9000 |    975.0000 |   22.5350 |
| extra                 |   -5.0000 |  0.0000 |   0.0000 |   0.8850 |   1.0000 |     12.5000 |    1.4259 |
| mta_tax               |   -0.5000 |  0.5000 |   0.5000 |   0.5513 |   0.5000 |      5.0000 |    0.3265 |
| tip_amount            |   -0.9000 |  0.0000 |   2.1600 |   2.8690 |   4.1100 |    100.0000 |    3.8533 |
| tolls_amount          |   -6.9400 |  0.0000 |   0.0000 |   0.3383 |   0.0000 |     35.0000 |    1.5974 |
| improvement_surcharge |   -1.0000 |  1.0000 |   1.0000 |   0.9369 |   1.0000 |      1.0000 |    0.2215 |
| total_amount          | -181.0000 | 15.4800 |  21.3000 |  27.6118 |  31.3800 |    976.0000 |   24.6770 |
| payment_type          |    1.0000 |  1.0000 |   1.0000 |   1.2496 |   1.0000 |      5.0000 |    0.4584 |
| trip_type             |    1.0000 |  1.0000 |   1.0000 |   1.0706 |   1.0000 |      2.0000 |    0.2561 |
| congestion_surcharge  |   -2.7500 |  0.0000 |   0.0000 |   0.9013 |   2.7500 |      2.7500 |    1.2913 |
| cbd_congestion_fee    |   -0.7500 |  0.0000 |   0.0000 |   0.0740 |   0.0000 |      0.7500 |    0.2238 |

## Datetime Coverage (full-data)

| column                | min_ts              | max_ts              | span             |
|:----------------------|:--------------------|:--------------------|:-----------------|
| lpep_pickup_datetime  | 2025-08-25 16:23:11 | 2025-10-01 20:08:10 | 37 days 03:44:59 |
| lpep_dropoff_datetime | 2025-08-25 16:53:02 | 2025-10-01 20:15:31 | 37 days 03:22:29 |

## Datetime Distribution by Day (full-data)

| column                | day        |   rows |   row_% |
|:----------------------|:-----------|-------:|--------:|
| lpep_pickup_datetime  | 2025-08-25 |      3 |  0.0061 |
| lpep_pickup_datetime  | 2025-08-26 |      4 |  0.0082 |
| lpep_pickup_datetime  | 2025-08-27 |      3 |  0.0061 |
| lpep_pickup_datetime  | 2025-08-28 |      2 |  0.0041 |
| lpep_pickup_datetime  | 2025-08-30 |      2 |  0.0041 |
| lpep_pickup_datetime  | 2025-08-31 |      5 |  0.0102 |
| lpep_pickup_datetime  | 2025-09-01 |   1361 |  2.7836 |
| lpep_pickup_datetime  | 2025-09-02 |   1705 |  3.4872 |
| lpep_pickup_datetime  | 2025-09-03 |   1811 |  3.7040 |
| lpep_pickup_datetime  | 2025-09-04 |   1858 |  3.8001 |
| lpep_pickup_datetime  | 2025-09-05 |   1731 |  3.5404 |
| lpep_pickup_datetime  | 2025-09-06 |   1365 |  2.7918 |
| lpep_pickup_datetime  | 2025-09-07 |   1314 |  2.6875 |
| lpep_pickup_datetime  | 2025-09-08 |   1583 |  3.2377 |
| lpep_pickup_datetime  | 2025-09-09 |   1591 |  3.2540 |
| lpep_pickup_datetime  | 2025-09-10 |   1761 |  3.6017 |
| lpep_pickup_datetime  | 2025-09-11 |   1785 |  3.6508 |
| lpep_pickup_datetime  | 2025-09-12 |   1778 |  3.6365 |
| lpep_pickup_datetime  | 2025-09-13 |   1404 |  2.8716 |
| lpep_pickup_datetime  | 2025-09-14 |   1431 |  2.9268 |
| lpep_pickup_datetime  | 2025-09-15 |   1660 |  3.3952 |
| lpep_pickup_datetime  | 2025-09-16 |   1729 |  3.5363 |
| lpep_pickup_datetime  | 2025-09-17 |   1816 |  3.7142 |
| lpep_pickup_datetime  | 2025-09-18 |   1852 |  3.7879 |
| lpep_pickup_datetime  | 2025-09-19 |   1766 |  3.6120 |
| lpep_pickup_datetime  | 2025-09-20 |   1476 |  3.0188 |
| lpep_pickup_datetime  | 2025-09-21 |   1436 |  2.9370 |
| lpep_pickup_datetime  | 2025-09-22 |   1675 |  3.4258 |
| lpep_pickup_datetime  | 2025-09-23 |   1595 |  3.2622 |
| lpep_pickup_datetime  | 2025-09-24 |   1742 |  3.5629 |
| lpep_pickup_datetime  | 2025-09-25 |   1857 |  3.7981 |
| lpep_pickup_datetime  | 2025-09-26 |   1678 |  3.4320 |
| lpep_pickup_datetime  | 2025-09-27 |   1400 |  2.8634 |
| lpep_pickup_datetime  | 2025-09-28 |   1383 |  2.8286 |
| lpep_pickup_datetime  | 2025-09-29 |   1684 |  3.4443 |
| lpep_pickup_datetime  | 2025-09-30 |   1633 |  3.3399 |
| lpep_pickup_datetime  | 2025-10-01 |     14 |  0.0286 |
| lpep_dropoff_datetime | 2025-08-25 |      3 |  0.0061 |
| lpep_dropoff_datetime | 2025-08-26 |      3 |  0.0061 |
| lpep_dropoff_datetime | 2025-08-27 |      4 |  0.0082 |
| lpep_dropoff_datetime | 2025-08-28 |      1 |  0.0020 |
| lpep_dropoff_datetime | 2025-08-29 |      1 |  0.0020 |
| lpep_dropoff_datetime | 2025-08-30 |      1 |  0.0020 |
| lpep_dropoff_datetime | 2025-08-31 |      5 |  0.0102 |
| lpep_dropoff_datetime | 2025-09-01 |   1352 |  2.7652 |
| lpep_dropoff_datetime | 2025-09-02 |   1694 |  3.4647 |
| lpep_dropoff_datetime | 2025-09-03 |   1810 |  3.7020 |
| lpep_dropoff_datetime | 2025-09-04 |   1860 |  3.8042 |
| lpep_dropoff_datetime | 2025-09-05 |   1728 |  3.5342 |
| lpep_dropoff_datetime | 2025-09-06 |   1362 |  2.7857 |
| lpep_dropoff_datetime | 2025-09-07 |   1331 |  2.7223 |
| lpep_dropoff_datetime | 2025-09-08 |   1589 |  3.2500 |
| lpep_dropoff_datetime | 2025-09-09 |   1589 |  3.2500 |
| lpep_dropoff_datetime | 2025-09-10 |   1752 |  3.5833 |
| lpep_dropoff_datetime | 2025-09-11 |   1781 |  3.6426 |
| lpep_dropoff_datetime | 2025-09-12 |   1772 |  3.6242 |
| lpep_dropoff_datetime | 2025-09-13 |   1407 |  2.8777 |
| lpep_dropoff_datetime | 2025-09-14 |   1438 |  2.9411 |
| lpep_dropoff_datetime | 2025-09-15 |   1662 |  3.3993 |
| lpep_dropoff_datetime | 2025-09-16 |   1736 |  3.5506 |
| lpep_dropoff_datetime | 2025-09-17 |   1816 |  3.7142 |
| lpep_dropoff_datetime | 2025-09-18 |   1847 |  3.7776 |
| lpep_dropoff_datetime | 2025-09-19 |   1757 |  3.5936 |
| lpep_dropoff_datetime | 2025-09-20 |   1479 |  3.0250 |
| lpep_dropoff_datetime | 2025-09-21 |   1443 |  2.9513 |
| lpep_dropoff_datetime | 2025-09-22 |   1674 |  3.4238 |
| lpep_dropoff_datetime | 2025-09-23 |   1593 |  3.2581 |
| lpep_dropoff_datetime | 2025-09-24 |   1740 |  3.5588 |
| lpep_dropoff_datetime | 2025-09-25 |   1855 |  3.7940 |
| lpep_dropoff_datetime | 2025-09-26 |   1682 |  3.4402 |
| lpep_dropoff_datetime | 2025-09-27 |   1393 |  2.8491 |
| lpep_dropoff_datetime | 2025-09-28 |   1392 |  2.8470 |
| lpep_dropoff_datetime | 2025-09-29 |   1680 |  3.4361 |
| lpep_dropoff_datetime | 2025-09-30 |   1638 |  3.3502 |
| lpep_dropoff_datetime | 2025-10-01 |     23 |  0.0470 |

## Top Values (full-data, top 5)

| column                | top_5_values                                             |
|:----------------------|:---------------------------------------------------------|
| VendorID              | 2: 40609, 1: 4659, 6: 3625                               |
| store_and_fwd_flag    | N: 43391, <NULL>: 5407, Y: 95                            |
| RatecodeID            | 1.0: 39962, <NULL>: 5407, 5.0: 3278, 2.0: 130, 4.0: 93   |
| passenger_count       | 1.0: 35850, <NULL>: 5407, 2.0: 4584, 5.0: 860, 0.0: 711  |
| mta_tax               | 0.5: 40978, 1.5: 4334, 0.0: 3466, -0.5: 105, 1.0: 8      |
| ehail_fee             | <NULL>: 48893                                            |
| improvement_surcharge | 1.0: 44886, 0.3: 3473, 0.0: 415, -1.0: 119               |
| payment_type          | 1.0: 33045, 2.0: 10113, <NULL>: 5407, 3.0: 245, 4.0: 82  |
| trip_type             | 1.0: 40417, <NULL>: 5408, 2.0: 3068                      |
| congestion_surcharge  | 0.0: 29225, 2.75: 14246, <NULL>: 5407, 2.5: 11, -2.75: 4 |
| cbd_congestion_fee    | 0.0: 44065, 0.75: 4827, -0.75: 1                         |

## Data Quality Signals

- Duplicate rows in full data: `0` / `48893`.
- Columns with >= 50% null in full data: `ehail_fee`.
- Near-constant columns in full data: `ehail_fee`.
- High-cardinality / ID-like columns: `lpep_pickup_datetime`, `lpep_dropoff_datetime`.
- Numeric columns containing negative values: `fare_amount`, `extra`, `mta_tax`, `tip_amount`, `tolls_amount`, `improvement_surcharge`, `total_amount`, `congestion_surcharge`, `cbd_congestion_fee`.

## Data Preview

|   VendorID | lpep_pickup_datetime   | lpep_dropoff_datetime   | store_and_fwd_flag   |   RatecodeID |   PULocationID |   DOLocationID |   passenger_count |   trip_distance |   fare_amount |   extra |   mta_tax |   tip_amount |   tolls_amount |   ehail_fee |   improvement_surcharge |   total_amount |   payment_type |   trip_type |   congestion_surcharge |   cbd_congestion_fee |
|-----------:|:-----------------------|:------------------------|:---------------------|-------------:|---------------:|---------------:|------------------:|----------------:|--------------:|--------:|----------:|-------------:|---------------:|------------:|------------------------:|---------------:|---------------:|------------:|-----------------------:|---------------------:|
|          2 | 2025-09-01 00:06:49    | 2025-09-01 00:17:31     | N                    |            1 |             74 |            263 |                 1 |            1.86 |          12.8 |       1 |       0.5 |         3.06 |              0 |         nan |                       1 |          18.36 |              1 |           1 |                   0    |                 0    |
|          2 | 2025-09-01 00:20:15    | 2025-09-01 00:40:57     | N                    |            1 |            255 |            261 |                 1 |            5.96 |          27.5 |       1 |       0.5 |         0    |              0 |         nan |                       1 |          33.5  |              1 |           1 |                   2.75 |                 0.75 |
|          2 | 2025-09-01 00:35:58    | 2025-09-01 00:36:01     | N                    |            5 |            130 |            130 |                 1 |            0.01 |          11   |       0 |       0   |         0.08 |              0 |         nan |                       1 |          12.08 |              1 |           2 |                   0    |                 0    |
|          2 | 2025-09-01 00:13:28    | 2025-09-01 00:17:11     | N                    |            1 |             74 |             75 |                 1 |            1.36 |           7.2 |       1 |       0.5 |         1.94 |              0 |         nan |                       1 |          11.64 |              1 |           1 |                   0    |                 0    |
|          2 | 2025-09-01 00:41:47    | 2025-09-01 00:45:10     | N                    |            1 |            240 |            200 |                 1 |            0.98 |           6.5 |       1 |       0.5 |         2.25 |              0 |         nan |                       1 |          11.25 |              1 |           1 |                   0    |                 0    |
|          2 | 2025-09-01 00:04:10    | 2025-09-01 00:29:29     | N                    |            1 |             93 |            234 |                 1 |           13.08 |          52   |       1 |       0.5 |        14.5  |              0 |         nan |                       1 |          72.5  |              1 |           1 |                   2.75 |                 0.75 |
|          2 | 2025-09-01 00:23:09    | 2025-09-01 00:47:30     | N                    |            1 |            243 |            238 |                 3 |            5.95 |          29.6 |       1 |       0.5 |         5    |              0 |         nan |                       1 |          39.85 |              1 |           1 |                   2.75 |                 0    |
|          2 | 2025-09-01 22:24:20    | 2025-09-02 00:32:11     | N                    |            5 |             95 |             95 |                 5 |            0    |          10   |       0 |       0   |         0    |              0 |         nan |                       0 |          10    |              1 |           2 |                   0    |                 0    |
|          2 | 2025-09-01 00:04:36    | 2025-09-01 00:28:06     | N                    |            5 |             93 |             65 |                 1 |           12.17 |          60   |       0 |       0   |        12.2  |              0 |         nan |                       1 |          73.2  |              1 |           2 |                   0    |                 0    |
|          2 | 2025-09-01 00:21:24    | 2025-09-01 00:21:40     | N                    |            5 |             80 |             80 |                 1 |            0.02 |         100   |       0 |       0   |         0    |              0 |         nan |                       1 |         101    |              1 |           2 |                   0    |                 0    |
