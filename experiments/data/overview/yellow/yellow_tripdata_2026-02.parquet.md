# Data Overview: yellow_tripdata_2026-02.parquet

## Dataset Summary

| metric       | value                                                                               |
|:-------------|:------------------------------------------------------------------------------------|
| file         | /root/Dev/DataGate/experiments/data/parquets/yellow/yellow_tripdata_2026-02.parquet |
| rows         | 3399866                                                                             |
| columns      | 20                                                                                  |
| row_groups   | 4                                                                                   |
| file_size_mb | 55.96                                                                               |
| rows_loaded  | 3399866                                                                             |

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
| VendorID              | int32          |    3399866 |       0 |   0.0000 |        4 |
| tpep_pickup_datetime  | datetime64[us] |    3399866 |       0 |   0.0000 |  1587963 |
| tpep_dropoff_datetime | datetime64[us] |    3399866 |       0 |   0.0000 |  1587241 |
| passenger_count       | float64        |    2376549 | 1023317 |  30.0987 |        9 |
| trip_distance         | float64        |    3399866 |       0 |   0.0000 |     4719 |
| RatecodeID            | float64        |    2376549 | 1023317 |  30.0987 |        7 |
| store_and_fwd_flag    | str            |    2376549 | 1023317 |  30.0987 |        2 |
| PULocationID          | int32          |    3399866 |       0 |   0.0000 |      259 |
| DOLocationID          | int32          |    3399866 |       0 |   0.0000 |      261 |
| payment_type          | int64          |    3399866 |       0 |   0.0000 |        5 |
| fare_amount           | float64        |    3399866 |       0 |   0.0000 |    12616 |
| extra                 | float64        |    3399866 |       0 |   0.0000 |       41 |
| mta_tax               | float64        |    3399866 |       0 |   0.0000 |       10 |
| tip_amount            | float64        |    3399866 |       0 |   0.0000 |     4210 |
| tolls_amount          | float64        |    3399866 |       0 |   0.0000 |     1169 |
| improvement_surcharge | float64        |    3399866 |       0 |   0.0000 |        4 |
| total_amount          | float64        |    3399866 |       0 |   0.0000 |    19930 |
| congestion_surcharge  | float64        |    2376549 | 1023317 |  30.0987 |        4 |
| Airport_fee           | float64        |    2376549 | 1023317 |  30.0987 |        8 |
| cbd_congestion_fee    | float64        |    3399866 |       0 |   0.0000 |        3 |

## Numeric Statistics (full-data)

| column                |        min |      p25 |   median |     mean |      p75 |         max |      std |
|:----------------------|-----------:|---------:|---------:|---------:|---------:|------------:|---------:|
| VendorID              |     1.0000 |   2.0000 |   2.0000 |   1.8782 |   2.0000 |      7.0000 |   0.7035 |
| passenger_count       |     0.0000 |   1.0000 |   1.0000 |   1.2299 |   1.0000 |      9.0000 |   0.6347 |
| trip_distance         |     0.0000 |   1.0000 |   1.8000 |   6.2420 |   3.6800 | 328522.2000 | 633.6499 |
| RatecodeID            |     1.0000 |   1.0000 |   1.0000 |   5.2509 |   1.0000 |     99.0000 |  19.7461 |
| PULocationID          |     1.0000 | 114.0000 | 161.0000 | 161.1912 | 233.0000 |    265.0000 |  67.1343 |
| DOLocationID          |     1.0000 | 107.0000 | 161.0000 | 160.8020 | 234.0000 |    265.0000 |  71.0726 |
| payment_type          |     0.0000 |   0.0000 |   1.0000 |   0.8211 |   1.0000 |      4.0000 |   0.6834 |
| fare_amount           | -2084.1000 |  10.0000 |  16.3000 |  21.6467 |  27.5000 |   2084.1000 |  18.5691 |
| extra                 |    -7.5000 |   0.0000 |   0.0000 |   1.0138 |   1.0000 |     20.7100 |   1.6973 |
| mta_tax               |    -0.5000 |   0.5000 |   0.5000 |   0.4866 |   0.5000 |      4.7500 |   0.1018 |
| tip_amount            |   -68.0000 |   0.0000 |   2.0000 |   2.6392 |   3.7900 |    500.0000 |   3.8346 |
| tolls_amount          |  -111.7900 |   0.0000 |   0.0000 |   0.4908 |   0.0000 |    111.7900 |   2.1019 |
| improvement_surcharge |    -1.0000 |   1.0000 |   1.0000 |   0.9530 |   1.0000 |      1.0000 |   0.2456 |
| total_amount          | -2088.8500 |  17.6400 |  24.0000 |  30.1133 |  35.4300 |   2088.8500 |  22.0799 |
| congestion_surcharge  |    -2.5000 |   2.5000 |   2.5000 |   2.1726 |   2.5000 |      2.5000 |   0.9073 |
| Airport_fee           |    -1.7500 |   0.0000 |   0.0000 |   0.1430 |   0.0000 |     26.7500 |   0.5204 |
| cbd_congestion_fee    |    -0.7500 |   0.0000 |   0.7500 |   0.5225 |   0.7500 |      0.7500 |   0.3531 |

