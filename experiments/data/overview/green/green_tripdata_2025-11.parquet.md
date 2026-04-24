# Data Overview: green_tripdata_2025-11.parquet

## Dataset Summary

| metric       | value                                                                             |
|:-------------|:----------------------------------------------------------------------------------|
| file         | /root/Dev/DataGate/experiments/data/parquets/green/green_tripdata_2025-11.parquet |
| rows         | 46912                                                                             |
| columns      | 21                                                                                |
| row_groups   | 1                                                                                 |
| file_size_mb | 1.11                                                                              |
| rows_loaded  | 46912                                                                             |

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
| VendorID              | int32          |      46912 |      0 |   0.0000 |        3 |
| lpep_pickup_datetime  | datetime64[us] |      46912 |      0 |   0.0000 |    46123 |
| lpep_dropoff_datetime | datetime64[us] |      46912 |      0 |   0.0000 |    46108 |
| store_and_fwd_flag    | str            |      41343 |   5569 |  11.8712 |        2 |
| RatecodeID            | float64        |      41343 |   5569 |  11.8712 |        6 |
| PULocationID          | int32          |      46912 |      0 |   0.0000 |      233 |
| DOLocationID          | int32          |      46912 |      0 |   0.0000 |      249 |
| passenger_count       | float64        |      41343 |   5569 |  11.8712 |       10 |
| trip_distance         | float64        |      46912 |      0 |   0.0000 |     2075 |
| fare_amount           | float64        |      46912 |      0 |   0.0000 |     1496 |
| extra                 | float64        |      46912 |      0 |   0.0000 |       17 |
| mta_tax               | float64        |      46912 |      0 |   0.0000 |        5 |
| tip_amount            | float64        |      46912 |      0 |   0.0000 |     1450 |
| tolls_amount          | float64        |      46912 |      0 |   0.0000 |       27 |
| ehail_fee             | float64        |          0 |  46912 | 100.0000 |        0 |
| improvement_surcharge | float64        |      46912 |      0 |   0.0000 |        4 |
| total_amount          | float64        |      46912 |      0 |   0.0000 |     4926 |
| payment_type          | float64        |      41343 |   5569 |  11.8712 |        5 |
| trip_type             | float64        |      41342 |   5570 |  11.8733 |        2 |
| congestion_surcharge  | float64        |      41343 |   5569 |  11.8712 |        4 |
| cbd_congestion_fee    | float64        |      46912 |      0 |   0.0000 |        3 |

## Numeric Statistics (full-data)

| column                |       min |     p25 |   median |     mean |      p75 |         max |       std |
|:----------------------|----------:|--------:|---------:|---------:|---------:|------------:|----------:|
| VendorID              |    1.0000 |  2.0000 |   2.0000 |   2.2406 |   2.0000 |      6.0000 |    1.1696 |
| RatecodeID            |    1.0000 |  1.0000 |   1.0000 |   1.2452 |   1.0000 |     99.0000 |    1.0628 |
| PULocationID          |    1.0000 | 74.0000 |  75.0000 |  97.5218 | 116.0000 |    265.0000 |   56.6221 |
| DOLocationID          |    1.0000 | 75.0000 | 140.0000 | 143.0667 | 230.0000 |    265.0000 |   77.3624 |
| passenger_count       |    0.0000 |  1.0000 |   1.0000 |   1.2907 |   1.0000 |      9.0000 |    0.8979 |
| trip_distance         |    0.0000 |  1.2800 |   2.0700 |  27.5819 |   3.6600 | 172273.8000 | 1386.5789 |
| fare_amount           | -150.0000 |  9.0000 |  13.5000 |  17.2603 |  19.8000 |    990.0000 |   17.2847 |
| extra                 |   -2.5000 |  0.0000 |   0.0000 |   0.7963 |   1.0000 |     10.0000 |    1.3640 |
| mta_tax               |   -0.5000 |  0.5000 |   0.5000 |   0.5563 |   0.5000 |      1.5000 |    0.3195 |
| tip_amount            |   -0.9000 |  0.0000 |   2.0800 |   2.6293 |   3.9200 |    122.1000 |    3.4115 |
| tolls_amount          |    0.0000 |  0.0000 |   0.0000 |   0.2734 |   0.0000 |    108.0000 |    1.5128 |
| improvement_surcharge |   -1.0000 |  1.0000 |   1.0000 |   0.9306 |   1.0000 |      1.0000 |    0.2332 |
| total_amount          | -151.0000 | 14.8400 |  20.3000 |  25.1932 |  29.6200 |    991.0000 |   19.3123 |
| payment_type          |    1.0000 |  1.0000 |   1.0000 |   1.2462 |   1.0000 |      5.0000 |    0.4610 |
| trip_type             |    1.0000 |  1.0000 |   1.0000 |   1.0554 |   1.0000 |      2.0000 |    0.2288 |
| congestion_surcharge  |   -2.7500 |  0.0000 |   0.0000 |   0.8841 |   2.7500 |      2.7500 |    1.2851 |
| cbd_congestion_fee    |   -0.7500 |  0.0000 |   0.0000 |   0.0649 |   0.0000 |      0.7500 |    0.2111 |

