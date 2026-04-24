# Data Overview: yellow_tripdata_2025-04.parquet

## Dataset Summary

| metric       | value                                                                               |
|:-------------|:------------------------------------------------------------------------------------|
| file         | /root/Dev/DataGate/experiments/data/parquets/yellow/yellow_tripdata_2025-04.parquet |
| rows         | 3970553                                                                             |
| columns      | 20                                                                                  |
| row_groups   | 4                                                                                   |
| file_size_mb | 64.23                                                                               |
| rows_loaded  | 3970553                                                                             |

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
| VendorID              | int32          |    3970553 |      0 |   0.0000 |        4 |
| tpep_pickup_datetime  | datetime64[us] |    3970553 |      0 |   0.0000 |  1766454 |
| tpep_dropoff_datetime | datetime64[us] |    3970553 |      0 |   0.0000 |  1764720 |
| passenger_count       | float64        |    3224823 | 745730 |  18.7815 |       10 |
| trip_distance         | float64        |    3970553 |      0 |   0.0000 |     4837 |
| RatecodeID            | float64        |    3224823 | 745730 |  18.7815 |        7 |
| store_and_fwd_flag    | str            |    3224823 | 745730 |  18.7815 |        2 |
| PULocationID          | int32          |    3970553 |      0 |   0.0000 |      261 |
| DOLocationID          | int32          |    3970553 |      0 |   0.0000 |      261 |
| payment_type          | int64          |    3970553 |      0 |   0.0000 |        5 |
| fare_amount           | float64        |    3970553 |      0 |   0.0000 |    10564 |
| extra                 | float64        |    3970553 |      0 |   0.0000 |       89 |
| mta_tax               | float64        |    3970553 |      0 |   0.0000 |        8 |
| tip_amount            | float64        |    3970553 |      0 |   0.0000 |     4449 |
| tolls_amount          | float64        |    3970553 |      0 |   0.0000 |     1256 |
| improvement_surcharge | float64        |    3970553 |      0 |   0.0000 |        4 |
| total_amount          | float64        |    3970553 |      0 |   0.0000 |    21831 |
| congestion_surcharge  | float64        |    3224823 | 745730 |  18.7815 |        4 |
| Airport_fee           | float64        |    3224823 | 745730 |  18.7815 |        6 |
| cbd_congestion_fee    | float64        |    3970553 |      0 |   0.0000 |        3 |

## Numeric Statistics (full-data)

| column                |        min |      p25 |   median |     mean |      p75 |         max |      std |
|:----------------------|-----------:|---------:|---------:|---------:|---------:|------------:|---------:|
| VendorID              |     1.0000 |   2.0000 |   2.0000 |   1.8415 |   2.0000 |      7.0000 |   0.6260 |
| passenger_count       |     0.0000 |   1.0000 |   1.0000 |   1.3083 |   1.0000 |      9.0000 |   0.7540 |
| trip_distance         |     0.0000 |   1.0300 |   1.8000 |   6.9947 |   3.4600 | 386088.4300 | 662.2386 |
| RatecodeID            |     1.0000 |   1.0000 |   1.0000 |   2.4684 |   1.0000 |     99.0000 |  11.5315 |
| PULocationID          |     1.0000 | 125.0000 | 161.0000 | 162.7289 | 233.0000 |    265.0000 |  65.8548 |
| DOLocationID          |     1.0000 | 113.0000 | 162.0000 | 162.2046 | 234.0000 |    265.0000 |  70.0115 |
| payment_type          |     0.0000 |   1.0000 |   1.0000 |   1.0038 |   1.0000 |      4.0000 |   0.7353 |
| fare_amount           | -1777.5000 |   8.6000 |  13.5000 |  17.9651 |  21.5000 |   1777.5000 |  18.6597 |
| extra                 |   -10.0000 |   0.0000 |   0.0000 |   1.2807 |   2.5000 |     25.0000 |   1.8757 |
| mta_tax               |    -0.5000 |   0.5000 |   0.5000 |   0.4764 |   0.5000 |     10.5000 |   0.1431 |
| tip_amount            |   -75.0000 |   0.0000 |   2.3800 |   2.9797 |   4.0100 |    525.0000 |   3.9131 |
| tolls_amount          |  -122.9900 |   0.0000 |   0.0000 |   0.4881 |   0.0000 |    122.9900 |   2.0950 |
| improvement_surcharge |    -1.0000 |   1.0000 |   1.0000 |   0.9529 |   1.0000 |      1.0000 |   0.2853 |
| total_amount          | -1793.3700 |  15.8700 |  21.0600 |  26.5949 |  29.8200 |   1793.3700 |  23.0733 |
| congestion_surcharge  |    -2.5000 |   2.5000 |   2.5000 |   2.2129 |   2.5000 |      2.5000 |   0.9299 |
| Airport_fee           |    -1.7500 |   0.0000 |   0.0000 |   0.1349 |   0.0000 |      6.7500 |   0.5069 |
| cbd_congestion_fee    |    -0.7500 |   0.0000 |   0.7500 |   0.5324 |   0.7500 |      0.7500 |   0.3608 |

