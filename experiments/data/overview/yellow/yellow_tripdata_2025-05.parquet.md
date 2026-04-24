# Data Overview: yellow_tripdata_2025-05.parquet

## Dataset Summary

| metric       | value                                                                               |
|:-------------|:------------------------------------------------------------------------------------|
| file         | /root/Dev/DataGate/experiments/data/parquets/yellow/yellow_tripdata_2025-05.parquet |
| rows         | 4591845                                                                             |
| columns      | 20                                                                                  |
| row_groups   | 5                                                                                   |
| file_size_mb | 74.23                                                                               |
| rows_loaded  | 4591845                                                                             |

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
| VendorID              | int32          |    4591845 |       0 |   0.0000 |        4 |
| tpep_pickup_datetime  | datetime64[us] |    4591845 |       0 |   0.0000 |  1920589 |
| tpep_dropoff_datetime | datetime64[us] |    4591845 |       0 |   0.0000 |  1919209 |
| passenger_count       | float64        |    3395669 | 1196176 |  26.0500 |        9 |
| trip_distance         | float64        |    4591845 |       0 |   0.0000 |     5305 |
| RatecodeID            | float64        |    3395669 | 1196176 |  26.0500 |        7 |
| store_and_fwd_flag    | str            |    3395669 | 1196176 |  26.0500 |        2 |
| PULocationID          | int32          |    4591845 |       0 |   0.0000 |      260 |
| DOLocationID          | int32          |    4591845 |       0 |   0.0000 |      261 |
| payment_type          | int64          |    4591845 |       0 |   0.0000 |        5 |
| fare_amount           | float64        |    4591845 |       0 |   0.0000 |    13895 |
| extra                 | float64        |    4591845 |       0 |   0.0000 |       81 |
| mta_tax               | float64        |    4591845 |       0 |   0.0000 |       10 |
| tip_amount            | float64        |    4591845 |       0 |   0.0000 |     4886 |
| tolls_amount          | float64        |    4591845 |       0 |   0.0000 |     1405 |
| improvement_surcharge | float64        |    4591845 |       0 |   0.0000 |        4 |
| total_amount          | float64        |    4591845 |       0 |   0.0000 |    25235 |
| congestion_surcharge  | float64        |    3395669 | 1196176 |  26.0500 |        3 |
| Airport_fee           | float64        |    3395669 | 1196176 |  26.0500 |        6 |
| cbd_congestion_fee    | float64        |    4591845 |       0 |   0.0000 |        4 |

## Numeric Statistics (full-data)

| column                |        min |      p25 |   median |     mean |      p75 |         max |      std |
|:----------------------|-----------:|---------:|---------:|---------:|---------:|------------:|---------:|
| VendorID              |     1.0000 |   2.0000 |   2.0000 |   1.8757 |   2.0000 |      7.0000 |   0.7239 |
| passenger_count       |     0.0000 |   1.0000 |   1.0000 |   1.2953 |   1.0000 |      9.0000 |   0.7253 |
| trip_distance         |     0.0000 |   1.0600 |   1.8900 |   7.6534 |   3.7700 | 263103.9800 | 653.3947 |
| RatecodeID            |     1.0000 |   1.0000 |   1.0000 |   2.4326 |   1.0000 |     99.0000 |  11.3349 |
| PULocationID          |     1.0000 | 114.0000 | 161.0000 | 161.1871 | 233.0000 |    265.0000 |  66.5505 |
| DOLocationID          |     1.0000 | 107.0000 | 162.0000 | 161.1876 | 233.0000 |    265.0000 |  70.5876 |
| payment_type          |     0.0000 |   0.0000 |   1.0000 |   0.9124 |   1.0000 |      4.0000 |   0.7591 |
| fare_amount           |  -998.0000 |   8.6000 |  14.1500 |  18.3579 |  23.0000 |   1583.6000 |  19.8206 |
| extra                 |   -17.3900 |   0.0000 |   0.0000 |   1.1648 |   2.5000 |    133.6000 |   1.8456 |
| mta_tax               |    -0.5000 |   0.5000 |   0.5000 |   0.4774 |   0.5000 |     22.1400 |   0.1380 |
| tip_amount            |   -90.4400 |   0.0000 |   2.0000 |   2.8581 |   4.0000 |    443.2100 |   4.0439 |
| tolls_amount          |  -148.1700 |   0.0000 |   0.0000 |   0.5115 |   0.0000 |    148.1700 |   2.1449 |
| improvement_surcharge |    -1.0000 |   1.0000 |   1.0000 |   0.9564 |   1.0000 |      1.0000 |   0.2750 |
| total_amount          | -1147.1700 |  15.5400 |  21.4200 |  26.8803 |  30.9800 |   1614.2900 |  24.1952 |
| congestion_surcharge  |    -2.5000 |   2.5000 |   2.5000 |   2.1977 |   2.5000 |      2.5000 |   0.9446 |
| Airport_fee           |    -1.7500 |   0.0000 |   0.0000 |   0.1532 |   0.0000 |      6.7500 |   0.5431 |
| cbd_congestion_fee    |    -0.7500 |   0.0000 |   0.7500 |   0.5279 |   0.7500 |      1.2500 |   0.3608 |

