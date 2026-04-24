# Data Overview: green_tripdata_2025-05.parquet

## Dataset Summary

| metric       | value                                                                             |
|:-------------|:----------------------------------------------------------------------------------|
| file         | /root/Dev/DataGate/experiments/data/parquets/green/green_tripdata_2025-05.parquet |
| rows         | 55399                                                                             |
| columns      | 21                                                                                |
| row_groups   | 1                                                                                 |
| file_size_mb | 1.28                                                                              |
| rows_loaded  | 55399                                                                             |

## Schema

| column                | parquet_type   | nullable   |
|:----------------------|:---------------|:-----------|
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

## Column Health (full-data)

| column                | dtype          |   non_null |   null |   null_% |   unique |
|:----------------------|:---------------|-----------:|-------:|---------:|---------:|
| VendorID              | int32          |      55399 |      0 |   0.0000 |        3 |
| lpep_pickup_datetime  | datetime64[us] |      55399 |      0 |   0.0000 |    54290 |
| lpep_dropoff_datetime | datetime64[us] |      55399 |      0 |   0.0000 |    54318 |
| store_and_fwd_flag    | str            |      52155 |   3244 |   5.8557 |        2 |
| RatecodeID            | float64        |      52155 |   3244 |   5.8557 |        7 |
| PULocationID          | int32          |      55399 |      0 |   0.0000 |      229 |
| DOLocationID          | int32          |      55399 |      0 |   0.0000 |      252 |
| passenger_count       | float64        |      52155 |   3244 |   5.8557 |       10 |
| trip_distance         | float64        |      55399 |      0 |   0.0000 |     1980 |
| fare_amount           | float64        |      55399 |      0 |   0.0000 |     1828 |
| extra                 | float64        |      55399 |      0 |   0.0000 |       19 |
| mta_tax               | float64        |      55399 |      0 |   0.0000 |        5 |
| tip_amount            | float64        |      55399 |      0 |   0.0000 |     1595 |
| tolls_amount          | float64        |      55399 |      0 |   0.0000 |       29 |
| ehail_fee             | float64        |          0 |  55399 | 100.0000 |        0 |
| improvement_surcharge | float64        |      55399 |      0 |   0.0000 |        4 |
| total_amount          | float64        |      55399 |      0 |   0.0000 |     4908 |
| payment_type          | float64        |      52155 |   3244 |   5.8557 |        5 |
| trip_type             | float64        |      52151 |   3248 |   5.8629 |        2 |
| congestion_surcharge  | float64        |      52155 |   3244 |   5.8557 |        4 |
| cbd_congestion_fee    | float64        |      55399 |      0 |   0.0000 |        2 |

## Numeric Statistics (full-data)

| column                |       min |     p25 |   median |     mean |      p75 |         max |       std |
|:----------------------|----------:|--------:|---------:|---------:|---------:|------------:|----------:|
| VendorID              |    1.0000 |  2.0000 |   2.0000 |   1.9479 |   2.0000 |      6.0000 |    0.6344 |
| RatecodeID            |    1.0000 |  1.0000 |   1.0000 |   1.3973 |   1.0000 |     99.0000 |    4.0751 |
| PULocationID          |    1.0000 | 74.0000 |  75.0000 |  96.5616 |  97.0000 |    265.0000 |   56.2027 |
| DOLocationID          |    1.0000 | 74.0000 | 140.0000 | 142.7801 | 231.0000 |    265.0000 |   77.4780 |
| passenger_count       |    0.0000 |  1.0000 |   1.0000 |   1.2935 |   1.0000 |      9.0000 |    0.9446 |
| trip_distance         |    0.0000 |  1.1700 |   1.9200 |  20.3180 |   3.3700 | 170400.1500 | 1166.9646 |
| fare_amount           | -200.0000 | 10.0000 |  14.2000 |  18.7632 |  21.2000 |   1086.6000 |   17.4300 |
| extra                 |   -6.0000 |  0.0000 |   0.0000 |   0.9189 |   1.0000 |     12.5000 |    1.4139 |
| mta_tax               |   -0.5000 |  0.5000 |   0.5000 |   0.5859 |   0.5000 |      1.5000 |    0.3536 |
| tip_amount            |   -0.9000 |  0.0000 |   2.2000 |   2.7699 |   4.0000 |    200.0000 |    3.6073 |
| tolls_amount          |   -6.9400 |  0.0000 |   0.0000 |   0.2632 |   0.0000 |     29.0600 |    1.4267 |
| improvement_surcharge |   -1.0000 |  1.0000 |   1.0000 |   0.9758 |   1.0000 |      1.0000 |    0.1620 |
| total_amount          | -201.0000 | 14.6400 |  20.2500 |  25.3725 |  29.4000 |   1095.5400 |   19.8461 |
| payment_type          |    1.0000 |  1.0000 |   1.0000 |   1.2544 |   1.0000 |      5.0000 |    0.4705 |
| trip_type             |    1.0000 |  1.0000 |   1.0000 |   1.0554 |   1.0000 |      2.0000 |    0.2288 |
| congestion_surcharge  |   -2.7500 |  0.0000 |   0.0000 |   0.8789 |   2.7500 |      2.7500 |    1.2824 |
| cbd_congestion_fee    |    0.0000 |  0.0000 |   0.0000 |   0.0747 |   0.0000 |      0.7500 |    0.2247 |

