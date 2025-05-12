"""Module to run the Streamlit Financial Dashboard"""
from os import environ
import pandas as pd
import streamlit as st
import pymysql.cursors
import pymysql
import altair as alt
from dotenv import load_dotenv


def get_connection() -> pymysql.connections.Connection:
    """Returns a connection object that connects to the remote database"""
    return pymysql.connections.Connection(host=environ.get('DB_HOST'),
                                          user=environ.get('DB_USER'),
                                          password=environ.get('DB_PASSWORD'),
                                          database=environ.get('DB_NAME'),
                                          cursorclass=pymysql.cursors.DictCursor)


def load_transaction_data_from_database(conn: pymysql.connections.Connection) \
        -> pd.DataFrame:
    """Returns a dataframe containing the data within the cloud database"""
    with conn.cursor() as cursor:
        cursor.execute("""SELECT event_at, payment_method, total_price, truck_id FROM
                       FACT_Transaction AS t
                       JOIN DIM_Payment_Method AS pm ON 
                       pm.payment_method_id = t.payment_method_id""")
        transaction_data_from_db = pd.DataFrame(cursor.fetchall())
        transaction_data_from_db.columns = [
            'timestamp',  'type',  'total',  'truck_id']
    return transaction_data_from_db


def draw_title(title: str):
    """Draws a title on the dashboard"""
    return st.title(title)


def add_day_column_to_data(transaction_data: pd.DataFrame) -> pd.DataFrame:
    """Returns the transaction data with an additional day column"""
    transaction_data['day_of_transaction'] = transaction_data['timestamp'].map(
        lambda row: str(row).split()[0][-2:])
    return transaction_data


def get_total_transactions_per_day(transaction_data: pd.DataFrame) -> pd.DataFrame:
    """Returns a dataframe containing the total transactions made by each day"""
    total_transactions = transaction_data.copy()

    total_transactions = add_day_column_to_data(total_transactions)
    total_transactions = total_transactions.drop(
        columns=['type', 'total', 'truck_id'])
    return total_transactions.groupby(
        ['day_of_transaction'], as_index=False)['timestamp'].count()


def get_percentage_profits_per_day(transaction_data: pd.DataFrame) -> pd.DataFrame:
    """
    Returns a dataframe containing the increase or decrease 
    in average profits per day as a percentage
    """
    percentage_of_profits = transaction_data.copy()
    percentage_of_profits = add_day_column_to_data(percentage_of_profits)

    total_average = round(percentage_of_profits['total'].sum(
    ) / percentage_of_profits['total'].count(), 2)

    average_profit_by_day = round(percentage_of_profits.groupby(
        ['day_of_transaction'], as_index=False)['total'].sum()['total'] /
        percentage_of_profits.groupby(
        ['day_of_transaction'], as_index=False)['total'].count()['total'], 2)

    average_profit_for_day = pd.DataFrame({'day_of_transaction':
                                           percentage_of_profits['day_of_transaction'].unique(
                                           ),
                                           'average_profit_by_day': average_profit_by_day
                                           })
    average_profit_for_day['percentage_profit_increase_per_day'] = \
        average_profit_for_day['average_profit_by_day'].map(
        lambda row: f'{round((row - total_average) * 100 / total_average, 1)} %')

    return average_profit_for_day


def extract_hour_and_day_from_timestamp(timestamp: str) -> str:
    """Returns a string containing the hour and date extracted from a timestamp"""
    time_of_day = ['am', 'pm']
    hour = f'{str(timestamp).split()[1][:2]} {time_of_day[0]}'

    if int(hour[:2]) > 11:
        hour = f'{str(timestamp).split()[1][:2]} {time_of_day[1]}'

    return f'{hour}, {str(timestamp).split()[0]}'


def get_total_profits_overtime_by_truck(transaction_data: pd.DataFrame) -> pd.DataFrame:
    """Returns a dataframe containing the total profits made by each truck over time"""
    total_profits = transaction_data.copy()

    total_profits['day_and_hour_of_transaction'] = total_profits['timestamp'].map(
        lambda row: extract_hour_and_day_from_timestamp(row))
    total_profits.drop(columns=['type'])

    return total_profits.groupby(
        ['truck_id', 'day_and_hour_of_transaction'], as_index=False)['total'].sum()


def get_total_transactions_and_profits_by_truck(transaction_data: pd.DataFrame) -> pd.DataFrame:
    """Returns a dataframe containing the total transactions and profits made by each truck"""
    total_transactions_profits = transaction_data.copy()

    total_transactions_profits.drop(columns=['type'])

    total_transactions_profits = \
        pd.DataFrame({'truck_id': total_transactions_profits['truck_id'].unique(),
                      'total_transactions': total_transactions_profits.groupby(
                          ['truck_id'], as_index=False)['timestamp'].count()['timestamp'],
                      'total_profits': total_transactions_profits.groupby(
                          ['truck_id'], as_index=False)['total'].sum()['total']})
    return total_transactions_profits


def get_truck_table(conn: pymysql.connections.Connection):
    """
    Returns the truck table as a dictionary with key: truck_id
    and value: fsa_rating
    """
    with conn.cursor() as cursor:
        cursor.execute("""SELECT truck_id, fsa_rating FROM
                       DIM_Truck;""")
        truck = cursor.fetchall()

    truck_table = {}
    for method in truck:
        truck_table[method['truck_id']
                    ] = method['fsa_rating']
    return truck_table


