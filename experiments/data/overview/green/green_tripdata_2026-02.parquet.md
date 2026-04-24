# Data Overview: green_tripdata_2026-02.parquet

## Dataset Summary

| metric       | value                                                                             |
|:-------------|:----------------------------------------------------------------------------------|
| file         | /root/Dev/DataGate/experiments/data/parquets/green/green_tripdata_2026-02.parquet |
| rows         | 37373                                                                             |
| columns      | 21                                                                                |
| row_groups   | 1                                                                                 |
| file_size_mb | 0.88                                                                              |
| rows_loaded  | 37373                                                                             |

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
| VendorID              | int32          |      37373 |      0 |   0.0000 |        3 |
| lpep_pickup_datetime  | datetime64[us] |      37373 |      0 |   0.0000 |    36808 |
| lpep_dropoff_datetime | datetime64[us] |      37373 |      0 |   0.0000 |    36803 |
| store_and_fwd_flag    | str            |      31986 |   5387 |  14.4141 |        2 |
| RatecodeID            | float64        |      31986 |   5387 |  14.4141 |        6 |
| PULocationID          | int32          |      37373 |      0 |   0.0000 |      231 |
| DOLocationID          | int32          |      37373 |      0 |   0.0000 |      245 |
| passenger_count       | float64        |      31986 |   5387 |  14.4141 |        9 |
| trip_distance         | float64        |      37373 |      0 |   0.0000 |     1847 |
| fare_amount           | float64        |      37373 |      0 |   0.0000 |     1394 |
| extra                 | float64        |      37373 |      0 |   0.0000 |       15 |
| mta_tax               | float64        |      37373 |      0 |   0.0000 |        4 |
| tip_amount            | float64        |      37373 |      0 |   0.0000 |     1391 |
| tolls_amount          | float64        |      37373 |      0 |   0.0000 |       24 |
| ehail_fee             | float64        |          0 |  37373 | 100.0000 |        0 |
| improvement_surcharge | float64        |      37373 |      0 |   0.0000 |        5 |
| total_amount          | float64        |      37373 |      0 |   0.0000 |     4406 |
| payment_type          | float64        |      31986 |   5387 |  14.4141 |        4 |
| trip_type             | float64        |      31985 |   5388 |  14.4168 |        2 |
| congestion_surcharge  | float64        |      31986 |   5387 |  14.4141 |        3 |
| cbd_congestion_fee    | float64        |      37373 |      0 |   0.0000 |        2 |

## Numeric Statistics (full-data)

| column                |       min |     p25 |   median |     mean |      p75 |         max |       std |
|:----------------------|----------:|--------:|---------:|---------:|---------:|------------:|----------:|
| VendorID              |    1.0000 |  2.0000 |   2.0000 |   2.3044 |   2.0000 |      6.0000 |    1.2658 |
| RatecodeID            |    1.0000 |  1.0000 |   1.0000 |   1.2080 |   1.0000 |     99.0000 |    1.0312 |
| PULocationID          |    3.0000 | 74.0000 |  75.0000 |  96.6663 | 102.0000 |    265.0000 |   55.5285 |
| DOLocationID          |    1.0000 | 74.0000 | 138.0000 | 141.1427 | 225.0000 |    265.0000 |   77.0639 |
| passenger_count       |    0.0000 |  1.0000 |   1.0000 |   1.3148 |   1.0000 |      8.0000 |    0.9942 |
| trip_distance         |    0.0000 |  1.2000 |   1.9600 |  21.4949 |   3.4600 | 117566.0000 | 1160.3487 |
| fare_amount           | -115.7000 |  8.6000 |  13.5000 |  16.2165 |  19.1000 |    399.9000 |   14.8192 |
| extra                 |   -5.0000 |  0.0000 |   0.0000 |   0.8241 |   1.0000 |      7.5000 |    1.3545 |
| mta_tax               |   -0.5000 |  0.5000 |   0.5000 |   0.5614 |   0.5000 |      1.5000 |    0.3202 |
| tip_amount            |   -1.4000 |  0.0000 |   2.0000 |   2.5269 |   3.7800 |    232.5000 |    3.8292 |
| tolls_amount          |  -24.5000 |  0.0000 |   0.0000 |   0.2751 |   0.0000 |     29.7100 |    1.4866 |
| improvement_surcharge |   -1.0000 |  1.0000 |   1.0000 |   0.9180 |   1.0000 |      1.0000 |    0.2488 |
| total_amount          | -144.2000 | 14.8800 |  20.0000 |  24.2490 |  28.7500 |    424.9000 |   17.1299 |
| payment_type          |    1.0000 |  1.0000 |   1.0000 |   1.2589 |   1.0000 |      4.0000 |    0.4727 |
| trip_type             |    1.0000 |  1.0000 |   1.0000 |   1.0470 |   1.0000 |      2.0000 |    0.2116 |
| congestion_surcharge  |   -2.7500 |  0.0000 |   0.0000 |   0.8041 |   2.7500 |      2.7500 |    1.2515 |
| cbd_congestion_fee    |    0.0000 |  0.0000 |   0.0000 |   0.0522 |   0.0000 |      0.7500 |    0.1909 |

