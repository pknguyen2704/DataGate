# Data Overview: yellow_tripdata_2025-03.parquet

## Dataset Summary

| metric       | value                                                                               |
|:-------------|:------------------------------------------------------------------------------------|
| file         | /root/Dev/DataGate/experiments/data/parquets/yellow/yellow_tripdata_2025-03.parquet |
| rows         | 4145257                                                                             |
| columns      | 20                                                                                  |
| row_groups   | 4                                                                                   |
| file_size_mb | 66.72                                                                               |
| rows_loaded  | 4145257                                                                             |

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
| VendorID              | int32          |    4145257 |      0 |   0.0000 |        4 |
| tpep_pickup_datetime  | datetime64[us] |    4145257 |      0 |   0.0000 |  1827891 |
| tpep_dropoff_datetime | datetime64[us] |    4145257 |      0 |   0.0000 |  1826116 |
| passenger_count       | float64        |    3228594 | 916663 |  22.1135 |       10 |
| trip_distance         | float64        |    4145257 |      0 |   0.0000 |     4688 |
| RatecodeID            | float64        |    3228594 | 916663 |  22.1135 |        7 |
| store_and_fwd_flag    | str            |    3228594 | 916663 |  22.1135 |        2 |
| PULocationID          | int32          |    4145257 |      0 |   0.0000 |      260 |
| DOLocationID          | int32          |    4145257 |      0 |   0.0000 |      259 |
| payment_type          | int64          |    4145257 |      0 |   0.0000 |        5 |
| fare_amount           | float64        |    4145257 |      0 |   0.0000 |    10673 |
| extra                 | float64        |    4145257 |      0 |   0.0000 |       77 |
| mta_tax               | float64        |    4145257 |      0 |   0.0000 |       10 |
| tip_amount            | float64        |    4145257 |      0 |   0.0000 |     4347 |
| tolls_amount          | float64        |    4145257 |      0 |   0.0000 |     1226 |
| improvement_surcharge | float64        |    4145257 |      0 |   0.0000 |        4 |
| total_amount          | float64        |    4145257 |      0 |   0.0000 |    21368 |
| congestion_surcharge  | float64        |    3228594 | 916663 |  22.1135 |        4 |
| Airport_fee           | float64        |    3228594 | 916663 |  22.1135 |        6 |
| cbd_congestion_fee    | float64        |    4145257 |      0 |   0.0000 |        6 |

## Numeric Statistics (full-data)

| column                |        min |      p25 |   median |     mean |      p75 |         max |      std |
|:----------------------|-----------:|---------:|---------:|---------:|---------:|------------:|---------:|
| VendorID              |     1.0000 |   2.0000 |   2.0000 |   1.8249 |   2.0000 |      7.0000 |   0.5491 |
| passenger_count       |     0.0000 |   1.0000 |   1.0000 |   1.2911 |   1.0000 |      9.0000 |   0.7317 |
| trip_distance         |     0.0000 |   1.0300 |   1.8000 |   6.5841 |   3.4200 | 320136.2900 | 626.4075 |
| RatecodeID            |     1.0000 |   1.0000 |   1.0000 |   2.4235 |   1.0000 |     99.0000 |  11.3601 |
| PULocationID          |     1.0000 | 114.0000 | 161.0000 | 161.7653 | 232.0000 |    265.0000 |  65.9220 |
| DOLocationID          |     1.0000 | 107.0000 | 162.0000 | 161.2287 | 233.0000 |    265.0000 |  70.1328 |
| payment_type          |     0.0000 |   1.0000 |   1.0000 |   0.9561 |   1.0000 |      4.0000 |   0.7363 |
| fare_amount           |  -999.0000 |   8.6000 |  13.5000 |  17.8003 |  21.2500 |  46263.8800 |  29.1014 |
| extra                 |    -9.2500 |   0.0000 |   0.0000 |   1.2209 |   2.5000 |     13.5000 |   1.8502 |
| mta_tax               |    -0.5000 |   0.5000 |   0.5000 |   0.4786 |   0.5000 |     10.5000 |   0.1365 |
| tip_amount            |   -92.0900 |   0.0000 |   2.1700 |   2.8589 |   3.9300 |    290.0000 |   3.8449 |
| tolls_amount          |  -142.1700 |   0.0000 |   0.0000 |   0.4750 |   0.0000 |    916.8700 |   2.1028 |
| improvement_surcharge |    -1.0000 |   1.0000 |   1.0000 |   0.9571 |   1.0000 |      1.0000 |   0.2722 |
| total_amount          | -1000.0000 |  15.6600 |  20.7500 |  26.2659 |  29.4500 |  46269.4400 |  31.9561 |
| congestion_surcharge  |    -2.5000 |   2.5000 |   2.5000 |   2.2194 |   2.5000 |      2.5000 |   0.9155 |
| Airport_fee           |    -1.7500 |   0.0000 |   0.0000 |   0.1351 |   0.0000 |      6.7500 |   0.4997 |
| cbd_congestion_fee    |    -0.7500 |   0.0000 |   0.7500 |   0.5364 |   0.7500 |      1.5000 |   0.3569 |

