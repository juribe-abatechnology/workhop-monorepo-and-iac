from typing import Union
import pandas as pd

class InterfaceConnection:
    """
    Interface for implementing other database connection classes.
    """

    def __init__(self):
        """
        Initializes the InterfaceConnection object.

        Parameters:
            None

        Returns:
            None

        Process:
            This is an abstract class and should not be instantiated directly.
        """
        pass

    def connect(self):
        """
        Connects to the database.

        Parameters:
            None

        Returns:
            None

        Process:
            This is an abstract method that should be implemented in the child classes.
            It is responsible for establishing a connection to the specific database.
        """
        raise NotImplementedError("connect() method must be implemented in the child class.")

    def disconnect(self):
        """
        Disconnects from the database.

        Parameters:
            None

        Returns:
            None

        Process:
            This is an abstract method that should be implemented in the child classes.
            It is responsible for closing the active connection to the database.
        """
        raise NotImplementedError("disconnect() method must be implemented in the child class.")

    def execute_query(self, query: str) -> Union[pd.DataFrame, None]:
        """
        Executes a SQL query on the connected database and returns the results as a DataFrame.

        Parameters:
            query (str): SQL query to execute.

        Returns:
            Union[pd.DataFrame, None]: A DataFrame containing the results of the query.
                                       Returns None if the connection is not established.

        Process:
            This is an abstract method that should be implemented in the child classes.
            It is responsible for executing the provided SQL query on the database and
            returning the results as a pandas DataFrame. If the connection is not established,
            it should return None.
        """
        raise NotImplementedError("execute_query() method must be implemented in the child class.")
