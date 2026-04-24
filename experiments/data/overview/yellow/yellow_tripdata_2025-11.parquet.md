# Data Overview: yellow_tripdata_2025-11.parquet

## Dataset Summary

| metric       | value                                                                               |
|:-------------|:------------------------------------------------------------------------------------|
| file         | /root/Dev/DataGate/experiments/data/parquets/yellow/yellow_tripdata_2025-11.parquet |
| rows         | 4181444                                                                             |
| columns      | 20                                                                                  |
| row_groups   | 4                                                                                   |
| file_size_mb | 67.84                                                                               |
| rows_loaded  | 4181444                                                                             |

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

| column                | dtype          |   non_null |    null |   null_% |   unique |
|:----------------------|:---------------|-----------:|--------:|---------:|---------:|
| VendorID              | int32          |    4181444 |       0 |   0.0000 |        4 |
| tpep_pickup_datetime  | datetime64[us] |    4181444 |       0 |   0.0000 |  1826937 |
| tpep_dropoff_datetime | datetime64[us] |    4181444 |       0 |   0.0000 |  1824141 |
| passenger_count       | float64        |    3166704 | 1014740 |  24.2677 |        9 |
| trip_distance         | float64        |    4181444 |       0 |   0.0000 |     4980 |
| RatecodeID            | float64        |    3166704 | 1014740 |  24.2677 |        7 |
| store_and_fwd_flag    | str            |    3166704 | 1014740 |  24.2677 |        2 |
| PULocationID          | int32          |    4181444 |       0 |   0.0000 |      260 |
| DOLocationID          | int32          |    4181444 |       0 |   0.0000 |      259 |
| payment_type          | int64          |    4181444 |       0 |   0.0000 |        5 |
| fare_amount           | float64        |    4181444 |       0 |   0.0000 |    14203 |
| extra                 | float64        |    4181444 |       0 |   0.0000 |       60 |
| mta_tax               | float64        |    4181444 |       0 |   0.0000 |       11 |
| tip_amount            | float64        |    4181444 |       0 |   0.0000 |     4525 |
| tolls_amount          | float64        |    4181444 |       0 |   0.0000 |     1375 |
| improvement_surcharge | float64        |    4181444 |       0 |   0.0000 |        6 |
| total_amount          | float64        |    4181444 |       0 |   0.0000 |    24422 |
| congestion_surcharge  | float64        |    3166704 | 1014740 |  24.2677 |        6 |
| Airport_fee           | float64        |    3166704 | 1014740 |  24.2677 |        6 |
| cbd_congestion_fee    | float64        |    4181444 |       0 |   0.0000 |        3 |

## Numeric Statistics (full-data)

| column                |        min |      p25 |   median |     mean |      p75 |         max |      std |
|:----------------------|-----------:|---------:|---------:|---------:|---------:|------------:|---------:|
| VendorID              |     1.0000 |   2.0000 |   2.0000 |   1.8794 |   2.0000 |      7.0000 |   0.7464 |
| passenger_count       |     0.0000 |   1.0000 |   1.0000 |   1.2871 |   1.0000 |      8.0000 |   0.7043 |
| trip_distance         |     0.0000 |   1.0500 |   1.8900 |   6.5309 |   3.8400 | 256067.6500 | 627.4616 |
| RatecodeID            |     1.0000 |   1.0000 |   1.0000 |   4.4645 |   1.0000 |     99.0000 |  17.8284 |
| PULocationID          |     1.0000 | 114.0000 | 161.0000 | 162.0342 | 233.0000 |    265.0000 |  66.3388 |
| DOLocationID          |     1.0000 | 107.0000 | 162.0000 | 161.5968 | 234.0000 |    265.0000 |  70.5463 |
| payment_type          |     0.0000 |   1.0000 |   1.0000 |   0.9051 |   1.0000 |      4.0000 |   0.6988 |
| fare_amount           | -1508.7000 |   7.9000 |  12.8000 |  17.1179 |  21.9000 |   1508.7000 |  19.5793 |
| extra                 |    -8.5000 |   0.0000 |   0.0000 |   1.0596 |   2.5000 |     15.0000 |   1.7361 |
| mta_tax               |    -0.5000 |   0.5000 |   0.5000 |   0.4818 |   0.5000 |     10.5000 |   0.1201 |
| tip_amount            |  -333.3300 |   0.0000 |   2.0000 |   2.8622 |   4.0000 |    575.0000 |   4.0024 |
| tolls_amount          |  -115.0500 |   0.0000 |   0.0000 |   0.5179 |   0.0000 |    300.0000 |   2.1405 |
| improvement_surcharge |    -1.0000 |   1.0000 |   1.0000 |   0.9499 |   1.0000 |      2.5000 |   0.2656 |
| total_amount          | -1514.4500 |  14.3500 |  20.5800 |  25.6150 |  30.0500 |   1514.4500 |  23.7747 |
| congestion_surcharge  |    -2.5000 |   2.5000 |   2.5000 |   2.1850 |   2.5000 |      2.5000 |   0.9159 |
| Airport_fee           |    -1.7500 |   0.0000 |   0.0000 |   0.1430 |   0.0000 |      6.7500 |   0.5190 |
| cbd_congestion_fee    |    -0.7500 |   0.0000 |   0.7500 |   0.5350 |   0.7500 |      0.7500 |   0.3517 |