## Datetime Coverage (full-data)

| column                | min_ts              | max_ts              | span             |
|:----------------------|:--------------------|:--------------------|:-----------------|
| lpep_pickup_datetime  | 2025-10-26 20:23:16 | 2025-12-01 20:29:00 | 36 days 00:05:44 |
| lpep_dropoff_datetime | 2025-10-26 20:31:18 | 2025-12-01 20:44:42 | 36 days 00:13:24 |

## Datetime Distribution by Day (full-data)

| column                | day        |   rows |   row_% |
|:----------------------|:-----------|-------:|--------:|
| lpep_pickup_datetime  | 2025-10-26 |      1 |  0.0021 |
| lpep_pickup_datetime  | 2025-10-27 |      1 |  0.0021 |
| lpep_pickup_datetime  | 2025-10-30 |      1 |  0.0021 |
| lpep_pickup_datetime  | 2025-10-31 |      5 |  0.0107 |
| lpep_pickup_datetime  | 2025-11-01 |   1465 |  3.1229 |
| lpep_pickup_datetime  | 2025-11-02 |   1295 |  2.7605 |
| lpep_pickup_datetime  | 2025-11-03 |   1642 |  3.5002 |
| lpep_pickup_datetime  | 2025-11-04 |   1470 |  3.1335 |
| lpep_pickup_datetime  | 2025-11-05 |   1804 |  3.8455 |
| lpep_pickup_datetime  | 2025-11-06 |   1862 |  3.9691 |
| lpep_pickup_datetime  | 2025-11-07 |   1645 |  3.5066 |
| lpep_pickup_datetime  | 2025-11-08 |   1398 |  2.9800 |
| lpep_pickup_datetime  | 2025-11-09 |   1228 |  2.6177 |
| lpep_pickup_datetime  | 2025-11-10 |   1729 |  3.6856 |
| lpep_pickup_datetime  | 2025-11-11 |   1590 |  3.3893 |
| lpep_pickup_datetime  | 2025-11-12 |   1686 |  3.5940 |
| lpep_pickup_datetime  | 2025-11-13 |   1821 |  3.8817 |
| lpep_pickup_datetime  | 2025-11-14 |   1726 |  3.6792 |
| lpep_pickup_datetime  | 2025-11-15 |   1431 |  3.0504 |
| lpep_pickup_datetime  | 2025-11-16 |   1391 |  2.9651 |
| lpep_pickup_datetime  | 2025-11-17 |   1764 |  3.7602 |
| lpep_pickup_datetime  | 2025-11-18 |   1773 |  3.7794 |
| lpep_pickup_datetime  | 2025-11-19 |   1810 |  3.8583 |
| lpep_pickup_datetime  | 2025-11-20 |   1932 |  4.1183 |
| lpep_pickup_datetime  | 2025-11-21 |   1810 |  3.8583 |
| lpep_pickup_datetime  | 2025-11-22 |   1330 |  2.8351 |
| lpep_pickup_datetime  | 2025-11-23 |   1280 |  2.7285 |
| lpep_pickup_datetime  | 2025-11-24 |   1724 |  3.6750 |
| lpep_pickup_datetime  | 2025-11-25 |   1861 |  3.9670 |
| lpep_pickup_datetime  | 2025-11-26 |   1506 |  3.2103 |
| lpep_pickup_datetime  | 2025-11-27 |   1035 |  2.2063 |
| lpep_pickup_datetime  | 2025-11-28 |   1178 |  2.5111 |
| lpep_pickup_datetime  | 2025-11-29 |   1307 |  2.7861 |
| lpep_pickup_datetime  | 2025-11-30 |   1398 |  2.9800 |
| lpep_pickup_datetime  | 2025-12-01 |     13 |  0.0277 |
| lpep_dropoff_datetime | 2025-10-26 |      1 |  0.0021 |
| lpep_dropoff_datetime | 2025-10-27 |      1 |  0.0021 |
| lpep_dropoff_datetime | 2025-10-30 |      1 |  0.0021 |
| lpep_dropoff_datetime | 2025-10-31 |      3 |  0.0064 |
| lpep_dropoff_datetime | 2025-11-01 |   1449 |  3.0888 |
| lpep_dropoff_datetime | 2025-11-02 |   1299 |  2.7690 |
| lpep_dropoff_datetime | 2025-11-03 |   1647 |  3.5108 |
| lpep_dropoff_datetime | 2025-11-04 |   1463 |  3.1186 |
| lpep_dropoff_datetime | 2025-11-05 |   1806 |  3.8498 |
| lpep_dropoff_datetime | 2025-11-06 |   1860 |  3.9649 |
| lpep_dropoff_datetime | 2025-11-07 |   1644 |  3.5044 |
| lpep_dropoff_datetime | 2025-11-08 |   1391 |  2.9651 |
| lpep_dropoff_datetime | 2025-11-09 |   1240 |  2.6432 |
| lpep_dropoff_datetime | 2025-11-10 |   1733 |  3.6942 |
| lpep_dropoff_datetime | 2025-11-11 |   1586 |  3.3808 |
| lpep_dropoff_datetime | 2025-11-12 |   1692 |  3.6068 |
| lpep_dropoff_datetime | 2025-11-13 |   1815 |  3.8689 |
| lpep_dropoff_datetime | 2025-11-14 |   1726 |  3.6792 |
| lpep_dropoff_datetime | 2025-11-15 |   1425 |  3.0376 |
| lpep_dropoff_datetime | 2025-11-16 |   1400 |  2.9843 |
| lpep_dropoff_datetime | 2025-11-17 |   1764 |  3.7602 |
| lpep_dropoff_datetime | 2025-11-18 |   1770 |  3.7730 |
| lpep_dropoff_datetime | 2025-11-19 |   1809 |  3.8562 |
| lpep_dropoff_datetime | 2025-11-20 |   1926 |  4.1056 |
| lpep_dropoff_datetime | 2025-11-21 |   1806 |  3.8498 |
| lpep_dropoff_datetime | 2025-11-22 |   1329 |  2.8330 |
| lpep_dropoff_datetime | 2025-11-23 |   1299 |  2.7690 |
| lpep_dropoff_datetime | 2025-11-24 |   1719 |  3.6643 |
| lpep_dropoff_datetime | 2025-11-25 |   1863 |  3.9713 |
| lpep_dropoff_datetime | 2025-11-26 |   1500 |  3.1975 |
| lpep_dropoff_datetime | 2025-11-27 |   1043 |  2.2233 |
| lpep_dropoff_datetime | 2025-11-28 |   1173 |  2.5004 |
| lpep_dropoff_datetime | 2025-11-29 |   1302 |  2.7754 |
| lpep_dropoff_datetime | 2025-11-30 |   1406 |  2.9971 |
| lpep_dropoff_datetime | 2025-12-01 |     21 |  0.0448 |

