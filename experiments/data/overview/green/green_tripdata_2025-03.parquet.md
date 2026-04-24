# Data Overview: green_tripdata_2025-03.parquet

## Dataset Summary

| metric       | value                                                                             |
|:-------------|:----------------------------------------------------------------------------------|
| file         | /root/Dev/DataGate/experiments/data/parquets/green/green_tripdata_2025-03.parquet |
| rows         | 51539                                                                             |
| columns      | 21                                                                                |
| row_groups   | 1                                                                                 |
| file_size_mb | 1.20                                                                              |
| rows_loaded  | 51539                                                                             |

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
| VendorID              | int32          |      51539 |      0 |   0.0000 |        3 |
| lpep_pickup_datetime  | datetime64[us] |      51539 |      0 |   0.0000 |    50595 |
| lpep_dropoff_datetime | datetime64[us] |      51539 |      0 |   0.0000 |    50570 |
| store_and_fwd_flag    | str            |      47990 |   3549 |   6.8860 |        2 |
| RatecodeID            | float64        |      47990 |   3549 |   6.8860 |        6 |
| PULocationID          | int32          |      51539 |      0 |   0.0000 |      231 |
| DOLocationID          | int32          |      51539 |      0 |   0.0000 |      247 |
| passenger_count       | float64        |      47990 |   3549 |   6.8860 |       10 |
| trip_distance         | float64        |      51539 |      0 |   0.0000 |     1934 |
| fare_amount           | float64        |      51539 |      0 |   0.0000 |     1786 |
| extra                 | float64        |      51539 |      0 |   0.0000 |       17 |
| mta_tax               | float64        |      51539 |      0 |   0.0000 |        6 |
| tip_amount            | float64        |      51539 |      0 |   0.0000 |     1456 |
| tolls_amount          | float64        |      51539 |      0 |   0.0000 |       24 |
| ehail_fee             | float64        |          0 |  51539 | 100.0000 |        0 |
| improvement_surcharge | float64        |      51539 |      0 |   0.0000 |        5 |
| total_amount          | float64        |      51539 |      0 |   0.0000 |     4465 |
| payment_type          | float64        |      47990 |   3549 |   6.8860 |        5 |
| trip_type             | float64        |      47983 |   3556 |   6.8996 |        2 |
| congestion_surcharge  | float64        |      47990 |   3549 |   6.8860 |        4 |
| cbd_congestion_fee    | float64        |      51539 |      0 |   0.0000 |        3 |

## Numeric Statistics (full-data)

| column                |       min |     p25 |   median |     mean |      p75 |         max |      std |
|:----------------------|----------:|--------:|---------:|---------:|---------:|------------:|---------:|
| VendorID              |    1.0000 |  2.0000 |   2.0000 |   1.9668 |   2.0000 |      6.0000 |   0.7115 |
| RatecodeID            |    1.0000 |  1.0000 |   1.0000 |   1.3779 |   1.0000 |     99.0000 |   4.2267 |
| PULocationID          |    1.0000 | 74.0000 |  75.0000 |  97.2050 | 116.0000 |    265.0000 |  56.6407 |
| DOLocationID          |    1.0000 | 74.0000 | 140.0000 | 141.0595 | 226.0000 |    265.0000 |  77.0144 |
| passenger_count       |    0.0000 |  1.0000 |   1.0000 |   1.2837 |   1.0000 |      9.0000 |   0.9312 |
| trip_distance         |    0.0000 |  1.1400 |   1.8600 |  15.5023 |   3.2700 | 147993.1100 | 941.5063 |
| fare_amount           | -470.6000 |  9.3000 |  13.5800 |  17.6785 |  20.5000 |    470.6000 |  15.5594 |
| extra                 |   -5.0000 |  0.0000 |   0.0000 |   0.8452 |   1.0000 |     11.0000 |   1.3541 |
| mta_tax               |   -0.5000 |  0.5000 |   0.5000 |   0.5990 |   0.5000 |     61.5000 |   0.4471 |
| tip_amount            |   -0.9000 |  0.0000 |   2.0000 |   2.5028 |   3.7500 |    215.0000 |   3.4413 |
| tolls_amount          |    0.0000 |  0.0000 |   0.0000 |   0.2248 |   0.0000 |     48.9400 |   1.3202 |
| improvement_surcharge |   -1.0000 |  1.0000 |   1.0000 |   0.9730 |   1.0000 |      1.0000 |   0.1647 |
| total_amount          | -473.1000 | 14.1600 |  19.3200 |  23.9653 |  28.0800 |    473.1000 |  17.7729 |
| payment_type          |    1.0000 |  1.0000 |   1.0000 |   1.2741 |   2.0000 |      5.0000 |   0.4792 |
| trip_type             |    1.0000 |  1.0000 |   1.0000 |   1.0472 |   1.0000 |      2.0000 |   0.2121 |
| congestion_surcharge  |   -2.7500 |  0.0000 |   0.0000 |   0.8264 |   2.7500 |      2.7500 |   1.2608 |
| cbd_congestion_fee    |   -0.7500 |  0.0000 |   0.0000 |   0.0702 |   0.0000 |      0.7500 |   0.2186 |