## Datetime Coverage (full-data)

| column                | min_ts              | max_ts              | span               |
|:----------------------|:--------------------|:--------------------|:-------------------|
| tpep_pickup_datetime  | 2009-01-01 00:20:39 | 2025-06-01 00:04:31 | 5994 days 23:43:52 |
| tpep_dropoff_datetime | 2009-01-01 00:20:49 | 2025-06-04 11:17:10 | 5998 days 10:56:21 |

## Datetime Distribution by Day (full-data)

| column                | day        |   rows |   row_% |
|:----------------------|:-----------|-------:|--------:|
| tpep_pickup_datetime  | 2009-01-01 |      1 |  0.0000 |
| tpep_pickup_datetime  | 2025-04-30 |     20 |  0.0004 |
| tpep_pickup_datetime  | 2025-05-01 | 157140 |  3.4222 |
| tpep_pickup_datetime  | 2025-05-02 | 147086 |  3.2032 |
| tpep_pickup_datetime  | 2025-05-03 | 164004 |  3.5716 |
| tpep_pickup_datetime  | 2025-05-04 | 142682 |  3.1073 |
| tpep_pickup_datetime  | 2025-05-05 | 137188 |  2.9876 |
| tpep_pickup_datetime  | 2025-05-06 | 144921 |  3.1561 |
| tpep_pickup_datetime  | 2025-05-07 | 149451 |  3.2547 |
| tpep_pickup_datetime  | 2025-05-08 | 165824 |  3.6113 |
| tpep_pickup_datetime  | 2025-05-09 | 163691 |  3.5648 |
| tpep_pickup_datetime  | 2025-05-10 | 159387 |  3.4711 |
| tpep_pickup_datetime  | 2025-05-11 | 147535 |  3.2130 |
| tpep_pickup_datetime  | 2025-05-12 | 128681 |  2.8024 |
| tpep_pickup_datetime  | 2025-05-13 | 151498 |  3.2993 |
| tpep_pickup_datetime  | 2025-05-14 | 162954 |  3.5488 |
| tpep_pickup_datetime  | 2025-05-15 | 168804 |  3.6762 |
| tpep_pickup_datetime  | 2025-05-16 | 163632 |  3.5635 |
| tpep_pickup_datetime  | 2025-05-17 | 179126 |  3.9010 |
| tpep_pickup_datetime  | 2025-05-18 | 143771 |  3.1310 |
| tpep_pickup_datetime  | 2025-05-19 | 135579 |  2.9526 |
| tpep_pickup_datetime  | 2025-05-20 | 151301 |  3.2950 |
| tpep_pickup_datetime  | 2025-05-21 | 164793 |  3.5888 |
| tpep_pickup_datetime  | 2025-05-22 | 162940 |  3.5485 |
| tpep_pickup_datetime  | 2025-05-23 | 135539 |  2.9517 |
| tpep_pickup_datetime  | 2025-05-24 | 120501 |  2.6242 |
| tpep_pickup_datetime  | 2025-05-25 | 113909 |  2.4807 |
| tpep_pickup_datetime  | 2025-05-26 |  98714 |  2.1498 |
| tpep_pickup_datetime  | 2025-05-27 | 124926 |  2.7206 |
| tpep_pickup_datetime  | 2025-05-28 | 156454 |  3.4072 |
| tpep_pickup_datetime  | 2025-05-29 | 149182 |  3.2488 |
| tpep_pickup_datetime  | 2025-05-30 | 147192 |  3.2055 |
| tpep_pickup_datetime  | 2025-05-31 | 153416 |  3.3411 |
| tpep_pickup_datetime  | 2025-06-01 |      3 |  0.0001 |
| tpep_dropoff_datetime | 2009-01-01 |      1 |  0.0000 |
| tpep_dropoff_datetime | 2025-04-30 |      8 |  0.0002 |
| tpep_dropoff_datetime | 2025-05-01 | 155427 |  3.3848 |
| tpep_dropoff_datetime | 2025-05-02 | 146223 |  3.1844 |
| tpep_dropoff_datetime | 2025-05-03 | 163755 |  3.5662 |
| tpep_dropoff_datetime | 2025-05-04 | 144676 |  3.1507 |
| tpep_dropoff_datetime | 2025-05-05 | 137051 |  2.9847 |
| tpep_dropoff_datetime | 2025-05-06 | 144925 |  3.1561 |
| tpep_dropoff_datetime | 2025-05-07 | 149274 |  3.2509 |
| tpep_dropoff_datetime | 2025-05-08 | 165102 |  3.5955 |
| tpep_dropoff_datetime | 2025-05-09 | 163173 |  3.5535 |
| tpep_dropoff_datetime | 2025-05-10 | 159106 |  3.4650 |
| tpep_dropoff_datetime | 2025-05-11 | 149337 |  3.2522 |
| tpep_dropoff_datetime | 2025-05-12 | 128628 |  2.8012 |
| tpep_dropoff_datetime | 2025-05-13 | 151301 |  3.2950 |
| tpep_dropoff_datetime | 2025-05-14 | 162647 |  3.5421 |
| tpep_dropoff_datetime | 2025-05-15 | 168150 |  3.6619 |
| tpep_dropoff_datetime | 2025-05-16 | 162906 |  3.5477 |
| tpep_dropoff_datetime | 2025-05-17 | 179042 |  3.8991 |
| tpep_dropoff_datetime | 2025-05-18 | 145633 |  3.1716 |
| tpep_dropoff_datetime | 2025-05-19 | 135658 |  2.9543 |
| tpep_dropoff_datetime | 2025-05-20 | 150872 |  3.2857 |
| tpep_dropoff_datetime | 2025-05-21 | 164394 |  3.5801 |
| tpep_dropoff_datetime | 2025-05-22 | 163177 |  3.5536 |
| tpep_dropoff_datetime | 2025-05-23 | 135347 |  2.9476 |
| tpep_dropoff_datetime | 2025-05-24 | 120252 |  2.6188 |
| tpep_dropoff_datetime | 2025-05-25 | 114335 |  2.4900 |
| tpep_dropoff_datetime | 2025-05-26 |  99341 |  2.1634 |
| tpep_dropoff_datetime | 2025-05-27 | 124969 |  2.7215 |
| tpep_dropoff_datetime | 2025-05-28 | 156074 |  3.3989 |
| tpep_dropoff_datetime | 2025-05-29 | 148723 |  3.2389 |
| tpep_dropoff_datetime | 2025-05-30 | 146458 |  3.1895 |
| tpep_dropoff_datetime | 2025-05-31 | 152950 |  3.3309 |
| tpep_dropoff_datetime | 2025-06-01 |   2926 |  0.0637 |
| tpep_dropoff_datetime | 2025-06-02 |      2 |  0.0000 |
| tpep_dropoff_datetime | 2025-06-03 |      1 |  0.0000 |
| tpep_dropoff_datetime | 2025-06-04 |      1 |  0.0000 |

