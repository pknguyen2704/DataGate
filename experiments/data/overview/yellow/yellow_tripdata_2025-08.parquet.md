# Data Overview: yellow_tripdata_2025-08.parquet

## Dataset Summary

| metric       | value                                                                               |
|:-------------|:------------------------------------------------------------------------------------|
| file         | /root/Dev/DataGate/experiments/data/parquets/yellow/yellow_tripdata_2025-08.parquet |
| rows         | 3574091                                                                             |
| columns      | 20                                                                                  |
| row_groups   | 4                                                                                   |
| file_size_mb | 59.41                                                                               |
| rows_loaded  | 3574091                                                                             |

## Schema

| column                | parquet_type   | nullable   |
|:----------------------|:---------------|:-----------|
| VendorID              | int32          | True       |
| tpep_pickup_datetime  | timestamp[us]  | True       |
| tpep_dropoff_datetime | timestamp[us]  | True       |
| passenger_count       | int64          | True       |
| trip_distance         | double         | True       |
| RatecodeID            | int64          | True       |
| store_and_fwd_flag    | large_string   | True       |
| PULocationID          | int32          | True       |
| DOLocationID          | int32          | True       |
| payment_type          | int64          | True       |
| fare_amount           | double         | True       |
| extra                 | double         | True       |
| mta_tax               | double         | True       |
| tip_amount            | double         | True       |
| tolls_amount          | double         | True       |
| improvement_surcharge | double         | True       |
| total_amount          | double         | True       |
| congestion_surcharge  | double         | True       |
| Airport_fee           | double         | True       |
| cbd_congestion_fee    | double         | True       |

## Column Health (full-data)

| column                | dtype          |   non_null |   null |   null_% |   unique |
|:----------------------|:---------------|-----------:|-------:|---------:|---------:|
| VendorID              | int32          |    3574091 |      0 |   0.0000 |        4 |
| tpep_pickup_datetime  | datetime64[us] |    3574091 |      0 |   0.0000 |  1759406 |
| tpep_dropoff_datetime | datetime64[us] |    3574091 |      0 |   0.0000 |  1759763 |
| passenger_count       | float64        |    2687857 | 886234 |  24.7961 |       10 |
| trip_distance         | float64        |    3574091 |      0 |   0.0000 |     5168 |
| RatecodeID            | float64        |    2687857 | 886234 |  24.7961 |        7 |
| store_and_fwd_flag    | str            |    2687857 | 886234 |  24.7961 |        2 |
| PULocationID          | int32          |    3574091 |      0 |   0.0000 |      260 |
| DOLocationID          | int32          |    3574091 |      0 |   0.0000 |      260 |
| payment_type          | int64          |    3574091 |      0 |   0.0000 |        5 |
| fare_amount           | float64        |    3574091 |      0 |   0.0000 |    12674 |
| extra                 | float64        |    3574091 |      0 |   0.0000 |       72 |
| mta_tax               | float64        |    3574091 |      0 |   0.0000 |        8 |
| tip_amount            | float64        |    3574091 |      0 |   0.0000 |     4559 |
| tolls_amount          | float64        |    3574091 |      0 |   0.0000 |     1330 |
| improvement_surcharge | float64        |    3574091 |      0 |   0.0000 |        4 |
| total_amount          | float64        |    3574091 |      0 |   0.0000 |    23760 |
| congestion_surcharge  | float64        |    2687857 | 886234 |  24.7961 |        4 |
| Airport_fee           | float64        |    2687857 | 886234 |  24.7961 |        6 |
| cbd_congestion_fee    | float64        |    3574091 |      0 |   0.0000 |        3 |

## Numeric Statistics (full-data)

