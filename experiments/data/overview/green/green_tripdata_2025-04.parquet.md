# Data Overview: green_tripdata_2025-04.parquet

## Dataset Summary

| metric       | value                                                                             |
|:-------------|:----------------------------------------------------------------------------------|
| file         | /root/Dev/DataGate/experiments/data/parquets/green/green_tripdata_2025-04.parquet |
| rows         | 52132                                                                             |
| columns      | 21                                                                                |
| row_groups   | 1                                                                                 |
| file_size_mb | 1.21                                                                              |
| rows_loaded  | 52132                                                                             |

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
| VendorID              | int32          |      52132 |      0 |   0.0000 |        3 |
| lpep_pickup_datetime  | datetime64[us] |      52132 |      0 |   0.0000 |    51136 |
| lpep_dropoff_datetime | datetime64[us] |      52132 |      0 |   0.0000 |    51150 |
| store_and_fwd_flag    | str            |      48944 |   3188 |   6.1152 |        2 |
| RatecodeID            | float64        |      48944 |   3188 |   6.1152 |        6 |
| PULocationID          | int32          |      52132 |      0 |   0.0000 |      227 |
| DOLocationID          | int32          |      52132 |      0 |   0.0000 |      252 |
| passenger_count       | float64        |      48944 |   3188 |   6.1152 |       10 |
| trip_distance         | float64        |      52132 |      0 |   0.0000 |     1967 |
| fare_amount           | float64        |      52132 |      0 |   0.0000 |     1636 |
| extra                 | float64        |      52132 |      0 |   0.0000 |       17 |
| mta_tax               | float64        |      52132 |      0 |   0.0000 |        5 |
| tip_amount            | float64        |      52132 |      0 |   0.0000 |     1458 |
| tolls_amount          | float64        |      52132 |      0 |   0.0000 |       28 |
| ehail_fee             | float64        |          0 |  52132 | 100.0000 |        0 |
| improvement_surcharge | float64        |      52132 |      0 |   0.0000 |        5 |
| total_amount          | float64        |      52132 |      0 |   0.0000 |     4520 |
| payment_type          | float64        |      48944 |   3188 |   6.1152 |        4 |
| trip_type             | float64        |      48937 |   3195 |   6.1287 |        2 |
| congestion_surcharge  | float64        |      48944 |   3188 |   6.1152 |        4 |
| cbd_congestion_fee    | float64        |      52132 |      0 |   0.0000 |        3 |

## Numeric Statistics (full-data)

| column                |       min |     p25 |   median |     mean |      p75 |         max |       std |
|:----------------------|----------:|--------:|---------:|---------:|---------:|------------:|----------:|
| VendorID              |    1.0000 |  2.0000 |   2.0000 |   1.9623 |   2.0000 |      6.0000 |    0.6943 |
| RatecodeID            |    1.0000 |  1.0000 |   1.0000 |   1.4310 |   1.0000 |     99.0000 |    4.7937 |
| PULocationID          |    1.0000 | 74.0000 |  75.0000 |  96.4206 | 106.0000 |    265.0000 |   55.8616 |
| DOLocationID          |    1.0000 | 75.0000 | 141.0000 | 143.5836 | 230.0000 |    265.0000 |   76.9995 |
| passenger_count       |    0.0000 |  1.0000 |   1.0000 |   1.2910 |   1.0000 |      9.0000 |    0.9453 |
| trip_distance         |    0.0000 |  1.1500 |   1.9000 |  17.9742 |   3.3000 | 143684.9100 | 1057.2505 |
| fare_amount           | -223.0000 | 10.0000 |  14.2000 |  18.1259 |  20.5000 |    320.0000 |   15.8069 |
| extra                 |   -5.0000 |  0.0000 |   0.0000 |   0.9086 |   2.5000 |     12.5000 |    1.3888 |
| mta_tax               |   -0.5000 |  0.5000 |   0.5000 |   0.5957 |   0.5000 |      1.5000 |    0.3549 |
| tip_amount            | -100.0000 |  0.0000 |   2.0800 |   2.6040 |   3.9100 |    140.0000 |    3.3637 |
| tolls_amount          |    0.0000 |  0.0000 |   0.0000 |   0.2474 |   0.0000 |     28.1200 |    1.3707 |
| improvement_surcharge |   -1.0000 |  1.0000 |   1.0000 |   0.9746 |   1.0000 |      1.0000 |    0.1584 |
| total_amount          | -224.0000 | 14.6000 |  19.9000 |  24.6282 |  28.8600 |    381.0000 |   18.0502 |
| payment_type          |    1.0000 |  1.0000 |   1.0000 |   1.2573 |   1.0000 |      4.0000 |    0.4662 |
| trip_type             |    1.0000 |  1.0000 |   1.0000 |   1.0482 |   1.0000 |      2.0000 |    0.2142 |
| congestion_surcharge  |   -2.7500 |  0.0000 |   0.0000 |   0.8734 |   2.7500 |      2.7500 |    1.2805 |
| cbd_congestion_fee    |   -0.7500 |  0.0000 |   0.0000 |   0.0731 |   0.0000 |      0.7500 |    0.2225 |

