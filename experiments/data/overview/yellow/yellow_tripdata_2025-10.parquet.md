# Data Overview: yellow_tripdata_2025-10.parquet

## Dataset Summary

| metric       | value                                                                               |
|:-------------|:------------------------------------------------------------------------------------|
| file         | /root/Dev/DataGate/experiments/data/parquets/yellow/yellow_tripdata_2025-10.parquet |
| rows         | 4428699                                                                             |
| columns      | 20                                                                                  |
| row_groups   | 5                                                                                   |
| file_size_mb | 71.78                                                                               |
| rows_loaded  | 4428699                                                                             |

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
| VendorID              | int32          |    4428699 |      0 |   0.0000 |        4 |
| tpep_pickup_datetime  | datetime64[us] |    4428699 |      0 |   0.0000 |  1897097 |
| tpep_dropoff_datetime | datetime64[us] |    4428699 |      0 |   0.0000 |  1896471 |
| passenger_count       | float64        |    3437812 | 990887 |  22.3742 |        9 |
| trip_distance         | float64        |    4428699 |      0 |   0.0000 |     5070 |
| RatecodeID            | float64        |    3437812 | 990887 |  22.3742 |        7 |
| store_and_fwd_flag    | str            |    3437812 | 990887 |  22.3742 |        2 |
| PULocationID          | int32          |    4428699 |      0 |   0.0000 |      262 |
| DOLocationID          | int32          |    4428699 |      0 |   0.0000 |      262 |
| payment_type          | int64          |    4428699 |      0 |   0.0000 |        5 |
| fare_amount           | float64        |    4428699 |      0 |   0.0000 |    13901 |
| extra                 | float64        |    4428699 |      0 |   0.0000 |       64 |
| mta_tax               | float64        |    4428699 |      0 |   0.0000 |        9 |
| tip_amount            | float64        |    4428699 |      0 |   0.0000 |     4716 |
| tolls_amount          | float64        |    4428699 |      0 |   0.0000 |     1384 |
| improvement_surcharge | float64        |    4428699 |      0 |   0.0000 |        4 |
| total_amount          | float64        |    4428699 |      0 |   0.0000 |    25076 |
| congestion_surcharge  | float64        |    3437812 | 990887 |  22.3742 |        4 |
| Airport_fee           | float64        |    3437812 | 990887 |  22.3742 |        5 |
| cbd_congestion_fee    | float64        |    4428699 |      0 |   0.0000 |        3 |

## Numeric Statistics (full-data)

| column                |       min |      p25 |   median |     mean |      p75 |         max |      std |
|:----------------------|----------:|---------:|---------:|---------:|---------:|------------:|---------:|
| VendorID              |    1.0000 |   2.0000 |   2.0000 |   1.8814 |   2.0000 |      7.0000 |   0.7603 |
| passenger_count       |    0.0000 |   1.0000 |   1.0000 |   1.2748 |   1.0000 |      9.0000 |   0.6914 |
| trip_distance         |    0.0000 |   1.0500 |   1.8900 |   6.6967 |   3.8400 | 276333.4800 | 656.9620 |
| RatecodeID            |    1.0000 |   1.0000 |   1.0000 |   4.0557 |   1.0000 |     99.0000 |  16.7327 |
| PULocationID          |    1.0000 | 117.0000 | 161.0000 | 161.9942 | 233.0000 |    265.0000 |  66.0776 |
| DOLocationID          |    1.0000 | 108.0000 | 162.0000 | 161.6615 | 234.0000 |    265.0000 |  70.4327 |
| payment_type          |    0.0000 |   1.0000 |   1.0000 |   0.9418 |   1.0000 |      4.0000 |   0.7245 |
| fare_amount           | -800.0000 |   8.6000 |  13.5000 |  18.2555 |  22.6100 |   1071.9000 |  19.6885 |
| extra                 |   -7.5000 |   0.0000 |   0.0000 |   1.1756 |   2.5000 |     23.6900 |   1.8231 |
| mta_tax               |   -0.5000 |   0.5000 |   0.5000 |   0.4779 |   0.5000 |     10.5000 |   0.1345 |
| tip_amount            |  -90.0000 |   0.0000 |   2.2200 |   2.9910 |   4.1100 |    550.0000 |   4.0809 |
| tolls_amount          |  -95.0000 |   0.0000 |   0.0000 |   0.5308 |   0.0000 |    141.1800 |   2.1692 |
| improvement_surcharge |   -1.0000 |   1.0000 |   1.0000 |   0.9449 |   1.0000 |      1.0000 |   0.2876 |
| total_amount          | -801.0000 |  15.5400 |  21.4500 |  26.9736 |  31.1400 |   1104.5900 |  24.1000 |
| congestion_surcharge  |   -2.5000 |   2.5000 |   2.5000 |   2.1736 |   2.5000 |      2.5000 |   0.9511 |
| Airport_fee           |   -1.7500 |   0.0000 |   0.0000 |   0.1470 |   0.0000 |      6.7500 |   0.5322 |
| cbd_congestion_fee    |   -0.7500 |   0.0000 |   0.7500 |   0.5356 |   0.7500 |      0.7500 |   0.3556 |