| column                |        min |      p25 |   median |     mean |      p75 |         max |      std |
|:----------------------|-----------:|---------:|---------:|---------:|---------:|------------:|---------:|
| VendorID              |     1.0000 |   2.0000 |   2.0000 |   1.8853 |   2.0000 |      7.0000 |   0.7161 |
| passenger_count       |     0.0000 |   1.0000 |   1.0000 |   1.3304 |   1.0000 |      9.0000 |   0.7628 |
| trip_distance         |     0.0000 |   1.1000 |   2.0000 |   7.0894 |   4.2600 | 274082.3800 | 665.3595 |
| RatecodeID            |     1.0000 |   1.0000 |   1.0000 |   3.6919 |   1.0000 |     99.0000 |  15.6395 |
| PULocationID          |     1.0000 | 113.0000 | 161.0000 | 158.1166 | 230.0000 |    265.0000 |  66.3968 |
| DOLocationID          |     1.0000 | 100.0000 | 161.0000 | 157.8169 | 231.0000 |    265.0000 |  71.0344 |
| payment_type          |     0.0000 |   1.0000 |   1.0000 |   0.9608 |   1.0000 |      4.0000 |   0.8061 |
| fare_amount           | -1143.3000 |   8.6000 |  13.5000 |  18.0953 |  22.6000 |   2092.5000 |  20.9394 |
| extra                 |    -7.5000 |   0.0000 |   0.0000 |   1.1091 |   2.5000 |     15.7500 |   1.8169 |
| mta_tax               |    -0.5000 |   0.5000 |   0.5000 |   0.4711 |   0.5000 |     10.5000 |   0.1546 |
| tip_amount            |   -85.2900 |   0.0000 |   2.0000 |   2.7172 |   3.8500 |    500.0000 |   4.0369 |
| tolls_amount          |   -90.0000 |   0.0000 |   0.0000 |   0.5482 |   0.0000 |    116.0500 |   2.2366 |
| improvement_surcharge |    -1.0000 |   1.0000 |   1.0000 |   0.9362 |   1.0000 |      1.0000 |   0.3208 |
| total_amount          | -1151.2300 |  15.1600 |  20.7000 |  26.3888 |  30.2800 |   2123.4400 |  25.2004 |
| congestion_surcharge  |    -2.5000 |   2.5000 |   2.5000 |   2.0970 |   2.5000 |      2.5000 |   1.0563 |
| Airport_fee           |    -1.7500 |   0.0000 |   0.0000 |   0.1688 |   0.0000 |      6.7500 |   0.5725 |
| cbd_congestion_fee    |    -0.7500 |   0.0000 |   0.7500 |   0.5287 |   0.7500 |      0.7500 |   0.3650 |

## Datetime Coverage (full-data)

| column                | min_ts              | max_ts              | span               |
|:----------------------|:--------------------|:--------------------|:-------------------|
| tpep_pickup_datetime  | 2009-01-01 12:52:15 | 2025-09-01 00:00:29 | 6086 days 11:08:14 |
| tpep_dropoff_datetime | 2009-01-01 13:12:15 | 2025-09-02 08:17:29 | 6087 days 19:05:14 |

## Datetime Distribution by Day (full-data)

