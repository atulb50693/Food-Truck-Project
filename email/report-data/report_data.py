
"""Module that test loads a couple of rows of the cleaned data to the MySQL database"""
from os import environ
from json import dump
from datetime import datetime, timedelta
import pymysql.cursors
import pymysql
import pandas as pd
from dotenv import load_dotenv

DATE_NOW = (datetime.now().date() - timedelta(days=1)).strftime('%Y-%m-%d')
DATA_TAG_VALUES = [('<th>', '</th>'), ('<td>', '</td>')]


def get_connection() -> pymysql.connections.Connection:
    """Returns a connection object that connects to remote MySQL database"""
    return pymysql.connections.Connection(host=environ.get('DB_HOST'),
                                          user=environ.get('DB_USER'),
                                          password=environ.get('DB_PASSWORD'),
                                          database=environ.get('DB_NAME'),
                                          cursorclass=pymysql.cursors.DictCursor)


def get_previous_day_data_from_database(conn: pymysql.connections.Connection) -> pd.DataFrame:
    """Returns all the transaction data from the previous day from the database as a Dataframe"""
    with conn.cursor() as cursor:

        sql_query = """SELECT transaction_id, truck_name, payment_method, total_price, event_at,
        has_card_reader, fsa_rating
        FROM FACT_Transaction AS t
        JOIN DIM_Payment_Method AS pm ON pm.payment_method_id = t.payment_method_id 
        JOIN DIM_Truck AS d_t ON d_t.truck_id = t.truck_id
        WHERE event_at > STR_TO_DATE(CURDATE()-1, '%Y%m%d')
        ORDER BY event_at;"""

        cursor.execute(sql_query)
        previous_day_data = pd.DataFrame(cursor.fetchall())
        previous_day_data.columns = ['transaction_id', 'truck_name', 'payment_method',
                                     'total_price', 'event_at',
                                     'has_card_reader', 'fsa_rating']
        return previous_day_data


def get_total_transaction_value_all_trucks(truck_data: pd.DataFrame) -> pd.DataFrame:
    """Returns the total transactions and profits made in the day"""
    total_transaction_value = truck_data.copy()

    total_transaction_value.drop(
        columns=['has_card_reader', 'payment_method', 'event_at', 'fsa_rating', 'transaction_id'])

    total_transaction_value = \
        pd.DataFrame({'total_transactions':
                      float(total_transaction_value['total_price'].count()),
                      'total_profits':
                      float(total_transaction_value['total_price'].sum())}, index=['all_trucks'])
    return total_transaction_value


def get_total_transaction_value_by_truck(truck_data: pd.DataFrame) -> pd.DataFrame:
    """Returns the total transactions and profits made in the day by each truck"""
    total_transactions_by_truck = truck_data.copy()

    total_transactions_by_truck.drop(
        columns=['has_card_reader', 'payment_method', 'event_at'])

    total_transactions_by_truck = \
        pd.DataFrame({'truck_name': total_transactions_by_truck['truck_name'].unique(),
                      'total_transactions':
                      total_transactions_by_truck.groupby(
            ['truck_name', 'fsa_rating'], as_index=False)['event_at'].count()['event_at'],
            'total_profits': total_transactions_by_truck.groupby(
                ['truck_name', 'fsa_rating'],
            as_index=False)['total_price'].sum()['total_price']})
    total_transactions_by_truck = total_transactions_by_truck.sort_values(
        by=['total_transactions', 'total_profits'], ascending=False)
    return total_transactions_by_truck


def extract_hour_from_timestamp(timestamp: str) -> str:
    """Returns a string containing the hour and date extracted from a timestamp"""
    time_of_day = ['am', 'pm']
    hour = f'{str(timestamp).split()[1][:2]} {time_of_day[0]}'

    if int(hour[:2]) > 11:
        hour = f'{str(timestamp).split()[1][:2]} {time_of_day[1]}'

    return f'{hour}'