## Datetime Coverage (full-data)

| column                | min_ts              | max_ts              | span             |
|:----------------------|:--------------------|:--------------------|:-----------------|
| tpep_pickup_datetime  | 2026-01-31 23:31:23 | 2026-03-01 00:51:48 | 28 days 01:20:25 |
| tpep_dropoff_datetime | 2026-01-31 23:36:52 | 2026-03-01 23:11:29 | 28 days 23:34:37 |

## Datetime Distribution by Day (full-data)

| column                | day        |   rows |   row_% |
|:----------------------|:-----------|-------:|--------:|
| tpep_pickup_datetime  | 2026-01-31 |     12 |  0.0004 |
| tpep_pickup_datetime  | 2026-02-01 | 123131 |  3.6216 |
| tpep_pickup_datetime  | 2026-02-02 | 113919 |  3.3507 |
| tpep_pickup_datetime  | 2026-02-03 | 125167 |  3.6815 |
| tpep_pickup_datetime  | 2026-02-04 | 131494 |  3.8676 |
| tpep_pickup_datetime  | 2026-02-05 | 136461 |  4.0137 |
| tpep_pickup_datetime  | 2026-02-06 | 135750 |  3.9928 |
| tpep_pickup_datetime  | 2026-02-07 | 154672 |  4.5494 |
| tpep_pickup_datetime  | 2026-02-08 | 130469 |  3.8375 |
| tpep_pickup_datetime  | 2026-02-09 | 112524 |  3.3097 |
| tpep_pickup_datetime  | 2026-02-10 | 118818 |  3.4948 |
| tpep_pickup_datetime  | 2026-02-11 | 130001 |  3.8237 |
| tpep_pickup_datetime  | 2026-02-12 | 143696 |  4.2265 |
| tpep_pickup_datetime  | 2026-02-13 | 141907 |  4.1739 |
| tpep_pickup_datetime  | 2026-02-14 | 133489 |  3.9263 |
| tpep_pickup_datetime  | 2026-02-15 | 113601 |  3.3413 |
| tpep_pickup_datetime  | 2026-02-16 |  86653 |  2.5487 |
| tpep_pickup_datetime  | 2026-02-17 | 106028 |  3.1186 |
| tpep_pickup_datetime  | 2026-02-18 | 121392 |  3.5705 |
| tpep_pickup_datetime  | 2026-02-19 | 125845 |  3.7015 |
| tpep_pickup_datetime  | 2026-02-20 | 129620 |  3.8125 |
| tpep_pickup_datetime  | 2026-02-21 | 136152 |  4.0046 |
| tpep_pickup_datetime  | 2026-02-22 |  85555 |  2.5164 |
| tpep_pickup_datetime  | 2026-02-23 |  26039 |  0.7659 |
| tpep_pickup_datetime  | 2026-02-24 | 104315 |  3.0682 |
| tpep_pickup_datetime  | 2026-02-25 | 122987 |  3.6174 |
| tpep_pickup_datetime  | 2026-02-26 | 133200 |  3.9178 |
| tpep_pickup_datetime  | 2026-02-27 | 139118 |  4.0919 |
| tpep_pickup_datetime  | 2026-02-28 | 137847 |  4.0545 |
| tpep_pickup_datetime  | 2026-03-01 |      4 |  0.0001 |
| tpep_dropoff_datetime | 2026-01-31 |      2 |  0.0001 |
| tpep_dropoff_datetime | 2026-02-01 | 122336 |  3.5983 |
| tpep_dropoff_datetime | 2026-02-02 | 114085 |  3.3556 |
| tpep_dropoff_datetime | 2026-02-03 | 125017 |  3.6771 |
| tpep_dropoff_datetime | 2026-02-04 | 131446 |  3.8662 |
| tpep_dropoff_datetime | 2026-02-05 | 136063 |  4.0020 |
| tpep_dropoff_datetime | 2026-02-06 | 134932 |  3.9687 |
| tpep_dropoff_datetime | 2026-02-07 | 154556 |  4.5459 |
| tpep_dropoff_datetime | 2026-02-08 | 131550 |  3.8693 |
| tpep_dropoff_datetime | 2026-02-09 | 113128 |  3.3274 |
| tpep_dropoff_datetime | 2026-02-10 | 118668 |  3.4904 |
| tpep_dropoff_datetime | 2026-02-11 | 129873 |  3.8199 |
| tpep_dropoff_datetime | 2026-02-12 | 143239 |  4.2131 |
| tpep_dropoff_datetime | 2026-02-13 | 140875 |  4.1435 |
| tpep_dropoff_datetime | 2026-02-14 | 133316 |  3.9212 |
| tpep_dropoff_datetime | 2026-02-15 | 115015 |  3.3829 |
| tpep_dropoff_datetime | 2026-02-16 |  87038 |  2.5600 |
| tpep_dropoff_datetime | 2026-02-17 | 106002 |  3.1178 |
| tpep_dropoff_datetime | 2026-02-18 | 121419 |  3.5713 |
| tpep_dropoff_datetime | 2026-02-19 | 125439 |  3.6895 |
| tpep_dropoff_datetime | 2026-02-20 | 128886 |  3.7909 |
| tpep_dropoff_datetime | 2026-02-21 | 135296 |  3.9795 |
| tpep_dropoff_datetime | 2026-02-22 |  87952 |  2.5869 |
| tpep_dropoff_datetime | 2026-02-23 |  26029 |  0.7656 |
| tpep_dropoff_datetime | 2026-02-24 | 103921 |  3.0566 |
| tpep_dropoff_datetime | 2026-02-25 | 122798 |  3.6118 |
| tpep_dropoff_datetime | 2026-02-26 | 132778 |  3.9054 |
| tpep_dropoff_datetime | 2026-02-27 | 138236 |  4.0659 |
| tpep_dropoff_datetime | 2026-02-28 | 137635 |  4.0482 |
| tpep_dropoff_datetime | 2026-03-01 |   2336 |  0.0687 |