## Datetime Coverage (full-data)

| column                | min_ts              | max_ts              | span             |
|:----------------------|:--------------------|:--------------------|:-----------------|
| lpep_pickup_datetime  | 2025-02-25 18:10:10 | 2025-04-01 23:41:29 | 35 days 05:31:19 |
| lpep_dropoff_datetime | 2025-02-25 18:12:33 | 2025-04-01 23:41:50 | 35 days 05:29:17 |

## Datetime Distribution by Day (full-data)

| column                | day        |   rows |   row_% |
|:----------------------|:-----------|-------:|--------:|
| lpep_pickup_datetime  | 2025-02-25 |      2 |  0.0039 |
| lpep_pickup_datetime  | 2025-02-27 |      2 |  0.0039 |
| lpep_pickup_datetime  | 2025-02-28 |      2 |  0.0039 |
| lpep_pickup_datetime  | 2025-03-01 |   1425 |  2.7649 |
| lpep_pickup_datetime  | 2025-03-02 |   1310 |  2.5418 |
| lpep_pickup_datetime  | 2025-03-03 |   1703 |  3.3043 |
| lpep_pickup_datetime  | 2025-03-04 |   1787 |  3.4673 |
| lpep_pickup_datetime  | 2025-03-05 |   1981 |  3.8437 |
| lpep_pickup_datetime  | 2025-03-06 |   2022 |  3.9232 |
| lpep_pickup_datetime  | 2025-03-07 |   1780 |  3.4537 |
| lpep_pickup_datetime  | 2025-03-08 |   1488 |  2.8871 |
| lpep_pickup_datetime  | 2025-03-09 |   1281 |  2.4855 |
| lpep_pickup_datetime  | 2025-03-10 |   1616 |  3.1355 |
| lpep_pickup_datetime  | 2025-03-11 |   1737 |  3.3703 |
| lpep_pickup_datetime  | 2025-03-12 |   1813 |  3.5177 |
| lpep_pickup_datetime  | 2025-03-13 |   2010 |  3.9000 |
| lpep_pickup_datetime  | 2025-03-14 |   1829 |  3.5488 |
| lpep_pickup_datetime  | 2025-03-15 |   1525 |  2.9589 |
| lpep_pickup_datetime  | 2025-03-16 |   1259 |  2.4428 |
| lpep_pickup_datetime  | 2025-03-17 |   1704 |  3.3062 |
| lpep_pickup_datetime  | 2025-03-18 |   1673 |  3.2461 |
| lpep_pickup_datetime  | 2025-03-19 |   1756 |  3.4071 |
| lpep_pickup_datetime  | 2025-03-20 |   1933 |  3.7506 |
| lpep_pickup_datetime  | 2025-03-21 |   1758 |  3.4110 |
| lpep_pickup_datetime  | 2025-03-22 |   1421 |  2.7571 |
| lpep_pickup_datetime  | 2025-03-23 |   1275 |  2.4739 |
| lpep_pickup_datetime  | 2025-03-24 |   1775 |  3.4440 |
| lpep_pickup_datetime  | 2025-03-25 |   1732 |  3.3606 |
| lpep_pickup_datetime  | 2025-03-26 |   1853 |  3.5953 |
| lpep_pickup_datetime  | 2025-03-27 |   1856 |  3.6012 |
| lpep_pickup_datetime  | 2025-03-28 |   1709 |  3.3159 |
| lpep_pickup_datetime  | 2025-03-29 |   1608 |  3.1200 |
| lpep_pickup_datetime  | 2025-03-30 |   1217 |  2.3613 |
| lpep_pickup_datetime  | 2025-03-31 |   1692 |  3.2830 |
| lpep_pickup_datetime  | 2025-04-01 |      5 |  0.0097 |
| lpep_dropoff_datetime | 2025-02-25 |      2 |  0.0039 |
| lpep_dropoff_datetime | 2025-02-27 |      2 |  0.0039 |
| lpep_dropoff_datetime | 2025-03-01 |   1409 |  2.7339 |
| lpep_dropoff_datetime | 2025-03-02 |   1311 |  2.5437 |
| lpep_dropoff_datetime | 2025-03-03 |   1707 |  3.3121 |
| lpep_dropoff_datetime | 2025-03-04 |   1784 |  3.4615 |
| lpep_dropoff_datetime | 2025-03-05 |   1984 |  3.8495 |
| lpep_dropoff_datetime | 2025-03-06 |   2010 |  3.9000 |
| lpep_dropoff_datetime | 2025-03-07 |   1790 |  3.4731 |
| lpep_dropoff_datetime | 2025-03-08 |   1485 |  2.8813 |
| lpep_dropoff_datetime | 2025-03-09 |   1286 |  2.4952 |
| lpep_dropoff_datetime | 2025-03-10 |   1621 |  3.1452 |
| lpep_dropoff_datetime | 2025-03-11 |   1740 |  3.3761 |
| lpep_dropoff_datetime | 2025-03-12 |   1805 |  3.5022 |
| lpep_dropoff_datetime | 2025-03-13 |   2016 |  3.9116 |
| lpep_dropoff_datetime | 2025-03-14 |   1818 |  3.5274 |
| lpep_dropoff_datetime | 2025-03-15 |   1518 |  2.9453 |
| lpep_dropoff_datetime | 2025-03-16 |   1275 |  2.4739 |
| lpep_dropoff_datetime | 2025-03-17 |   1697 |  3.2927 |
| lpep_dropoff_datetime | 2025-03-18 |   1679 |  3.2577 |
| lpep_dropoff_datetime | 2025-03-19 |   1756 |  3.4071 |
| lpep_dropoff_datetime | 2025-03-20 |   1931 |  3.7467 |
| lpep_dropoff_datetime | 2025-03-21 |   1757 |  3.4091 |
| lpep_dropoff_datetime | 2025-03-22 |   1419 |  2.7533 |
| lpep_dropoff_datetime | 2025-03-23 |   1284 |  2.4913 |
| lpep_dropoff_datetime | 2025-03-24 |   1768 |  3.4304 |
| lpep_dropoff_datetime | 2025-03-25 |   1730 |  3.3567 |
| lpep_dropoff_datetime | 2025-03-26 |   1852 |  3.5934 |
| lpep_dropoff_datetime | 2025-03-27 |   1858 |  3.6050 |
| lpep_dropoff_datetime | 2025-03-28 |   1704 |  3.3062 |
| lpep_dropoff_datetime | 2025-03-29 |   1606 |  3.1161 |
| lpep_dropoff_datetime | 2025-03-30 |   1231 |  2.3885 |
| lpep_dropoff_datetime | 2025-03-31 |   1693 |  3.2849 |
| lpep_dropoff_datetime | 2025-04-01 |     11 |  0.0213 |

