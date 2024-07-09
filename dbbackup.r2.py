#!/usr/bin/env python3

import subprocess
import os
#from dotenv import load_dotenv
from datetime import datetime


class DBBackupR2:
    def __init__(self):
        #load_dotenv()

        #self.backup_dir = os.getenv('BACKUP_DIR')
        self.backup_dir = '/config/dbbackup'

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
            '/usr/bin/bzip2',
            file
        ]

        result = subprocess.run(lst_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                universal_newlines=True)
        if result.returncode > 0:
            print(result.stderr)
            return False

        return True

    def restore_database(self, db, host):
        # TODO: less urgent, more like nice to have
        pass

    def __remove_old_backups(self):
        # TODO: needs to be implemented soon
        pass

    def backup_databases(self):
        # TODO: should I enable removal of old backup file?

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
