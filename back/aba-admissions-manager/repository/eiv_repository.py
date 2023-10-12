import pandas as pd
from typing import List
from connectors.interface_connection import InterfaceConnection
from connectors.postgresql_connection import PostgreSQLConnection
from connectors.snowflake_connection import SnowflakeConnection
from repository.interface_repository import InterfaceRepository
from datetime import datetime

class EIVRepository(InterfaceRepository):
    """
    Manage SQL queries for reading and writing eiv information.

    Variables:
        connectors (List[InterfaceConnection]): A list of database connectors (e.g., PostgreSQLConnection, SnowflakeConnection).

    Interactions:
        - Interacts with PostgreSQLConnection and SnowflakeConnection classes for database operations.
    """

    def __init__(self, connectors: List[InterfaceConnection]):
        """
        Initializes the EIVRepository object.

        Parameters:
            connectors (List[InterfaceConnection]): A list of InterfaceConnection objects.

        Returns:
            None

        Process:
            - Calls the constructor of the InterfaceRepository to save the provided InterfaceConnection objects as class attributes.
        """
        super().__init__(connectors)

    def retrieve_data(self, query: str) -> pd.DataFrame:
        """
        Retrieves data from the database using the provided query.

        Parameters:
            query (str): SQL query to retrieve data.

        Returns:
            pd.DataFrame: A DataFrame containing the query results.

        Process:
            - Calls the 'retrieve_data_from_snowflake()' method to execute the provided query and get the results as a DataFrame.
            - Returns the DataFrame.
        """
        return self.retrieve_data_from_snowflake(query)

    def save_data(self, data: pd.DataFrame, table_name: str) -> None:
        """
        Saves data to the database table.

        Parameters:
            data (pd.DataFrame): DataFrame containing the data to be saved.
            table_name (str): Name of the database table to save the data.

        Returns:
            None

        Process:
            - Calls the 'save_data_to_postgresql()' method to save the provided data in the specified table.
        """
        self.save_data_to_postgresql(data, table_name)

    def retrieve_data_from_snowflake(self, query: str) -> pd.DataFrame:
        """
        Retrieves data from Snowflake using the provided query.

        Parameters:
            query (str): SQL query to retrieve data.

        Returns:
            pd.DataFrame: A DataFrame containing the query results.

        Process:
            - Calls the 'execute_query()' method of the appropriate SnowflakeConnection instance
              to execute the provided query and get the results as a DataFrame.
            - Returns the DataFrame.
        """
        try:
            for connector in self.connectors:
                if isinstance(connector, SnowflakeConnection):
                    return connector.execute_query(query)

            raise Exception("No SnowflakeConnection found in the list of connectors.")
        except Exception as e:
            raise Exception(f"Error retrieving data from Snowflake: {str(e)}")

    def save_data_to_postgresql(self, data: pd.DataFrame, table_name: str) -> None:
        """
        Saves data to PostgreSQL table.

        Parameters:
            data (pd.DataFrame): DataFrame containing the data to be saved.
            table_name (str): Name of the PostgreSQL table to save the data.

        Returns:
            None

        Process:
            - Calls the 'execute_query()' method of the appropriate PostgreSQLConnection instance
              to insert or update the provided data in the specified table.
            - If the 'claim_id' and 'prediction_date' exist in the table, the 'future_collected_cash'
              column will be updated. Otherwise, a new row will be inserted.
        """
        try:
            for connector in self.connectors:
                if isinstance(connector, PostgreSQLConnection):
                    
                    query = ''
                    
                    for _, row in data.iterrows():
                        vob_id = row['VOB_ID'] if row['VOB_ID'] is not None else '001'
                        client_name = row['CLIENT_NAME']
                        prediction_date = datetime.now().date()
                        SCA_EIV_percentage = row['SCA_EIV_percentage']
                        SCA_EIV_money = row['SCA_EIV_money']
                        SCA_client_type = row['SCA_client_type']
                        SCA_probability = row['SCA_probability']
                        SCA_z_score = row['SCA_z_score']
                        SCA_financial_status = row['SCA_financial_status']
                        NSCA_EIV_percentage = row['NSCA_EIV_percentage']
                        NSCA_EIV_money = row['NSCA_EIV_money']
                        NSCA_client_type = row['NSCA_client_type']
                        NSCA_probability = row['NSCA_probability']
                        NSCA_z_score = row['NSCA_z_score']
                        NSCA_financial_status = row['NSCA_financial_status'] 
                        time_stamp = datetime.now()

                        query = query + f"""
                            INSERT INTO {table_name} (vob_id, CLIENT_NAME, prediction_date, 
                              SCA_EIV_percentage, SCA_EIV_money, SCA_client_type, SCA_probability,
                              SCA_z_score, SCA_financial_status, NSCA_EIV_percentage, NSCA_EIV_money, 
                              NSCA_client_type, NSCA_probability, NSCA_z_score, NSCA_financial_status, 
                              timestamp)
                            VALUES ('{vob_id}','{client_name}', '{prediction_date}', 
                              '{SCA_EIV_percentage}', '{SCA_EIV_money}', '{SCA_client_type}', '{SCA_probability}',
                              '{SCA_z_score}', '{SCA_financial_status}', '{NSCA_EIV_percentage}', '{NSCA_EIV_money}', 
                              '{NSCA_client_type}', '{NSCA_probability}', '{NSCA_z_score}', '{NSCA_financial_status}',
                              '{time_stamp}')
                            ON CONFLICT (vob_id, prediction_date)
                            DO UPDATE SET vob_id = '{vob_id}', CLIENT_NAME = '{client_name}', prediction_date = '{prediction_date}', 
                              SCA_EIV_percentage = '{SCA_EIV_percentage}', SCA_EIV_money = '{SCA_EIV_money}', 
                              SCA_client_type = '{SCA_client_type}', SCA_probability = '{SCA_probability}',
                              SCA_z_score = '{SCA_z_score}', SCA_financial_status = '{SCA_financial_status}', 
                              NSCA_EIV_percentage = '{NSCA_EIV_percentage}', NSCA_EIV_money = '{NSCA_EIV_money}', 
                              NSCA_client_type = '{NSCA_client_type}', NSCA_probability = '{NSCA_probability}', 
                              NSCA_z_score = '{NSCA_z_score}', NSCA_financial_status = '{NSCA_financial_status}',
                              timestamp = '{time_stamp}';
                        """

                    connector.execute_query(query)

                    return

            raise Exception("No PostgreSQLConnection found in the list of connectors.")
        except Exception as e:
            raise Exception(f"Error saving data to PostgreSQL: {str(e)}")
