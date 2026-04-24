# Data Overview: yellow_tripdata_2025-01.parquet

## Dataset Summary

| metric       | value                                                                               |
|:-------------|:------------------------------------------------------------------------------------|
| file         | /root/Dev/DataGate/experiments/data/parquets/yellow/yellow_tripdata_2025-01.parquet |
| rows         | 3475226                                                                             |
| columns      | 20                                                                                  |
| row_groups   | 4                                                                                   |
| file_size_mb | 56.42                                                                               |
| rows_loaded  | 3475226                                                                             |

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
| VendorID              | int32          |    3475226 |      0 |   0.0000 |        4 |
| tpep_pickup_datetime  | datetime64[us] |    3475226 |      0 |   0.0000 |  1672077 |
| tpep_dropoff_datetime | datetime64[us] |    3475226 |      0 |   0.0000 |  1671993 |
| passenger_count       | float64        |    2935077 | 540149 |  15.5428 |       10 |
| trip_distance         | float64        |    3475226 |      0 |   0.0000 |     4545 |
| RatecodeID            | float64        |    2935077 | 540149 |  15.5428 |        7 |
| store_and_fwd_flag    | str            |    2935077 | 540149 |  15.5428 |        2 |
| PULocationID          | int32          |    3475226 |      0 |   0.0000 |      261 |
| DOLocationID          | int32          |    3475226 |      0 |   0.0000 |      260 |
| payment_type          | int64          |    3475226 |      0 |   0.0000 |        6 |
| fare_amount           | float64        |    3475226 |      0 |   0.0000 |    11538 |
| extra                 | float64        |    3475226 |      0 |   0.0000 |       77 |
| mta_tax               | float64        |    3475226 |      0 |   0.0000 |        9 |
| tip_amount            | float64        |    3475226 |      0 |   0.0000 |     4197 |
| tolls_amount          | float64        |    3475226 |      0 |   0.0000 |     1234 |
| improvement_surcharge | float64        |    3475226 |      0 |   0.0000 |        4 |
| total_amount          | float64        |    3475226 |      0 |   0.0000 |    21995 |
| congestion_surcharge  | float64        |    2935077 | 540149 |  15.5428 |        3 |
| Airport_fee           | float64        |    2935077 | 540149 |  15.5428 |        7 |
| cbd_congestion_fee    | float64        |    3475226 |      0 |   0.0000 |        3 |

## Numeric Statistics (full-data)

| column                |       min |      p25 |   median |     mean |      p75 |         max |      std |
|:----------------------|----------:|---------:|---------:|---------:|---------:|------------:|---------:|
| VendorID              |    1.0000 |   2.0000 |   2.0000 |   1.7854 |   2.0000 |      7.0000 |   0.4263 |
| passenger_count       |    0.0000 |   1.0000 |   1.0000 |   1.2979 |   1.0000 |      9.0000 |   0.7508 |
| trip_distance         |    0.0000 |   0.9800 |   1.6700 |   5.8551 |   3.1000 | 276423.5700 | 564.6016 |
| RatecodeID            |    1.0000 |   1.0000 |   1.0000 |   2.4825 |   1.0000 |     99.0000 |  11.6328 |
| PULocationID          |    1.0000 | 132.0000 | 162.0000 | 165.1916 | 234.0000 |    265.0000 |  64.5295 |
| DOLocationID          |    1.0000 | 113.0000 | 162.0000 | 164.1252 | 234.0000 |    265.0000 |  69.4017 |
| payment_type          |    0.0000 |   1.0000 |   1.0000 |   1.0366 |   1.0000 |      5.0000 |   0.7013 |
| fare_amount           | -900.0000 |   8.6000 |  12.1100 |  17.0818 |  19.5000 | 863372.1200 | 463.4729 |
| extra                 |   -7.5000 |   0.0000 |   0.0000 |   1.3177 |   2.5000 |     15.0000 |   1.8615 |
| mta_tax               |   -0.5000 |   0.5000 |   0.5000 |   0.4781 |   0.5000 |     10.5000 |   0.1375 |
| tip_amount            |  -86.0000 |   0.0000 |   2.4500 |   2.9598 |   3.9300 |    400.0000 |   3.7797 |
| tolls_amount          | -126.9400 |   0.0000 |   0.0000 |   0.4493 |   0.0000 |    170.9400 |   2.0026 |
| improvement_surcharge |   -1.0000 |   1.0000 |   1.0000 |   0.9548 |   1.0000 |      1.0000 |   0.2782 |
| total_amount          | -901.0000 |  15.2000 |  19.9500 |  25.6113 |  27.7800 | 863380.3700 | 463.6585 |
| congestion_surcharge  |   -2.5000 |   2.5000 |   2.5000 |   2.2252 |   2.5000 |      2.5000 |   0.9040 |
| Airport_fee           |   -1.7500 |   0.0000 |   0.0000 |   0.1239 |   0.0000 |      6.7500 |   0.4725 |
| cbd_congestion_fee    |   -0.7500 |   0.0000 |   0.7500 |   0.4834 |   0.7500 |      0.7500 |   0.3619 |

