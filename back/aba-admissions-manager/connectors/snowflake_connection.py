import pandas as pd
from snowflake.connector import connect
from typing import Union
from connectors.interface_connection import InterfaceConnection

class SnowflakeConnection(InterfaceConnection):
    """
    Connects to Snowflake, executes queries, and returns dataframes.
    """

    def __init__(self, account: str, user: str, password: str, database: str, 
                 schema: str, warehouse: str, role: str):
        """
        Initializes the SnowflakeConnection object.

        Parameters:
            account (str): Snowflake account name.
            user (str): Snowflake username.
            password (str): Snowflake password.
            database (str): Snowflake database.
            schema (str): Snowflake schema.
            warehouse (str): Snowflake warehouse name.
            role (str): Snowflake role name.

        Returns:
            None

        Process:
            - Saves the provided connection details as class attributes.
        """
        self.account = account
        self.user = user
        self.password = password
        self.database = database
        self.schema = schema
        self.warehouse = warehouse
        self.role = role
        self.connection = None

    def connect(self):
        """
        Connects to Snowflake using the provided credentials.

        Parameters:
            None

        Returns:
            None

        Process:
            - Uses snowflake.connector library to establish a connection to Snowflake
              using the provided account, user, password, database, schema, warehouse, 
              and role.
            - Assigns the connection to the 'self.connection' attribute.
        """
        try:
            self.connection = connect(
                account=self.account,
                user=self.user,
                password=self.password,
                database=self.database,
                schema=self.schema,
                warehouse=self.warehouse
            )
        except Exception as e:
            raise Exception(f"Error connecting to Snowflake: {str(e)}")

    def disconnect(self):
        """
        Disconnects from the Snowflake database.

        Parameters:
            None

        Returns:
            None

        Process:
            - Closes the active Snowflake connection.
        """
        if self.connection is not None:
            self.connection.close()
            self.connection = None

    def execute_query(self, query: str) -> Union[pd.DataFrame, None]:
        """
        Executes a SQL query on the connected Snowflake database and returns the results as a DataFrame.

        Parameters:
            query (str): SQL query to execute.

        Returns:
            Union[pd.DataFrame, None]: A DataFrame containing the results of the query.
                                       Returns None if the connection is not established.

        Process:
            - Executes the provided SQL query on the Snowflake database using the
              active connection.
            - Fetches the results and converts them into a pandas DataFrame.
            - Returns the DataFrame or None if the connection is not established.
        """
        try:
            # Connect to the database if not connected already
            if self.connection is None:
                self.connect()
                
            # Remove leading comments, if any
            # clean_query = query.strip().lstrip('-')

            with self.connection.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchall()
                
                cursor.close()
                self.disconnect()

                if result:
                    columns = [desc[0] for desc in cursor.description]
                    df = pd.DataFrame(result, columns=columns)
                    return df
                else:
                    return pd.DataFrame()

        except Exception as e:

            raise Exception(f"Error executing query: {str(e)}")
