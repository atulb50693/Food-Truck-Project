"""Module for ETL pipeline script"""
import logging
from argparse import ArgumentParser
import pymysql.cursors
import pymysql
from boto3 import client
import pandas as pd
from dotenv import load_dotenv
from extract import create_boto_client, get_objects_in_bucket, filter_valid_filenames_by_date, \
    create_directory_for_files, download_truck_data_files, BUCKET_NAME, \
    PATH_TO_DOWNLOAD, VALID_FILE_PATTERN, VALID_DATE, VALID_TIME, check_valid_time
from transform import get_list_of_data_files, load_truck_data_from_file, add_ids_to_column, \
    combine_transaction_data_files, remove_invalid_rows_from_total_column, \
    convert_column_data_types, filter_files_to_clean, remove_timezone_from_timestamp, \
    fix_extreme_values_that_have_a_normal_version
from load import get_connection

VALID_FILE_PATTERN_TRANSFORM = ['T3_T', '.csv']


def get_logger(log_level: str) -> logging:
    """Returns a logger with a set log level for use"""
    log = logging.getLogger(__name__)
    log.setLevel(log_level)
    return log


def setup_log_handler(is_logging: bool, log: logging.Logger,
                      formatter: logging.Formatter) -> logging.Logger:
    """
    Returns the log with the appropriate handler setup for it based on is_logging
    """
    console_handler = logging.StreamHandler()
    console_handler.setLevel("INFO")
    console_handler.setFormatter(formatter)

    if is_logging:
        file_handler = logging.FileHandler(
            './logs/message_logs.txt', mode='a', encoding='utf-8')
        file_handler.setLevel('DEBUG')
        file_handler.setFormatter(formatter)
        log.addHandler(file_handler)

        console_handler.addFilter(filter_log_messages_by_level_console)

    log.addHandler(console_handler)

    return log


def setup_formatter() -> logging.Formatter:
    """Returns a formatter for a handler"""
    formatter = logging.Formatter('{asctime} - {levelname}: {message}',
                                  style="{", datefmt='%Y-%m-%d %H:%M')
    return formatter


def filter_log_messages_by_level_console(record: logging.LogRecord) -> bool:
    """
    Returns a bool that filters log messages so that 
    only info level messages are logged
    """
    if record.levelno > logging.INFO:
        return False
    return True


def get_argument_parser() -> ArgumentParser:
    """Returns a parser for arguments given in command line"""
    parser = ArgumentParser(prog='ETL Pipeline Script',
                            description='Pipeline to automate upload of data to database.')
    parser.add_argument('-l', '--log', help='when flagged, outputs logs to a file called app.log',
                        action='store_true')
    parser.add_argument('-n', '--number', help='The number of rows to upload to database',
                        type=int, default=1_000_000)
    parser.add_argument('-p', '--path', help='specifies the path to the data files',
                        type=str, default=PATH_TO_DOWNLOAD)

    return parser


def extract_files_from_bucket(boto_client: client,
                              bucket_name: str,
                              path_to_download: str,
                              valid_files: list[str]) -> str:
    """Extracts the valid files from the S3 bucket and downloads them in ./data-files"""
    check_valid_time(VALID_TIME)
    filenames_in_bucket = get_objects_in_bucket(boto_client, bucket_name)
    files_to_download = filter_valid_filenames_by_date(
        filenames_in_bucket, valid_files, VALID_DATE, VALID_TIME)
    create_directory_for_files(path_to_download)
    download_status = download_truck_data_files(
        boto_client, files_to_download, bucket_name, path_to_download)
    return download_status