## Datetime Coverage (full-data)

| column                | min_ts              | max_ts              | span             |
|:----------------------|:--------------------|:--------------------|:-----------------|
| lpep_pickup_datetime  | 2026-01-26 23:38:06 | 2026-03-01 09:48:53 | 33 days 10:10:47 |
| lpep_dropoff_datetime | 2026-01-26 23:53:46 | 2026-03-01 21:20:11 | 33 days 21:26:25 |

## Datetime Distribution by Day (full-data)

| column                | day        |   rows |   row_% |
|:----------------------|:-----------|-------:|--------:|
| lpep_pickup_datetime  | 2026-01-26 |      1 |  0.0027 |
| lpep_pickup_datetime  | 2026-01-27 |      2 |  0.0054 |
| lpep_pickup_datetime  | 2026-01-28 |      2 |  0.0054 |
| lpep_pickup_datetime  | 2026-01-30 |      1 |  0.0027 |
| lpep_pickup_datetime  | 2026-01-31 |      2 |  0.0054 |
| lpep_pickup_datetime  | 2026-02-01 |   1073 |  2.8711 |
| lpep_pickup_datetime  | 2026-02-02 |   1518 |  4.0618 |
| lpep_pickup_datetime  | 2026-02-03 |   1549 |  4.1447 |
| lpep_pickup_datetime  | 2026-02-04 |   1575 |  4.2143 |
| lpep_pickup_datetime  | 2026-02-05 |   1590 |  4.2544 |
| lpep_pickup_datetime  | 2026-02-06 |   1573 |  4.2089 |
| lpep_pickup_datetime  | 2026-02-07 |   1169 |  3.1279 |
| lpep_pickup_datetime  | 2026-02-08 |   1054 |  2.8202 |
| lpep_pickup_datetime  | 2026-02-09 |   1550 |  4.1474 |
| lpep_pickup_datetime  | 2026-02-10 |   1480 |  3.9601 |
| lpep_pickup_datetime  | 2026-02-11 |   1585 |  4.2410 |
| lpep_pickup_datetime  | 2026-02-12 |   1790 |  4.7896 |
| lpep_pickup_datetime  | 2026-02-13 |   1553 |  4.1554 |
| lpep_pickup_datetime  | 2026-02-14 |   1163 |  3.1119 |
| lpep_pickup_datetime  | 2026-02-15 |   1059 |  2.8336 |
| lpep_pickup_datetime  | 2026-02-16 |    971 |  2.5981 |
| lpep_pickup_datetime  | 2026-02-17 |   1373 |  3.6738 |
| lpep_pickup_datetime  | 2026-02-18 |   1519 |  4.0644 |
| lpep_pickup_datetime  | 2026-02-19 |   1530 |  4.0939 |
| lpep_pickup_datetime  | 2026-02-20 |   1409 |  3.7701 |
| lpep_pickup_datetime  | 2026-02-21 |   1123 |  3.0048 |
| lpep_pickup_datetime  | 2026-02-22 |    834 |  2.2316 |
| lpep_pickup_datetime  | 2026-02-23 |    146 |  0.3907 |
| lpep_pickup_datetime  | 2026-02-24 |   1301 |  3.4811 |
| lpep_pickup_datetime  | 2026-02-25 |   1476 |  3.9494 |
| lpep_pickup_datetime  | 2026-02-26 |   1599 |  4.2785 |
| lpep_pickup_datetime  | 2026-02-27 |   1561 |  4.1768 |
| lpep_pickup_datetime  | 2026-02-28 |   1239 |  3.3152 |
| lpep_pickup_datetime  | 2026-03-01 |      3 |  0.0080 |
| lpep_dropoff_datetime | 2026-01-26 |      1 |  0.0027 |
| lpep_dropoff_datetime | 2026-01-27 |      2 |  0.0054 |
| lpep_dropoff_datetime | 2026-01-28 |      2 |  0.0054 |
| lpep_dropoff_datetime | 2026-01-30 |      1 |  0.0027 |
| lpep_dropoff_datetime | 2026-01-31 |      2 |  0.0054 |
| lpep_dropoff_datetime | 2026-02-01 |   1066 |  2.8523 |
| lpep_dropoff_datetime | 2026-02-02 |   1516 |  4.0564 |
| lpep_dropoff_datetime | 2026-02-03 |   1552 |  4.1527 |
| lpep_dropoff_datetime | 2026-02-04 |   1577 |  4.2196 |
| lpep_dropoff_datetime | 2026-02-05 |   1587 |  4.2464 |
| lpep_dropoff_datetime | 2026-02-06 |   1567 |  4.1929 |
| lpep_dropoff_datetime | 2026-02-07 |   1171 |  3.1333 |
| lpep_dropoff_datetime | 2026-02-08 |   1059 |  2.8336 |
| lpep_dropoff_datetime | 2026-02-09 |   1546 |  4.1367 |
| lpep_dropoff_datetime | 2026-02-10 |   1486 |  3.9761 |
| lpep_dropoff_datetime | 2026-02-11 |   1582 |  4.2330 |
| lpep_dropoff_datetime | 2026-02-12 |   1784 |  4.7735 |
| lpep_dropoff_datetime | 2026-02-13 |   1550 |  4.1474 |
| lpep_dropoff_datetime | 2026-02-14 |   1169 |  3.1279 |
| lpep_dropoff_datetime | 2026-02-15 |   1060 |  2.8363 |
| lpep_dropoff_datetime | 2026-02-16 |    973 |  2.6035 |
| lpep_dropoff_datetime | 2026-02-17 |   1372 |  3.6711 |
| lpep_dropoff_datetime | 2026-02-18 |   1517 |  4.0591 |
| lpep_dropoff_datetime | 2026-02-19 |   1521 |  4.0698 |
| lpep_dropoff_datetime | 2026-02-20 |   1418 |  3.7942 |
| lpep_dropoff_datetime | 2026-02-21 |   1121 |  2.9995 |
| lpep_dropoff_datetime | 2026-02-22 |    842 |  2.2530 |
| lpep_dropoff_datetime | 2026-02-23 |    149 |  0.3987 |
| lpep_dropoff_datetime | 2026-02-24 |   1294 |  3.4624 |
| lpep_dropoff_datetime | 2026-02-25 |   1479 |  3.9574 |
| lpep_dropoff_datetime | 2026-02-26 |   1596 |  4.2705 |
| lpep_dropoff_datetime | 2026-02-27 |   1558 |  4.1688 |
| lpep_dropoff_datetime | 2026-02-28 |   1236 |  3.3072 |
| lpep_dropoff_datetime | 2026-03-01 |     17 |  0.0455 |