## Datetime Coverage (full-data)

| column                | min_ts              | max_ts              | span             |
|:----------------------|:--------------------|:--------------------|:-----------------|
| lpep_pickup_datetime  | 2025-03-25 22:50:59 | 2025-05-01 22:59:12 | 37 days 00:08:13 |
| lpep_dropoff_datetime | 2025-03-25 22:58:02 | 2025-05-01 23:10:01 | 37 days 00:11:59 |

## Datetime Distribution by Day (full-data)

| column                | day        |   rows |   row_% |
|:----------------------|:-----------|-------:|--------:|
| lpep_pickup_datetime  | 2025-03-25 |      1 |  0.0019 |
| lpep_pickup_datetime  | 2025-03-27 |      2 |  0.0038 |
| lpep_pickup_datetime  | 2025-03-28 |      2 |  0.0038 |
| lpep_pickup_datetime  | 2025-03-31 |      3 |  0.0058 |
| lpep_pickup_datetime  | 2025-04-01 |   1800 |  3.4528 |
| lpep_pickup_datetime  | 2025-04-02 |   1924 |  3.6906 |
| lpep_pickup_datetime  | 2025-04-03 |   1930 |  3.7021 |
| lpep_pickup_datetime  | 2025-04-04 |   1894 |  3.6331 |
| lpep_pickup_datetime  | 2025-04-05 |   1672 |  3.2072 |
| lpep_pickup_datetime  | 2025-04-06 |   1449 |  2.7795 |
| lpep_pickup_datetime  | 2025-04-07 |   1879 |  3.6043 |
| lpep_pickup_datetime  | 2025-04-08 |   1950 |  3.7405 |
| lpep_pickup_datetime  | 2025-04-09 |   1952 |  3.7443 |
| lpep_pickup_datetime  | 2025-04-10 |   2008 |  3.8518 |
| lpep_pickup_datetime  | 2025-04-11 |   1962 |  3.7635 |
| lpep_pickup_datetime  | 2025-04-12 |   1428 |  2.7392 |
| lpep_pickup_datetime  | 2025-04-13 |   1265 |  2.4265 |
| lpep_pickup_datetime  | 2025-04-14 |   1611 |  3.0902 |
| lpep_pickup_datetime  | 2025-04-15 |   1805 |  3.4624 |
| lpep_pickup_datetime  | 2025-04-16 |   1816 |  3.4835 |
| lpep_pickup_datetime  | 2025-04-17 |   1890 |  3.6254 |
| lpep_pickup_datetime  | 2025-04-18 |   1589 |  3.0480 |
| lpep_pickup_datetime  | 2025-04-19 |   1348 |  2.5857 |
| lpep_pickup_datetime  | 2025-04-20 |   1435 |  2.7526 |
| lpep_pickup_datetime  | 2025-04-21 |   1785 |  3.4240 |
| lpep_pickup_datetime  | 2025-04-22 |   1812 |  3.4758 |
| lpep_pickup_datetime  | 2025-04-23 |   1782 |  3.4182 |
| lpep_pickup_datetime  | 2025-04-24 |   1904 |  3.6523 |
| lpep_pickup_datetime  | 2025-04-25 |   1912 |  3.6676 |
| lpep_pickup_datetime  | 2025-04-26 |   1565 |  3.0020 |
| lpep_pickup_datetime  | 2025-04-27 |   1445 |  2.7718 |
| lpep_pickup_datetime  | 2025-04-28 |   1747 |  3.3511 |
| lpep_pickup_datetime  | 2025-04-29 |   1717 |  3.2936 |
| lpep_pickup_datetime  | 2025-04-30 |   1844 |  3.5372 |
| lpep_pickup_datetime  | 2025-05-01 |      4 |  0.0077 |
| lpep_dropoff_datetime | 2025-03-25 |      1 |  0.0019 |
| lpep_dropoff_datetime | 2025-03-27 |      1 |  0.0019 |
| lpep_dropoff_datetime | 2025-03-28 |      3 |  0.0058 |
| lpep_dropoff_datetime | 2025-03-31 |      3 |  0.0058 |
| lpep_dropoff_datetime | 2025-04-01 |   1783 |  3.4202 |
| lpep_dropoff_datetime | 2025-04-02 |   1932 |  3.7060 |
| lpep_dropoff_datetime | 2025-04-03 |   1931 |  3.7041 |
| lpep_dropoff_datetime | 2025-04-04 |   1877 |  3.6005 |
| lpep_dropoff_datetime | 2025-04-05 |   1675 |  3.2130 |
| lpep_dropoff_datetime | 2025-04-06 |   1459 |  2.7987 |
| lpep_dropoff_datetime | 2025-04-07 |   1881 |  3.6081 |
| lpep_dropoff_datetime | 2025-04-08 |   1942 |  3.7252 |
| lpep_dropoff_datetime | 2025-04-09 |   1953 |  3.7463 |
| lpep_dropoff_datetime | 2025-04-10 |   2009 |  3.8537 |
| lpep_dropoff_datetime | 2025-04-11 |   1963 |  3.7654 |
| lpep_dropoff_datetime | 2025-04-12 |   1429 |  2.7411 |
| lpep_dropoff_datetime | 2025-04-13 |   1267 |  2.4304 |
| lpep_dropoff_datetime | 2025-04-14 |   1608 |  3.0845 |
| lpep_dropoff_datetime | 2025-04-15 |   1806 |  3.4643 |
| lpep_dropoff_datetime | 2025-04-16 |   1815 |  3.4815 |
| lpep_dropoff_datetime | 2025-04-17 |   1884 |  3.6139 |
| lpep_dropoff_datetime | 2025-04-18 |   1591 |  3.0519 |
| lpep_dropoff_datetime | 2025-04-19 |   1350 |  2.5896 |
| lpep_dropoff_datetime | 2025-04-20 |   1440 |  2.7622 |
| lpep_dropoff_datetime | 2025-04-21 |   1788 |  3.4298 |
| lpep_dropoff_datetime | 2025-04-22 |   1804 |  3.4604 |
| lpep_dropoff_datetime | 2025-04-23 |   1784 |  3.4221 |
| lpep_dropoff_datetime | 2025-04-24 |   1904 |  3.6523 |
| lpep_dropoff_datetime | 2025-04-25 |   1906 |  3.6561 |
| lpep_dropoff_datetime | 2025-04-26 |   1561 |  2.9943 |
| lpep_dropoff_datetime | 2025-04-27 |   1456 |  2.7929 |
| lpep_dropoff_datetime | 2025-04-28 |   1752 |  3.3607 |
| lpep_dropoff_datetime | 2025-04-29 |   1714 |  3.2878 |
| lpep_dropoff_datetime | 2025-04-30 |   1842 |  3.5333 |
| lpep_dropoff_datetime | 2025-05-01 |     18 |  0.0345 |