def transform_files_from_bucket(filenames: list[list[str]],
                                path_to_load: str, logger: logging.Logger) -> pd.DataFrame:
    """Transforms the data by loading into a Pandas Dataframe and then cleans it"""
    logger.info('Loading truck data...')
    truck_data = load_truck_data_from_file(
        filenames, path_to_load)
    logger.info('Transforming and cleaning truck data...')
    transformed_data = add_ids_to_column(truck_data, filenames)
    combined_data = combine_transaction_data_files(transformed_data)
    removed_invalid_rows = remove_invalid_rows_from_total_column(combined_data)
    remove_timezone = remove_timezone_from_timestamp(removed_invalid_rows)
    removed_extreme_values = fix_extreme_values_that_have_a_normal_version(
        remove_timezone)
    removed_extreme_values = removed_extreme_values.dropna()
    cleaned_truck_data = convert_column_data_types(removed_extreme_values)
    return cleaned_truck_data


def convert_dataframe_to_list(df_truck_data: pd.DataFrame) -> list[list[str]]:
    """Converts a Pandas Dataframe to a python list"""
    return df_truck_data.values.tolist()


def get_payment_method_table(conn: pymysql.connections.Connection):
    """
    Returns the payment method table as a dictionary with key: payment_method
    and value: payment_method_id
    """
    with conn.cursor() as cursor:
        cursor.execute("""SELECT payment_method_id, payment_method \
                       FROM DIM_Payment_Method;""")
        payment_method = cursor.fetchall()

    payment_method_table = {}
    for method in payment_method:
        payment_method_table[method['payment_method']
                             ] = method['payment_method_id']
    return payment_method_table


def replace_payment_method_with_id_in_column(
        transaction_data: list[list[str]], payment_table_name: dict) -> list[list[str]]:
    """Replaces the payment method with the corresponding id in data"""
    for row in transaction_data:
        payment_method = row[1]
        if payment_table_name.get(payment_method) is not None:
            row[1] = payment_table_name.get(payment_method)
    return transaction_data


def upload_transaction_data(conn: pymysql.connections.Connection,
                            transaction_data: list[list[str]],
                            number_of_rows_to_insert: int) -> None:
    """Uploads transaction data to the database."""
    if number_of_rows_to_insert == 0:
        raise ValueError(
            'Invalid number of rows to insert: value cannot be zero.')

    if number_of_rows_to_insert <= len(transaction_data):
        transaction_data = transaction_data[:number_of_rows_to_insert]
    else:
        number_of_rows_to_insert = len(transaction_data)

    with conn.cursor() as cursor:
        sql_query = """INSERT INTO FACT_Transaction \
            (event_at, payment_method_id, total_price, truck_id)
        VALUES (%s, %s, %s, %s);"""
        cursor.executemany(sql_query, tuple(transaction_data))

    conn.commit()
    return \
        f'Successfully uploaded {number_of_rows_to_insert} of transaction rows into the database.'


def main():
    """
    ETL script that downloads relevant files from S3, 
    cleans and then uploads the data to the database
    """
    # SET UP
    parsed_arguments = get_argument_parser()
    args = parsed_arguments.parse_args()

    formatter = setup_formatter()
    logger = get_logger('INFO')
    logger = setup_log_handler(
        args.log, logger, formatter)

    # EXTRACT
    s3_client = create_boto_client()
    download_status = extract_files_from_bucket(s3_client, BUCKET_NAME,
                                                args.path, VALID_FILE_PATTERN)
    logger.info(download_status)
    filenames = get_list_of_data_files(args.path)
    filenames = filter_files_to_clean(
        filenames, VALID_FILE_PATTERN_TRANSFORM)

    # TRANSFORM
    cleaned_truck_data = transform_files_from_bucket(
        filenames, args.path, logger)
    cleaned_truck_data = convert_dataframe_to_list(cleaned_truck_data)

    # LOAD
    conn = get_connection()
    try:
        payment_method_table = get_payment_method_table(conn)
        transaction_data = replace_payment_method_with_id_in_column(
            cleaned_truck_data, payment_method_table)
        upload_status = upload_transaction_data(
            conn, transaction_data, args.number)
        logger.info(upload_status)
    except ValueError as err:
        logger.error(err)
    finally:
        conn.close()


if __name__ == '__main__':
    load_dotenv()
    main()
