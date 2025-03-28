## Introduction
This is a simple Python script to back up databases. 
Right now, it only backs up MySQL databases, but _'maybe maybe'_ in the future 
we might want to extend to RPM and Postgres as well.

## How it works
All settings are read from the environment. The script first tries to read the file `.env`. 
If not found, it will then try to read `dbbackupr2.env`. If that is not found either, the script will
simply assume the existence of the needed environment variables. Unset variables will result in unexpected results.
An example of the needed variables can be found in `dbbackupr2.env`.

The script makes a list of all databases existing on the MySQL/MariaDB host, does a
`mysqldump` per database, and then makes it into a bzip2 archive, to save space.
The resulting files, that look like `myql-my_database-2024-07-09.bz2`, 
are stored in `BACKUP_DIR`.  

Old database backups are retained for `MYSQL_KEEP_DAYS` days.

It is **assumed** that `mysqldump` and `bzip2` are available on the sytem. 
No checks are done, so the script simply raises a gory Exception when 
these CLI tools cannot be found.

## Builds
### Standalone binary
One beautiful day, I would like to see this script being built into a binary with the help of [pyinstaller](https://pyinstaller.org/en/stable/), 

Running pyinstaller, when a `.venv` has been created.
```
pyinstaller --onefile --paths=.venv/lib/python3.10/site-packages dbbackupr2.py
```

### Running with a .venv
Setup your .venv, install the requirements, and run.
Maybe instructions coming soon...

### Docker build
Please see the included `Dockerfile`. After building, you can run the job as follows
```commandline
docker run -it --rm --env-file /path/to/dbbackupr2.env -v /path/to/backup:/dbbackup myuser/dbbackupr2 
```

File paths:
- `/path/to/dbbackupr2.env` (your local environment file)
- `/path/to/backup` (where your backups are stored)