## Datetime Coverage (full-data)

| column                | min_ts              | max_ts              | span               |
|:----------------------|:--------------------|:--------------------|:-------------------|
| tpep_pickup_datetime  | 2008-12-31 23:04:21 | 2025-11-30 23:59:59 | 6178 days 00:55:38 |
| tpep_dropoff_datetime | 2008-12-31 23:32:25 | 2025-12-01 21:41:00 | 6178 days 22:08:35 |

## Datetime Distribution by Day (full-data)

| column                | day        |   rows |   row_% |
|:----------------------|:-----------|-------:|--------:|
| tpep_pickup_datetime  | 2008-12-31 |      1 |  0.0000 |
| tpep_pickup_datetime  | 2009-01-01 |      2 |  0.0000 |
| tpep_pickup_datetime  | 2025-10-31 |     21 |  0.0005 |
| tpep_pickup_datetime  | 2025-11-01 | 183032 |  4.3772 |
| tpep_pickup_datetime  | 2025-11-02 | 152130 |  3.6382 |
| tpep_pickup_datetime  | 2025-11-03 | 129816 |  3.1046 |
| tpep_pickup_datetime  | 2025-11-04 | 131512 |  3.1451 |
| tpep_pickup_datetime  | 2025-11-05 | 142587 |  3.4100 |
| tpep_pickup_datetime  | 2025-11-06 | 158170 |  3.7827 |
| tpep_pickup_datetime  | 2025-11-07 | 147795 |  3.5345 |
| tpep_pickup_datetime  | 2025-11-08 | 153432 |  3.6694 |
| tpep_pickup_datetime  | 2025-11-09 | 133197 |  3.1854 |
| tpep_pickup_datetime  | 2025-11-10 | 131860 |  3.1535 |
| tpep_pickup_datetime  | 2025-11-11 | 131252 |  3.1389 |
| tpep_pickup_datetime  | 2025-11-12 | 142267 |  3.4023 |
| tpep_pickup_datetime  | 2025-11-13 | 156277 |  3.7374 |
| tpep_pickup_datetime  | 2025-11-14 | 154779 |  3.7016 |
| tpep_pickup_datetime  | 2025-11-15 | 162604 |  3.8887 |
| tpep_pickup_datetime  | 2025-11-16 | 136369 |  3.2613 |
| tpep_pickup_datetime  | 2025-11-17 | 130552 |  3.1222 |
| tpep_pickup_datetime  | 2025-11-18 | 143933 |  3.4422 |
| tpep_pickup_datetime  | 2025-11-19 | 153531 |  3.6717 |
| tpep_pickup_datetime  | 2025-11-20 | 160579 |  3.8403 |
| tpep_pickup_datetime  | 2025-11-21 | 153946 |  3.6816 |
| tpep_pickup_datetime  | 2025-11-22 | 154131 |  3.6861 |
| tpep_pickup_datetime  | 2025-11-23 | 126561 |  3.0267 |
| tpep_pickup_datetime  | 2025-11-24 | 120517 |  2.8822 |
| tpep_pickup_datetime  | 2025-11-25 | 144794 |  3.4628 |
| tpep_pickup_datetime  | 2025-11-26 | 122438 |  2.9281 |
| tpep_pickup_datetime  | 2025-11-27 |  96815 |  2.3153 |
| tpep_pickup_datetime  | 2025-11-28 | 100936 |  2.4139 |
| tpep_pickup_datetime  | 2025-11-29 | 114334 |  2.7343 |
| tpep_pickup_datetime  | 2025-11-30 | 111274 |  2.6611 |
| tpep_dropoff_datetime | 2008-12-31 |      1 |  0.0000 |
| tpep_dropoff_datetime | 2009-01-01 |      2 |  0.0000 |
| tpep_dropoff_datetime | 2025-10-31 |      3 |  0.0001 |
| tpep_dropoff_datetime | 2025-11-01 | 180069 |  4.3064 |
| tpep_dropoff_datetime | 2025-11-02 | 154310 |  3.6904 |
| tpep_dropoff_datetime | 2025-11-03 | 129860 |  3.1056 |
| tpep_dropoff_datetime | 2025-11-04 | 131226 |  3.1383 |
| tpep_dropoff_datetime | 2025-11-05 | 142556 |  3.4093 |
| tpep_dropoff_datetime | 2025-11-06 | 157478 |  3.7661 |
| tpep_dropoff_datetime | 2025-11-07 | 147058 |  3.5169 |
| tpep_dropoff_datetime | 2025-11-08 | 153322 |  3.6667 |
| tpep_dropoff_datetime | 2025-11-09 | 135011 |  3.2288 |
| tpep_dropoff_datetime | 2025-11-10 | 131759 |  3.1510 |
| tpep_dropoff_datetime | 2025-11-11 | 131333 |  3.1409 |
| tpep_dropoff_datetime | 2025-11-12 | 141995 |  3.3958 |
| tpep_dropoff_datetime | 2025-11-13 | 155478 |  3.7183 |
| tpep_dropoff_datetime | 2025-11-14 | 154131 |  3.6861 |
| tpep_dropoff_datetime | 2025-11-15 | 162362 |  3.8829 |
| tpep_dropoff_datetime | 2025-11-16 | 138460 |  3.3113 |
| tpep_dropoff_datetime | 2025-11-17 | 130476 |  3.1204 |
| tpep_dropoff_datetime | 2025-11-18 | 143744 |  3.4377 |
| tpep_dropoff_datetime | 2025-11-19 | 153204 |  3.6639 |
| tpep_dropoff_datetime | 2025-11-20 | 160000 |  3.8264 |
| tpep_dropoff_datetime | 2025-11-21 | 153332 |  3.6670 |
| tpep_dropoff_datetime | 2025-11-22 | 153705 |  3.6759 |
| tpep_dropoff_datetime | 2025-11-23 | 128721 |  3.0784 |
| tpep_dropoff_datetime | 2025-11-24 | 120520 |  2.8823 |
| tpep_dropoff_datetime | 2025-11-25 | 144770 |  3.4622 |
| tpep_dropoff_datetime | 2025-11-26 | 122192 |  2.9222 |
| tpep_dropoff_datetime | 2025-11-27 |  96882 |  2.3170 |
| tpep_dropoff_datetime | 2025-11-28 | 100697 |  2.4082 |
| tpep_dropoff_datetime | 2025-11-29 | 113763 |  2.7207 |
| tpep_dropoff_datetime | 2025-11-30 | 112221 |  2.6838 |
| tpep_dropoff_datetime | 2025-12-01 |    803 |  0.0192 |

