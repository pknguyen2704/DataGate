# Data Overview: green_tripdata_2025-01.parquet

## Dataset Summary

| metric             | value                                                                                              |
|--------------------|----------------------------------------------------------------------------------------------------|
| file               | /Users/andrew/Dev/Projects/DataGate/experiments/data/parquets/green/green_tripdata_2025-01.parquet |
| rows               | 48326                                                                                              |
| columns            | 21                                                                                                 |
| row_groups         | 1                                                                                                  |
| file_size_mb       | 1.12                                                                                               |
| sample_rows_loaded | 5000                                                                                               |

## Schema

| column                | parquet_type   | nullable   |
|-----------------------|----------------|------------|
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

## Column Health (sample-based)

| column                | dtype          |   non_null |   null |   null_% |   unique_in_sample |
|-----------------------|----------------|------------|--------|----------|--------------------|
| VendorID              | int32          |       5000 |      0 |   0.0000 |                  2 |
| lpep_pickup_datetime  | datetime64[us] |       5000 |      0 |   0.0000 |               4936 |
| lpep_dropoff_datetime | datetime64[us] |       5000 |      0 |   0.0000 |               4938 |
| store_and_fwd_flag    | str            |       5000 |      0 |   0.0000 |                  2 |
| RatecodeID            | int64          |       5000 |      0 |   0.0000 |                  7 |
| PULocationID          | int32          |       5000 |      0 |   0.0000 |                145 |
| DOLocationID          | int32          |       5000 |      0 |   0.0000 |                216 |
| passenger_count       | int64          |       5000 |      0 |   0.0000 |                  8 |
| trip_distance         | float64        |       5000 |      0 |   0.0000 |                909 |
| fare_amount           | float64        |       5000 |      0 |   0.0000 |                228 |
| extra                 | float64        |       5000 |      0 |   0.0000 |                 11 |
| mta_tax               | float64        |       5000 |      0 |   0.0000 |                  6 |
| tip_amount            | float64        |       5000 |      0 |   0.0000 |                608 |
| tolls_amount          | float64        |       5000 |      0 |   0.0000 |                 10 |
| ehail_fee             | float64        |          0 |   5000 | 100.0000 |                  0 |
| improvement_surcharge | float64        |       5000 |      0 |   0.0000 |                  4 |
| total_amount          | float64        |       5000 |      0 |   0.0000 |               1343 |
| payment_type          | int64          |       5000 |      0 |   0.0000 |                  4 |
| trip_type             | float64        |       4998 |      2 |   0.0400 |                  2 |
| congestion_surcharge  | float64        |       5000 |      0 |   0.0000 |                  3 |
| cbd_congestion_fee    | float64        |       5000 |      0 |   0.0000 |                  1 |

## Numeric Statistics (sample-based)

| column                |       min |     p25 |   median |     mean |      p75 |      max |     std |
|-----------------------|-----------|---------|----------|----------|----------|----------|---------|
| VendorID              |    1.0000 |  2.0000 |   2.0000 |   1.8790 |   2.0000 |   2.0000 |  0.3262 |
| RatecodeID            |    1.0000 |  1.0000 |   1.0000 |   1.3044 |   1.0000 |  99.0000 |  2.1900 |
| PULocationID          |    7.0000 | 74.0000 |  75.0000 |  93.6444 |  97.0000 | 265.0000 | 54.5772 |
| DOLocationID          |    1.0000 | 74.0000 | 138.0000 | 139.9092 | 226.0000 | 265.0000 | 78.0846 |
| passenger_count       |    0.0000 |  1.0000 |   1.0000 |   1.3308 |   1.0000 |   8.0000 |  1.0153 |
| trip_distance         |    0.0000 |  1.0500 |   1.7500 |   2.6537 |   3.0000 |  86.5000 |  3.3213 |
| fare_amount           | -113.0000 |  9.3000 |  12.8000 |  17.4996 |  19.8000 | 336.2000 | 16.6660 |
| extra                 |   -1.0000 |  0.0000 |   0.0000 |   0.8451 |   1.0000 |   7.5000 |  1.2210 |
| mta_tax               |   -0.5000 |  0.5000 |   0.5000 |   0.5816 |   0.5000 |   4.2500 |  0.3625 |
| tip_amount            |    0.0000 |  0.0000 |   2.0000 |   2.3884 |   3.5000 |  62.0000 |  3.3820 |
| tolls_amount          |    0.0000 |  0.0000 |   0.0000 |   0.2019 |   0.0000 |  33.7000 |  1.4217 |
| improvement_surcharge |   -1.0000 |  1.0000 |   1.0000 |   0.9841 |   1.0000 |   1.0000 |  0.1456 |
| total_amount          | -114.0000 | 12.9600 |  18.2250 |  23.1094 |  26.4225 | 371.4000 | 18.9218 |
| payment_type          |    1.0000 |  1.0000 |   1.0000 |   1.2984 |   2.0000 |   4.0000 |  0.4819 |
| trip_type             |    1.0000 |  1.0000 |   1.0000 |   1.0608 |   1.0000 |   2.0000 |  0.2390 |
| congestion_surcharge  |    0.0000 |  0.0000 |   0.0000 |   0.7990 |   2.7500 |   2.7500 |  1.2485 |
| cbd_congestion_fee    |    0.0000 |  0.0000 |   0.0000 |   0.0000 |   0.0000 |   0.0000 |  0.0000 |

## Datetime Coverage (sample-based)

| column                | min_ts              | max_ts              | span             |
|-----------------------|---------------------|---------------------|------------------|
| lpep_pickup_datetime  | 2024-12-25 23:13:15 | 2025-01-05 16:17:50 | 10 days 17:04:35 |
| lpep_dropoff_datetime | 2024-12-25 23:13:17 | 2025-01-05 16:48:21 | 10 days 17:35:04 |