## Datetime Coverage (full-data)

| column                | min_ts              | max_ts              | span             |
|:----------------------|:--------------------|:--------------------|:-----------------|
| tpep_pickup_datetime  | 2025-09-30 22:54:51 | 2025-11-01 00:32:12 | 31 days 01:37:21 |
| tpep_dropoff_datetime | 2025-09-30 23:04:41 | 2025-11-03 09:38:20 | 33 days 10:33:39 |

## Datetime Distribution by Day (full-data)

| column                | day        |   rows |   row_% |
|:----------------------|:-----------|-------:|--------:|
| tpep_pickup_datetime  | 2025-09-30 |     10 |  0.0002 |
| tpep_pickup_datetime  | 2025-10-01 | 135028 |  3.0489 |
| tpep_pickup_datetime  | 2025-10-02 | 131906 |  2.9784 |
| tpep_pickup_datetime  | 2025-10-03 | 142690 |  3.2219 |
| tpep_pickup_datetime  | 2025-10-04 | 147729 |  3.3357 |
| tpep_pickup_datetime  | 2025-10-05 | 126963 |  2.8668 |
| tpep_pickup_datetime  | 2025-10-06 | 120579 |  2.7227 |
| tpep_pickup_datetime  | 2025-10-07 | 134704 |  3.0416 |
| tpep_pickup_datetime  | 2025-10-08 | 149074 |  3.3661 |
| tpep_pickup_datetime  | 2025-10-09 | 162293 |  3.6646 |
| tpep_pickup_datetime  | 2025-10-10 | 156862 |  3.5419 |
| tpep_pickup_datetime  | 2025-10-11 | 154335 |  3.4849 |
| tpep_pickup_datetime  | 2025-10-12 | 129982 |  2.9350 |
| tpep_pickup_datetime  | 2025-10-13 | 112005 |  2.5291 |
| tpep_pickup_datetime  | 2025-10-14 | 139132 |  3.1416 |
| tpep_pickup_datetime  | 2025-10-15 | 146153 |  3.3001 |
| tpep_pickup_datetime  | 2025-10-16 | 161458 |  3.6457 |
| tpep_pickup_datetime  | 2025-10-17 | 153567 |  3.4675 |
| tpep_pickup_datetime  | 2025-10-18 | 152292 |  3.4388 |
| tpep_pickup_datetime  | 2025-10-19 | 138473 |  3.1267 |
| tpep_pickup_datetime  | 2025-10-20 | 116870 |  2.6389 |
| tpep_pickup_datetime  | 2025-10-21 | 136833 |  3.0897 |
| tpep_pickup_datetime  | 2025-10-22 | 146946 |  3.3180 |
| tpep_pickup_datetime  | 2025-10-23 | 159975 |  3.6122 |
| tpep_pickup_datetime  | 2025-10-24 | 153910 |  3.4753 |
| tpep_pickup_datetime  | 2025-10-25 | 156536 |  3.5346 |
| tpep_pickup_datetime  | 2025-10-26 | 126484 |  2.8560 |
| tpep_pickup_datetime  | 2025-10-27 | 122604 |  2.7684 |
| tpep_pickup_datetime  | 2025-10-28 | 135969 |  3.0702 |
| tpep_pickup_datetime  | 2025-10-29 | 144370 |  3.2599 |
| tpep_pickup_datetime  | 2025-10-30 | 163577 |  3.6936 |
| tpep_pickup_datetime  | 2025-10-31 | 169387 |  3.8248 |
| tpep_pickup_datetime  | 2025-11-01 |      3 |  0.0001 |
| tpep_dropoff_datetime | 2025-09-30 |      2 |  0.0000 |
| tpep_dropoff_datetime | 2025-10-01 | 134081 |  3.0275 |
| tpep_dropoff_datetime | 2025-10-02 | 131551 |  2.9704 |
| tpep_dropoff_datetime | 2025-10-03 | 141858 |  3.2032 |
| tpep_dropoff_datetime | 2025-10-04 | 147252 |  3.3249 |
| tpep_dropoff_datetime | 2025-10-05 | 128720 |  2.9065 |
| tpep_dropoff_datetime | 2025-10-06 | 120709 |  2.7256 |
| tpep_dropoff_datetime | 2025-10-07 | 134415 |  3.0351 |
| tpep_dropoff_datetime | 2025-10-08 | 148870 |  3.3615 |
| tpep_dropoff_datetime | 2025-10-09 | 161380 |  3.6440 |
| tpep_dropoff_datetime | 2025-10-10 | 156704 |  3.5384 |
| tpep_dropoff_datetime | 2025-10-11 | 154379 |  3.4859 |
| tpep_dropoff_datetime | 2025-10-12 | 131262 |  2.9639 |
| tpep_dropoff_datetime | 2025-10-13 | 112202 |  2.5335 |
| tpep_dropoff_datetime | 2025-10-14 | 138884 |  3.1360 |
| tpep_dropoff_datetime | 2025-10-15 | 146101 |  3.2990 |
| tpep_dropoff_datetime | 2025-10-16 | 160695 |  3.6285 |
| tpep_dropoff_datetime | 2025-10-17 | 153097 |  3.4569 |
| tpep_dropoff_datetime | 2025-10-18 | 151934 |  3.4307 |
| tpep_dropoff_datetime | 2025-10-19 | 140270 |  3.1673 |
| tpep_dropoff_datetime | 2025-10-20 | 116808 |  2.6375 |
| tpep_dropoff_datetime | 2025-10-21 | 136748 |  3.0878 |
| tpep_dropoff_datetime | 2025-10-22 | 146767 |  3.3140 |
| tpep_dropoff_datetime | 2025-10-23 | 159184 |  3.5944 |
| tpep_dropoff_datetime | 2025-10-24 | 153336 |  3.4623 |
| tpep_dropoff_datetime | 2025-10-25 | 156208 |  3.5272 |
| tpep_dropoff_datetime | 2025-10-26 | 128678 |  2.9055 |
| tpep_dropoff_datetime | 2025-10-27 | 122495 |  2.7659 |
| tpep_dropoff_datetime | 2025-10-28 | 135807 |  3.0665 |
| tpep_dropoff_datetime | 2025-10-29 | 144076 |  3.2532 |
| tpep_dropoff_datetime | 2025-10-30 | 162842 |  3.6770 |
| tpep_dropoff_datetime | 2025-10-31 | 167397 |  3.7798 |
| tpep_dropoff_datetime | 2025-11-01 |   3985 |  0.0900 |
| tpep_dropoff_datetime | 2025-11-03 |      2 |  0.0000 |

