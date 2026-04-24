# Data Overview: yellow_tripdata_2025-07.parquet

## Dataset Summary

| metric       | value                                                                               |
|:-------------|:------------------------------------------------------------------------------------|
| file         | /root/Dev/DataGate/experiments/data/parquets/yellow/yellow_tripdata_2025-07.parquet |
| rows         | 3898963                                                                             |
| columns      | 20                                                                                  |
| row_groups   | 4                                                                                   |
| file_size_mb | 63.84                                                                               |
| rows_loaded  | 3898963                                                                             |

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
| VendorID              | int32          |    3898963 |       0 |   0.0000 |        4 |
| tpep_pickup_datetime  | datetime64[us] |    3898963 |       0 |   0.0000 |  1810838 |
| tpep_dropoff_datetime | datetime64[us] |    3898963 |       0 |   0.0000 |  1810965 |
| passenger_count       | float64        |    2860208 | 1038755 |  26.6418 |       10 |
| trip_distance         | float64        |    3898963 |       0 |   0.0000 |     5075 |
| RatecodeID            | float64        |    2860208 | 1038755 |  26.6418 |        7 |
| store_and_fwd_flag    | str            |    2860208 | 1038755 |  26.6418 |        2 |
| PULocationID          | int32          |    3898963 |       0 |   0.0000 |      261 |
| DOLocationID          | int32          |    3898963 |       0 |   0.0000 |      261 |
| payment_type          | int64          |    3898963 |       0 |   0.0000 |        5 |
| fare_amount           | float64        |    3898963 |       0 |   0.0000 |    11023 |
| extra                 | float64        |    3898963 |       0 |   0.0000 |       71 |
| mta_tax               | float64        |    3898963 |       0 |   0.0000 |       11 |
| tip_amount            | float64        |    3898963 |       0 |   0.0000 |     4610 |
| tolls_amount          | float64        |    3898963 |       0 |   0.0000 |     1295 |
| improvement_surcharge | float64        |    3898963 |       0 |   0.0000 |        4 |
| total_amount          | float64        |    3898963 |       0 |   0.0000 |    22826 |
| congestion_surcharge  | float64        |    2860208 | 1038755 |  26.6418 |        5 |
| Airport_fee           | float64        |    2860208 | 1038755 |  26.6418 |        5 |
| cbd_congestion_fee    | float64        |    3898963 |       0 |   0.0000 |        5 |

## Numeric Statistics (full-data)

| column                |        min |      p25 |   median |     mean |      p75 |         max |      std |
|:----------------------|-----------:|---------:|---------:|---------:|---------:|------------:|---------:|
| VendorID              |     1.0000 |   2.0000 |   2.0000 |   1.8875 |   2.0000 |      7.0000 |   0.7337 |
| passenger_count       |     0.0000 |   1.0000 |   1.0000 |   1.3159 |   1.0000 |      9.0000 |   0.7590 |
| trip_distance         |     0.0000 |   1.0600 |   1.9100 |   7.1048 |   3.9000 | 397994.3700 | 670.0148 |
| RatecodeID            |     1.0000 |   1.0000 |   1.0000 |   3.0058 |   1.0000 |     99.0000 |  13.4903 |
| PULocationID          |     1.0000 | 114.0000 | 161.0000 | 159.3296 | 230.0000 |    265.0000 |  66.2488 |
| DOLocationID          |     1.0000 | 107.0000 | 161.0000 | 159.0559 | 231.0000 |    265.0000 |  70.6247 |
| payment_type          |     0.0000 |   0.0000 |   1.0000 |   0.9270 |   1.0000 |      4.0000 |   0.7939 |
| fare_amount           | -1591.3000 |   8.8200 |  14.2000 |  18.5477 |  23.3000 |   2495.0000 |  20.0714 |
| extra                 |    -7.5000 |   0.0000 |   0.0000 |   1.1072 |   2.5000 |     15.0000 |   1.8039 |
| mta_tax               |    -0.5000 |   0.5000 |   0.5000 |   0.4758 |   0.5000 |   5243.3800 |   2.6593 |
| tip_amount            |   -52.7500 |   0.0000 |   2.0000 |   2.6861 |   3.8500 |    500.0000 |   3.9351 |
| tolls_amount          |  -112.8400 |   0.0000 |   0.0000 |   0.5005 |   0.0000 |    204.1800 |   2.1326 |
| improvement_surcharge |    -1.0000 |   1.0000 |   1.0000 |   0.9460 |   1.0000 |      1.0000 |   0.3002 |
| total_amount          | -1634.7500 |  15.8000 |  21.4200 |  26.8274 |  30.7800 |   5297.8700 |  24.2746 |
| congestion_surcharge  |    -2.5000 |   2.5000 |   2.5000 |   2.1457 |   2.5000 |      2.5000 |   1.0082 |
| Airport_fee           |    -1.7500 |   0.0000 |   0.0000 |   0.1588 |   0.0000 |      6.7500 |   0.5559 |
| cbd_congestion_fee    |    -0.7500 |   0.0000 |   0.7500 |   0.5356 |   0.7500 |      1.5000 |   0.3599 |

