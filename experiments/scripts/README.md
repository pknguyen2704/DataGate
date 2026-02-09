# Scripts Instructions

## Upload Data to Postgres
Run the following script to upload parquet files to the local Postgres instance:
```bash
./experiments/scripts/data_source_upload_data.sh
```

## Fix Postgres Data Permissions
If the `postgres_data` folder appears blank or locked, it is because it's owned by root (from Docker). To view it, run:
```bash
sudo chmod -R a+rX ../data_source/postgres_data
```