## Top Values (full-data, top 5)

| column                | top_5_values                                             |
|:----------------------|:---------------------------------------------------------|
| VendorID              | 2: 43719, 1: 6598, 6: 1222                               |
| store_and_fwd_flag    | N: 47921, <NULL>: 3549, Y: 69                            |
| RatecodeID            | 1.0: 45367, <NULL>: 3549, 5.0: 2351, 2.0: 111, 99.0: 86  |
| passenger_count       | 1.0: 40445, 2.0: 4319, <NULL>: 3549, 5.0: 1021, 6.0: 753 |
| mta_tax               | 0.5: 42667, 1.5: 6353, 0.0: 2365, -0.5: 138, 1.0: 15     |
| ehail_fee             | <NULL>: 51539                                            |
| improvement_surcharge | 1.0: 49915, 0.3: 1298, 0.0: 166, -1.0: 157, -0.3: 3      |
| payment_type          | 1.0: 35445, 2.0: 12064, <NULL>: 3549, 3.0: 357, 4.0: 122 |
| trip_type             | 1.0: 45717, <NULL>: 3556, 2.0: 2266                      |
| congestion_surcharge  | 0.0: 33555, 2.75: 14353, <NULL>: 3549, 2.5: 79, -2.75: 3 |
| cbd_congestion_fee    | 0.0: 46710, 0.75: 4828, -0.75: 1                         |

