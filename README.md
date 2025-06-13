# S3SQL

## Overview
S3SQL is a lightweight command line utility for querying data stored in s3.

## Features
- Return S3 data straight to your terminal
- Write SQL queries to filter and manipulate S3 data
- List S3 objects available to current scoped credentials

## Installation
1. Install with:
   ```bash
   pip install s3sql
   ```

## Usage
1. Open a new terminal window
2. Test the CLI is properly configured with:
   ```bash
   s3sql --help
   ```
3. Set the AWS access key with:
   ```bash
   s3sql set-key --api-key AKIA*******
   ```
   This command returns the following message:

   ```bash
   API secret saved successfully!
   ```

> [!TIP]
> Credentials are stored in the `~/s3sql` directory. I.E. Windows = `C:\Users\Ian\s3sql\credentials` MacOS = `/Users/Ian/s3sql`

4. Set the AWS access secret with:

   ```bash
   s3sql set-secret --api-secret Gy096********
   ```

   This command returns the following message:

   ```bash
   API key saved successfully!
   ```

> [!TIP]
> Credentials are stored in the `~/s3sql` directory. I.E. Windows = `C:\Users\Ian\s3sql\credentials` MacOS = `/Users/Ian/s3sql`

5. List objects available. For example, to list the objects in the bucket named: `osg-repo-scan-data`:

   ```bash
   s3sql ls --bucket "s3sql-demo"
   ```

   This command returns a formatted table of the objects available in the bucket:
   ```bash
   +------------------------------------------+---------------------------+------------------------------------+---------------------+--------+----------------+
   | Key                                      | LastModified              | ETag                               | ChecksumAlgorithm   |   Size |StorageClass   |
   +==========================================+===========================+====================================+=====================+========+================+
   | folder_example/                          | 2025-06-13 01:22:05+00:00 | "d41d8cd98f00b204e9800998ecf8427e" | ['CRC64NVME']       |      0 | STANDARD       |
   +------------------------------------------+---------------------------+------------------------------------+---------------------+--------+----------------+
   | folder_example/sql_database_releases.csv | 2025-06-13 01:57:02+00:00 | "90089983c8e30097002094756b5f7478" | ['CRC64NVME']       |    438 | STANDARD       |
   +------------------------------------------+---------------------------+------------------------------------+---------------------+--------+----------------+
   | sql_database_features.csv                | 2025-06-13 01:45:38+00:00 | "8a46b42d596d9310bcd4ac9db14df718" | ['CRC64NVME']       |   1991 | STANDARD       |
   +------------------------------------------+---------------------------+------------------------------------+---------------------+--------+----------------+
   | sql_engines.csv                          | 2025-06-13 01:21:49+00:00 | "586f00530a11fcbb46c244210f625292" | ['CRC64NVME']       |    407 | STANDARD       |
   +------------------------------------------+---------------------------+------------------------------------+---------------------+--------+----------------+
   | sql_user_base.csv                        | 2025-06-13 01:45:58+00:00 | "ff5e96d2ca7f3475dc38c537cc1f6c36" | ['CRC64NVME']       |    597 | STANDARD       |
   +------------------------------------------+---------------------------+------------------------------------+---------------------+--------+----------------+
   ```

6. Query an object with the following command:

   ```bash
   s3sql query --uri "s3://s3sql-demo/sql_engines.csv" --query "SELECT * FROM df WHERE 1=1"
   ```

   This command returns a formatted table of the data from the specified object:

   ```bash
   +------+---------------+-----------+--------------------+-------------------------------------+-------------------------+
   |   Id | engine_name   |   version | license_type       | developer                           | primary_use_case        |
   +======+===============+===========+====================+=====================================+=========================+
   |    1 | SQLite        |      3.46 | Public Domain      | D. Richard Hipp                     | Embedded systems        |
   +------+---------------+-----------+--------------------+-------------------------------------+-------------------------+
   |    2 | PostgreSQL    |     16.4  | PostgreSQL License | PostgreSQL Global Development Group | General-purpose OLTP    |
   +------+---------------+-----------+--------------------+-------------------------------------+-------------------------+
   |    3 | MySQL         |      8.4  | GPLv2              | Oracle Corporation                  | Web applications        |
   +------+---------------+-----------+--------------------+-------------------------------------+-------------------------+
   |    4 | SQLServer     |   2022    | Proprietary        | Microsoft Corporation               | Enterprise applications |
   +------+---------------+-----------+--------------------+-------------------------------------+-------------------------+
   |    5 | DuckDB        |      1    | MIT License        | DuckDB Labs                         | Analytical queries      |
   +------+---------------+-----------+--------------------+-------------------------------------+-------------------------+
   ```

   Apply a `LIMIT 1` to the previous query:

   ```bash
   s3sql query --uri "s3://s3sql-demo/sql_engines.csv" --query "SELECT * FROM df WHERE 1=1 LIMIT 1"
   ```

   This command returns a formatted table of the data from the specified object:
   ```bash
   +------+---------------+-----------+----------------+-----------------+--------------------+
   |   Id | engine_name   |   version | license_type   | developer       | primary_use_case   |
   +======+===============+===========+================+=================+====================+
   |    1 | SQLite        |      3.46 | Public Domain  | D. Richard Hipp | Embedded systems   |
   +------+---------------+-----------+----------------+-----------------+--------------------+
   ```

7. Query an object within the `folder_example` folder with the following command:

   ```bash
   s3sql query --uri "s3://s3sql-demo/folder_example/sql_database_releases.csv" --query "SELECT * FROM df WHERE 1=1"
   ```

   This command returns a formatted table of the data from the specified object:

   ```bash
   +---------------+------------------------+-------------------------------------+------------------------------------+--------------------------+
   | engine_name   |   initial_release_year | designer                            | organization                       | current_stable_version   |
   +===============+========================+=====================================+====================================+==========================+
   | SQLite        |                   2000 | D. Richard Hipp                     | Hipp Wyrick & Company              | 3.50.1                   |
   +---------------+------------------------+-------------------------------------+------------------------------------+--------------------------+
   | PostgreSQL    |                   1986 | Michael Stonebraker                 | University of California  Berkeley | 16.4                     |
   +---------------+------------------------+-------------------------------------+------------------------------------+--------------------------+
   | MySQL         |                   1995 | Michael Widenius and David Axmark   | MySQL AB                           | 8.4                      |
   +---------------+------------------------+-------------------------------------+------------------------------------+--------------------------+
   | SQLServer     |                   1989 | Donald Chamberlin and Raymond Boyce | Microsoft Corporation              | 2022                     |
   +---------------+------------------------+-------------------------------------+------------------------------------+--------------------------+
   | DuckDB        |                   2019 | Mark Raasveldt and Hannes Muhleisen | Centrum Wiskunde & Informatica     | 1.0.0                    |
   +---------------+------------------------+-------------------------------------+------------------------------------+--------------------------+
   ```

## Directory Structure
```
project/
├── dist/
│   └── s3sql-*.*.*-py3-none-any.whl
│   └── s3sql-*.*.*.tar.gz
├── s3sql/
│   └── cli.py
├── .env
├── .gitignore
├── mycli.spec
├── poetry.lock
└── README.md
```

## Contributing
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Rebase your current branch (`git pull --rebase`)
4. Add changes to your commit (`git add .`)
4. Commit your changes (`git commit -m 'Add your feature'`)
5. Push to the branch (`git push origin feature/your-feature`)
6. Create a Pull Request

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.