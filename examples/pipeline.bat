:: This .bat file runs the CLI command specified. Consider using a CRON schedule or Windows task schedule to automate execution.
:: For details see: https://www.makeuseof.com/automate-batch-files-task-scheduler-windows/
s3sql query --uri "s3://s3sql-demo/folder_example/sql_database_releases.csv" --sql "SELECT COUNT(*) as CNT FROM df WHERE 1=1" --out "output.csv"