## Top Values (full-data, top 5)

| column                | top_5_values                                            |
|:----------------------|:--------------------------------------------------------|
| VendorID              | 2: 30069, 6: 3736, 1: 3568                              |
| store_and_fwd_flag    | N: 31952, <NULL>: 5387, Y: 34                           |
| RatecodeID            | 1.0: 30270, <NULL>: 5387, 5.0: 1580, 2.0: 77, 4.0: 41   |
| passenger_count       | 1.0: 26293, <NULL>: 5387, 2.0: 3242, 5.0: 860, 6.0: 588 |
| extra                 | 0.0: 23567, 2.5: 6523, 1.0: 5147, 2.75: 611, 5.0: 527   |
| mta_tax               | 0.5: 31909, 1.5: 3383, 0.0: 1989, -0.5: 92              |
| ehail_fee             | <NULL>: 37373                                           |
| improvement_surcharge | 1.0: 33399, 0.3: 3390, 0.0: 477, -1.0: 106, -0.3: 1     |
| payment_type          | 1.0: 24119, 2.0: 7541, <NULL>: 5387, 3.0: 237, 4.0: 89  |
| trip_type             | 1.0: 30483, <NULL>: 5388, 2.0: 1502                     |
| congestion_surcharge  | 0.0: 22627, 2.75: 9356, <NULL>: 5387, -2.75: 3          |
| cbd_congestion_fee    | 0.0: 34772, 0.75: 2601                                  |

