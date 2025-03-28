#!/usr/bin/env python3

import subprocess
import os
import time
import logging

from dotenv import load_dotenv
from datetime import datetime
import re
import pprint


class DBBackupR2:
    def __init__(self):
        # Loading environment
        if os.path.exists('./.env'):
            print('Loading environment from .env')
            load_dotenv()
        elif os.path.exists('./dbbackupr2.env'):
            print('Loading environment from .dbbackupr2.env')
            load_dotenv('./dbbackupr2.env')

        # Setup the logger
        self.__logger = self.__init_logger()

        # Internal variables
        self.__backup_dir = os.getenv('BACKUP_DIR')
        self.__db_host = os.getenv('DB_HOST')
        self.__db_user = os.getenv('DB_USER')
        self.__db_password = os.getenv('DB_PASSWORD')
        self.__compression = True if os.getenv('COMPRESS_BACKUP') == 'true' else False

    def __init_logger(self):
        this_logger = logging.getLogger()

        if not this_logger.hasHandlers():
            c_handler = logging.StreamHandler()
            if os.getenv('DEBUG') and os.getenv('DEBUG') == 'true':
                c_handler.setLevel(logging.DEBUG)
                this_logger.setLevel(logging.DEBUG)
            else:
                c_handler.setLevel(logging.INFO)
                this_logger.setLevel(logging.INFO)

            log_format = '%(asctime)s  %(levelname)-8s %(message)s'
            c_format = logging.Formatter(log_format, datefmt='%Y-%m-%d %H:%M:%S')
            c_handler.setFormatter(c_format)

            this_logger.addHandler(c_handler)

        return this_logger

    def __redact_log_line(self, logline):
        return re.sub('(-p)[A-Za-z0-9]+', '\\1HIDDEN', logline)

    def __get_databases(self):
        if os.getenv('DBS_EXCLUDED') and os.getenv('DBS'):
            if len(os.getenv('DBS_EXCLUDED')) > 0 and len(os.getenv('DBS')) > 0:
                self.__logger.fatal('Conflict: you cannot use DBS or DBS_EXCLUDED at the same time')
                return False

        # We only want certain tables
        if os.getenv('DBS'):
            lst_databases = os.getenv('DBS').split(',')

        # We want them all (possibly excluding a couple)
        else:
            lst_cmd = [
                '/usr/bin/mariadb', '-h', self.__db_host, '-u', self.__db_user, '-p' + self.__db_password,
                '-se', 'show databases;'
            ]

            self.__logger.debug(self.__redact_log_line(' '.join(lst_cmd)))

            result = subprocess.run(lst_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    universal_newlines=True)
            if result.returncode > 0:
                self.__logger.fatal('Cannot load list of databases')
                self.__logger.fatal(result.stderr)
                return False

            # split output into a list
            lst_databases = result.stdout.split('\n')

            # Exclude system objects
            if os.getenv('DBS_EXCLUDED'):
                dbs_excluded = os.getenv('DBS_EXCLUDED').split(',')

                lst_databases = list(set(lst_databases) - set(dbs_excluded))

        # Return that list of databases to back up
        return lst_databases

    def __make_backup(self, db):

        # Dump the DB
        lst_cmd = [
            '/usr/bin/mariadb-dump',
            '-h', self.__db_host,
            '-u', self.__db_user,
            '-p' + self.__db_password,
            '--routines',
            db
        ]

        if os.getenv('BACKUP_OPTS'):
            lst_cmd.insert(-1, os.getenv('BACKUP_OPTS'))

        # Log, but redact password out
        self.__logger.debug(self.__redact_log_line(' '.join(lst_cmd)))

        # Write to file
        datestamp = datetime.now().strftime('%Y-%m-%d')
        prefix = os.getenv('BACKUP_PREFIX')
        backup_file = f"{self.__backup_dir}/{prefix}-{db}-{datestamp}.sql"

        # Create backup file
        with open(backup_file, 'w') as f_backup:
            result = subprocess.run(lst_cmd, stdout=f_backup, stderr=subprocess.PIPE,
                                    universal_newlines=True, text=True)

            if result.returncode > 0:
                self.__logger.error(f'Cannot backup database {db}')
                self.__logger.error(result.stderr)
                return False

        # First line of the sql dump reads '/*!999999\- enable the sandbox mode */'
        # This line breaks the restore. We have to remove it from the backup first
        # Here, sed simply removes the first line of the backup.
        cmd = f'sed -i \'1d\' {backup_file}'
        result = subprocess.run(cmd, shell=True)
        if result.returncode > 0:
            self.__logger.error('Could not remove \'sandbox\' line from backup file')
            self.__logger.error(result.stderr)
            return False

        # Backup so far has succeeded
        return backup_file

    def __compress_backup(self, file):
        lst_cmd = [
            '/usr/bin/bzip2', '-f',
            file
        ]

        self.__logger.debug(' '.join(lst_cmd))

        result = subprocess.run(lst_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                universal_newlines=True)
        if result.returncode > 0:
            self.__logger.error(f'Could not compress file {file}')
            self.__logger.error(result.stderr)
            return False

        return True

    def restore_database(self, db, host):
        # TODO: less urgent, maybe nice to have?
        pass

    def __remove_old_backups(self, prefix, keep_days):
        path = self.__backup_dir
        now = time.time()

        for filename in os.listdir(path):
            if filename.find(prefix) == 0:  # Starts with the prefix
                full_path = os.path.join(path, filename)
                if os.path.getmtime(full_path) < now - keep_days * 86400:
                    if os.path.isfile(full_path):
                        self.__logger.info(f'Removing old backup: {full_path}')
                        os.remove(full_path)

    def backup_databases(self):
        # Remove old backups
        mysql_keep_days = int(os.getenv('MYSQL_KEEP_DAYS'))
        self.__remove_old_backups('mysql-', mysql_keep_days)

        # Get all the DB's we want to back up
        lst_databases = self.__get_databases()

        if type(lst_databases) == list:

            for db in lst_databases:
                if len(db) > 0:
                    self.__logger.info(f'Backing up database: {db}')
                    backup_file = self.__make_backup(db)
                    if backup_file:
                        if self.__compression:
                            success = self.__compress_backup(backup_file)
                            if success:
                                self.__logger.info(f'Backup file: {backup_file}.bz2')
                                self.__logger.info('Backup successful!')
                        else:
                            self.__logger.info('Backup successful!')
                    else:
                        self.__logger.info(f'Backup file: {backup_file}')


obj_dbbackup = DBBackupR2()
obj_dbbackup.backup_databases()