| column                | day        |   rows |   row_% |
|:----------------------|:-----------|-------:|--------:|
| tpep_pickup_datetime  | 2009-01-01 |      1 |  0.0000 |
| tpep_pickup_datetime  | 2025-07-31 |     15 |  0.0004 |
| tpep_pickup_datetime  | 2025-08-01 | 123253 |  3.4485 |
| tpep_pickup_datetime  | 2025-08-02 | 128651 |  3.5995 |
| tpep_pickup_datetime  | 2025-08-03 | 110831 |  3.1010 |
| tpep_pickup_datetime  | 2025-08-04 | 105176 |  2.9427 |
| tpep_pickup_datetime  | 2025-08-05 | 117583 |  3.2899 |
| tpep_pickup_datetime  | 2025-08-06 | 126842 |  3.5489 |
| tpep_pickup_datetime  | 2025-08-07 | 121674 |  3.4043 |
| tpep_pickup_datetime  | 2025-08-08 | 115538 |  3.2327 |
| tpep_pickup_datetime  | 2025-08-09 | 114880 |  3.2142 |
| tpep_pickup_datetime  | 2025-08-10 | 102769 |  2.8754 |
| tpep_pickup_datetime  | 2025-08-11 |  99484 |  2.7835 |
| tpep_pickup_datetime  | 2025-08-12 | 114599 |  3.2064 |
| tpep_pickup_datetime  | 2025-08-13 | 134000 |  3.7492 |
| tpep_pickup_datetime  | 2025-08-14 | 123193 |  3.4468 |
| tpep_pickup_datetime  | 2025-08-15 | 118200 |  3.3071 |
| tpep_pickup_datetime  | 2025-08-16 | 121365 |  3.3957 |
| tpep_pickup_datetime  | 2025-08-17 | 115203 |  3.2233 |
| tpep_pickup_datetime  | 2025-08-18 |  94785 |  2.6520 |
| tpep_pickup_datetime  | 2025-08-19 | 107047 |  2.9951 |
| tpep_pickup_datetime  | 2025-08-20 | 132182 |  3.6983 |
| tpep_pickup_datetime  | 2025-08-21 | 114532 |  3.2045 |
| tpep_pickup_datetime  | 2025-08-22 | 113785 |  3.1836 |
| tpep_pickup_datetime  | 2025-08-23 | 126686 |  3.5446 |
| tpep_pickup_datetime  | 2025-08-24 | 112316 |  3.1425 |
| tpep_pickup_datetime  | 2025-08-25 |  99132 |  2.7736 |
| tpep_pickup_datetime  | 2025-08-26 | 107701 |  3.0134 |
| tpep_pickup_datetime  | 2025-08-27 | 113712 |  3.1816 |
| tpep_pickup_datetime  | 2025-08-28 | 116732 |  3.2661 |
| tpep_pickup_datetime  | 2025-08-29 | 113683 |  3.1808 |
| tpep_pickup_datetime  | 2025-08-30 | 117063 |  3.2753 |
| tpep_pickup_datetime  | 2025-08-31 | 111477 |  3.1190 |
| tpep_pickup_datetime  | 2025-09-01 |      1 |  0.0000 |
| tpep_dropoff_datetime | 2009-01-01 |      1 |  0.0000 |
| tpep_dropoff_datetime | 2025-07-31 |      1 |  0.0000 |
| tpep_dropoff_datetime | 2025-08-01 | 121093 |  3.3881 |
| tpep_dropoff_datetime | 2025-08-02 | 128795 |  3.6036 |
| tpep_dropoff_datetime | 2025-08-03 | 111955 |  3.1324 |
| tpep_dropoff_datetime | 2025-08-04 | 105189 |  2.9431 |
| tpep_dropoff_datetime | 2025-08-05 | 117610 |  3.2906 |
| tpep_dropoff_datetime | 2025-08-06 | 126666 |  3.5440 |
| tpep_dropoff_datetime | 2025-08-07 | 121374 |  3.3959 |
| tpep_dropoff_datetime | 2025-08-08 | 115036 |  3.2186 |
| tpep_dropoff_datetime | 2025-08-09 | 114770 |  3.2112 |
| tpep_dropoff_datetime | 2025-08-10 | 103886 |  2.9066 |
| tpep_dropoff_datetime | 2025-08-11 |  99572 |  2.7859 |
| tpep_dropoff_datetime | 2025-08-12 | 114481 |  3.2031 |
| tpep_dropoff_datetime | 2025-08-13 | 133771 |  3.7428 |
| tpep_dropoff_datetime | 2025-08-14 | 122915 |  3.4391 |
| tpep_dropoff_datetime | 2025-08-15 | 117725 |  3.2938 |
| tpep_dropoff_datetime | 2025-08-16 | 121265 |  3.3929 |
| tpep_dropoff_datetime | 2025-08-17 | 116248 |  3.2525 |
| tpep_dropoff_datetime | 2025-08-18 |  94906 |  2.6554 |
| tpep_dropoff_datetime | 2025-08-19 | 106939 |  2.9921 |
| tpep_dropoff_datetime | 2025-08-20 | 132098 |  3.6960 |
| tpep_dropoff_datetime | 2025-08-21 | 114171 |  3.1944 |
| tpep_dropoff_datetime | 2025-08-22 | 113202 |  3.1673 |
| tpep_dropoff_datetime | 2025-08-23 | 126478 |  3.5387 |
| tpep_dropoff_datetime | 2025-08-24 | 113495 |  3.1755 |
| tpep_dropoff_datetime | 2025-08-25 |  99274 |  2.7776 |
| tpep_dropoff_datetime | 2025-08-26 | 107390 |  3.0047 |
| tpep_dropoff_datetime | 2025-08-27 | 113409 |  3.1731 |
| tpep_dropoff_datetime | 2025-08-28 | 116751 |  3.2666 |
| tpep_dropoff_datetime | 2025-08-29 | 113349 |  3.1714 |
| tpep_dropoff_datetime | 2025-08-30 | 116929 |  3.2716 |
| tpep_dropoff_datetime | 2025-08-31 | 111856 |  3.1296 |
| tpep_dropoff_datetime | 2025-09-01 |   1490 |  0.0417 |
| tpep_dropoff_datetime | 2025-09-02 |      1 |  0.0000 |

## Top Values (full-data, top 5)

| column                | top_5_values                                                         |
|:----------------------|:---------------------------------------------------------------------|
| VendorID              | 2: 2867667, 1: 656568, 7: 47276, 6: 2580                             |
| passenger_count       | 1.0: 2084772, <NULL>: 886234, 2.0: 385427, 3.0: 104083, 4.0: 79650   |
| RatecodeID            | 1.0: 2446064, <NULL>: 886234, 2.0: 102947, 99.0: 70383, 5.0: 43088   |
| store_and_fwd_flag    | N: 2683298, <NULL>: 886234, Y: 4559                                  |
| payment_type          | 1: 2182738, 0: 886234, 2: 370677, 4: 106641, 3: 27801                |
| mta_tax               | 0.5: 3439488, -0.5: 72442, 0.0: 62017, 1.0: 136, 10.5: 4             |
| improvement_surcharge | 1.0: 3422798, -1.0: 77462, 0.0: 71264, 0.3: 2567                     |
| congestion_surcharge  | 2.5: 2312777, <NULL>: 886234, 0.0: 316869, -2.5: 58210, 1.0: 1       |
| Airport_fee           | 0.0: 2396519, <NULL>: 886234, 1.75: 271359, -1.75: 18277, 6.75: 1361 |
| cbd_congestion_fee    | 0.75: 2570870, 0.0: 951715, -0.75: 51506                             |

