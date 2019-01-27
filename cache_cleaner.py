########################################################################
# Script will clean useless files from local cache.                    #
# Files are deemed useless when there exists an experiment with status #
# set to 'finished'.                                                   #
# Files without corresponding experiment in database won't be deleted. #
# Inconsistency like that shouldn't happen too often but...            #
# better be safe than sorry...                                         #
########################################################################
import os
import time
from rtt_pyutils.RttConfigParser import RttConfigParser
from rtt_pyutils.Utilities import Utilities
from rtt_pyutils.MySQLDatabaseInfo import MySQLDatabaseInfo

# Don't change these constants without good reason.
# TODO: Set this to something like 60 seconds after finishing development
secs_between_loops = 10

# Script initialization
script_name = Utilities.get_script_name(__file__)
script_cnf_file_path = Utilities.get_default_script_config_path(script_name)
script_logger = Utilities.init_basic_logger(script_name)


def delete_cache_files(exp_id, cache_data_dir, cache_config_dir):
    cache_data_file = os.path.join(cache_data_dir, f"{exp_id}.bin")
    cache_config_file = os.path.join(cache_config_dir, f"{exp_id}.json")
    if os.path.exists(cache_data_file):
        script_logger.info(f"Deleting file {cache_data_file}")
        # TODO remove comment
        # os.remove(cache_data_file)
    else:
        script_logger.info(f"File is not in local cache: {cache_data_file}")

    if os.path.exists(cache_config_file):
        script_logger.info(f"Deleting file {cache_config_file}")
        # TODO remove comment
        # os.remove(cache_config_file)
    else:
        script_logger.info(f"File is not in local cache: {cache_config_file}")


def clean_cache(cnf_file_path):
    main_cnf = RttConfigParser(cnf_file_path)
    cache_data_dir = main_cnf.safe_get("Local-cache", "Data-directory")
    cache_config_dir = main_cnf.safe_get("Local-cache", "Config-directory")
    
    with Utilities.create_mysql_database_connection(MySQLDatabaseInfo.get_from_cnf(main_cnf)) as db:
        with db.cursor() as cursor:
            for data_file in sorted(os.listdir(cache_data_dir)):
                exp_id = int(os.path.splitext(os.path.basename(data_file))[0])
                cursor.execute("SELECT status FROM experiments WHERE id=%s", (exp_id,))

                if cursor.rowcount == 1:
                    row = cursor.fetchone()
                    if row[0] == 'finished':
                        script_logger.info(f"Deleting cached experiment files: {exp_id}")
                        delete_cache_files(exp_id, cache_data_dir, cache_config_dir)
                    else:
                        # This is reported only during development
                        # TODO: Remove this else branch after testing
                        script_logger.info(f"Experiment is not yet finished: {exp_id}")


if __name__ == "__main__":
    script_logger.info(f"Starting script {script_name}")

    try:
        while True:
            try:
                # Error during execution will not break subsequent iterations
                Utilities.run_with_timeout(script_logger, lambda: clean_cache(script_cnf_file_path))
                time.sleep(secs_between_loops)
            except Exception as ex:
                script_logger.error(f"executing main function: {ex}")

    except Exception as ex:
        script_logger.error(f"unrecoverable error: {ex}")