## Datetime Coverage (full-data)

| column                | min_ts              | max_ts              | span             |
|:----------------------|:--------------------|:--------------------|:-----------------|
| tpep_pickup_datetime  | 2025-03-31 23:45:01 | 2025-05-01 00:48:13 | 30 days 01:03:12 |
| tpep_dropoff_datetime | 2025-03-31 23:54:54 | 2025-05-01 21:42:14 | 30 days 21:47:20 |

## Datetime Distribution by Day (full-data)

| column                | day        |   rows |   row_% |
|:----------------------|:-----------|-------:|--------:|
| tpep_pickup_datetime  | 2025-03-31 |      4 |  0.0001 |
| tpep_pickup_datetime  | 2025-04-01 | 128955 |  3.2478 |
| tpep_pickup_datetime  | 2025-04-02 | 137393 |  3.4603 |
| tpep_pickup_datetime  | 2025-04-03 | 138411 |  3.4859 |
| tpep_pickup_datetime  | 2025-04-04 | 135084 |  3.4021 |
| tpep_pickup_datetime  | 2025-04-05 | 153237 |  3.8593 |
| tpep_pickup_datetime  | 2025-04-06 | 122921 |  3.0958 |
| tpep_pickup_datetime  | 2025-04-07 | 115829 |  2.9172 |
| tpep_pickup_datetime  | 2025-04-08 | 131574 |  3.3137 |
| tpep_pickup_datetime  | 2025-04-09 | 137646 |  3.4667 |
| tpep_pickup_datetime  | 2025-04-10 | 147648 |  3.7186 |
| tpep_pickup_datetime  | 2025-04-11 | 154758 |  3.8976 |
| tpep_pickup_datetime  | 2025-04-12 | 149391 |  3.7625 |
| tpep_pickup_datetime  | 2025-04-13 | 109780 |  2.7649 |
| tpep_pickup_datetime  | 2025-04-14 |  99795 |  2.5134 |
| tpep_pickup_datetime  | 2025-04-15 | 122082 |  3.0747 |
| tpep_pickup_datetime  | 2025-04-16 | 133969 |  3.3741 |
| tpep_pickup_datetime  | 2025-04-17 | 135522 |  3.4132 |
| tpep_pickup_datetime  | 2025-04-18 | 125581 |  3.1628 |
| tpep_pickup_datetime  | 2025-04-19 | 134049 |  3.3761 |
| tpep_pickup_datetime  | 2025-04-20 | 115504 |  2.9090 |
| tpep_pickup_datetime  | 2025-04-21 | 107881 |  2.7170 |
| tpep_pickup_datetime  | 2025-04-22 | 124843 |  3.1442 |
| tpep_pickup_datetime  | 2025-04-23 | 135843 |  3.4213 |
| tpep_pickup_datetime  | 2025-04-24 | 148387 |  3.7372 |
| tpep_pickup_datetime  | 2025-04-25 | 147589 |  3.7171 |
| tpep_pickup_datetime  | 2025-04-26 | 158506 |  3.9920 |
| tpep_pickup_datetime  | 2025-04-27 | 141509 |  3.5640 |
| tpep_pickup_datetime  | 2025-04-28 | 110105 |  2.7730 |
| tpep_pickup_datetime  | 2025-04-29 | 126466 |  3.1851 |
| tpep_pickup_datetime  | 2025-04-30 | 140288 |  3.5332 |
| tpep_pickup_datetime  | 2025-05-01 |      3 |  0.0001 |
| tpep_dropoff_datetime | 2025-03-31 |      1 |  0.0000 |
| tpep_dropoff_datetime | 2025-04-01 | 128177 |  3.2282 |
| tpep_dropoff_datetime | 2025-04-02 | 137377 |  3.4599 |
| tpep_dropoff_datetime | 2025-04-03 | 137901 |  3.4731 |
| tpep_dropoff_datetime | 2025-04-04 | 134070 |  3.3766 |
| tpep_dropoff_datetime | 2025-04-05 | 152877 |  3.8503 |
| tpep_dropoff_datetime | 2025-04-06 | 124919 |  3.1461 |
| tpep_dropoff_datetime | 2025-04-07 | 115905 |  2.9191 |
| tpep_dropoff_datetime | 2025-04-08 | 131386 |  3.3090 |
| tpep_dropoff_datetime | 2025-04-09 | 137513 |  3.4633 |
| tpep_dropoff_datetime | 2025-04-10 | 147321 |  3.7103 |
| tpep_dropoff_datetime | 2025-04-11 | 153664 |  3.8701 |
| tpep_dropoff_datetime | 2025-04-12 | 149753 |  3.7716 |
| tpep_dropoff_datetime | 2025-04-13 | 111140 |  2.7991 |
| tpep_dropoff_datetime | 2025-04-14 |  99864 |  2.5151 |
| tpep_dropoff_datetime | 2025-04-15 | 121783 |  3.0672 |
| tpep_dropoff_datetime | 2025-04-16 | 133808 |  3.3700 |
| tpep_dropoff_datetime | 2025-04-17 | 134993 |  3.3999 |
| tpep_dropoff_datetime | 2025-04-18 | 125386 |  3.1579 |
| tpep_dropoff_datetime | 2025-04-19 | 133656 |  3.3662 |
| tpep_dropoff_datetime | 2025-04-20 | 116895 |  2.9440 |
| tpep_dropoff_datetime | 2025-04-21 | 107931 |  2.7183 |
| tpep_dropoff_datetime | 2025-04-22 | 124682 |  3.1402 |
| tpep_dropoff_datetime | 2025-04-23 | 135751 |  3.4189 |
| tpep_dropoff_datetime | 2025-04-24 | 147771 |  3.7217 |
| tpep_dropoff_datetime | 2025-04-25 | 146610 |  3.6924 |
| tpep_dropoff_datetime | 2025-04-26 | 158312 |  3.9872 |
| tpep_dropoff_datetime | 2025-04-27 | 143515 |  3.6145 |
| tpep_dropoff_datetime | 2025-04-28 | 110096 |  2.7728 |
| tpep_dropoff_datetime | 2025-04-29 | 126326 |  3.1816 |
| tpep_dropoff_datetime | 2025-04-30 | 140068 |  3.5277 |
| tpep_dropoff_datetime | 2025-05-01 |   1102 |  0.0278 |