## Data Quality Signals

- Duplicate rows in full data: `0` / `3574091`.
- Numeric columns containing negative values: `fare_amount`, `extra`, `mta_tax`, `tip_amount`, `tolls_amount`, `improvement_surcharge`, `total_amount`, `congestion_surcharge`, `Airport_fee`, `cbd_congestion_fee`.

## Data Preview

|   VendorID | tpep_pickup_datetime   | tpep_dropoff_datetime   |   passenger_count |   trip_distance |   RatecodeID | store_and_fwd_flag   |   PULocationID |   DOLocationID |   payment_type |   fare_amount |   extra |   mta_tax |   tip_amount |   tolls_amount |   improvement_surcharge |   total_amount |   congestion_surcharge |   Airport_fee |   cbd_congestion_fee |
|-----------:|:-----------------------|:------------------------|------------------:|----------------:|-------------:|:---------------------|---------------:|---------------:|---------------:|--------------:|--------:|----------:|-------------:|---------------:|------------------------:|---------------:|-----------------------:|--------------:|---------------------:|
|          2 | 2025-08-01 00:52:23    | 2025-08-01 01:12:20     |                 1 |            8.44 |            1 | N                    |            138 |            141 |              1 |          33.8 |       6 |       0.5 |         5    |           6.94 |                       1 |          57.49 |                    2.5 |          1.75 |                 0    |
|          2 | 2025-08-01 00:03:01    | 2025-08-01 00:15:33     |                 2 |            4.98 |            1 | N                    |            138 |            193 |              1 |          21.2 |       6 |       0.5 |         0    |           0    |                       1 |          30.45 |                    0   |          1.75 |                 0    |
|          7 | 2025-08-01 00:24:38    | 2025-08-01 00:24:38     |                 2 |            1.89 |            1 | N                    |            249 |             45 |              1 |          14.2 |       0 |       0.5 |         3.99 |           0    |                       1 |          23.94 |                    2.5 |          0    |                 0.75 |
|          7 | 2025-08-01 00:48:19    | 2025-08-01 00:48:19     |                 1 |            2.35 |            1 | N                    |             79 |            229 |              1 |          11.4 |       0 |       0.5 |         3.43 |           0    |                       1 |          20.58 |                    2.5 |          0    |                 0.75 |
|          2 | 2025-08-01 00:25:34    | 2025-08-01 00:33:18     |                 1 |            2.14 |            1 | N                    |             43 |             48 |              1 |          11.4 |       1 |       0.5 |         2.57 |           0    |                       1 |          19.72 |                    2.5 |          0    |                 0.75 |
|          2 | 2025-08-01 00:16:36    | 2025-08-01 00:33:41     |                 1 |            3.06 |            1 | N                    |            114 |            230 |              2 |          18.4 |       1 |       0.5 |         0    |           0    |                       1 |          24.15 |                    2.5 |          0    |                 0.75 |
|          2 | 2025-08-01 00:56:02    | 2025-08-01 01:15:37     |                 1 |            5.25 |            1 | N                    |            163 |             13 |              1 |          24.7 |       1 |       0.5 |         1    |           0    |                       1 |          31.45 |                    2.5 |          0    |                 0.75 |
|          2 | 2025-08-01 00:12:10    | 2025-08-01 00:15:58     |                 1 |            1.45 |            1 | N                    |            163 |            236 |              1 |           7.9 |       1 |       0.5 |         2.73 |           0    |                       1 |          16.38 |                    2.5 |          0    |                 0.75 |
|          2 | 2025-08-01 00:05:30    | 2025-08-01 00:09:19     |                 1 |            0.73 |            1 | N                    |            263 |            262 |              2 |           5.8 |       1 |       0.5 |         0    |           0    |                       1 |          10.8  |                    2.5 |          0    |                 0    |
|          2 | 2025-08-01 00:11:29    | 2025-08-01 00:22:26     |                 1 |            1.81 |            1 | N                    |            249 |            231 |              1 |          12.1 |       1 |       0.5 |         3.57 |           0    |                       1 |          21.42 |                    2.5 |          0    |                 0.75 |