## Top Values (full-data, top 5)

| column                | top_5_values                                                        |
|:----------------------|:--------------------------------------------------------------------|
| VendorID              | 2: 2716417, 1: 637609, 7: 40241, 6: 5599                            |
| passenger_count       | 1.0: 1974695, <NULL>: 1023317, 2.0: 283138, 3.0: 57521, 4.0: 36347  |
| RatecodeID            | 1.0: 2162640, <NULL>: 1023317, 99.0: 100895, 2.0: 70087, 5.0: 25861 |
| store_and_fwd_flag    | N: 2374445, <NULL>: 1023317, Y: 2104                                |
| payment_type          | 1: 2051661, 0: 1023317, 2: 273616, 4: 38888, 3: 12384               |
| mta_tax               | 0.5: 3334358, 0.0: 39670, -0.5: 25829, 4.75: 2, 3.75: 2             |
| improvement_surcharge | 1.0: 3265497, 0.0: 101745, -1.0: 27043, 0.3: 5581                   |
| congestion_surcharge  | 2.5: 2086570, <NULL>: 1023317, 0.0: 268699, -2.5: 21279, 1.0: 1     |
| Airport_fee           | 0.0: 2175248, <NULL>: 1023317, 1.75: 194546, -1.75: 5487, 6.75: 953 |
| cbd_congestion_fee    | 0.75: 2385966, 0.0: 996421, -0.75: 17479                            |