def replace_truck_id_in_column(
        truck_id: int, truck_table: dict) -> int:
    """Replaces the truck id with the corresponding fsa_rating in data"""
    if truck_table.get(truck_id) is not None:
        return truck_table.get(truck_id)
    return 0


def get_total_transactions_by_fsa_rating(conn: pymysql.connections.Connection,
                                         transaction_data: pd.DataFrame) -> pd.DataFrame:
    """Returns a dataframe containing the count of transactions by fsa rating"""
    truck_table = get_truck_table(conn)
    fsa_rating_transactions = transaction_data.copy()
    fsa_rating_transactions['fsa_rating'] = fsa_rating_transactions['truck_id'].map(
        lambda row: replace_truck_id_in_column(row, truck_table))
    fsa_rating_transactions.drop(columns=['type'])
    return fsa_rating_transactions.groupby(['fsa_rating'], as_index=False)['timestamp'].count()


def containerise_dashboard() -> tuple:
    """Returns two columns that split the dashboard into 2 halves"""
    left_column, right_column = st.columns(2)
    return left_column, right_column


def draw_chart_for_profits_by_truck(transaction_data: pd.DataFrame) -> None:
    """Draws a line chart showing the total profits made by each truck over time"""
    st.header('Total Profits by Truck Over Time')
    st.line_chart(transaction_data,
                  x='day_and_hour_of_transaction', y='total', color='truck_id')


def draw_chart_for_transactions_profits_by_truck(transaction_data: pd.DataFrame,
                                                 container: st) -> None:
    """Draws a bar chart that orders trucks by total transactions and profits"""
    with container:
        st.header('Total Profits and Transactions by Truck')
        st.bar_chart(transaction_data,
                     x='total_transactions', y='total_profits', color='truck_id')


def draw_kpis(transaction_data: pd.DataFrame, profit_data: pd.DataFrame,
              container: tuple) -> None:
    """
    Draws the KPI's of total transactions per day and the 
    percentage increase or decrease in profits based on the average per day
    """
    selected_day_t = st.multiselect(
        "Filter Transactions by day", transaction_data['day_of_transaction'],
        key='transaction'
    )
    if not selected_day_t:
        selected_day_t = ['13']
    value_at_day = transaction_data[transaction_data['day_of_transaction']
                                    == selected_day_t[0]]['timestamp']

    profit_for_day = profit_data[profit_data['day_of_transaction']
                                 == selected_day_t[0]]['percentage_profit_increase_per_day']

    with container[0]:
        st.metric("Total Transactions Today", int(value_at_day))
    with container[1]:
        st.metric("Percentage Increase from Average Profits per Day",
                  str(profit_for_day)[1:11])


def draw_chart_fsa_rating_transactions(transaction_data: pd.DataFrame,
                                       container: st) -> pd.DataFrame:
    """Draws a pie chart for total transactions by fsa rating """
    alt.data_transformers.disable_max_rows()

    base = alt.Chart(transaction_data).encode(
        theta=alt.Theta('timestamp:Q').stack(True),
        color=alt.Color('fsa_rating:N')
    ).properties(
        width=300,
        height=400,
    )

    pie = base.mark_arc(outerRadius=120)
    text = base.mark_text(radius=150, size=10).encode(
        text="timestamp:Q")
    chart = pie + text

    with container:
        st.header('Count of Transactions by FSA Rating')
        st.altair_chart(chart)


def draw_dashboard(total_transaction_by_day: pd.DataFrame,
                   percentage_profits_per_day: pd.DataFrame,
                   total_transactions_profits_by_truck: pd.DataFrame,
                   fsa_rating_transactions: pd.DataFrame,
                   total_profits_by_time: pd.DataFrame):
    """Draws the relevant elements onto the dashboard"""
    with st.container():
        draw_title('Financial Dashboard for T3')

        st.header("KPI's", divider='gray')
        kpi_one, kpi_two = containerise_dashboard()
        draw_kpis(total_transaction_by_day,
                  percentage_profits_per_day, (kpi_one, kpi_two))

        main_left_col, main_right_col = containerise_dashboard()
        draw_chart_for_transactions_profits_by_truck(
            total_transactions_profits_by_truck, main_left_col)
        draw_chart_fsa_rating_transactions(
            fsa_rating_transactions, main_right_col)
        draw_chart_for_profits_by_truck(total_profits_by_time)


def main():
    """Runs the Streamlit Financial Dashboard"""
    conn = get_connection()
    try:
        transaction_data = load_transaction_data_from_database(conn)
    except ValueError as err:
        print(err)
    finally:
        conn.close()

    total_transaction_by_day = get_total_transactions_per_day(transaction_data)
    percentage_profits_per_day = get_percentage_profits_per_day(
        transaction_data)
    total_profits_by_time = get_total_profits_overtime_by_truck(
        transaction_data)
    total_transactions_profits_by_truck = get_total_transactions_and_profits_by_truck(
        transaction_data)

    conn = get_connection()
    try:
        fsa_rating_transactions = get_total_transactions_by_fsa_rating(
            conn, transaction_data)
    except ValueError as err:
        print(err)
    finally:
        conn.close()

    draw_dashboard(total_transaction_by_day, percentage_profits_per_day,
                   total_transactions_profits_by_truck, fsa_rating_transactions,
                   total_profits_by_time)


if __name__ == '__main__':
    load_dotenv()
    main()