## Datetime Coverage (full-data)

| column                | min_ts              | max_ts              | span               |
|:----------------------|:--------------------|:--------------------|:-------------------|
| tpep_pickup_datetime  | 2009-01-01 08:52:26 | 2025-07-31 23:59:59 | 6055 days 15:07:33 |
| tpep_dropoff_datetime | 2009-01-01 10:00:26 | 2025-08-03 17:03:02 | 6058 days 07:02:36 |

## Datetime Distribution by Day (full-data)

| column                | day        |   rows |   row_% |
|:----------------------|:-----------|-------:|--------:|
| tpep_pickup_datetime  | 2009-01-01 |      1 |  0.0000 |
| tpep_pickup_datetime  | 2025-06-30 |      6 |  0.0002 |
| tpep_pickup_datetime  | 2025-07-01 | 131478 |  3.3721 |
| tpep_pickup_datetime  | 2025-07-02 | 112327 |  2.8809 |
| tpep_pickup_datetime  | 2025-07-03 | 105435 |  2.7042 |
| tpep_pickup_datetime  | 2025-07-04 |  88185 |  2.2618 |
| tpep_pickup_datetime  | 2025-07-05 |  94764 |  2.4305 |
| tpep_pickup_datetime  | 2025-07-06 |  96065 |  2.4639 |
| tpep_pickup_datetime  | 2025-07-07 | 102807 |  2.6368 |
| tpep_pickup_datetime  | 2025-07-08 | 131924 |  3.3836 |
| tpep_pickup_datetime  | 2025-07-09 | 136134 |  3.4915 |
| tpep_pickup_datetime  | 2025-07-10 | 129180 |  3.3132 |
| tpep_pickup_datetime  | 2025-07-11 | 124211 |  3.1857 |
| tpep_pickup_datetime  | 2025-07-12 | 136207 |  3.4934 |
| tpep_pickup_datetime  | 2025-07-13 | 118992 |  3.0519 |
| tpep_pickup_datetime  | 2025-07-14 | 136073 |  3.4900 |
| tpep_pickup_datetime  | 2025-07-15 | 133444 |  3.4226 |
| tpep_pickup_datetime  | 2025-07-16 | 144325 |  3.7016 |
| tpep_pickup_datetime  | 2025-07-17 | 147848 |  3.7920 |
| tpep_pickup_datetime  | 2025-07-18 | 128409 |  3.2934 |
| tpep_pickup_datetime  | 2025-07-19 | 136926 |  3.5119 |
| tpep_pickup_datetime  | 2025-07-20 | 123945 |  3.1789 |
| tpep_pickup_datetime  | 2025-07-21 | 111317 |  2.8550 |
| tpep_pickup_datetime  | 2025-07-22 | 123086 |  3.1569 |
| tpep_pickup_datetime  | 2025-07-23 | 130406 |  3.3446 |
| tpep_pickup_datetime  | 2025-07-24 | 134564 |  3.4513 |
| tpep_pickup_datetime  | 2025-07-25 | 137005 |  3.5139 |
| tpep_pickup_datetime  | 2025-07-26 | 140599 |  3.6061 |
| tpep_pickup_datetime  | 2025-07-27 | 118777 |  3.0464 |
| tpep_pickup_datetime  | 2025-07-28 | 120972 |  3.1027 |
| tpep_pickup_datetime  | 2025-07-29 | 139067 |  3.5668 |
| tpep_pickup_datetime  | 2025-07-30 | 142973 |  3.6669 |
| tpep_pickup_datetime  | 2025-07-31 | 141511 |  3.6295 |
| tpep_dropoff_datetime | 2009-01-01 |      1 |  0.0000 |
| tpep_dropoff_datetime | 2025-06-30 |      2 |  0.0001 |
| tpep_dropoff_datetime | 2025-07-01 | 130650 |  3.3509 |
| tpep_dropoff_datetime | 2025-07-02 | 112128 |  2.8758 |
| tpep_dropoff_datetime | 2025-07-03 | 105520 |  2.7064 |
| tpep_dropoff_datetime | 2025-07-04 |  87384 |  2.2412 |
| tpep_dropoff_datetime | 2025-07-05 |  95224 |  2.4423 |
| tpep_dropoff_datetime | 2025-07-06 |  96369 |  2.4717 |
| tpep_dropoff_datetime | 2025-07-07 | 102908 |  2.6394 |
| tpep_dropoff_datetime | 2025-07-08 | 131786 |  3.3800 |
| tpep_dropoff_datetime | 2025-07-09 | 135973 |  3.4874 |
| tpep_dropoff_datetime | 2025-07-10 | 128614 |  3.2987 |
| tpep_dropoff_datetime | 2025-07-11 | 123694 |  3.1725 |
| tpep_dropoff_datetime | 2025-07-12 | 135956 |  3.4870 |
| tpep_dropoff_datetime | 2025-07-13 | 120246 |  3.0841 |
| tpep_dropoff_datetime | 2025-07-14 | 136530 |  3.5017 |
| tpep_dropoff_datetime | 2025-07-15 | 132995 |  3.4110 |
| tpep_dropoff_datetime | 2025-07-16 | 144239 |  3.6994 |
| tpep_dropoff_datetime | 2025-07-17 | 147392 |  3.7803 |
| tpep_dropoff_datetime | 2025-07-18 | 127786 |  3.2774 |
| tpep_dropoff_datetime | 2025-07-19 | 137104 |  3.5164 |
| tpep_dropoff_datetime | 2025-07-20 | 125123 |  3.2091 |
| tpep_dropoff_datetime | 2025-07-21 | 111420 |  2.8577 |
| tpep_dropoff_datetime | 2025-07-22 | 122989 |  3.1544 |
| tpep_dropoff_datetime | 2025-07-23 | 130119 |  3.3373 |
| tpep_dropoff_datetime | 2025-07-24 | 134323 |  3.4451 |
| tpep_dropoff_datetime | 2025-07-25 | 136083 |  3.4902 |
| tpep_dropoff_datetime | 2025-07-26 | 140409 |  3.6012 |
| tpep_dropoff_datetime | 2025-07-27 | 120557 |  3.0920 |
| tpep_dropoff_datetime | 2025-07-28 | 120987 |  3.1031 |
| tpep_dropoff_datetime | 2025-07-29 | 138919 |  3.5630 |
| tpep_dropoff_datetime | 2025-07-30 | 142753 |  3.6613 |
| tpep_dropoff_datetime | 2025-07-31 | 141566 |  3.6309 |
| tpep_dropoff_datetime | 2025-08-01 |   1213 |  0.0311 |
| tpep_dropoff_datetime | 2025-08-03 |      1 |  0.0000 |