## Top Values (full-data, top 5)

| column                | top_5_values                                                          |
|:----------------------|:----------------------------------------------------------------------|
| VendorID              | 2: 3295835, 1: 821333, 7: 60043, 6: 4233                              |
| passenger_count       | 1.0: 2518496, <NULL>: 1014740, 2.0: 438172, 3.0: 102742, 4.0: 70436   |
| RatecodeID            | 1.0: 2891153, <NULL>: 1014740, 99.0: 108669, 2.0: 102901, 5.0: 40413  |
| store_and_fwd_flag    | N: 3161473, <NULL>: 1014740, Y: 5231                                  |
| payment_type          | 1: 2704695, 0: 1014740, 2: 373932, 4: 67726, 3: 20351                 |
| mta_tax               | 0.5: 4074477, 0.0: 60811, -0.5: 45872, 1.0: 269, 10.5: 4              |
| improvement_surcharge | 1.0: 4018909, 0.0: 109909, -1.0: 48388, 0.3: 4236, 2.5: 1             |
| congestion_surcharge  | 2.5: 2805917, <NULL>: 1014740, 0.0: 322595, -2.5: 38183, 1.0: 4       |
| Airport_fee           | 0.0: 2892195, <NULL>: 1014740, 1.75: 261914, -1.75: 10552, 6.75: 1572 |
| cbd_congestion_fee    | 0.75: 3014923, 0.0: 1134377, -0.75: 32144                             |