## Top Values (full-data, top 5)

| column                | top_5_values                                                         |
|:----------------------|:---------------------------------------------------------------------|
| VendorID              | 2: 3135417, 1: 800747, 7: 33844, 6: 545                              |
| passenger_count       | 1.0: 2543892, <NULL>: 745730, 2.0: 442205, 3.0: 108670, 4.0: 79082   |
| RatecodeID            | 1.0: 3013813, <NULL>: 745730, 2.0: 111623, 99.0: 45293, 5.0: 34157   |
| store_and_fwd_flag    | N: 3217141, <NULL>: 745730, Y: 7682                                  |
| payment_type          | 1: 2686812, 0: 745730, 2: 412754, 4: 97491, 3: 27766                 |
| mta_tax               | 0.5: 3851578, -0.5: 69101, 0.0: 49809, 1.0: 41, 10.5: 19             |
| improvement_surcharge | 1.0: 3855751, -1.0: 72491, 0.0: 41769, 0.3: 542                      |
| congestion_surcharge  | 2.5: 2913709, <NULL>: 745730, 0.0: 251937, -2.5: 59175, 0.75: 2      |
| Airport_fee           | 0.0: 2952613, <NULL>: 745730, 1.75: 257193, -1.75: 13636, 6.75: 1136 |
| cbd_congestion_fee    | 0.75: 2869036, 0.0: 1050871, -0.75: 50646                            |

