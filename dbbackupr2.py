#!/usr/bin/env python3

import subprocess
import os
import time
from dotenv import dotenv_values
from datetime import datetime


class DBBackupR2:
    def __init__(self):
        self.__config = dotenv_values("/etc/dbbackupr2.conf")

        self.backup_dir = self.__config['BACKUP_DIR']

    def __get_databases(self, exclude_system=True):
        lst_cmd = [
            'mysql', 'mysql',
            '-se', 'show databases;'
        ]

        result = subprocess.run(lst_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                universal_newlines=True)
        if result.returncode > 0:
            print(result.stderr)

        # split output into a list
        lst_databases = result.stdout.split('\n')

        # remove first element (header)
        lst_databases.pop(0)

        # Exclude system objects
        if exclude_system:
            exclude_dbs = ['information_schema', 'mysql', 'performance_schema', 'sys']

            lst_databases = set(lst_databases) - set(exclude_dbs)

        return lst_databases

    def __make_backup(self, db):
        lst_cmd = [
            '/usr/bin/mysqldump',
            db
        ]

        # Write to file
        datestamp = datetime.now().strftime('%Y-%m-%d')
        backup_file = f"{self.backup_dir}/mysql-{db}-{datestamp}.sql"

        with open(backup_file, 'w') as f_backup:
            result = subprocess.run(lst_cmd, stdout=f_backup, stderr=subprocess.PIPE,
                                    universal_newlines=True)
            if result.returncode > 0:
                print(result.stderr)

        return backup_file

    def __compress_backup(self, file):
        lst_cmd = [
            '/usr/bin/bzip2', '-f',
            file
        ]

        result = subprocess.run(lst_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                universal_newlines=True)
        if result.returncode > 0:
            print(result.stderr)
            return False

        return True

    def restore_database(self, db, host):
        # TODO: less urgent, maybe nice to have?
        pass

    def __remove_old_backups(self, prefix, keep_days):
        path = self.backup_dir
        now = time.time()

        for filename in os.listdir(path):
            if filename.find(prefix) == 0:  # Starts with the prefix
                full_path = os.path.join(path, filename)
                if os.path.getmtime(full_path) < now - keep_days * 86400:
                    if os.path.isfile(full_path):
                        print(f'Removing: {full_path}')
                        os.remove(full_path)

    def backup_databases(self):
        # Remove old backups
        mysql_keep_days = int(self.__config['MYSQL_KEEP_DAYS'])
        self.__remove_old_backups('mysql-', mysql_keep_days)

        # Get all the DB's we want to back up
        lst_databases = self.__get_databases()

        for db in lst_databases:
            if len(db) > 0:
                print(f'Backing up: {db}')
                backup_file = self.__make_backup(db)
                success = self.__compress_backup(backup_file)
                if success:
                    print('Succeeded!')


obj_dbbackup = DBBackupR2()
obj_dbbackup.backup_databases()