## Datetime Coverage (full-data)

| column                | min_ts              | max_ts              | span               |
|:----------------------|:--------------------|:--------------------|:-------------------|
| tpep_pickup_datetime  | 2007-12-05 18:45:00 | 2025-04-01 00:00:17 | 6326 days 05:15:17 |
| tpep_dropoff_datetime | 2007-12-05 19:02:00 | 2025-04-03 14:07:50 | 6328 days 19:05:50 |

## Datetime Distribution by Day (full-data)

| column                | day        |   rows |   row_% |
|:----------------------|:-----------|-------:|--------:|
| tpep_pickup_datetime  | 2007-12-05 |      1 |  0.0000 |
| tpep_pickup_datetime  | 2009-01-01 |      1 |  0.0000 |
| tpep_pickup_datetime  | 2025-02-28 |     29 |  0.0007 |
| tpep_pickup_datetime  | 2025-03-01 | 164225 |  3.9618 |
| tpep_pickup_datetime  | 2025-03-02 | 128857 |  3.1085 |
| tpep_pickup_datetime  | 2025-03-03 | 111319 |  2.6855 |
| tpep_pickup_datetime  | 2025-03-04 | 125887 |  3.0369 |
| tpep_pickup_datetime  | 2025-03-05 | 148102 |  3.5728 |
| tpep_pickup_datetime  | 2025-03-06 | 146400 |  3.5317 |
| tpep_pickup_datetime  | 2025-03-07 | 137877 |  3.3261 |
| tpep_pickup_datetime  | 2025-03-08 | 147698 |  3.5631 |
| tpep_pickup_datetime  | 2025-03-09 | 117402 |  2.8322 |
| tpep_pickup_datetime  | 2025-03-10 | 105213 |  2.5382 |
| tpep_pickup_datetime  | 2025-03-11 | 125981 |  3.0392 |
| tpep_pickup_datetime  | 2025-03-12 | 138868 |  3.3500 |
| tpep_pickup_datetime  | 2025-03-13 | 156893 |  3.7849 |
| tpep_pickup_datetime  | 2025-03-14 | 145063 |  3.4995 |
| tpep_pickup_datetime  | 2025-03-15 | 152910 |  3.6888 |
| tpep_pickup_datetime  | 2025-03-16 | 118920 |  2.8688 |
| tpep_pickup_datetime  | 2025-03-17 | 112592 |  2.7162 |
| tpep_pickup_datetime  | 2025-03-18 | 125058 |  3.0169 |
| tpep_pickup_datetime  | 2025-03-19 | 128292 |  3.0949 |
| tpep_pickup_datetime  | 2025-03-20 | 153239 |  3.6967 |
| tpep_pickup_datetime  | 2025-03-21 | 134581 |  3.2466 |
| tpep_pickup_datetime  | 2025-03-22 | 142104 |  3.4281 |
| tpep_pickup_datetime  | 2025-03-23 | 121065 |  2.9206 |
| tpep_pickup_datetime  | 2025-03-24 | 110918 |  2.6758 |
| tpep_pickup_datetime  | 2025-03-25 | 119934 |  2.8933 |
| tpep_pickup_datetime  | 2025-03-26 | 131537 |  3.1732 |
| tpep_pickup_datetime  | 2025-03-27 | 142834 |  3.4457 |
| tpep_pickup_datetime  | 2025-03-28 | 136362 |  3.2896 |
| tpep_pickup_datetime  | 2025-03-29 | 163096 |  3.9345 |
| tpep_pickup_datetime  | 2025-03-30 | 136781 |  3.2997 |
| tpep_pickup_datetime  | 2025-03-31 | 115216 |  2.7795 |
| tpep_pickup_datetime  | 2025-04-01 |      2 |  0.0000 |
| tpep_dropoff_datetime | 2007-12-05 |      1 |  0.0000 |
| tpep_dropoff_datetime | 2009-01-01 |      1 |  0.0000 |
| tpep_dropoff_datetime | 2025-02-28 |     10 |  0.0002 |
| tpep_dropoff_datetime | 2025-03-01 | 161800 |  3.9033 |
| tpep_dropoff_datetime | 2025-03-02 | 130615 |  3.1510 |
| tpep_dropoff_datetime | 2025-03-03 | 111450 |  2.6886 |
| tpep_dropoff_datetime | 2025-03-04 | 125831 |  3.0355 |
| tpep_dropoff_datetime | 2025-03-05 | 147975 |  3.5697 |
| tpep_dropoff_datetime | 2025-03-06 | 145892 |  3.5195 |
| tpep_dropoff_datetime | 2025-03-07 | 137096 |  3.3073 |
| tpep_dropoff_datetime | 2025-03-08 | 147339 |  3.5544 |
| tpep_dropoff_datetime | 2025-03-09 | 119244 |  2.8766 |
| tpep_dropoff_datetime | 2025-03-10 | 105028 |  2.5337 |
| tpep_dropoff_datetime | 2025-03-11 | 125963 |  3.0387 |
| tpep_dropoff_datetime | 2025-03-12 | 138752 |  3.3472 |
| tpep_dropoff_datetime | 2025-03-13 | 156436 |  3.7739 |
| tpep_dropoff_datetime | 2025-03-14 | 143993 |  3.4737 |
| tpep_dropoff_datetime | 2025-03-15 | 152769 |  3.6854 |
| tpep_dropoff_datetime | 2025-03-16 | 120873 |  2.9159 |
| tpep_dropoff_datetime | 2025-03-17 | 112404 |  2.7116 |
| tpep_dropoff_datetime | 2025-03-18 | 125098 |  3.0179 |
| tpep_dropoff_datetime | 2025-03-19 | 128100 |  3.0903 |
| tpep_dropoff_datetime | 2025-03-20 | 152396 |  3.6764 |
| tpep_dropoff_datetime | 2025-03-21 | 134232 |  3.2382 |
| tpep_dropoff_datetime | 2025-03-22 | 141607 |  3.4161 |
| tpep_dropoff_datetime | 2025-03-23 | 122994 |  2.9671 |
| tpep_dropoff_datetime | 2025-03-24 | 110995 |  2.6776 |
| tpep_dropoff_datetime | 2025-03-25 | 119795 |  2.8899 |
| tpep_dropoff_datetime | 2025-03-26 | 131400 |  3.1699 |
| tpep_dropoff_datetime | 2025-03-27 | 142468 |  3.4369 |
| tpep_dropoff_datetime | 2025-03-28 | 135378 |  3.2659 |
| tpep_dropoff_datetime | 2025-03-29 | 162617 |  3.9230 |
| tpep_dropoff_datetime | 2025-03-30 | 138775 |  3.3478 |
| tpep_dropoff_datetime | 2025-03-31 | 114953 |  2.7731 |
| tpep_dropoff_datetime | 2025-04-01 |    976 |  0.0235 |
| tpep_dropoff_datetime | 2025-04-03 |      1 |  0.0000 |

