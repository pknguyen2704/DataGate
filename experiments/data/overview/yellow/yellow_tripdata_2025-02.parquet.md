# Data Overview: yellow_tripdata_2025-02.parquet

## Dataset Summary

| metric       | value                                                                               |
|:-------------|:------------------------------------------------------------------------------------|
| file         | /root/Dev/DataGate/experiments/data/parquets/yellow/yellow_tripdata_2025-02.parquet |
| rows         | 3577543                                                                             |
| columns      | 20                                                                                  |
| row_groups   | 4                                                                                   |
| file_size_mb | 57.55                                                                               |
| rows_loaded  | 3577543                                                                             |

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
| VendorID              | int32          |    3577543 |      0 |   0.0000 |        4 |
| tpep_pickup_datetime  | datetime64[us] |    3577543 |      0 |   0.0000 |  1607109 |
| tpep_dropoff_datetime | datetime64[us] |    3577543 |      0 |   0.0000 |  1606589 |
| passenger_count       | float64        |    2770606 | 806937 |  22.5556 |       10 |
| trip_distance         | float64        |    3577543 |      0 |   0.0000 |     4365 |
| RatecodeID            | float64        |    2770606 | 806937 |  22.5556 |        7 |
| store_and_fwd_flag    | str            |    2770606 | 806937 |  22.5556 |        2 |
| PULocationID          | int32          |    3577543 |      0 |   0.0000 |      257 |
| DOLocationID          | int32          |    3577543 |      0 |   0.0000 |      260 |
| payment_type          | int64          |    3577543 |      0 |   0.0000 |        5 |
| fare_amount           | float64        |    3577543 |      0 |   0.0000 |     9548 |
| extra                 | float64        |    3577543 |      0 |   0.0000 |       78 |
| mta_tax               | float64        |    3577543 |      0 |   0.0000 |       11 |
| tip_amount            | float64        |    3577543 |      0 |   0.0000 |     4099 |
| tolls_amount          | float64        |    3577543 |      0 |   0.0000 |     1025 |
| improvement_surcharge | float64        |    3577543 |      0 |   0.0000 |        4 |
| total_amount          | float64        |    3577543 |      0 |   0.0000 |    19619 |
| congestion_surcharge  | float64        |    2770606 | 806937 |  22.5556 |        3 |
| Airport_fee           | float64        |    2770606 | 806937 |  22.5556 |        5 |
| cbd_congestion_fee    | float64        |    3577543 |      0 |   0.0000 |        4 |

## Numeric Statistics (full-data)

| column                |        min |      p25 |   median |     mean |      p75 |         max |      std |
|:----------------------|-----------:|---------:|---------:|---------:|---------:|------------:|---------:|
| VendorID              |     1.0000 |   2.0000 |   2.0000 |   1.7955 |   2.0000 |      7.0000 |   0.4490 |
| passenger_count       |     0.0000 |   1.0000 |   1.0000 |   1.2760 |   1.0000 |      9.0000 |   0.7223 |
| trip_distance         |     0.0000 |   1.0000 |   1.7000 |   6.0254 |   3.1800 | 228782.5100 | 543.3970 |
| RatecodeID            |     1.0000 |   1.0000 |   1.0000 |   2.4589 |   1.0000 |     99.0000 |  11.5633 |
| PULocationID          |     1.0000 | 125.0000 | 161.0000 | 163.2846 | 233.0000 |    265.0000 |  65.6296 |
| DOLocationID          |     1.0000 | 113.0000 | 162.0000 | 162.4813 | 234.0000 |    265.0000 |  69.8642 |
| payment_type          |     0.0000 |   1.0000 |   1.0000 |   0.9429 |   1.0000 |      4.0000 |   0.7249 |
| fare_amount           | -1807.6000 |   8.6000 |  12.8000 |  16.7490 |  19.8000 | 132531.3600 |  72.1293 |
| extra                 |    -7.5000 |   0.0000 |   0.0000 |   1.2381 |   2.5000 |     22.5500 |   1.8423 |
| mta_tax               |    -0.5000 |   0.5000 |   0.5000 |   0.4805 |   0.5000 |     10.5000 |   0.1299 |
| tip_amount            |  -220.0000 |   0.0000 |   2.1100 |   2.7301 |   3.7900 |    440.0000 |   3.6527 |
| tolls_amount          |  -113.9300 |   0.0000 |   0.0000 |   0.4053 |   0.0000 |    115.8700 |   1.8896 |
| improvement_surcharge |    -1.0000 |   1.0000 |   1.0000 |   0.9592 |   1.0000 |      1.0000 |   0.2644 |
| total_amount          | -1832.8500 |  15.3100 |  20.1900 |  25.0306 |  27.9700 | 132555.4100 |  73.1854 |
| congestion_surcharge  |    -2.5000 |   2.5000 |   2.5000 |   2.2317 |   2.5000 |      2.5000 |   0.8952 |
| Airport_fee           |    -1.7500 |   0.0000 |   0.0000 |   0.1216 |   0.0000 |      6.7500 |   0.4691 |
| cbd_congestion_fee    |    -0.7500 |   0.0000 |   0.7500 |   0.5373 |   0.7500 |      1.2500 |   0.3550 |

