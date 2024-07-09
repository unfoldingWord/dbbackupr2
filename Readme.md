## Introduction
This is a simple Python script to back up databases. 
Right now, it only backs up MySQL databases, but _'maybe maybe'_ in the future 
we might want to extend to RPM and Postgres as well.

## How it works
It is **assumed** that a configuration file `/etc/dbbackupr2.conf` exists. 
An example of the file can be found in this repo as `dbbackupr2.conf`

The script makes a list of all databases existing on the MySQL host, does a
`mysqldump` per database, and then makes it into a bzip2 archive, to save space.
The resulting files, that look like `myql-my_database-2024-07-09.bz2`, 
are stored in `BACKUP_DIR`.  

Old database backups are retained for `MYSQL_KEEP_DAYS` days.

It is **assumed** that `mysqldump` and `bzip2` are available on the sytem. 
No checks are done, so the script simply raises a gory Exception when 
these CLI tools cannot be found.

It is also **assumed** that the MySQL connnection has already been defined 
via the file ~/.my.cnf:
```ini
[client]
host=<mysql hostname>
user=<mysql username>
password=<mysql password>
default-character-set = utf8mb4
```

## Builds
### Standalone binary
This script is being built into a binary with the help of [pyinstaller](https://pyinstaller.org/en/stable/), 

Running pyinstaller, when a `.venv` has been created.
```
pyinstaller --onefile --paths=.venv/lib/python3.10/site-packages dbbackupr2.py
```

I could get this script to work locally, on Python 3.10, 
but not on our server, which still has Python 3.7. Hence
the next approach...

### Docker build
Please see the included `Dockerfile`. After building, you can run the job as follows
```commandline
docker run --rm -v /path/to/backup:/config/dbbackup -v /path/to/dbbackupr2.conf:/etc/dbbackupr2.conf -v ~/.my.cnf:/root/.my.cnf myuser/dbbackupr2 
```
Mounts:
- /path/to/backup (where your backups are stored)
- /path/to/dbbackupr2.conf (your local config file)
- ~/.my.cnf (MySQL credentials)