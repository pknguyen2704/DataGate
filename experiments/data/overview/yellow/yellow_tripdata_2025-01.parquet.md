# Data Overview: yellow_tripdata_2025-01.parquet

## Dataset Summary

| metric             | value                                                                                                |
|--------------------|------------------------------------------------------------------------------------------------------|
| file               | /Users/andrew/Dev/Projects/DataGate/experiments/data/parquets/yellow/yellow_tripdata_2025-01.parquet |
| rows               | 3475226                                                                                              |
| columns            | 20                                                                                                   |
| row_groups         | 4                                                                                                    |
| file_size_mb       | 56.42                                                                                                |
| sample_rows_loaded | 5000                                                                                                 |

## Schema

| column                | parquet_type   | nullable   |
|-----------------------|----------------|------------|
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

## Column Health (sample-based)

| column                | dtype          |   non_null |   null |   null_% |   unique_in_sample |
|-----------------------|----------------|------------|--------|----------|--------------------|
| VendorID              | int32          |       5000 |      0 |   0.0000 |                  2 |
| tpep_pickup_datetime  | datetime64[us] |       5000 |      0 |   0.0000 |               2610 |
| tpep_dropoff_datetime | datetime64[us] |       5000 |      0 |   0.0000 |               2988 |
| passenger_count       | int64          |       5000 |      0 |   0.0000 |                  8 |
| trip_distance         | float64        |       5000 |      0 |   0.0000 |                913 |
| RatecodeID            | int64          |       5000 |      0 |   0.0000 |                  6 |
| store_and_fwd_flag    | str            |       5000 |      0 |   0.0000 |                  2 |
| PULocationID          | int32          |       5000 |      0 |   0.0000 |                 95 |
| DOLocationID          | int32          |       5000 |      0 |   0.0000 |                174 |
| payment_type          | int64          |       5000 |      0 |   0.0000 |                  4 |
| fare_amount           | float64        |       5000 |      0 |   0.0000 |                197 |
| extra                 | float64        |       5000 |      0 |   0.0000 |                 12 |
| mta_tax               | float64        |       5000 |      0 |   0.0000 |                  3 |
| tip_amount            | float64        |       5000 |      0 |   0.0000 |                491 |
| tolls_amount          | float64        |       5000 |      0 |   0.0000 |                 16 |
| improvement_surcharge | float64        |       5000 |      0 |   0.0000 |                  3 |
| total_amount          | float64        |       5000 |      0 |   0.0000 |               1012 |
| congestion_surcharge  | float64        |       5000 |      0 |   0.0000 |                  3 |
| Airport_fee           | float64        |       5000 |      0 |   0.0000 |                  3 |
| cbd_congestion_fee    | float64        |       5000 |      0 |   0.0000 |                  1 |

## Numeric Statistics (sample-based)

| column                |       min |      p25 |   median |     mean |      p75 |      max |     std |
|-----------------------|-----------|----------|----------|----------|----------|----------|---------|
| VendorID              |    1.0000 |   2.0000 |   2.0000 |   1.7980 |   2.0000 |   2.0000 |  0.4015 |
| passenger_count       |    0.0000 |   1.0000 |   1.0000 |   1.5140 |   2.0000 |   9.0000 |  0.8998 |
| trip_distance         |    0.0000 |   1.0800 |   1.8700 |   2.9037 |   3.3900 |  40.7900 |  3.3883 |
| RatecodeID            |    1.0000 |   1.0000 |   1.0000 |   1.1712 |   1.0000 |  99.0000 |  3.4174 |
| PULocationID          |    4.0000 | 114.0000 | 161.0000 | 163.7378 | 234.0000 | 265.0000 | 64.6260 |
| DOLocationID          |    4.0000 | 107.0000 | 162.0000 | 164.0938 | 236.0000 | 265.0000 | 71.0851 |
| payment_type          |    1.0000 |   1.0000 |   1.0000 |   1.2632 |   1.0000 |   4.0000 |  0.6334 |
| fare_amount           | -111.5000 |   8.6000 |  13.5000 |  17.2309 |  21.9000 | 450.0000 | 16.8815 |
| extra                 |   -6.0000 |   1.0000 |   1.0000 |   1.5131 |   1.0000 |  10.2500 |  1.2971 |
| mta_tax               |   -0.5000 |   0.5000 |   0.5000 |   0.4734 |   0.5000 |   0.5000 |  0.1526 |
| tip_amount            |   -3.0000 |   1.0000 |   3.0000 |   3.3300 |   4.5675 |  46.4200 |  3.2656 |
| tolls_amount          |   -6.9400 |   0.0000 |   0.0000 |   0.2536 |   0.0000 |  40.6800 |  1.6168 |
| improvement_surcharge |   -1.0000 |   1.0000 |   1.0000 |   0.9558 |   1.0000 |   1.0000 |  0.2930 |
| total_amount          | -123.4400 |  15.7225 |  21.3200 |  25.5913 |  31.0000 | 451.0000 | 19.7912 |
| congestion_surcharge  |   -2.5000 |   2.5000 |   2.5000 |   2.2620 |   2.5000 |   2.5000 |  0.8837 |
| Airport_fee           |   -1.7500 |   0.0000 |   0.0000 |   0.0525 |   0.0000 |   1.7500 |  0.3126 |
| cbd_congestion_fee    |    0.0000 |   0.0000 |   0.0000 |   0.0000 |   0.0000 |   0.0000 |  0.0000 |

## Datetime Coverage (sample-based)

| column                | min_ts              | max_ts              | span            |
|-----------------------|---------------------|---------------------|-----------------|
| tpep_pickup_datetime  | 2024-12-31 23:24:31 | 2025-01-01 01:03:32 | 0 days 01:39:01 |
| tpep_dropoff_datetime | 2024-12-31 23:25:35 | 2025-01-02 00:00:00 | 1 days 00:34:25 |

## Top Values (sample-based, top 5)

| column                | top_5_values_in_sample                           |
|-----------------------|--------------------------------------------------|
| VendorID              | 2: 3990, 1: 1010                                 |
| passenger_count       | 1: 3270, 2: 1145, 3: 257, 4: 247, 0: 35          |
| RatecodeID            | 1: 4894, 5: 45, 2: 37, 4: 15, 99: 6              |
| store_and_fwd_flag    | N: 4987, Y: 13                                   |
| payment_type          | 1: 4040, 2: 766, 4: 162, 3: 32                   |
| extra                 | 1.0: 3773, 3.5: 928, -1.0: 101, 0.0: 90, 6.0: 68 |
| mta_tax               | 0.5: 4841, -0.5: 107, 0.0: 52                    |
| improvement_surcharge | 1.0: 4888, -1.0: 109, 0.0: 3                     |
| congestion_surcharge  | 2.5: 4621, 0.0: 282, -2.5: 97                    |
| Airport_fee           | 0.0: 4836, 1.75: 157, -1.75: 7                   |
| cbd_congestion_fee    | 0.0: 5000                                        |

## Data Quality Signals

- Duplicate rows in sample: `0` / `5000`.
- Near-constant columns in sample: `cbd_congestion_fee`.
- Numeric columns containing negative values: `fare_amount`, `extra`, `mta_tax`, `tip_amount`, `tolls_amount`, `improvement_surcharge`, `total_amount`, `congestion_surcharge`, `Airport_fee`.

## Sample Preview

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
