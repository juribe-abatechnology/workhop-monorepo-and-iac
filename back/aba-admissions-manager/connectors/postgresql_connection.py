import psycopg2
import pandas as pd
from typing import Union
from connectors.interface_connection import InterfaceConnection

class PostgreSQLConnection(InterfaceConnection):
    """
    Connects to PostgreSQL, executes queries, and returns dataframes.
    """

    def __init__(self, host: str, port: str, database: str, user: str, password: str):
        """
        Initializes the PostgreSQLConnection object.

        Parameters:
            host (str): PostgreSQL host address.
            port (str): PostgreSQL port number.
            database (str): PostgreSQL database name.
            user (str): PostgreSQL username.
            password (str): PostgreSQL password.

        Returns:
            None

        Process:
            - Saves the provided connection details as class attributes.
        """
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.connection = None

    def connect(self):
        """
        Connects to the PostgreSQL database using the provided credentials.

        Parameters:
            None

        Returns:
            None

        Process:
            - Uses psycopg2 library to establish a connection to PostgreSQL using
              the provided host, port, database, user, and password.
            - Assigns the connection to the 'self.connection' attribute.
        """
        try:
            self.connection = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password
            )
        except Exception as e:
            raise Exception(f"Error connecting to PostgreSQL: {str(e)}")

    def disconnect(self):
        """
        Disconnects from the PostgreSQL database.

        Parameters:
            None

        Returns:
            None

        Process:
            - Closes the active PostgreSQL connection.
        """
        if self.connection is not None:
            self.connection.close()
            self.connection = None

    def execute_query(self, query: str) -> Union[pd.DataFrame, None]:
        """
        Executes a SQL query on the connected PostgreSQL database and returns the results as a DataFrame.

        Parameters:
            query (str): SQL query to execute.

        Returns:
            Union[pd.DataFrame, None]: A DataFrame containing the results of the query.
                                       Returns None if the connection is not established.

        Process:
            - Executes the provided SQL query on the PostgreSQL database using the
              active connection.
            - Fetches the results and converts them into a pandas DataFrame.
            - Returns the DataFrame or None if the connection is not established.
        """
        try:
            # Connect to the database if not connected already
            if self.connection is None:
                self.connect()
                
            # Remove leading comments, if any
            clean_query = query.strip().lstrip('-')
                
            with self.connection.cursor() as cursor:
                # Execute the query without parameters
                cursor.execute(clean_query)
                
                
                if query.strip().lower().startswith("insert") | query.strip().lower().startswith("update"):
                    # For other queries (e.g., INSERT, UPDATE), commit the transaction
                    self.connection.commit()
                    
                    # No result to return for non-SELECT queries
                    return None
                else:
                    # If it's a SELECT query, fetch the result and construct a DataFrame
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