## Top Values (full-data, top 5)

| column                | top_5_values                                                        |
|:----------------------|:--------------------------------------------------------------------|
| VendorID              | 2: 3289048, 1: 834394, 7: 21481, 6: 334                             |
| passenger_count       | 1.0: 2569487, <NULL>: 916663, 2.0: 442696, 3.0: 100511, 4.0: 64214  |
| RatecodeID            | 1.0: 3021866, <NULL>: 916663, 2.0: 112287, 99.0: 43988, 5.0: 32008  |
| store_and_fwd_flag    | N: 3221152, <NULL>: 916663, Y: 7442                                 |
| payment_type          | 1: 2704166, 0: 916663, 2: 405847, 4: 91657, 3: 26924                |
| mta_tax               | 0.5: 4032773, -0.5: 65652, 0.0: 46774, 1.0: 33, 10.5: 17            |
| improvement_surcharge | 1.0: 4035861, -1.0: 68502, 0.0: 40554, 0.3: 340                     |
| congestion_surcharge  | 2.5: 2921843, <NULL>: 916663, 0.0: 251116, -2.5: 55634, 1.0: 1      |
| Airport_fee           | 0.0: 2956124, <NULL>: 916663, 1.75: 259032, -1.75: 12645, 6.75: 641 |
| cbd_congestion_fee    | 0.75: 3011786, 0.0: 1086178, -0.75: 47165, 1.25: 118, 1.5: 9        |