## Datetime Coverage (full-data)

| column                | min_ts              | max_ts              | span             |
|:----------------------|:--------------------|:--------------------|:-----------------|
| tpep_pickup_datetime  | 2024-12-31 20:47:55 | 2025-02-01 00:00:44 | 31 days 03:12:49 |
| tpep_dropoff_datetime | 2024-12-18 07:52:40 | 2025-02-01 23:44:11 | 45 days 15:51:31 |

## Datetime Distribution by Day (full-data)

| column                | day        |   rows |   row_% |
|:----------------------|:-----------|-------:|--------:|
| tpep_pickup_datetime  | 2024-12-31 |     21 |  0.0006 |
| tpep_pickup_datetime  | 2025-01-01 |  90188 |  2.5952 |
| tpep_pickup_datetime  | 2025-01-02 |  84832 |  2.4410 |
| tpep_pickup_datetime  | 2025-01-03 |  91250 |  2.6257 |
| tpep_pickup_datetime  | 2025-01-04 |  97804 |  2.8143 |
| tpep_pickup_datetime  | 2025-01-05 |  79624 |  2.2912 |
| tpep_pickup_datetime  | 2025-01-06 |  80126 |  2.3056 |
| tpep_pickup_datetime  | 2025-01-07 | 100643 |  2.8960 |
| tpep_pickup_datetime  | 2025-01-08 | 113897 |  3.2774 |
| tpep_pickup_datetime  | 2025-01-09 | 119285 |  3.4324 |
| tpep_pickup_datetime  | 2025-01-10 | 111494 |  3.2083 |
| tpep_pickup_datetime  | 2025-01-11 | 121966 |  3.5096 |
| tpep_pickup_datetime  | 2025-01-12 | 102510 |  2.9497 |
| tpep_pickup_datetime  | 2025-01-13 | 100492 |  2.8917 |
| tpep_pickup_datetime  | 2025-01-14 | 121735 |  3.5029 |
| tpep_pickup_datetime  | 2025-01-15 | 125359 |  3.6072 |
| tpep_pickup_datetime  | 2025-01-16 | 138711 |  3.9914 |
| tpep_pickup_datetime  | 2025-01-17 | 120994 |  3.4816 |
| tpep_pickup_datetime  | 2025-01-18 | 119812 |  3.4476 |
| tpep_pickup_datetime  | 2025-01-19 | 118232 |  3.4021 |
| tpep_pickup_datetime  | 2025-01-20 |  90094 |  2.5925 |
| tpep_pickup_datetime  | 2025-01-21 | 117592 |  3.3837 |
| tpep_pickup_datetime  | 2025-01-22 | 127259 |  3.6619 |
| tpep_pickup_datetime  | 2025-01-23 | 138136 |  3.9749 |
| tpep_pickup_datetime  | 2025-01-24 | 129546 |  3.7277 |
| tpep_pickup_datetime  | 2025-01-25 | 136816 |  3.9369 |
| tpep_pickup_datetime  | 2025-01-26 | 102228 |  2.9416 |
| tpep_pickup_datetime  | 2025-01-27 |  93060 |  2.6778 |
| tpep_pickup_datetime  | 2025-01-28 | 114002 |  3.2804 |
| tpep_pickup_datetime  | 2025-01-29 | 120672 |  3.4723 |
| tpep_pickup_datetime  | 2025-01-30 | 133266 |  3.8347 |
| tpep_pickup_datetime  | 2025-01-31 | 133579 |  3.8438 |
| tpep_pickup_datetime  | 2025-02-01 |      1 |  0.0000 |
| tpep_dropoff_datetime | 2024-12-18 |      1 |  0.0000 |
| tpep_dropoff_datetime | 2024-12-31 |     13 |  0.0004 |
| tpep_dropoff_datetime | 2025-01-01 |  89789 |  2.5837 |
| tpep_dropoff_datetime | 2025-01-02 |  84616 |  2.4348 |
| tpep_dropoff_datetime | 2025-01-03 |  91066 |  2.6204 |
| tpep_dropoff_datetime | 2025-01-04 |  97677 |  2.8107 |
| tpep_dropoff_datetime | 2025-01-05 |  80088 |  2.3045 |
| tpep_dropoff_datetime | 2025-01-06 |  80087 |  2.3045 |
| tpep_dropoff_datetime | 2025-01-07 | 100664 |  2.8966 |
| tpep_dropoff_datetime | 2025-01-08 | 113837 |  3.2757 |
| tpep_dropoff_datetime | 2025-01-09 | 118892 |  3.4211 |
| tpep_dropoff_datetime | 2025-01-10 | 110903 |  3.1912 |
| tpep_dropoff_datetime | 2025-01-11 | 121578 |  3.4984 |
| tpep_dropoff_datetime | 2025-01-12 | 103973 |  2.9918 |
| tpep_dropoff_datetime | 2025-01-13 | 100514 |  2.8923 |
| tpep_dropoff_datetime | 2025-01-14 | 121696 |  3.5018 |
| tpep_dropoff_datetime | 2025-01-15 | 125246 |  3.6040 |
| tpep_dropoff_datetime | 2025-01-16 | 138358 |  3.9813 |
| tpep_dropoff_datetime | 2025-01-17 | 120310 |  3.4619 |
| tpep_dropoff_datetime | 2025-01-18 | 119557 |  3.4403 |
| tpep_dropoff_datetime | 2025-01-19 | 119004 |  3.4244 |
| tpep_dropoff_datetime | 2025-01-20 |  90536 |  2.6052 |
| tpep_dropoff_datetime | 2025-01-21 | 117791 |  3.3894 |
| tpep_dropoff_datetime | 2025-01-22 | 127155 |  3.6589 |
| tpep_dropoff_datetime | 2025-01-23 | 137729 |  3.9632 |
| tpep_dropoff_datetime | 2025-01-24 | 128528 |  3.6984 |
| tpep_dropoff_datetime | 2025-01-25 | 136563 |  3.9296 |
| tpep_dropoff_datetime | 2025-01-26 | 104036 |  2.9936 |
| tpep_dropoff_datetime | 2025-01-27 |  93091 |  2.6787 |
| tpep_dropoff_datetime | 2025-01-28 | 113805 |  3.2748 |
| tpep_dropoff_datetime | 2025-01-29 | 120582 |  3.4698 |
| tpep_dropoff_datetime | 2025-01-30 | 133006 |  3.8273 |
| tpep_dropoff_datetime | 2025-01-31 | 132738 |  3.8196 |
| tpep_dropoff_datetime | 2025-02-01 |   1797 |  0.0517 |