## Datetime Coverage (full-data)

| column                | min_ts              | max_ts              | span             |
|:----------------------|:--------------------|:--------------------|:-----------------|
| tpep_pickup_datetime  | 2025-01-31 22:22:53 | 2025-03-01 00:06:32 | 28 days 01:43:39 |
| tpep_dropoff_datetime | 2025-01-31 22:30:00 | 2025-03-01 23:13:42 | 29 days 00:43:42 |

## Datetime Distribution by Day (full-data)

| column                | day        |   rows |   row_% |
|:----------------------|:-----------|-------:|--------:|
| tpep_pickup_datetime  | 2025-01-31 |     30 |  0.0008 |
| tpep_pickup_datetime  | 2025-02-01 | 148649 |  4.1551 |
| tpep_pickup_datetime  | 2025-02-02 | 123646 |  3.4562 |
| tpep_pickup_datetime  | 2025-02-03 |  98476 |  2.7526 |
| tpep_pickup_datetime  | 2025-02-04 | 119863 |  3.3504 |
| tpep_pickup_datetime  | 2025-02-05 | 128369 |  3.5882 |
| tpep_pickup_datetime  | 2025-02-06 | 126082 |  3.5243 |
| tpep_pickup_datetime  | 2025-02-07 | 138099 |  3.8602 |
| tpep_pickup_datetime  | 2025-02-08 | 146049 |  4.0824 |
| tpep_pickup_datetime  | 2025-02-09 | 123431 |  3.4502 |
| tpep_pickup_datetime  | 2025-02-10 | 108569 |  3.0347 |
| tpep_pickup_datetime  | 2025-02-11 | 125526 |  3.5087 |
| tpep_pickup_datetime  | 2025-02-12 | 128920 |  3.6036 |
| tpep_pickup_datetime  | 2025-02-13 | 142760 |  3.9904 |
| tpep_pickup_datetime  | 2025-02-14 | 158575 |  4.4325 |
| tpep_pickup_datetime  | 2025-02-15 | 148473 |  4.1501 |
| tpep_pickup_datetime  | 2025-02-16 | 113726 |  3.1789 |
| tpep_pickup_datetime  | 2025-02-17 |  94574 |  2.6435 |
| tpep_pickup_datetime  | 2025-02-18 | 117355 |  3.2803 |
| tpep_pickup_datetime  | 2025-02-19 | 123679 |  3.4571 |
| tpep_pickup_datetime  | 2025-02-20 | 142246 |  3.9761 |
| tpep_pickup_datetime  | 2025-02-21 | 133980 |  3.7450 |
| tpep_pickup_datetime  | 2025-02-22 | 141862 |  3.9653 |
| tpep_pickup_datetime  | 2025-02-23 | 108970 |  3.0459 |
| tpep_pickup_datetime  | 2025-02-24 |  97348 |  2.7211 |
| tpep_pickup_datetime  | 2025-02-25 | 115804 |  3.2370 |
| tpep_pickup_datetime  | 2025-02-26 | 128974 |  3.6051 |
| tpep_pickup_datetime  | 2025-02-27 | 144052 |  4.0266 |
| tpep_pickup_datetime  | 2025-02-28 | 149455 |  4.1776 |
| tpep_pickup_datetime  | 2025-03-01 |      1 |  0.0000 |
| tpep_dropoff_datetime | 2025-01-31 |     11 |  0.0003 |
| tpep_dropoff_datetime | 2025-02-01 | 146192 |  4.0864 |
| tpep_dropoff_datetime | 2025-02-02 | 125428 |  3.5060 |
| tpep_dropoff_datetime | 2025-02-03 |  98685 |  2.7585 |
| tpep_dropoff_datetime | 2025-02-04 | 119820 |  3.3492 |
| tpep_dropoff_datetime | 2025-02-05 | 128170 |  3.5826 |
| tpep_dropoff_datetime | 2025-02-06 | 125773 |  3.5156 |
| tpep_dropoff_datetime | 2025-02-07 | 136921 |  3.8272 |
| tpep_dropoff_datetime | 2025-02-08 | 146012 |  4.0813 |
| tpep_dropoff_datetime | 2025-02-09 | 124976 |  3.4933 |
| tpep_dropoff_datetime | 2025-02-10 | 108774 |  3.0405 |
| tpep_dropoff_datetime | 2025-02-11 | 125450 |  3.5066 |
| tpep_dropoff_datetime | 2025-02-12 | 128703 |  3.5975 |
| tpep_dropoff_datetime | 2025-02-13 | 142237 |  3.9758 |
| tpep_dropoff_datetime | 2025-02-14 | 157558 |  4.4041 |
| tpep_dropoff_datetime | 2025-02-15 | 148787 |  4.1589 |
| tpep_dropoff_datetime | 2025-02-16 | 114753 |  3.2076 |
| tpep_dropoff_datetime | 2025-02-17 |  95020 |  2.6560 |
| tpep_dropoff_datetime | 2025-02-18 | 117248 |  3.2773 |
| tpep_dropoff_datetime | 2025-02-19 | 123695 |  3.4575 |
| tpep_dropoff_datetime | 2025-02-20 | 141588 |  3.9577 |
| tpep_dropoff_datetime | 2025-02-21 | 133084 |  3.7200 |
| tpep_dropoff_datetime | 2025-02-22 | 141775 |  3.9629 |
| tpep_dropoff_datetime | 2025-02-23 | 110767 |  3.0962 |
| tpep_dropoff_datetime | 2025-02-24 |  97315 |  2.7202 |
| tpep_dropoff_datetime | 2025-02-25 | 115761 |  3.2358 |
| tpep_dropoff_datetime | 2025-02-26 | 128726 |  3.5982 |
| tpep_dropoff_datetime | 2025-02-27 | 143485 |  4.0107 |
| tpep_dropoff_datetime | 2025-02-28 | 148434 |  4.1490 |
| tpep_dropoff_datetime | 2025-03-01 |   2395 |  0.0669 |