## Top Values (sample-based, top 5)

| column                | top_5_values_in_sample                           |
|-----------------------|--------------------------------------------------|
| VendorID              | 2: 4395, 1: 605                                  |
| store_and_fwd_flag    | N: 4993, Y: 7                                    |
| RatecodeID            | 1: 4652, 5: 321, 2: 15, 3: 5, 4: 4               |
| passenger_count       | 1: 4093, 2: 524, 6: 112, 5: 110, 0: 76           |
| extra                 | 0.0: 2895, 2.5: 973, 1.0: 900, 2.75: 97, 5.0: 60 |
| mta_tax               | 0.5: 4077, 1.5: 580, 0.0: 326, -0.5: 14, 1.0: 2  |
| tolls_amount          | 0.0: 4872, 6.94: 113, 13.38: 5, 3.18: 4, 14.0: 1 |
| ehail_fee             | <NULL>: 5000                                     |
| improvement_surcharge | 1.0: 4928, 0.3: 31, 0.0: 24, -1.0: 17            |
| payment_type          | 1: 3559, 2: 1396, 3: 39, 4: 6                    |
| trip_type             | 1.0: 4694, 2.0: 304, <NULL>: 2                   |
| congestion_surcharge  | 0.0: 3547, 2.75: 1450, 2.5: 3                    |
| cbd_congestion_fee    | 0.0: 5000                                        |

## Data Quality Signals

- Duplicate rows in sample: `0` / `5000`.
- Columns with >= 50% null in sample: `ehail_fee`.
- Near-constant columns in sample: `ehail_fee`, `cbd_congestion_fee`.
- High-cardinality / ID-like columns: `lpep_pickup_datetime`, `lpep_dropoff_datetime`.
- Numeric columns containing negative values: `fare_amount`, `extra`, `mta_tax`, `improvement_surcharge`, `total_amount`.

## Sample Preview

|   VendorID | lpep_pickup_datetime   | lpep_dropoff_datetime   | store_and_fwd_flag   |   RatecodeID |   PULocationID |   DOLocationID |   passenger_count |   trip_distance |   fare_amount |   extra |   mta_tax |   tip_amount |   tolls_amount |   ehail_fee |   improvement_surcharge |   total_amount |   payment_type |   trip_type |   congestion_surcharge |   cbd_congestion_fee |
|-----------:|:-----------------------|:------------------------|:---------------------|-------------:|---------------:|---------------:|------------------:|----------------:|--------------:|--------:|----------:|-------------:|---------------:|------------:|------------------------:|---------------:|---------------:|------------:|-----------------------:|---------------------:|
|          2 | 2025-01-01 00:03:01    | 2025-01-01 00:17:12     | N                    |            1 |             75 |            235 |                 1 |            5.93 |         24.7  |       1 |       0.5 |         6.8  |           0    |         nan |                       1 |          34    |              1 |           1 |                   0    |                    0 |
|          2 | 2025-01-01 00:19:59    | 2025-01-01 00:25:52     | N                    |            1 |            166 |             75 |                 1 |            1.32 |          8.6  |       1 |       0.5 |         0    |           0    |         nan |                       1 |          11.1  |              2 |           1 |                   0    |                    0 |
|          2 | 2025-01-01 00:05:29    | 2025-01-01 00:07:21     | N                    |            5 |            171 |             73 |                 1 |            0.41 |         25.55 |       0 |       0   |         0    |           0    |         nan |                       1 |          26.55 |              2 |           2 |                   0    |                    0 |
|          2 | 2025-01-01 00:52:24    | 2025-01-01 01:07:52     | N                    |            1 |             74 |            223 |                 1 |            4.12 |         21.2  |       1 |       0.5 |         6.13 |           6.94 |         nan |                       1 |          36.77 |              1 |           1 |                   0    |                    0 |
|          2 | 2025-01-01 00:25:05    | 2025-01-01 01:01:10     | N                    |            1 |             66 |            158 |                 1 |            4.71 |         33.8  |       1 |       0.5 |         7.81 |           0    |         nan |                       1 |          46.86 |              1 |           1 |                   2.75 |                    0 |
|          2 | 2025-01-01 01:03:45    | 2025-01-01 01:42:09     | N                    |            1 |            260 |            260 |                 1 |            4.26 |         31    |       1 |       0.5 |         0    |           0    |         nan |                       1 |          33.5  |              2 |           1 |                   0    |                    0 |
|          2 | 2025-01-01 00:28:12    | 2025-01-01 00:37:53     | N                    |            1 |              7 |            202 |                 1 |            2    |         11.4  |       1 |       0.5 |        22    |           0    |         nan |                       1 |          35.9  |              1 |           1 |                   0    |                    0 |
|          2 | 2025-01-01 00:25:38    | 2025-01-01 00:36:47     | N                    |            1 |            166 |            244 |                 1 |            2.09 |         13.5  |       1 |       0.5 |         0    |           0    |         nan |                       1 |          16    |              2 |           1 |                   0    |                    0 |
|          2 | 2025-01-01 00:52:04    | 2025-01-01 00:58:36     | N                    |            1 |            166 |            151 |                 1 |            0.95 |          7.9  |       1 |       0.5 |         2.08 |           0    |         nan |                       1 |          12.48 |              1 |           1 |                   0    |                    0 |
|          2 | 2024-12-31 22:42:13    | 2024-12-31 22:42:31     | N                    |            3 |             74 |             74 |                 1 |            0.06 |         23    |       1 |       0   |         0    |           0    |         nan |                       1 |          25    |              2 |           1 |                   0    |                    0 |