## Top Values (full-data, top 5)

| column                | top_5_values                                                      |
|:----------------------|:------------------------------------------------------------------|
| VendorID              | 2: 2719860, 1: 753671, 7: 1206, 6: 489                            |
| passenger_count       | 1.0: 2322434, <NULL>: 540149, 2.0: 407761, 3.0: 91409, 4.0: 59009 |
| RatecodeID            | 1.0: 2756472, <NULL>: 540149, 2.0: 94420, 99.0: 41963, 5.0: 26501 |
| store_and_fwd_flag    | N: 2927431, <NULL>: 540149, Y: 7646                               |
| payment_type          | 1: 2444393, 0: 540149, 2: 390429, 4: 76481, 3: 23773              |
| mta_tax               | 0.5: 3379839, -0.5: 57140, 0.0: 38170, 1.0: 64, 10.5: 5           |
| improvement_surcharge | 1.0: 3377509, -1.0: 59530, 0.0: 37694, 0.3: 493                   |
| congestion_surcharge  | 2.5: 2660818, <NULL>: 540149, 0.0: 225938, -2.5: 48321            |
| Airport_fee           | 0.0: 2706446, <NULL>: 540149, 1.75: 218203, -1.75: 10411, 1.25: 8 |
| cbd_congestion_fee    | 0.75: 2246495, 0.0: 1222178, -0.75: 6553                          |