## Top Values (full-data, top 5)

| column                | top_5_values                                                          |
|:----------------------|:----------------------------------------------------------------------|
| VendorID              | 2: 3116106, 1: 725095, 7: 55438, 6: 2324                              |
| passenger_count       | 1.0: 2246693, <NULL>: 1038755, 2.0: 389469, 3.0: 103564, 4.0: 79918   |
| RatecodeID            | 1.0: 2637013, <NULL>: 1038755, 2.0: 106210, 99.0: 55307, 5.0: 37925   |
| store_and_fwd_flag    | N: 2848340, <NULL>: 1038755, Y: 11868                                 |
| payment_type          | 1: 2343668, 0: 1038755, 2: 383976, 4: 105080, 3: 27484                |
| mta_tax               | 0.5: 3771398, -0.5: 71936, 0.0: 55438, 1.0: 172, 10.5: 7              |
| improvement_surcharge | 1.0: 3763971, -1.0: 76299, 0.0: 56385, 0.3: 2308                      |
| congestion_surcharge  | 2.5: 2513544, <NULL>: 1038755, 0.0: 288005, -2.5: 58655, 1.0: 3       |
| Airport_fee           | 0.0: 2571193, <NULL>: 1038755, 1.75: 269919, -1.75: 17228, 6.75: 1451 |
| cbd_congestion_fee    | 0.75: 2835632, 0.0: 1012271, -0.75: 51043, 1.5: 15, 1.25: 2           |