def get_transactions_by_time_of_day(truck_data: pd.DataFrame) -> pd.DataFrame:
    """Returns the total transactions and profits at each hour of the day"""
    transactions_by_time_of_day = truck_data.copy()

    transactions_by_time_of_day['hour_of_event'] = transactions_by_time_of_day['event_at'].map(
        lambda row: extract_hour_from_timestamp(row))

    transactions_by_time_of_day.drop(
        columns=['has_card_reader', 'payment_method', 'event_at', 'fsa_rating', 'truck_name',
                 'transaction_id'])

    transactions_by_time_of_day = \
        pd.DataFrame({'hour_of_purchase': transactions_by_time_of_day['hour_of_event'].unique(),
                      'total_transactions':
                      transactions_by_time_of_day.groupby(
                          ['hour_of_event'], as_index=False)['total_price'].count()['total_price'],
                      'total_profits': transactions_by_time_of_day.groupby(
                          ['hour_of_event'], as_index=False)['total_price'].sum()['total_price']})
    transactions_by_time_of_day = transactions_by_time_of_day.sort_values(
        by=['hour_of_purchase'])
    return transactions_by_time_of_day


def convert_key_metrics_to_dict(key_metrics: list[pd.DataFrame]) -> list[dict]:
    """Returns the dataframes as a list of dictionaries"""
    key_metrics_as_dictionary_list = []
    for table in key_metrics:
        key_metrics_as_dictionary_list.append(table.to_dict())
    return key_metrics_as_dictionary_list


def write_to_json_file(key_metrics: list[dict]):
    """Creates a JSON file from key metric data"""
    with open(f'report_data_{DATE_NOW}.json', 'w', encoding='utf-8') as f:
        dump(key_metrics, f, indent=4)


def convert_key_metrics_to_list(key_metrics: list[pd.DataFrame]) -> list[list[str]]:
    """Returns the dataframes as a list of list of strings"""
    key_metrics_as_list = []
    for table in key_metrics:
        key_metrics_as_list.append(
            [table.columns.values.tolist()] + table.values.tolist())
    return key_metrics_as_list


def create_html_table(metric: list[str]) -> str:
    """Returns a string resembling a HTML table using data passed in"""
    html_table = ['<br>', '<table>']
    data_tag = DATA_TAG_VALUES[0]
    for i, row in enumerate(metric):
        if i == 1:
            data_tag = DATA_TAG_VALUES[1]

        html_table.append('<tr>')
        for value in row:
            html_table.append(f'{data_tag[0]}{value}{data_tag[1]}')
        html_table.append('</tr>')
    html_table.append('</table>')
    html_table.append('<br>')
    return '\n'.join(html_table)


def email_html_template(key_metrics: list[dict]):
    """Returns a HTML email report from key metric data as a string"""
    html_template = \
        f"""<html>
<body>

<h1>Report on Truck Performance for {DATE_NOW}</h1>
<p>A couple of key metrics based on truck performance are listed below for the previous day:
<ul>
  <li><b>Total Transactions and Profits Made by All Trucks</b></li>
  {create_html_table(key_metrics[0])}
  <li><b>Total Transactions and Profits Made by Each Truck</b></li>
  {create_html_table(key_metrics[1])}
  <li><b>Total Transactions and Profits Made by Hour of Purchase</b></li>
  {create_html_table(key_metrics[2])}
</ul>
</p>

</body>
</html>"""
    return html_template


def write_to_html_file(key_metrics: list[dict]) -> list[dict]:
    """Creates a HTML file from key metric data"""
    with open(f'report_data_{DATE_NOW}.html', 'w', encoding='utf-8') as f:
        f.write(email_html_template(key_metrics))


def handler(event=None, context=None) -> dict:
    """
    Main Lambda handler function
    Parameters:
        event: Dict containing the Lambda function event data
        context: Lambda runtime context
    Returns:
        Dict containing html data as a string
    """
    conn = get_connection()
    transaction_data = get_previous_day_data_from_database(conn)
    conn.close()

    total_transactions_and_profits = get_total_transaction_value_all_trucks(
        transaction_data)
    total_transaction_profits_per_truck = get_total_transaction_value_by_truck(
        transaction_data)
    total_transactions_by_time_of_day = get_transactions_by_time_of_day(
        transaction_data)

    key_metrics_list = [total_transactions_and_profits,
                        total_transaction_profits_per_truck,
                        total_transactions_by_time_of_day]

    key_metrics_list = convert_key_metrics_to_list(key_metrics_list)
    html_email_report = email_html_template(key_metrics_list)
    return {
        'report': html_email_report
    }


if __name__ == "__main__":
    load_dotenv()
    print(handler())