## Top Values (full-data, top 5)

| column                | top_5_values                                              |
|:----------------------|:----------------------------------------------------------|
| VendorID              | 2: 44358, 1: 6612, 6: 1162                                |
| store_and_fwd_flag    | N: 48862, <NULL>: 3188, Y: 82                             |
| RatecodeID            | 1.0: 46207, <NULL>: 3188, 5.0: 2379, 2.0: 145, 99.0: 114  |
| passenger_count       | 1.0: 41130, 2.0: 4342, <NULL>: 3188, 5.0: 1086, 6.0: 774  |
| mta_tax               | 0.5: 43268, 1.5: 6316, 0.0: 2417, -0.5: 121, 1.0: 10      |
| ehail_fee             | <NULL>: 52132                                             |
| improvement_surcharge | 1.0: 50587, 0.3: 1194, 0.0: 215, -1.0: 135, -0.3: 1       |
| payment_type          | 1.0: 36873, 2.0: 11665, <NULL>: 3188, 3.0: 288, 4.0: 118  |
| trip_type             | 1.0: 46577, <NULL>: 3195, 2.0: 2360                       |
| congestion_surcharge  | 0.0: 33378, 2.75: 15457, <NULL>: 3188, 2.5: 103, -2.75: 6 |
| cbd_congestion_fee    | 0.0: 47049, 0.75: 5081, -0.75: 2                          |