## Top Values (full-data, top 5)

| column                | top_5_values                                                          |
|:----------------------|:----------------------------------------------------------------------|
| VendorID              | 2: 3639117, 1: 889031, 7: 63261, 6: 436                               |
| passenger_count       | 1.0: 2680957, <NULL>: 1196176, 2.0: 487777, 3.0: 107372, 4.0: 68093   |
| RatecodeID            | 1.0: 3154399, <NULL>: 1196176, 2.0: 130689, 99.0: 46056, 5.0: 40191   |
| store_and_fwd_flag    | N: 3387410, <NULL>: 1196176, Y: 8259                                  |
| payment_type          | 1: 2842165, 0: 1196176, 2: 418529, 4: 105323, 3: 29652                |
| mta_tax               | 0.5: 4457684, -0.5: 73747, 0.0: 60274, 1.0: 130, 10.5: 5              |
| improvement_surcharge | 1.0: 4469350, -1.0: 77950, 0.0: 44103, 0.3: 442                       |
| congestion_surcharge  | 2.5: 3046951, <NULL>: 1196176, 0.0: 286800, -2.5: 61918               |
| Airport_fee           | 0.0: 3072083, <NULL>: 1196176, 1.75: 304951, -1.75: 16286, 6.75: 1891 |
| cbd_congestion_fee    | 0.75: 3284506, 0.0: 1254714, -0.75: 52624, 1.25: 1                    |

