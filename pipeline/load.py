"""Module that test loads a couple of rows of the cleaned data to the MySQL database"""
from os import environ
import csv
import pymysql.cursors
import pymysql
from dotenv import load_dotenv

PATH_TO_LOAD = './data-files/'
TRANSACTION_FILE = 'TRUCK_HIST_DATA.csv'


def get_connection() -> pymysql.connections.Connection:
    """Returns a connection object that connects to remote MySQL database"""
    return pymysql.connections.Connection(host=environ.get('DB_HOST'),
                                          user=environ.get('DB_USER'),
                                          password=environ.get('DB_PASSWORD'),
                                          database=environ.get('DB_NAME'),
                                          cursorclass=pymysql.cursors.DictCursor)


def load_transaction_data_from_file(filename: str) -> list[list[str]]:
    """Returns a list of the transaction data from the csv file in /data-files"""
    data = []
    with open(f'{PATH_TO_LOAD}{filename}', 'r', encoding='utf-8') as f:
        transaction_data = csv.reader(f)
        for line in transaction_data:
            data.append(line)
    return data


def replace_payment_method_with_id_in_column(
        transaction_data: list[list[str]]) -> list[list[str]]:
    """Returns the modified dataframe with the payment method replaced with the id"""
    payment_method_table = {'cash': 1, 'card': 2}
    for row in transaction_data:
        payment_method = row[1]
        if payment_method_table.get(payment_method) is not None:
            row[1] = payment_method_table.get(payment_method)
    return transaction_data


def upload_transaction_data(conn: pymysql.connections.Connection,
                            transaction_data: list[list[str]]) -> None:
    """Uploads transaction data to the database."""

    with conn.cursor() as cursor:
        sql_query = \
            """INSERT INTO FACT_Transaction \
                (event_at, payment_method_id, total_price, truck_id)
          VALUES (%s, %s, %s, %s);"""
        cursor.executemany(sql_query, tuple(transaction_data))

    conn.commit()
    return 'Successfully uploaded transaction data to the database.'


def main():
    """Loads the truck data into the remote MySQL database"""
    truck_data = load_transaction_data_from_file(TRANSACTION_FILE)[1:11]
    truck_data = replace_payment_method_with_id_in_column(
        truck_data)
    connection = get_connection()
    print(upload_transaction_data(connection, truck_data))


if __name__ == "__main__":
    load_dotenv()
    main()