## Top Values (full-data, top 5)

| column                | top_5_values                                                         |
|:----------------------|:---------------------------------------------------------------------|
| VendorID              | 2: 3480300, 1: 877225, 7: 67360, 6: 3814                             |
| passenger_count       | 1.0: 2755776, <NULL>: 990887, 2.0: 467451, 3.0: 104189, 4.0: 68445   |
| RatecodeID            | 1.0: 3140941, <NULL>: 990887, 2.0: 122079, 99.0: 103459, 5.0: 45128  |
| store_and_fwd_flag    | N: 3430189, <NULL>: 990887, Y: 7623                                  |
| payment_type          | 1: 2918737, 0: 990887, 2: 399080, 4: 93891, 3: 26104                 |
| mta_tax               | 0.5: 4296496, 0.0: 67395, -0.5: 64544, 1.0: 249, 10.5: 7             |
| improvement_surcharge | 1.0: 4251921, 0.0: 104795, -1.0: 68261, 0.3: 3722                    |
| congestion_surcharge  | 2.5: 3042637, <NULL>: 990887, 0.0: 341500, -2.5: 53672, 1.0: 3       |
| Airport_fee           | 0.0: 3126030, <NULL>: 990887, 1.75: 294565, -1.75: 14748, 6.75: 1892 |
| cbd_congestion_fee    | 0.75: 3208179, 0.0: 1174853, -0.75: 45667                            |

