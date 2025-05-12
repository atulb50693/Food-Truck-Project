"""Module that formats and cleans the truck data before writing to a .csv file"""
from os import listdir
from datetime import datetime
import pandas as pd


VALID_FILE_PATTERN = ['T3_', '.csv']
VALID_DATE = datetime.now().date().strftime('%Y-%-m/%-d')
VALID_TIME = datetime.now().hour
PATH_TO_LOAD_DATA = f'./data-files/{VALID_DATE}/{VALID_TIME}'
CSV_FILENAME = 'TRUCK_HIST_DATA.csv'


def get_list_of_data_files(path_to_load: str):
    """Returns a list of files in the ./data-files directory"""
    return listdir(path_to_load)


def load_truck_data_from_file(filenames: list[str], path_to_load: str) -> list[pd.DataFrame]:
    """Loads all the truck data from each file into a pandas dataframe"""
    loaded_truck_data = []
    for filename in filenames:
        loaded_truck_data.append(pd.read_csv(
            f'{path_to_load}/{filename}'))
    return loaded_truck_data


def filter_files_to_clean(filenames: list[str], file_pattern: list[str]) -> list[str]:
    """Filters out the relevant files based on naming convention used"""
    valid_filenames = []
    for file in filenames:
        if file.startswith(f'{file_pattern[0]}') and file.endswith(file_pattern[1]):
            valid_filenames.append(file)
    return valid_filenames


def add_ids_to_column(truck_data: list[pd.DataFrame], filenames: list[str]) -> list[pd.DataFrame]:
    """Returns all the pandas dataframes with the relevant truck id taken from filename"""
    for truck, file in zip(truck_data, filenames):
        truck_id = ''.join(file.split('T3_T')[1])[0]
        truck['truck_id'] = truck_id
        truck.columns = ['timestamp', 'type', 'total', 'truck_id']
    return truck_data


def combine_transaction_data_files(truck_data: list[pd.DataFrame]) -> pd.DataFrame:
    """Combines the dataframes containing each truck's transaction data
    into one pandas dataframe"""
    data_for_csv_file = pd.concat(truck_data).reset_index(drop=True)
    return data_for_csv_file


def validate_if_invalid_row(row_value: str) -> str:
    """Returns the value 'None' for any invalid rows otherwise it's original value"""
    if '-' in str(row_value):
        return 'None'

    if row_value in {'0', '0.00', '0.0', '0. '}:
        return 'None'

    if (isinstance(row_value, (float, int))) and row_value in {0, 0.0, 0.00, 0.}:
        return 'None'

    if (isinstance(row_value, (float, int))):
        return row_value

    if row_value == '' or row_value.lower() == 'void' or \
            row_value == 'NULL' or row_value == 'None':
        return 'None'

    if row_value.lower() == 'blank' \
            or row_value == 'ERR' or '-' in row_value or row_value == 'extreme':
        return 'None'

    return row_value


def remove_invalid_rows_from_total_column(truck_data: pd.DataFrame) -> pd.DataFrame:
    """Removing any rows where the total column is zero, blank, NULL or VOID
    Discarding invalid rows"""
    truck_data['total'] = truck_data['total'].map(
        lambda row: validate_if_invalid_row(row))
    indexes_of_invalid_columns = truck_data[truck_data['total']
                                            == 'None'].index
    truck_data = truck_data.drop(indexes_of_invalid_columns)
    truck_data = truck_data.dropna()
    return truck_data


def remove_timezone_from_timestamp(truck_data: pd.DataFrame) -> pd.DataFrame:
    """Returns dataframe with timestamp reduced to the format: YYYY-MM-DD HH:MM:SS"""
    truck_data['timestamp'] = truck_data['timestamp'].map(
        lambda row: row[:-6])
    return truck_data


def convert_column_data_types(truck_data: pd.DataFrame) -> pd.DataFrame:
    """Converting columns to the most appropriate data type or format"""
    truck_data = truck_data.astype({'timestamp': 'datetime64[ns]', 'type': str, 'total': float,
                                    'truck_id': int})
    return truck_data


def is_extreme_value_and_have_normal_version(row_value: float,
                                             valid_normal_values: list[float]) -> float:
    """
    Returns legitimate extreme values that could be mistyped 
    based on other values in the truck, corrected
    e.g: 499.0 to 4.99
    """
    if row_value < 50:
        return row_value

    normal_row = list(filter(lambda number: number != '.',
                             str(row_value)))

    if len(normal_row) == 3:
        normal_row.insert(0, '0')

    normal_row.insert(1, '.')
    normal_row.pop(-1)
    normal_row = ''.join(normal_row)
    if normal_row in valid_normal_values:
        return normal_row
    return None


def fix_extreme_values_that_have_a_normal_version(truck_data: pd.DataFrame) -> pd.DataFrame:
    """Returns a dataframe with corrected or removed extreme values"""
    normal_values = list(truck_data['total'].unique())
    valid_normal_values = list(
        filter(lambda val: 0 < float(val) < 50, normal_values))

    truck_data['total'] = truck_data['total'].map(
        lambda row: is_extreme_value_and_have_normal_version(float(row), valid_normal_values))
    return truck_data


def write_to_csv_file(data_for_csv: pd.DataFrame, path_to_write_to: str) -> None:
    """Writes the truck data as a pandas dataframe to a csv file"""
    data_for_csv.to_csv(path_to_write_to, index=False)


def main():
    """Transforms the truck data into a clean and single .csv file"""
    filenames = get_list_of_data_files(PATH_TO_LOAD_DATA)
    print('Loading truck data...')
    filtered_filenames = filter_files_to_clean(
        filenames, VALID_FILE_PATTERN)
    truck_data = load_truck_data_from_file(
        filtered_filenames, PATH_TO_LOAD_DATA)
    print('Transforming and cleaning truck data...')
    transformed_data = add_ids_to_column(truck_data, filtered_filenames)
    combined_data = combine_transaction_data_files(transformed_data)
    removed_invalid_rows = remove_invalid_rows_from_total_column(combined_data)
    remove_timezone = remove_timezone_from_timestamp(removed_invalid_rows)
    cleaned_data = fix_extreme_values_that_have_a_normal_version(
        remove_timezone)
    cleaned_data = cleaned_data.dropna()
    converted_column_types = convert_column_data_types(cleaned_data)
    print(f'Writing truck data to {PATH_TO_LOAD_DATA}/{CSV_FILENAME}...')
    write_to_csv_file(converted_column_types,
                      f'{PATH_TO_LOAD_DATA}/{CSV_FILENAME}')
    print('Successfully transformed truck data.')


if __name__ == "__main__":
    main()