## Data Quality Signals

- Duplicate rows in full data: `0` / `4145257`.
- Numeric columns containing negative values: `fare_amount`, `extra`, `mta_tax`, `tip_amount`, `tolls_amount`, `improvement_surcharge`, `total_amount`, `congestion_surcharge`, `Airport_fee`, `cbd_congestion_fee`.

## Data Preview

|   VendorID | tpep_pickup_datetime   | tpep_dropoff_datetime   |   passenger_count |   trip_distance |   RatecodeID | store_and_fwd_flag   |   PULocationID |   DOLocationID |   payment_type |   fare_amount |   extra |   mta_tax |   tip_amount |   tolls_amount |   improvement_surcharge |   total_amount |   congestion_surcharge |   Airport_fee |   cbd_congestion_fee |
|-----------:|:-----------------------|:------------------------|------------------:|----------------:|-------------:|:---------------------|---------------:|---------------:|---------------:|--------------:|--------:|----------:|-------------:|---------------:|------------------------:|---------------:|-----------------------:|--------------:|---------------------:|
|          1 | 2025-03-01 00:17:16    | 2025-03-01 00:25:52     |                 1 |            0.9  |            1 | N                    |            140 |            236 |              1 |           7.9 |    3.5  |       0.5 |         2.6  |              0 |                       1 |          15.5  |                    2.5 |             0 |                 0    |
|          1 | 2025-03-01 00:37:38    | 2025-03-01 00:43:51     |                 1 |            0.6  |            1 | N                    |            140 |            262 |              1 |           6.5 |    3.5  |       0.5 |         2.3  |              0 |                       1 |          13.8  |                    2.5 |             0 |                 0    |
|          2 | 2025-03-01 00:24:35    | 2025-03-01 00:39:49     |                 1 |            1.94 |            1 | N                    |            161 |             68 |              1 |          14.9 |    1    |       0.5 |         5.16 |              0 |                       1 |          25.81 |                    2.5 |             0 |                 0.75 |
|          2 | 2025-03-01 00:56:16    | 2025-03-01 01:01:35     |                 2 |            0.95 |            1 | N                    |            231 |             13 |              1 |           7.2 |    1    |       0.5 |         2.59 |              0 |                       1 |          15.54 |                    2.5 |             0 |                 0.75 |
|          1 | 2025-03-01 00:01:44    | 2025-03-01 00:10:00     |                 1 |            1.5  |            1 | N                    |            163 |            236 |              1 |           8.6 |    4.25 |       0.5 |         2.85 |              0 |                       1 |          17.2  |                    2.5 |             0 |                 0.75 |
|          1 | 2025-03-01 00:11:57    | 2025-03-01 00:28:33     |                 0 |            2    |            1 | N                    |            166 |             74 |              1 |          16.3 |    1    |       0.5 |         2    |              0 |                       1 |          20.8  |                    0   |             0 |                 0    |
|          2 | 2025-03-01 00:22:35    | 2025-03-01 00:34:06     |                 2 |            3.27 |            1 | N                    |             88 |             79 |              1 |          17   |    1    |       0.5 |         4.55 |              0 |                       1 |          27.3  |                    2.5 |             0 |                 0.75 |
|          2 | 2025-03-01 00:37:22    | 2025-03-01 00:45:03     |                 1 |            0.95 |            1 | N                    |            114 |            107 |              1 |           8.6 |    1    |       0.5 |         2    |              0 |                       1 |          16.35 |                    2.5 |             0 |                 0.75 |
|          2 | 2025-02-28 23:50:41    | 2025-03-01 00:03:51     |                 1 |            2.09 |            1 | N                    |             79 |            186 |              1 |          13.5 |    1    |       0.5 |         3.85 |              0 |                       1 |          23.1  |                    2.5 |             0 |                 0.75 |
|          2 | 2025-03-01 00:06:48    | 2025-03-01 00:18:44     |                 1 |            1.43 |            1 | N                    |            186 |            107 |              1 |          12.1 |    1    |       0.5 |         3.57 |              0 |                       1 |          21.42 |                    2.5 |             0 |                 0.75 |