## Data Quality Signals

- Duplicate rows in full data: `0` / `3970553`.
- Numeric columns containing negative values: `fare_amount`, `extra`, `mta_tax`, `tip_amount`, `tolls_amount`, `improvement_surcharge`, `total_amount`, `congestion_surcharge`, `Airport_fee`, `cbd_congestion_fee`.

## Data Preview

|   VendorID | tpep_pickup_datetime   | tpep_dropoff_datetime   |   passenger_count |   trip_distance |   RatecodeID | store_and_fwd_flag   |   PULocationID |   DOLocationID |   payment_type |   fare_amount |   extra |   mta_tax |   tip_amount |   tolls_amount |   improvement_surcharge |   total_amount |   congestion_surcharge |   Airport_fee |   cbd_congestion_fee |
|-----------:|:-----------------------|:------------------------|------------------:|----------------:|-------------:|:---------------------|---------------:|---------------:|---------------:|--------------:|--------:|----------:|-------------:|---------------:|------------------------:|---------------:|-----------------------:|--------------:|---------------------:|
|          1 | 2025-04-01 00:47:06    | 2025-04-01 01:13:25     |                 1 |            9.5  |            1 | N                    |            138 |            230 |              1 |          38.7 |   11    |       0.5 |        11.65 |           6.94 |                       1 |          69.79 |                    2.5 |          1.75 |                 0.75 |
|          2 | 2025-04-01 00:27:35    | 2025-04-01 00:38:19     |                 2 |            3.77 |            1 | N                    |            138 |             92 |              1 |          17   |    6    |       0.5 |         4.9  |           0    |                       1 |          31.15 |                    0   |          1.75 |                 0    |
|          2 | 2025-04-01 00:24:07    | 2025-04-01 00:35:12     |                 1 |            5.41 |            1 | N                    |            132 |            130 |              1 |          22.6 |    1    |       0.5 |         5.37 |           0    |                       1 |          32.22 |                    0   |          1.75 |                 0    |
|          1 | 2025-04-01 00:56:30    | 2025-04-01 01:00:49     |                 2 |            0.6  |            1 | N                    |             79 |              4 |              1 |           6.5 |    4.25 |       0.5 |         2.45 |           0    |                       1 |          14.7  |                    2.5 |          0    |                 0.75 |
|          2 | 2025-04-01 00:00:17    | 2025-04-01 00:16:19     |                 1 |            0.43 |            1 | N                    |            161 |            229 |              2 |           4.4 |    1    |       0.5 |         0    |           0    |                       1 |          10.15 |                    2.5 |          0    |                 0.75 |
|          7 | 2025-04-01 00:39:00    | 2025-04-01 00:39:00     |                 1 |            0.95 |            1 | N                    |            233 |            164 |              1 |           5.8 |    0    |       0.5 |         0    |           0    |                       1 |          11.55 |                    2.5 |          0    |                 0.75 |
|          2 | 2025-04-01 00:54:37    | 2025-04-01 01:14:10     |                 1 |            8.94 |            1 | N                    |            138 |            140 |              1 |          35.9 |    6    |       0.5 |        10.57 |           6.94 |                       1 |          65.16 |                    2.5 |          1.75 |                 0    |
|          2 | 2025-04-01 00:11:13    | 2025-04-01 00:28:08     |                 2 |            8.79 |            1 | N                    |            138 |            116 |              1 |          35.2 |    6    |       0.5 |         5.14 |           6.94 |                       1 |          56.53 |                    0   |          1.75 |                 0    |
|          1 | 2025-04-01 00:33:16    | 2025-04-01 00:34:46     |                 1 |            0.5  |            1 | N                    |            239 |            238 |              1 |           4.4 |    3.5  |       0.5 |         1.85 |           0    |                       1 |          11.25 |                    2.5 |          0    |                 0    |
|          2 | 2025-04-01 00:48:56    | 2025-04-01 01:18:35     |                 1 |           16.62 |            2 | N                    |            132 |            162 |              1 |          70   |    0    |       0.5 |        16.34 |           6.94 |                       1 |          99.78 |                    2.5 |          1.75 |                 0.75 |