## Data Quality Signals

- Duplicate rows in full data: `0` / `4181444`.
- Numeric columns containing negative values: `fare_amount`, `extra`, `mta_tax`, `tip_amount`, `tolls_amount`, `improvement_surcharge`, `total_amount`, `congestion_surcharge`, `Airport_fee`, `cbd_congestion_fee`.

## Data Preview

|   VendorID | tpep_pickup_datetime   | tpep_dropoff_datetime   |   passenger_count |   trip_distance |   RatecodeID | store_and_fwd_flag   |   PULocationID |   DOLocationID |   payment_type |   fare_amount |   extra |   mta_tax |   tip_amount |   tolls_amount |   improvement_surcharge |   total_amount |   congestion_surcharge |   Airport_fee |   cbd_congestion_fee |
|-----------:|:-----------------------|:------------------------|------------------:|----------------:|-------------:|:---------------------|---------------:|---------------:|---------------:|--------------:|--------:|----------:|-------------:|---------------:|------------------------:|---------------:|-----------------------:|--------------:|---------------------:|
|          7 | 2025-11-01 00:13:25    | 2025-11-01 00:13:25     |                 1 |            1.68 |            1 | N                    |             43 |            186 |              1 |          14.9 |    0    |       0.5 |         1.5  |           0    |                       1 |          22.15 |                    2.5 |          0    |                 0.75 |
|          2 | 2025-11-01 00:49:07    | 2025-11-01 01:01:22     |                 1 |            2.28 |            1 | N                    |            142 |            237 |              1 |          14.2 |    1    |       0.5 |         4.99 |           0    |                       1 |          24.94 |                    2.5 |          0    |                 0.75 |
|          1 | 2025-11-01 00:07:19    | 2025-11-01 00:20:41     |                 0 |            2.7  |            1 | N                    |            163 |            238 |              1 |          15.6 |    4.25 |       0.5 |         4.27 |           0    |                       1 |          25.62 |                    2.5 |          0    |                 0.75 |
|          2 | 2025-11-01 00:00:00    | 2025-11-01 01:01:03     |                 3 |           12.87 |            1 | N                    |            138 |            261 |              1 |          66.7 |    6    |       0.5 |         0    |           6.94 |                       1 |          86.14 |                    2.5 |          1.75 |                 0.75 |
|          1 | 2025-11-01 00:18:50    | 2025-11-01 00:49:32     |                 0 |            8.4  |            1 | N                    |            138 |             37 |              2 |          39.4 |    7.75 |       0.5 |         0    |           0    |                       1 |          48.65 |                    0   |          1.75 |                 0    |
|          2 | 2025-11-01 00:21:11    | 2025-11-01 00:31:39     |                 1 |            0.85 |            1 | N                    |             90 |            100 |              2 |          10.7 |    1    |       0.5 |         0    |           0    |                       1 |          16.45 |                    2.5 |          0    |                 0.75 |
|          2 | 2025-11-01 00:07:31    | 2025-11-01 00:25:44     |                 1 |            3.01 |            1 | N                    |            142 |            170 |              1 |          19.1 |    1    |       0.5 |         1    |           0    |                       1 |          25.85 |                    2.5 |          0    |                 0.75 |
|          2 | 2025-11-01 00:46:52    | 2025-11-01 01:38:55     |                 3 |            3.82 |            1 | N                    |            237 |            144 |              1 |          42.2 |    1    |       0.5 |         9.59 |           0    |                       1 |          57.54 |                    2.5 |          0    |                 0.75 |
|          2 | 2025-11-01 00:56:59    | 2025-11-01 01:02:05     |                 1 |            0.89 |            1 | N                    |            162 |            161 |              2 |           7.2 |    1    |       0.5 |         0    |           0    |                       1 |          12.95 |                    2.5 |          0    |                 0.75 |
|          2 | 2025-11-01 00:10:43    | 2025-11-01 00:39:25     |                 3 |            2.28 |            1 | N                    |            234 |            162 |              1 |          24   |    1    |       0.5 |         8.93 |           0    |                       1 |          38.68 |                    2.5 |          0    |                 0.75 |