## Data Quality Signals

- Duplicate rows in full data: `0` / `3399866`.
- Numeric columns containing negative values: `fare_amount`, `extra`, `mta_tax`, `tip_amount`, `tolls_amount`, `improvement_surcharge`, `total_amount`, `congestion_surcharge`, `Airport_fee`, `cbd_congestion_fee`.

## Data Preview

|   VendorID | tpep_pickup_datetime   | tpep_dropoff_datetime   |   passenger_count |   trip_distance |   RatecodeID | store_and_fwd_flag   |   PULocationID |   DOLocationID |   payment_type |   fare_amount |   extra |   mta_tax |   tip_amount |   tolls_amount |   improvement_surcharge |   total_amount |   congestion_surcharge |   Airport_fee |   cbd_congestion_fee |
|-----------:|:-----------------------|:------------------------|------------------:|----------------:|-------------:|:---------------------|---------------:|---------------:|---------------:|--------------:|--------:|----------:|-------------:|---------------:|------------------------:|---------------:|-----------------------:|--------------:|---------------------:|
|          7 | 2026-02-01 00:05:57    | 2026-02-01 00:05:57     |                 1 |            0.94 |            1 | N                    |            107 |            170 |              1 |           7.2 |    0    |       0.5 |         0    |              0 |                       1 |          12.95 |                    2.5 |          0    |                 0.75 |
|          7 | 2026-02-01 00:35:58    | 2026-02-01 00:35:58     |                 1 |            1.93 |            1 | N                    |            234 |            141 |              1 |          11.4 |    0    |       0.5 |         3.43 |              0 |                       1 |          20.58 |                    2.5 |          0    |                 0.75 |
|          2 | 2026-02-01 00:08:41    | 2026-02-01 00:39:32     |                 1 |            9.99 |            1 | N                    |            138 |             68 |              1 |          44.3 |    6    |       0.5 |        11.01 |              0 |                       1 |          67.81 |                    2.5 |          1.75 |                 0.75 |
|          1 | 2026-02-01 00:29:06    | 2026-02-01 00:41:04     |                 0 |            1.7  |            1 | N                    |            209 |             13 |              1 |          12.8 |    4.25 |       0.5 |         3.7  |              0 |                       1 |          22.25 |                    2.5 |          0    |                 0.75 |
|          1 | 2026-02-01 00:53:52    | 2026-02-01 01:11:21     |                 0 |            3.7  |            1 | N                    |            249 |            229 |              1 |          19.8 |    4.25 |       0.5 |         6.35 |              0 |                       1 |          31.9  |                    2.5 |          0    |                 0.75 |
|          2 | 2026-02-01 00:24:29    | 2026-02-01 00:36:01     |                 1 |            1.6  |            1 | N                    |            113 |             90 |              1 |          12.1 |    1    |       0.5 |         0.09 |              0 |                       1 |          17.94 |                    2.5 |          0    |                 0.75 |
|          2 | 2026-02-01 00:40:20    | 2026-02-01 00:54:57     |                 2 |            1.73 |            1 | N                    |            234 |            144 |              1 |          14.2 |    1    |       0.5 |         1    |              0 |                       1 |          20.95 |                    2.5 |          0    |                 0.75 |
|          2 | 2026-02-01 00:11:48    | 2026-02-01 00:22:41     |                 1 |            2.27 |            1 | N                    |            237 |            151 |              1 |          12.8 |    1    |       0.5 |         2    |              0 |                       1 |          19.8  |                    2.5 |          0    |                 0    |
|          2 | 2026-02-01 00:02:38    | 2026-02-01 00:26:38     |                 1 |            4.92 |            1 | N                    |            148 |            263 |              1 |          26.1 |    1    |       0.5 |         4.78 |              0 |                       1 |          36.63 |                    2.5 |          0    |                 0.75 |
|          2 | 2026-02-01 00:05:56    | 2026-02-01 00:22:06     |                 1 |            1.98 |            1 | N                    |             79 |            170 |              1 |          15.6 |    1    |       0.5 |         4.27 |              0 |                       1 |          25.62 |                    2.5 |          0    |                 0.75 |