## Top Values (full-data, top 5)

| column                | top_5_values                                                      |
|:----------------------|:------------------------------------------------------------------|
| VendorID              | 2: 2817803, 1: 754990, 7: 4420, 6: 330                            |
| passenger_count       | 1.0: 2226109, <NULL>: 806937, 2.0: 370813, 3.0: 78032, 4.0: 46625 |
| RatecodeID            | 1.0: 2612715, <NULL>: 806937, 2.0: 81895, 99.0: 39132, 5.0: 22523 |
| store_and_fwd_flag    | N: 2742663, <NULL>: 806937, Y: 27943                              |
| payment_type          | 1: 2336175, 0: 806937, 2: 339481, 4: 73101, 3: 21849              |
| mta_tax               | 0.5: 3490941, -0.5: 53034, 0.0: 33502, 1.0: 55, 4.75: 4           |
| improvement_surcharge | 1.0: 3486357, -1.0: 55016, 0.0: 35831, 0.3: 339                   |
| congestion_surcharge  | 2.5: 2518145, <NULL>: 806937, 0.0: 207568, -2.5: 44893            |
| Airport_fee           | 0.0: 2558344, <NULL>: 806937, 1.75: 202355, -1.75: 9877, 5.0: 27  |
| cbd_congestion_fee    | 0.75: 2600256, 0.0: 940038, -0.75: 37238, 1.25: 11                |