## Datetime Coverage (full-data)

| column                | min_ts              | max_ts              | span             |
|:----------------------|:--------------------|:--------------------|:-----------------|
| lpep_pickup_datetime  | 2025-04-29 21:06:34 | 2025-06-01 06:57:21 | 32 days 09:50:47 |
| lpep_dropoff_datetime | 2025-04-29 21:33:48 | 2025-06-01 15:15:35 | 32 days 17:41:47 |

## Datetime Distribution by Day (full-data)

| column                | day        |   rows |   row_% |
|:----------------------|:-----------|-------:|--------:|
| lpep_pickup_datetime  | 2025-04-29 |      2 |  0.0036 |
| lpep_pickup_datetime  | 2025-04-30 |      7 |  0.0126 |
| lpep_pickup_datetime  | 2025-05-01 |   1987 |  3.5867 |
| lpep_pickup_datetime  | 2025-05-02 |   1936 |  3.4946 |
| lpep_pickup_datetime  | 2025-05-03 |   1585 |  2.8611 |
| lpep_pickup_datetime  | 2025-05-04 |   1492 |  2.6932 |
| lpep_pickup_datetime  | 2025-05-05 |   1896 |  3.4224 |
| lpep_pickup_datetime  | 2025-05-06 |   1864 |  3.3647 |
| lpep_pickup_datetime  | 2025-05-07 |   1957 |  3.5326 |
| lpep_pickup_datetime  | 2025-05-08 |   2067 |  3.7311 |
| lpep_pickup_datetime  | 2025-05-09 |   2033 |  3.6697 |
| lpep_pickup_datetime  | 2025-05-10 |   1561 |  2.8177 |
| lpep_pickup_datetime  | 2025-05-11 |   1597 |  2.8827 |
| lpep_pickup_datetime  | 2025-05-12 |   1737 |  3.1354 |
| lpep_pickup_datetime  | 2025-05-13 |   1865 |  3.3665 |
| lpep_pickup_datetime  | 2025-05-14 |   2067 |  3.7311 |
| lpep_pickup_datetime  | 2025-05-15 |   2062 |  3.7221 |
| lpep_pickup_datetime  | 2025-05-16 |   1962 |  3.5416 |
| lpep_pickup_datetime  | 2025-05-17 |   1775 |  3.2040 |
| lpep_pickup_datetime  | 2025-05-18 |   1526 |  2.7546 |
| lpep_pickup_datetime  | 2025-05-19 |   1830 |  3.3033 |
| lpep_pickup_datetime  | 2025-05-20 |   1954 |  3.5271 |
| lpep_pickup_datetime  | 2025-05-21 |   2097 |  3.7853 |
| lpep_pickup_datetime  | 2025-05-22 |   2076 |  3.7474 |
| lpep_pickup_datetime  | 2025-05-23 |   1764 |  3.1842 |
| lpep_pickup_datetime  | 2025-05-24 |   1225 |  2.2112 |
| lpep_pickup_datetime  | 2025-05-25 |   1291 |  2.3304 |
| lpep_pickup_datetime  | 2025-05-26 |   1324 |  2.3899 |
| lpep_pickup_datetime  | 2025-05-27 |   1760 |  3.1770 |
| lpep_pickup_datetime  | 2025-05-28 |   1965 |  3.5470 |
| lpep_pickup_datetime  | 2025-05-29 |   1859 |  3.3557 |
| lpep_pickup_datetime  | 2025-05-30 |   1759 |  3.1751 |
| lpep_pickup_datetime  | 2025-05-31 |   1516 |  2.7365 |
| lpep_pickup_datetime  | 2025-06-01 |      1 |  0.0018 |
| lpep_dropoff_datetime | 2025-04-29 |      2 |  0.0036 |
| lpep_dropoff_datetime | 2025-04-30 |      5 |  0.0090 |
| lpep_dropoff_datetime | 2025-05-01 |   1976 |  3.5669 |
| lpep_dropoff_datetime | 2025-05-02 |   1923 |  3.4712 |
| lpep_dropoff_datetime | 2025-05-03 |   1575 |  2.8430 |
| lpep_dropoff_datetime | 2025-05-04 |   1514 |  2.7329 |
| lpep_dropoff_datetime | 2025-05-05 |   1895 |  3.4206 |
| lpep_dropoff_datetime | 2025-05-06 |   1864 |  3.3647 |
| lpep_dropoff_datetime | 2025-05-07 |   1959 |  3.5362 |
| lpep_dropoff_datetime | 2025-05-08 |   2065 |  3.7275 |
| lpep_dropoff_datetime | 2025-05-09 |   2015 |  3.6372 |
| lpep_dropoff_datetime | 2025-05-10 |   1570 |  2.8340 |
| lpep_dropoff_datetime | 2025-05-11 |   1610 |  2.9062 |
| lpep_dropoff_datetime | 2025-05-12 |   1733 |  3.1282 |
| lpep_dropoff_datetime | 2025-05-13 |   1866 |  3.3683 |
| lpep_dropoff_datetime | 2025-05-14 |   2055 |  3.7095 |
| lpep_dropoff_datetime | 2025-05-15 |   2068 |  3.7329 |
| lpep_dropoff_datetime | 2025-05-16 |   1958 |  3.5344 |
| lpep_dropoff_datetime | 2025-05-17 |   1774 |  3.2022 |
| lpep_dropoff_datetime | 2025-05-18 |   1536 |  2.7726 |
| lpep_dropoff_datetime | 2025-05-19 |   1830 |  3.3033 |
| lpep_dropoff_datetime | 2025-05-20 |   1951 |  3.5217 |
| lpep_dropoff_datetime | 2025-05-21 |   2095 |  3.7817 |
| lpep_dropoff_datetime | 2025-05-22 |   2084 |  3.7618 |
| lpep_dropoff_datetime | 2025-05-23 |   1754 |  3.1661 |
| lpep_dropoff_datetime | 2025-05-24 |   1237 |  2.2329 |
| lpep_dropoff_datetime | 2025-05-25 |   1287 |  2.3231 |
| lpep_dropoff_datetime | 2025-05-26 |   1332 |  2.4044 |
| lpep_dropoff_datetime | 2025-05-27 |   1758 |  3.1733 |
| lpep_dropoff_datetime | 2025-05-28 |   1964 |  3.5452 |
| lpep_dropoff_datetime | 2025-05-29 |   1855 |  3.3484 |
| lpep_dropoff_datetime | 2025-05-30 |   1755 |  3.1679 |
| lpep_dropoff_datetime | 2025-05-31 |   1517 |  2.7383 |
| lpep_dropoff_datetime | 2025-06-01 |     17 |  0.0307 |