## Data Quality Signals

- Duplicate rows in full data: `0` / `4591845`.
- Numeric columns containing negative values: `fare_amount`, `extra`, `mta_tax`, `tip_amount`, `tolls_amount`, `improvement_surcharge`, `total_amount`, `congestion_surcharge`, `Airport_fee`, `cbd_congestion_fee`.

## Data Preview

|   VendorID | tpep_pickup_datetime   | tpep_dropoff_datetime   |   passenger_count |   trip_distance |   RatecodeID | store_and_fwd_flag   |   PULocationID |   DOLocationID |   payment_type |   fare_amount |   extra |   mta_tax |   tip_amount |   tolls_amount |   improvement_surcharge |   total_amount |   congestion_surcharge |   Airport_fee |   cbd_congestion_fee |
|-----------:|:-----------------------|:------------------------|------------------:|----------------:|-------------:|:---------------------|---------------:|---------------:|---------------:|--------------:|--------:|----------:|-------------:|---------------:|------------------------:|---------------:|-----------------------:|--------------:|---------------------:|
|          1 | 2025-05-01 00:07:06    | 2025-05-01 00:24:15     |                 1 |            3.7  |            1 | N                    |            140 |            202 |              1 |          18.4 |    4.25 |       0.5 |         4.85 |           0    |                       1 |          29    |                    2.5 |          0    |                 0.75 |
|          2 | 2025-05-01 00:07:44    | 2025-05-01 00:14:27     |                 1 |            1.03 |            1 | N                    |            234 |            161 |              1 |           8.6 |    1    |       0.5 |         4.3  |           0    |                       1 |          18.65 |                    2.5 |          0    |                 0.75 |
|          2 | 2025-05-01 00:15:56    | 2025-05-01 00:23:53     |                 1 |            1.57 |            1 | N                    |            161 |            234 |              2 |          10   |    1    |       0.5 |         0    |           0    |                       1 |          15.75 |                    2.5 |          0    |                 0.75 |
|          2 | 2025-05-01 00:00:09    | 2025-05-01 00:25:29     |                 1 |            9.48 |            1 | N                    |            138 |             90 |              1 |          40.8 |    6    |       0.5 |        11.7  |           6.94 |                       1 |          71.94 |                    2.5 |          1.75 |                 0.75 |
|          2 | 2025-05-01 00:45:07    | 2025-05-01 00:52:45     |                 1 |            1.8  |            1 | N                    |             90 |            231 |              1 |          10   |    1    |       0.5 |         1.5  |           0    |                       1 |          17.25 |                    2.5 |          0    |                 0.75 |
|          2 | 2025-05-01 00:09:24    | 2025-05-01 00:22:04     |                 1 |            5.11 |            1 | N                    |            138 |            226 |              1 |          22.6 |    6    |       0.5 |         6.02 |           0    |                       1 |          37.87 |                    0   |          1.75 |                 0    |
|          1 | 2025-05-01 00:18:14    | 2025-05-01 00:27:38     |                 0 |            1.5  |            1 | N                    |            140 |            263 |              1 |          11.4 |    3.5  |       0.5 |         4.05 |           0    |                       1 |          20.45 |                    2.5 |          0    |                 0    |
|          2 | 2025-04-30 23:50:34    | 2025-04-30 23:56:06     |                 2 |            0.99 |            1 | N                    |            234 |             79 |              1 |           7.9 |    1    |       0.5 |         2.73 |           0    |                       1 |          16.38 |                    2.5 |          0    |                 0.75 |
|          2 | 2025-05-01 00:04:45    | 2025-05-01 00:07:43     |                 1 |            0.47 |            1 | N                    |            114 |            144 |              2 |           5.1 |    1    |       0.5 |         0    |           0    |                       1 |          10.85 |                    2.5 |          0    |                 0.75 |
|          7 | 2025-05-01 00:22:31    | 2025-05-01 00:22:31     |                 1 |            1.09 |            1 | N                    |            229 |             43 |              1 |           8.6 |    0    |       0.5 |         2.87 |           0    |                       1 |          17.22 |                    2.5 |          0    |                 0.75 |