## Top Values (full-data, top 5)

| column                | top_5_values                                             |
|:----------------------|:---------------------------------------------------------|
| VendorID              | 2: 38655, 1: 4348, 6: 3909                               |
| store_and_fwd_flag    | N: 41217, <NULL>: 5569, Y: 126                           |
| RatecodeID            | 1.0: 38725, <NULL>: 5569, 5.0: 2432, 2.0: 112, 4.0: 53   |
| passenger_count       | 1.0: 33852, <NULL>: 5569, 2.0: 4707, 5.0: 954, 0.0: 612  |
| mta_tax               | 0.5: 39903, 1.5: 4131, 0.0: 2752, -0.5: 117, 1.0: 9      |
| ehail_fee             | <NULL>: 46912                                            |
| improvement_surcharge | 1.0: 42710, 0.3: 3630, 0.0: 430, -1.0: 142               |
| payment_type          | 1.0: 31628, 2.0: 9341, <NULL>: 5569, 3.0: 286, 4.0: 86   |
| trip_type             | 1.0: 39051, <NULL>: 5570, 2.0: 2291                      |
| congestion_surcharge  | 0.0: 28038, 2.75: 13275, <NULL>: 5569, 2.5: 24, -2.75: 6 |
| cbd_congestion_fee    | 0.0: 42845, 0.75: 4063, -0.75: 4                         |