## Top Values (full-data, top 5)

| column                | top_5_values                                              |
|:----------------------|:----------------------------------------------------------|
| VendorID              | 2: 47621, 1: 6800, 6: 978                                 |
| store_and_fwd_flag    | N: 52039, <NULL>: 3244, Y: 116                            |
| RatecodeID            | 1.0: 48846, <NULL>: 3244, 5.0: 2968, 2.0: 156, 99.0: 86   |
| passenger_count       | 1.0: 43514, 2.0: 4868, <NULL>: 3244, 5.0: 1140, 6.0: 823  |
| mta_tax               | 0.5: 45806, 1.5: 6420, 0.0: 3003, -0.5: 162, 1.0: 8       |
| ehail_fee             | <NULL>: 55399                                             |
| improvement_surcharge | 1.0: 53944, 0.3: 979, 0.0: 299, -1.0: 177                 |
| payment_type          | 1.0: 39553, 2.0: 12088, <NULL>: 3244, 3.0: 366, 4.0: 143  |
| trip_type             | 1.0: 49262, <NULL>: 3248, 2.0: 2889                       |
| congestion_surcharge  | 0.0: 35463, 2.75: 16555, <NULL>: 3244, 2.5: 131, -2.75: 6 |
| cbd_congestion_fee    | 0.0: 49878, 0.75: 5521                                    |