## Data Quality Signals

- Duplicate rows in full data: `0` / `51539`.
- Columns with >= 50% null in full data: `ehail_fee`.
- Near-constant columns in full data: `ehail_fee`.
- High-cardinality / ID-like columns: `lpep_pickup_datetime`, `lpep_dropoff_datetime`.
- Numeric columns containing negative values: `fare_amount`, `extra`, `mta_tax`, `tip_amount`, `improvement_surcharge`, `total_amount`, `congestion_surcharge`, `cbd_congestion_fee`.

## Data Preview

|   VendorID | lpep_pickup_datetime   | lpep_dropoff_datetime   | store_and_fwd_flag   |   RatecodeID |   PULocationID |   DOLocationID |   passenger_count |   trip_distance |   fare_amount |   extra |   mta_tax |   tip_amount |   tolls_amount |   ehail_fee |   improvement_surcharge |   total_amount |   payment_type |   trip_type |   congestion_surcharge |   cbd_congestion_fee |
|-----------:|:-----------------------|:------------------------|:---------------------|-------------:|---------------:|---------------:|------------------:|----------------:|--------------:|--------:|----------:|-------------:|---------------:|------------:|------------------------:|---------------:|---------------:|------------:|-----------------------:|---------------------:|
|          2 | 2025-03-01 00:07:34    | 2025-03-01 00:24:52     | N                    |            1 |             75 |            239 |                 1 |            2.2  |         18.4  |       1 |       0.5 |         5.91 |           0    |         nan |                       1 |          29.56 |              1 |           1 |                   2.75 |                    0 |
|          2 | 2025-03-01 00:01:24    | 2025-03-01 00:10:03     | N                    |            1 |             41 |             42 |                 1 |            1.06 |          8.6  |       1 |       0.5 |         3.33 |           0    |         nan |                       1 |          14.43 |              1 |           1 |                   0    |                    0 |
|          2 | 2025-03-01 00:45:03    | 2025-03-01 01:05:38     | N                    |            1 |            265 |             56 |                 1 |           18.91 |         69.5  |       1 |       0.5 |         0    |           0    |         nan |                       1 |          72    |              2 |           1 |                   0    |                    0 |
|          2 | 2025-03-01 00:10:10    | 2025-03-01 00:29:35     | N                    |            5 |             82 |            236 |                 1 |            8.36 |         30.17 |       0 |       0.5 |         3.35 |           6.94 |         nan |                       1 |          44.71 |              1 |           1 |                   2.75 |                    0 |
|          2 | 2025-03-01 00:16:14    | 2025-03-01 00:19:44     | N                    |            1 |             66 |             33 |                 1 |            0.82 |          5.8  |       1 |       0.5 |         0    |           0    |         nan |                       1 |           8.3  |              2 |           1 |                   0    |                    0 |
|          2 | 2025-03-01 00:02:43    | 2025-03-01 00:15:52     | N                    |            1 |            134 |            122 |                 1 |            4.94 |         21.9  |       1 |       0.5 |         0    |           0    |         nan |                       1 |          24.4  |              2 |           1 |                   0    |                    0 |
|          2 | 2025-03-01 00:03:47    | 2025-03-01 00:10:45     | N                    |            1 |            260 |            260 |                 1 |            0.81 |          8.6  |       1 |       0.5 |         2    |           0    |         nan |                       1 |          13.1  |              1 |           1 |                   0    |                    0 |
|          2 | 2025-03-01 00:16:56    | 2025-03-01 00:26:26     | N                    |            1 |            244 |            243 |                 2 |            1.56 |         11.4  |       1 |       0.5 |         0    |           0    |         nan |                       1 |          13.9  |              2 |           1 |                   0    |                    0 |
|          2 | 2025-03-01 00:49:43    | 2025-03-01 00:58:25     | N                    |            1 |             75 |            262 |                 1 |            1.53 |         10.7  |       1 |       0.5 |         2.39 |           0    |         nan |                       1 |          18.34 |              1 |           1 |                   2.75 |                    0 |
|          1 | 2025-03-01 00:52:31    | 2025-03-01 00:53:00     | N                    |            5 |            129 |            129 |                 1 |            0    |         35    |       0 |       0   |         7    |           0    |         nan |                       0 |          42    |              1 |           2 |                   0    |                    0 |