## Data Quality Signals

- Duplicate rows in full data: `0` / `3577543`.
- Numeric columns containing negative values: `fare_amount`, `extra`, `mta_tax`, `tip_amount`, `tolls_amount`, `improvement_surcharge`, `total_amount`, `congestion_surcharge`, `Airport_fee`, `cbd_congestion_fee`.

## Data Preview

|   VendorID | tpep_pickup_datetime   | tpep_dropoff_datetime   |   passenger_count |   trip_distance |   RatecodeID | store_and_fwd_flag   |   PULocationID |   DOLocationID |   payment_type |   fare_amount |   extra |   mta_tax |   tip_amount |   tolls_amount |   improvement_surcharge |   total_amount |   congestion_surcharge |   Airport_fee |   cbd_congestion_fee |
|-----------:|:-----------------------|:------------------------|------------------:|----------------:|-------------:|:---------------------|---------------:|---------------:|---------------:|--------------:|--------:|----------:|-------------:|---------------:|------------------------:|---------------:|-----------------------:|--------------:|---------------------:|
|          2 | 2025-02-01 00:12:18    | 2025-02-01 00:32:33     |                 3 |            3.12 |            1 | N                    |            246 |             79 |              1 |          19.8 |    1    |       0.5 |         5.11 |              0 |                       1 |          30.66 |                    2.5 |             0 |                 0.75 |
|          2 | 2025-02-01 00:40:04    | 2025-02-01 00:49:15     |                 1 |            1.4  |            1 | N                    |            114 |             79 |              1 |          10   |    1    |       0.5 |         3.15 |              0 |                       1 |          18.9  |                    2.5 |             0 |                 0.75 |
|          1 | 2025-02-01 00:06:09    | 2025-02-01 00:11:51     |                 0 |            0.4  |            1 | N                    |            211 |            144 |              1 |           6.5 |    4.25 |       0.5 |         1    |              0 |                       1 |          13.25 |                    2.5 |             0 |                 0.75 |
|          1 | 2025-02-01 00:15:13    | 2025-02-01 00:20:19     |                 0 |            0.7  |            1 | N                    |            113 |            249 |              1 |           7.2 |    4.25 |       0.5 |         2    |              0 |                       1 |          14.95 |                    2.5 |             0 |                 0.75 |
|          2 | 2025-02-01 00:02:52    | 2025-02-01 00:20:25     |                 1 |            4.19 |            1 | N                    |            113 |            263 |              1 |          19.8 |    1    |       0.5 |         5.11 |              0 |                       1 |          30.66 |                    2.5 |             0 |                 0.75 |
|          2 | 2025-02-01 00:33:47    | 2025-02-01 00:41:49     |                 1 |            1.57 |            1 | N                    |            162 |            236 |              1 |          10   |    1    |       0.5 |         3.15 |              0 |                       1 |          18.9  |                    2.5 |             0 |                 0.75 |
|          2 | 2025-02-01 00:37:12    | 2025-02-01 00:39:49     |                 1 |            0.3  |            1 | N                    |            164 |            186 |              1 |           4.4 |    1    |       0.5 |         3    |              0 |                       1 |          13.15 |                    2.5 |             0 |                 0.75 |
|          2 | 2025-02-01 00:12:12    | 2025-02-01 00:23:30     |                 1 |            1.41 |            1 | N                    |             45 |            249 |              1 |          11.4 |    1    |       0.5 |         3.43 |              0 |                       1 |          20.58 |                    2.5 |             0 |                 0.75 |
|          2 | 2025-02-01 00:29:30    | 2025-02-01 00:44:51     |                 1 |            2.72 |            1 | N                    |            114 |            186 |              1 |          16.3 |    1    |       0.5 |         2    |              0 |                       1 |          24.05 |                    2.5 |             0 |                 0.75 |
|          1 | 2025-02-01 00:15:18    | 2025-02-01 00:26:00     |                 1 |            2.2  |            1 | N                    |            158 |             48 |              2 |          12.8 |    4.25 |       0.5 |         0    |              0 |                       1 |          18.55 |                    2.5 |             0 |                 0.75 |