## Data Quality Signals

- Duplicate rows in full data: `0` / `3475226`.
- Numeric columns containing negative values: `fare_amount`, `extra`, `mta_tax`, `tip_amount`, `tolls_amount`, `improvement_surcharge`, `total_amount`, `congestion_surcharge`, `Airport_fee`, `cbd_congestion_fee`.

## Data Preview

|   VendorID | tpep_pickup_datetime   | tpep_dropoff_datetime   |   passenger_count |   trip_distance |   RatecodeID | store_and_fwd_flag   |   PULocationID |   DOLocationID |   payment_type |   fare_amount |   extra |   mta_tax |   tip_amount |   tolls_amount |   improvement_surcharge |   total_amount |   congestion_surcharge |   Airport_fee |   cbd_congestion_fee |
|-----------:|:-----------------------|:------------------------|------------------:|----------------:|-------------:|:---------------------|---------------:|---------------:|---------------:|--------------:|--------:|----------:|-------------:|---------------:|------------------------:|---------------:|-----------------------:|--------------:|---------------------:|
|          1 | 2025-01-01 00:18:38    | 2025-01-01 00:26:59     |                 1 |            1.6  |            1 | N                    |            229 |            237 |              1 |          10   |     3.5 |       0.5 |         3    |              0 |                       1 |          18    |                    2.5 |             0 |                    0 |
|          1 | 2025-01-01 00:32:40    | 2025-01-01 00:35:13     |                 1 |            0.5  |            1 | N                    |            236 |            237 |              1 |           5.1 |     3.5 |       0.5 |         2.02 |              0 |                       1 |          12.12 |                    2.5 |             0 |                    0 |
|          1 | 2025-01-01 00:44:04    | 2025-01-01 00:46:01     |                 1 |            0.6  |            1 | N                    |            141 |            141 |              1 |           5.1 |     3.5 |       0.5 |         2    |              0 |                       1 |          12.1  |                    2.5 |             0 |                    0 |
|          2 | 2025-01-01 00:14:27    | 2025-01-01 00:20:01     |                 3 |            0.52 |            1 | N                    |            244 |            244 |              2 |           7.2 |     1   |       0.5 |         0    |              0 |                       1 |           9.7  |                    0   |             0 |                    0 |
|          2 | 2025-01-01 00:21:34    | 2025-01-01 00:25:06     |                 3 |            0.66 |            1 | N                    |            244 |            116 |              2 |           5.8 |     1   |       0.5 |         0    |              0 |                       1 |           8.3  |                    0   |             0 |                    0 |
|          2 | 2025-01-01 00:48:24    | 2025-01-01 01:08:26     |                 2 |            2.63 |            1 | N                    |            239 |             68 |              2 |          19.1 |     1   |       0.5 |         0    |              0 |                       1 |          24.1  |                    2.5 |             0 |                    0 |
|          1 | 2025-01-01 00:14:47    | 2025-01-01 00:16:15     |                 0 |            0.4  |            1 | N                    |            170 |            170 |              1 |           4.4 |     3.5 |       0.5 |         2.35 |              0 |                       1 |          11.75 |                    2.5 |             0 |                    0 |
|          1 | 2025-01-01 00:39:27    | 2025-01-01 00:51:51     |                 0 |            1.6  |            1 | N                    |            234 |            148 |              1 |          12.1 |     3.5 |       0.5 |         2    |              0 |                       1 |          19.1  |                    2.5 |             0 |                    0 |
|          1 | 2025-01-01 00:53:43    | 2025-01-01 01:13:23     |                 0 |            2.8  |            1 | N                    |            148 |            170 |              1 |          19.1 |     3.5 |       0.5 |         3    |              0 |                       1 |          27.1  |                    2.5 |             0 |                    0 |
|          2 | 2025-01-01 00:00:02    | 2025-01-01 00:09:36     |                 1 |            1.71 |            1 | N                    |            237 |            262 |              2 |          11.4 |     1   |       0.5 |         0    |              0 |                       1 |          16.4  |                    2.5 |             0 |                    0 |