## Data Quality Signals

- Duplicate rows in full data: `1` / `3898963`.
- Numeric columns containing negative values: `fare_amount`, `extra`, `mta_tax`, `tip_amount`, `tolls_amount`, `improvement_surcharge`, `total_amount`, `congestion_surcharge`, `Airport_fee`, `cbd_congestion_fee`.

## Data Preview

|   VendorID | tpep_pickup_datetime   | tpep_dropoff_datetime   |   passenger_count |   trip_distance |   RatecodeID | store_and_fwd_flag   |   PULocationID |   DOLocationID |   payment_type |   fare_amount |   extra |   mta_tax |   tip_amount |   tolls_amount |   improvement_surcharge |   total_amount |   congestion_surcharge |   Airport_fee |   cbd_congestion_fee |
|-----------:|:-----------------------|:------------------------|------------------:|----------------:|-------------:|:---------------------|---------------:|---------------:|---------------:|--------------:|--------:|----------:|-------------:|---------------:|------------------------:|---------------:|-----------------------:|--------------:|---------------------:|
|          1 | 2025-07-01 00:29:37    | 2025-07-01 00:45:30     |                 1 |            7.3  |            1 | N                    |            138 |             74 |              1 |          29.6 |    7.75 |       0.5 |         9    |           6.94 |                       1 |          54.79 |                    0   |          1.75 |                 0    |
|          1 | 2025-07-01 00:23:28    | 2025-07-01 01:07:44     |                 1 |           17.7  |            2 | N                    |            132 |            142 |              1 |          70   |    4.25 |       0.5 |         5    |           0    |                       1 |          80.75 |                    2.5 |          1.75 |                 0    |
|          2 | 2025-07-01 00:53:50    | 2025-07-01 01:27:12     |                 1 |            9.98 |            1 | N                    |            138 |             48 |              1 |          43.6 |    6    |       0.5 |        10.87 |           0    |                       1 |          66.97 |                    2.5 |          1.75 |                 0.75 |
|          2 | 2025-07-01 00:58:49    | 2025-07-01 01:15:55     |                 1 |           10.27 |            1 | N                    |            138 |            229 |              1 |          38.7 |    6    |       0.5 |        14.1  |           6.94 |                       1 |          72.24 |                    2.5 |          1.75 |                 0.75 |
|          2 | 2025-07-01 00:09:22    | 2025-07-01 00:23:54     |                 1 |            2.94 |            1 | N                    |            211 |             97 |              1 |          17   |    1    |       0.5 |         3    |           0    |                       1 |          25.75 |                    2.5 |          0    |                 0.75 |
|          1 | 2025-07-01 00:39:14    | 2025-07-01 00:55:21     |                 1 |           11.8  |            1 | N                    |            132 |            155 |              1 |          44.3 |    1    |       0.5 |        14.05 |           0    |                       1 |          60.85 |                    0   |          0    |                 0    |
|          2 | 2025-07-01 00:15:26    | 2025-07-01 00:29:39     |                 1 |            3.87 |            1 | N                    |             79 |            263 |              1 |          17.7 |    1    |       0.5 |         4.69 |           0    |                       1 |          28.14 |                    2.5 |          0    |                 0.75 |
|          2 | 2025-07-01 00:40:58    | 2025-07-01 00:44:15     |                 1 |            0.85 |            1 | N                    |            140 |            262 |              1 |           5.8 |    1    |       0.5 |         2.16 |           0    |                       1 |          12.96 |                    2.5 |          0    |                 0    |
|          2 | 2025-07-01 00:28:12    | 2025-07-01 00:39:49     |                 2 |            2.54 |            1 | N                    |            114 |             50 |              1 |          14.2 |    1    |       0.5 |         3.99 |           0    |                       1 |          23.94 |                    2.5 |          0    |                 0.75 |
|          2 | 2025-07-01 00:38:17    | 2025-07-01 00:55:44     |                 1 |            6.37 |            1 | N                    |            132 |            197 |              1 |          26.8 |    1    |       0.5 |         5.86 |           0    |                       1 |          36.91 |                    0   |          1.75 |                 0    |
