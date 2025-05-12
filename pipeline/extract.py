"""Module for downloading the relevant truck data from the S3 bucket"""
from os import environ
import sys
from pathlib import Path
from datetime import datetime
from boto3 import client

BUCKET_NAME = 'sigma-resources-truck'
VALID_FILE_PATTERN = ['trucks/', '.csv']
VALID_DATE = datetime.now().date().strftime('%Y-%-m/%-d')
VALID_TIME = datetime.now().hour
VALID_TIMES = [12, 15, 18, 21]
PATH_TO_DOWNLOAD = f'./data-files/{VALID_DATE}/{VALID_TIME}'


def create_boto_client():
    """Returns a boto3 client"""
    return client('s3',
                  aws_access_key_id=environ.get('aws_access_key_id'),
                  aws_secret_access_key=environ.get('aws_secret_access_key'))


def check_valid_time(hour: str) -> None:
    """Exits the program if the hour isn't correct"""
    if hour not in VALID_TIMES:
        print('No new truck files at this time.')
        sys.exit()


def identify_different_files_in_bucket(boto_client: client) -> list[str]:
    """Returns a list of all buckets for a user"""
    response = boto_client.list_buckets(
        MaxBuckets=123,
    )
    bucket_names = []
    for bucket in response['Buckets']:
        bucket_names.append(bucket['Name'])
    return bucket_names


def get_objects_in_bucket(boto_client: client, bucket_name: str) -> list[str]:
    """Returns a list of all the files present in a specific bucket"""
    response = boto_client.list_objects_v2(
        Bucket=bucket_name
    )
    filenames = []
    for file in response['Contents']:
        filenames.append(file['Key'])
    return filenames


def filter_valid_filenames_by_date(filenames: list[str],
                                   file_pattern: list[str],
                                   valid_date: str,
                                   valid_time: str) -> list[str]:
    """Filters out the relevant files based on naming convention used"""
    valid_filenames = []
    for file in filenames:
        if file.startswith(f'{file_pattern[0]}{valid_date}/{valid_time}/T3') \
                and file.endswith(file_pattern[1]):
            valid_filenames.append(file)
    return valid_filenames


def create_directory_for_files(path: str):
    """Creates a directory for the downloaded data files"""
    Path(path).mkdir(parents=True, exist_ok=True)


def download_truck_data_files(boto_client: client, files_to_download: list[str],
                              bucket_name: str, path: str) -> str:
    """Downloads relevant files from S3 to a data/ folder."""
    for file in files_to_download:
        filename = file.split('/')[-1]
        boto_client.download_file(
            bucket_name, file, f'{path}/{filename}')
    return 'Successfully downloaded files.'


def main():
    """Runs the process of extracting the files from S3"""
    check_valid_time(VALID_TIME)
    s3_client = create_boto_client()
    buckets_for_user = identify_different_files_in_bucket(s3_client)
    print(buckets_for_user)
    filenames_present = get_objects_in_bucket(s3_client, BUCKET_NAME)
    filtered_filenames = filter_valid_filenames_by_date(
        filenames_present, VALID_FILE_PATTERN, VALID_DATE, VALID_TIME)
    print(filtered_filenames)
    create_directory_for_files(PATH_TO_DOWNLOAD)
    download_status = download_truck_data_files(
        s3_client, filtered_filenames, BUCKET_NAME, PATH_TO_DOWNLOAD)
    print(download_status)


if __name__ == "__main__":
    main()