## Data Quality Signals

- Duplicate rows in full data: `0` / `52132`.
- Columns with >= 50% null in full data: `ehail_fee`.
- Near-constant columns in full data: `ehail_fee`.
- High-cardinality / ID-like columns: `lpep_pickup_datetime`, `lpep_dropoff_datetime`.
- Numeric columns containing negative values: `fare_amount`, `extra`, `mta_tax`, `tip_amount`, `improvement_surcharge`, `total_amount`, `congestion_surcharge`, `cbd_congestion_fee`.

## Data Preview

|   VendorID | lpep_pickup_datetime   | lpep_dropoff_datetime   | store_and_fwd_flag   |   RatecodeID |   PULocationID |   DOLocationID |   passenger_count |   trip_distance |   fare_amount |   extra |   mta_tax |   tip_amount |   tolls_amount |   ehail_fee |   improvement_surcharge |   total_amount |   payment_type |   trip_type |   congestion_surcharge |   cbd_congestion_fee |
|-----------:|:-----------------------|:------------------------|:---------------------|-------------:|---------------:|---------------:|------------------:|----------------:|--------------:|--------:|----------:|-------------:|---------------:|------------:|------------------------:|---------------:|---------------:|------------:|-----------------------:|---------------------:|
|          2 | 2025-04-01 00:36:05    | 2025-04-01 00:42:00     | N                    |            1 |             75 |             41 |                 1 |            1.37 |           8.6 |       1 |       0.5 |         1    |              0 |         nan |                       1 |          12.1  |              1 |           1 |                   0    |                    0 |
|          2 | 2025-04-01 00:10:24    | 2025-04-01 00:30:29     | N                    |            1 |             74 |            143 |                 1 |            3.99 |          21.9 |       1 |       0.5 |         5.43 |              0 |         nan |                       1 |          32.58 |              1 |           1 |                   2.75 |                    0 |
|          2 | 2025-04-01 00:13:12    | 2025-04-01 00:26:10     | N                    |            1 |            260 |            129 |                 1 |            2.37 |          14.9 |       1 |       0.5 |         0    |              0 |         nan |                       1 |          17.4  |              2 |           1 |                   0    |                    0 |
|          2 | 2025-04-01 00:15:37    | 2025-04-01 00:38:07     | N                    |            1 |            130 |              7 |                 1 |           10.4  |          42.2 |       1 |       0.5 |        11.18 |              0 |         nan |                       1 |          55.88 |              1 |           1 |                   0    |                    0 |
|          2 | 2025-04-01 00:14:27    | 2025-04-01 00:24:08     | N                    |            1 |            244 |            166 |                 2 |            2.98 |          14.9 |       1 |       0.5 |         0    |              0 |         nan |                       1 |          17.4  |              2 |           1 |                   0    |                    0 |
|          2 | 2025-04-01 00:31:57    | 2025-04-01 00:39:35     | N                    |            1 |             75 |             41 |                 1 |            1.68 |          10   |       1 |       0.5 |         2.5  |              0 |         nan |                       1 |          15    |              1 |           1 |                   0    |                    0 |
|          2 | 2025-03-31 20:58:45    | 2025-03-31 21:04:03     | N                    |            1 |            129 |            129 |                 1 |            0.54 |           6.5 |       1 |       0.5 |         5    |              0 |         nan |                       1 |          14    |              1 |           1 |                   0    |                    0 |
|          2 | 2025-04-01 00:15:27    | 2025-04-01 00:15:30     | N                    |            5 |            191 |            264 |                 1 |            0    |          20   |       0 |       0   |         4.2  |              0 |         nan |                       1 |          25.2  |              1 |           2 |                   0    |                    0 |
|          2 | 2025-04-01 00:38:40    | 2025-04-01 00:46:17     | N                    |            1 |            130 |            197 |                 1 |            2.04 |          11.4 |       1 |       0.5 |         2.78 |              0 |         nan |                       1 |          16.68 |              1 |           1 |                   0    |                    0 |
|          2 | 2025-04-01 00:04:36    | 2025-04-01 00:09:20     | N                    |            1 |             95 |             95 |                 1 |            0.73 |           6.5 |       1 |       0.5 |         1    |              0 |         nan |                       1 |          10    |              1 |           1 |                   0    |                    0 |