## Data Quality Signals

- Duplicate rows in full data: `0` / `37373`.
- Columns with >= 50% null in full data: `ehail_fee`.
- Near-constant columns in full data: `ehail_fee`.
- High-cardinality / ID-like columns: `lpep_pickup_datetime`, `lpep_dropoff_datetime`.
- Numeric columns containing negative values: `fare_amount`, `extra`, `mta_tax`, `tip_amount`, `tolls_amount`, `improvement_surcharge`, `total_amount`, `congestion_surcharge`.

## Data Preview

|   VendorID | lpep_pickup_datetime   | lpep_dropoff_datetime   | store_and_fwd_flag   |   RatecodeID |   PULocationID |   DOLocationID |   passenger_count |   trip_distance |   fare_amount |   extra |   mta_tax |   tip_amount |   tolls_amount |   ehail_fee |   improvement_surcharge |   total_amount |   payment_type |   trip_type |   congestion_surcharge |   cbd_congestion_fee |
|-----------:|:-----------------------|:------------------------|:---------------------|-------------:|---------------:|---------------:|------------------:|----------------:|--------------:|--------:|----------:|-------------:|---------------:|------------:|------------------------:|---------------:|---------------:|------------:|-----------------------:|---------------------:|
|          2 | 2026-02-01 00:58:25    | 2026-02-01 01:03:26     | N                    |            1 |             82 |            129 |                 1 |            0.5  |           6.5 |    1    |       0.5 |         1.8  |              0 |         nan |                       1 |          10.8  |              1 |           1 |                   0    |                 0    |
|          2 | 2026-02-01 00:05:50    | 2026-02-01 00:13:19     | N                    |            1 |             33 |             65 |                 1 |            1.08 |           9.3 |    1    |       0.5 |         2.95 |              0 |         nan |                       1 |          14.75 |              1 |           1 |                   0    |                 0    |
|          1 | 2026-02-01 00:45:54    | 2026-02-01 01:28:27     | N                    |            5 |            226 |            143 |                 1 |            5.2  |          75   |    0.75 |       0   |        22.7  |              0 |         nan |                       0 |          98.45 |              1 |           2 |                   0    |                 0.75 |
|          2 | 2026-02-01 00:06:38    | 2026-02-01 00:15:56     | N                    |            1 |             74 |            235 |                 1 |            4.7  |          20.5 |    1    |       0.5 |         0    |              0 |         nan |                       1 |          23    |              2 |           1 |                   0    |                 0    |
|          2 | 2026-02-01 00:37:31    | 2026-02-01 00:51:10     | N                    |            1 |            120 |            119 |                 1 |            2.47 |          16.3 |    1    |       0.5 |         0    |              0 |         nan |                       1 |          18.8  |              2 |           1 |                   0    |                 0    |
|          2 | 2026-02-01 00:03:26    | 2026-02-01 00:09:43     | N                    |            1 |             75 |             74 |                 1 |            1.44 |           8.6 |    1    |       0.5 |         2.22 |              0 |         nan |                       1 |          13.32 |              1 |           1 |                   0    |                 0    |
|          2 | 2026-02-01 00:11:26    | 2026-02-01 00:34:43     | N                    |            1 |             40 |            256 |                 2 |            6.25 |          30.3 |    1    |       0.5 |         3.94 |              0 |         nan |                       1 |          36.74 |              1 |           1 |                   0    |                 0    |
|          2 | 2026-02-01 00:41:26    | 2026-02-01 00:57:44     | N                    |            1 |            256 |             25 |                 2 |            3.94 |          20.5 |    1    |       0.5 |         4.6  |              0 |         nan |                       1 |          27.6  |              1 |           1 |                   0    |                 0    |
|          2 | 2026-02-01 00:35:20    | 2026-02-01 00:43:48     | N                    |            1 |             74 |            263 |                 1 |            2.03 |          11.4 |    1    |       0.5 |         3.33 |              0 |         nan |                       1 |          19.98 |              1 |           1 |                   2.75 |                 0    |
|          2 | 2026-02-01 00:12:51    | 2026-02-01 00:15:05     | N                    |            1 |            223 |            223 |                 1 |            0.42 |           4.4 |    1    |       0.5 |         1.38 |              0 |         nan |                       1 |           8.28 |              1 |           1 |                   0    |                 0    |