## Data Quality Signals

- Duplicate rows in full data: `0` / `55399`.
- Columns with >= 50% null in full data: `ehail_fee`.
- Near-constant columns in full data: `ehail_fee`.
- High-cardinality / ID-like columns: `lpep_pickup_datetime`, `lpep_dropoff_datetime`.
- Numeric columns containing negative values: `fare_amount`, `extra`, `mta_tax`, `tip_amount`, `tolls_amount`, `improvement_surcharge`, `total_amount`, `congestion_surcharge`.

## Data Preview

|   VendorID | lpep_pickup_datetime   | lpep_dropoff_datetime   | store_and_fwd_flag   |   RatecodeID |   PULocationID |   DOLocationID |   passenger_count |   trip_distance |   fare_amount |   extra |   mta_tax |   tip_amount |   tolls_amount |   ehail_fee |   improvement_surcharge |   total_amount |   payment_type |   trip_type |   congestion_surcharge |   cbd_congestion_fee |
|-----------:|:-----------------------|:------------------------|:---------------------|-------------:|---------------:|---------------:|------------------:|----------------:|--------------:|--------:|----------:|-------------:|---------------:|------------:|------------------------:|---------------:|---------------:|------------:|-----------------------:|---------------------:|
|          2 | 2025-05-01 00:17:04    | 2025-05-01 00:56:06     | N                    |            1 |             25 |            216 |                 1 |            9.34 |          44.3 |       1 |       0.5 |         0    |              0 |         nan |                       1 |          46.8  |              1 |           1 |                   0    |                    0 |
|          2 | 2025-05-01 00:56:16    | 2025-05-01 01:10:26     | N                    |            1 |            160 |            129 |                 1 |            2.95 |          16.3 |       1 |       0.5 |         0    |              0 |         nan |                       1 |          18.8  |              2 |           1 |                   0    |                    0 |
|          1 | 2025-05-01 00:24:49    | 2025-05-01 00:42:29     | N                    |            1 |            260 |            179 |                 1 |            3    |          18.4 |       1 |       1.5 |         0    |              0 |         nan |                       1 |          20.9  |              2 |           1 |                   0    |                    0 |
|          2 | 2025-05-01 00:27:11    | 2025-05-01 00:33:21     | N                    |            1 |            130 |            216 |                 1 |            1.61 |           9.3 |       1 |       0.5 |         0    |              0 |         nan |                       1 |          11.8  |              2 |           1 |                   0    |                    0 |
|          2 | 2025-05-01 00:32:59    | 2025-05-01 00:41:34     | N                    |            1 |            244 |            151 |                 2 |            3.44 |          15.6 |       1 |       0.5 |         4.52 |              0 |         nan |                       1 |          22.62 |              1 |           1 |                   0    |                    0 |
|          2 | 2025-04-30 23:58:57    | 2025-05-01 00:02:31     | N                    |            1 |             42 |             41 |                 1 |            0.66 |           6.5 |       1 |       0.5 |         2    |              0 |         nan |                       1 |          11    |              1 |           1 |                   0    |                    0 |
|          2 | 2025-05-01 00:38:03    | 2025-05-01 00:43:28     | N                    |            1 |            240 |            265 |                 1 |            1.63 |           9.3 |       1 |       0.5 |         0    |              0 |         nan |                       1 |          11.8  |              1 |           1 |                   0    |                    0 |
|          2 | 2025-05-01 00:13:48    | 2025-05-01 00:26:19     | N                    |            1 |            129 |             70 |                 1 |            2.15 |          13.5 |       1 |       0.5 |         0    |              0 |         nan |                       1 |          16    |              2 |           1 |                   0    |                    0 |
|          2 | 2025-05-01 00:08:00    | 2025-05-01 00:22:00     | N                    |            1 |            244 |             42 |                 1 |            2.87 |          15.6 |       1 |       0.5 |         0    |              0 |         nan |                       1 |          18.1  |              2 |           1 |                   0    |                    0 |
|          2 | 2025-05-01 00:48:03    | 2025-05-01 00:57:01     | N                    |            1 |             75 |            262 |                 1 |            1.52 |          10.7 |       1 |       0.5 |         2.39 |              0 |         nan |                       1 |          18.34 |              1 |           1 |                   2.75 |                    0 |