## Data Quality Signals

- Duplicate rows in full data: `0` / `4428699`.
- Numeric columns containing negative values: `fare_amount`, `extra`, `mta_tax`, `tip_amount`, `tolls_amount`, `improvement_surcharge`, `total_amount`, `congestion_surcharge`, `Airport_fee`, `cbd_congestion_fee`.

## Data Preview

|   VendorID | tpep_pickup_datetime   | tpep_dropoff_datetime   |   passenger_count |   trip_distance |   RatecodeID | store_and_fwd_flag   |   PULocationID |   DOLocationID |   payment_type |   fare_amount |   extra |   mta_tax |   tip_amount |   tolls_amount |   improvement_surcharge |   total_amount |   congestion_surcharge |   Airport_fee |   cbd_congestion_fee |
|-----------:|:-----------------------|:------------------------|------------------:|----------------:|-------------:|:---------------------|---------------:|---------------:|---------------:|--------------:|--------:|----------:|-------------:|---------------:|------------------------:|---------------:|-----------------------:|--------------:|---------------------:|
|          1 | 2025-10-01 00:15:32    | 2025-10-01 01:04:03     |                 1 |           17.2  |            2 | N                    |            132 |            107 |              1 |          70   |    5    |       0.5 |         0    |           6.94 |                       1 |          83.44 |                    2.5 |          1.75 |                 0.75 |
|          7 | 2025-10-01 00:00:08    | 2025-10-01 00:00:08     |                 1 |            5    |            1 | N                    |            107 |            225 |              1 |          28.2 |    0    |       0.5 |         8.49 |           0    |                       1 |          42.44 |                    2.5 |          0    |                 0.75 |
|          2 | 2025-10-01 00:08:54    | 2025-10-01 00:14:44     |                 1 |            2.75 |            1 | N                    |            263 |            229 |              1 |          12.8 |    1    |       0.5 |         3.71 |           0    |                       1 |          22.26 |                    2.5 |          0    |                 0.75 |
|          1 | 2025-10-01 00:58:48    | 2025-10-01 01:04:40     |                 1 |            1.3  |            1 | N                    |            211 |            231 |              2 |           7.9 |    4.25 |       0.5 |         0    |           0    |                       1 |          13.65 |                    2.5 |          0    |                 0.75 |
|          2 | 2025-10-01 00:39:51    | 2025-10-01 00:49:40     |                 1 |            2.88 |            1 | N                    |            230 |            151 |              1 |          14.2 |    1    |       0.5 |         3.99 |           0    |                       1 |          23.94 |                    2.5 |          0    |                 0.75 |
|          1 | 2025-10-01 00:30:54    | 2025-10-01 00:37:50     |                 1 |            1.6  |            1 | N                    |            237 |            142 |              2 |           9.3 |    3.5  |       0.5 |         0    |           0    |                       1 |          14.3  |                    2.5 |          0    |                 0    |
|          2 | 2025-10-01 00:10:12    | 2025-10-01 00:17:29     |                 1 |            2.81 |            1 | N                    |            142 |            166 |              1 |          12.8 |    1    |       0.5 |         3.56 |           0    |                       1 |          21.36 |                    2.5 |          0    |                 0    |
|          2 | 2025-10-01 00:48:19    | 2025-10-01 01:01:02     |                 1 |            2.17 |            1 | N                    |            230 |            246 |              1 |          13.5 |    1    |       0.5 |         0    |           0    |                       1 |          19.25 |                    2.5 |          0    |                 0.75 |
|          2 | 2025-10-01 00:08:44    | 2025-10-01 00:24:17     |                 1 |            3.71 |            1 | N                    |            140 |              7 |              1 |          19.1 |    1    |       0.5 |         6.21 |           0    |                       1 |          31.06 |                    2.5 |          0    |                 0.75 |
|          2 | 2025-10-01 00:25:23    | 2025-10-01 00:33:02     |                 1 |            1.2  |            1 | N                    |            234 |            249 |              2 |           8.6 |    1    |       0.5 |         0    |           0    |                       1 |          14.35 |                    2.5 |          0    |                 0.75 |