## Data Quality Signals

- Duplicate rows in full data: `0` / `46912`.
- Columns with >= 50% null in full data: `ehail_fee`.
- Near-constant columns in full data: `ehail_fee`.
- High-cardinality / ID-like columns: `lpep_pickup_datetime`, `lpep_dropoff_datetime`.
- Numeric columns containing negative values: `fare_amount`, `extra`, `mta_tax`, `tip_amount`, `improvement_surcharge`, `total_amount`, `congestion_surcharge`, `cbd_congestion_fee`.

## Data Preview

|   VendorID | lpep_pickup_datetime   | lpep_dropoff_datetime   | store_and_fwd_flag   |   RatecodeID |   PULocationID |   DOLocationID |   passenger_count |   trip_distance |   fare_amount |   extra |   mta_tax |   tip_amount |   tolls_amount |   ehail_fee |   improvement_surcharge |   total_amount |   payment_type |   trip_type |   congestion_surcharge |   cbd_congestion_fee |
|-----------:|:-----------------------|:------------------------|:---------------------|-------------:|---------------:|---------------:|------------------:|----------------:|--------------:|--------:|----------:|-------------:|---------------:|------------:|------------------------:|---------------:|---------------:|------------:|-----------------------:|---------------------:|
|          2 | 2025-11-01 00:34:48    | 2025-11-01 00:41:39     | N                    |            1 |             74 |             42 |                 1 |            0.74 |           7.2 |    1    |       0.5 |         1.94 |              0 |         nan |                       1 |          11.64 |              1 |           1 |                   0    |                 0    |
|          2 | 2025-11-01 00:18:52    | 2025-11-01 00:24:27     | N                    |            1 |             74 |             42 |                 2 |            0.95 |           7.2 |    1    |       0.5 |         0    |              0 |         nan |                       1 |           9.7  |              2 |           1 |                   0    |                 0    |
|          2 | 2025-11-01 01:03:14    | 2025-11-01 01:15:24     | N                    |            1 |             83 |            160 |                 1 |            2.19 |          13.5 |    1    |       0.5 |         5    |              0 |         nan |                       1 |          21    |              1 |           1 |                   0    |                 0    |
|          2 | 2025-11-01 00:10:57    | 2025-11-01 00:24:53     | N                    |            1 |            166 |            127 |                 1 |            5.44 |          24.7 |    1    |       0.5 |         0.5  |              0 |         nan |                       1 |          27.7  |              1 |           1 |                   0    |                 0    |
|          1 | 2025-11-01 00:03:48    | 2025-11-01 00:19:38     | N                    |            1 |            166 |            262 |                 1 |            3.2  |          18.4 |    3.75 |       1.5 |         1    |              0 |         nan |                       1 |          24.65 |              1 |           1 |                   2.75 |                 0    |
|          1 | 2025-11-01 00:42:13    | 2025-11-01 01:04:50     | N                    |            1 |            112 |             48 |                 2 |            5.1  |          26.8 |    4.5  |       1.5 |         6.55 |              0 |         nan |                       1 |          39.35 |              1 |           1 |                   2.75 |                 0.75 |
|          2 | 2025-11-01 00:05:41    | 2025-11-01 00:39:20     | N                    |            1 |             83 |             87 |                 1 |            9.8  |          43.6 |    1    |       0.5 |         9.92 |              0 |         nan |                       1 |          59.52 |              1 |           1 |                   2.75 |                 0.75 |
|          2 | 2025-11-01 00:42:14    | 2025-11-01 01:13:20     | N                    |            1 |             66 |            233 |                 1 |            5.01 |          28.9 |    1    |       0.5 |         6.98 |              0 |         nan |                       1 |          41.88 |              1 |           1 |                   2.75 |                 0.75 |
|          2 | 2025-11-01 00:03:08    | 2025-11-01 00:06:27     | N                    |            1 |            223 |            223 |                 1 |            0.63 |           5.1 |    1    |       0.5 |         1.52 |              0 |         nan |                       1 |           9.12 |              1 |           1 |                   0    |                 0    |
|          2 | 2025-11-01 00:56:33    | 2025-11-01 01:01:34     | N                    |            1 |            130 |            130 |                 1 |            1.15 |           7.9 |    1    |       0.5 |         0    |              0 |         nan |                       1 |          10.4  |              2 |           1 |                   0    |                 0    |
